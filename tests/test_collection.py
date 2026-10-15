import pytest
from nextstep.ingest.collect import SourceSpec, collect_source, validate_target
from nextstep.storage import LocalArtifactStore


def test_network_targets_block_local_private_and_embedded_credentials():
    for url in [
        "file:///etc/passwd",
        "http://127.0.0.1/a",
        "http://[::1]/",
        "http://169.254.169.254/latest",
        "https://user:password@example.org",
    ]:
        with pytest.raises(ValueError):
            validate_target(url)


def test_changed_and_unchanged_collection_preserves_originals(tmp_path):
    source = SourceSpec(
        id="test", url="https://example.org", format="html", sponsor="Fixture"
    )
    store = LocalArtifactStore(tmp_path)

    def fetch(url):
        return b"<h1>Original</h1>", url

    one = collect_source(source, store, fetcher=fetch)
    two = collect_source(source, store, fetcher=fetch)
    assert one.content_hash == two.content_hash
    assert one.artifact_key == two.artifact_key
    assert store.get(one.artifact_key) == b"<h1>Original</h1>"

    def fail(url):
        raise OSError("private diagnostic")

    failed = collect_source(source, store, fetcher=fail)
    assert failed.status == "failed" and failed.error == "OSError"
    assert "withdraw" not in failed.model_dump_json()


def test_app_storage_cache_miss_is_normalized():
    from nextstep.storage import ReplitArtifactStore
    from replit.object_storage.errors import ObjectNotFoundError

    class Client:
        def download_as_bytes(self, key):
            raise ObjectNotFoundError("missing")

    store = object.__new__(ReplitArtifactStore)
    store.client = Client()
    with __import__("pytest").raises(FileNotFoundError):
        store.get("normalized/missing.json")
