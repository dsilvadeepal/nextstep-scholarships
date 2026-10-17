import subprocess
import sys


def test_cli_help_and_offline_run_fail_before_any_paid_provider():
    result = subprocess.run(
        [sys.executable, "-m", "nextstep.ingest.cli", "--help"],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0 and "collect" in result.stdout
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nextstep.ingest.cli",
            "run",
            "--sources",
            "data/sources.yaml",
            "--version",
            "test",
        ],
        capture_output=True,
        check=False,
        text=True,
        env={**__import__("os").environ, "LIVE_CALLS_ENABLED": "false"},
    )
    assert result.returncode != 0 and "disabled" in result.stderr.lower()


def test_rollback_requires_no_paid_access(tmp_path, monkeypatch):
    from nextstep.db import metadata
    from nextstep.ingest.cli import main
    from nextstep.models import Scholarship
    from nextstep.repository import Repository
    from sqlalchemy import create_engine

    url = f"sqlite:///{tmp_path}/rollback.db"
    engine = create_engine(url)
    metadata.create_all(engine)
    repo = Repository(engine)
    for v in ["old", "new"]:
        repo.stage_catalog(v, [Scholarship(id="s", name="S", corpus_version=v)])
        repo.mark_ready(v)
    repo.activate_version(None, "new")
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("LIVE_CALLS_ENABLED", "false")
    main(["rollback", "--version", "old", "--artifacts", str(tmp_path / "artifacts")])
    assert repo.active_version() == "old"


def test_interrupted_staging_resumes_and_rejects_changed_chunks(tmp_path):
    import pytest
    from nextstep.db import metadata
    from nextstep.ingest.cli import stage_or_resume
    from nextstep.models import Chunk, Scholarship
    from nextstep.repository import Repository
    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{tmp_path}/resume.db")
    metadata.create_all(engine)
    repo = Repository(engine)
    records = [Scholarship(id="a", name="A", corpus_version="v")]
    chunks = [
        Chunk(
            id="c",
            program_id="a",
            source_id="s",
            corpus_version="v",
            text="Rule",
            heading="A",
            section_ids=["s"],
            token_count=1,
        )
    ]
    repo.stage_catalog("v", records)
    stage_or_resume(repo, "v", records, chunks)
    assert repo.get_chunks("v") == chunks
    stage_or_resume(repo, "v", records, chunks)
    with pytest.raises(ValueError):
        stage_or_resume(
            repo, "v", records, [chunks[0].model_copy(update={"text": "different"})]
        )
