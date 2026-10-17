import pytest
from fastapi.testclient import TestClient
from nextstep.app import create_app
from nextstep.config import Settings
from nextstep.db import metadata
from sqlalchemy import create_engine


def test_configured_database_and_admin_boundary(tmp_path):
    url = f"sqlite:///{tmp_path}/app.db"
    metadata.create_all(create_engine(url))
    app = create_app(Settings(database_url=url))
    with TestClient(app) as client:
        assert client.post("/api/matches", json={"profile": {}}).status_code == 503
        assert (
            client.get(
                "/api/admin/runs", headers={"X-Replit-User-Id": "owner"}
            ).status_code
            == 401
        )
        assert client.post("/api/admin/runs", json={}).status_code == 401
        assert client.get("/api/auth/status").json()["configured"] is False


def test_oversize_request_rejected_without_parsing():
    with TestClient(create_app()) as client:
        assert (
            client.post(
                "/api/matches",
                content=b"x" * 33000,
                headers={"Content-Type": "application/json"},
            ).status_code
            == 413
        )


def test_authorized_eval_routes_pin_server_configuration(tmp_path):
    from nextstep.auth import AdminIdentity, require_admin
    from nextstep.models import Scholarship

    url = f"sqlite:///{tmp_path}/admin.db"
    metadata.create_all(create_engine(url))
    app = create_app(Settings(database_url=url))
    app.dependency_overrides[require_admin] = lambda: AdminIdentity("fixture-only")
    repo = app.state.repository
    repo.stage_catalog("v", [Scholarship(id="a", corpus_version="v", name="fixture")])
    repo.mark_ready("v")
    repo.activate_version(None, "v")
    with TestClient(app) as client:
        assert client.get("/api/admin/suite").status_code == 200
        assert (
            client.post("/api/admin/runs", json={"split": "tuning"}).status_code == 503
        )
        app.state.eval_execute = lambda config, case, method: {
            "scores": {"passed": False},
            "fixture": True,
        }
        started = client.post("/api/admin/runs", json={"split": "tuning"})
        assert started.status_code == 200
        run = started.json()["id"]
        state = client.get(f"/api/admin/runs/{run}").json()
        assert state["config"]["corpus_version"] == "v"
        case = state["config"]["cases"][0]
        path = f"/api/admin/runs/{run}/cases/{case}?method=semantic"
        assert client.post(path).status_code == 200
        assert client.post(path).json()["fixture"] is True
        assert client.post(f"/api/admin/runs/{run}/cancel").status_code == 200
        assert client.get(f"/api/admin/runs/{run}").json()["status"] == "cancelled"


def test_production_configuration_rejects_unstable_security_defaults():
    import pytest

    with pytest.raises(ValueError):
        Settings(environment="production", database_url="sqlite:///demo.db")
    with pytest.raises(ValueError):
        Settings(
            environment="production",
            database_url="postgresql+psycopg://host/db",
            public_origin="http://example.org",
        )


def test_chat_pins_active_version_and_failure_keeps_catalog(tmp_path):
    from nextstep.models import AnswerResult, RetrievedEvidence, Scholarship

    url = f"sqlite:///{tmp_path}/chat.db"
    metadata.create_all(create_engine(url))
    app = create_app(Settings(database_url=url))
    repo = app.state.repository
    repo.stage_catalog(
        "current", [Scholarship(id="a", name="A", corpus_version="current")]
    )
    repo.mark_ready("current")
    repo.activate_version(None, "current")

    class Service:
        fail = False

        def answer_question(self, profile, request, history):
            assert request.corpus_version == "current"
            if self.fail:
                raise RuntimeError("secret-provider-detail")
            return AnswerResult(
                blocks=[],
                gaps=["No evidence"],
                corpus_version=request.corpus_version,
                method=request.method,
                evidence=RetrievedEvidence(chunks=[]),
            )

    service = Service()
    app.state.answer_factory = lambda version, records: service
    body = {
        "profile": {},
        "request": {"question": "Rule?", "corpus_version": "old", "program_ids": ["a"]},
    }
    with TestClient(app) as client:
        assert client.post("/api/chat", json=body).json()["corpus_version"] == "current"
        service.fail = True
        result = client.post("/api/chat", json=body)
        assert result.status_code == 503 and "secret-provider" not in result.text
        assert client.post("/api/matches", json={"profile": {}}).status_code == 200


def test_admin_reads_configured_app_storage_report(tmp_path, monkeypatch):
    from nextstep.auth import AdminIdentity, require_admin

    class Store:
        def __init__(self, bucket):
            assert bucket == "fixture-bucket"

        def get(self, key):
            assert key == "reports/collection.json"
            return b'[{"source":{"id":"public-source","url":"https://example.org"},"status":"parsed","characters":20}]'

    monkeypatch.setattr("nextstep.storage.ReplitArtifactStore", Store)
    app = create_app(Settings(_env_file=None, app_storage_bucket_id="fixture-bucket"))
    app.dependency_overrides[require_admin] = lambda: AdminIdentity("fixture")
    with TestClient(app) as client:
        report = client.get("/api/admin/ingestion").json()["reports"]
        assert report == [
            {
                "source_id": "public-source",
                "url": "https://example.org",
                "status": "parsed",
                "characters": 20,
            }
        ]


@pytest.mark.parametrize("question", ["   ", chr(9) + chr(10), chr(8195) * 2])
def test_blank_chat_question_rejected_before_provider_work(tmp_path, question):
    from fastapi.testclient import TestClient
    from nextstep.app import create_app
    from nextstep.config import Settings

    app = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'blank.db'}"))
    calls = []
    app.state.answer_factory = lambda *args: calls.append(args)
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"profile": {}, "request": {"question": question}, "history": []},
        )
    assert response.status_code == 422
    assert calls == []
