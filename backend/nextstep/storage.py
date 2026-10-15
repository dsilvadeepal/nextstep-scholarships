from pathlib import Path
from typing import Protocol


class ArtifactStore(Protocol):
    def put(self, key: str, data: bytes) -> str: ...
    def get(self, key: str) -> bytes: ...


class LocalArtifactStore:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def _path(self, key):
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root) or path == self.root:
            raise ValueError("Artifact key escapes storage root")
        return path

    def put(self, key, data):
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def get(self, key):
        return self._path(key).read_bytes()


class ReplitArtifactStore:
    """Requires the supported Replit runtime identity; never falls back to local storage."""

    def __init__(self, bucket_id):
        from replit.object_storage import Client

        self.client = Client(bucket_id=bucket_id)

    def put(self, key, data):
        if key.startswith("/") or ".." in key.split("/"):
            raise ValueError("Invalid artifact key")
        self.client.upload_from_bytes(key, data)
        return key

    def get(self, key):
        if key.startswith("/") or ".." in key.split("/"):
            raise ValueError("Invalid artifact key")
        from replit.object_storage.errors import ObjectNotFoundError

        try:
            return self.client.download_as_bytes(key)
        except ObjectNotFoundError:
            raise FileNotFoundError(key) from None
