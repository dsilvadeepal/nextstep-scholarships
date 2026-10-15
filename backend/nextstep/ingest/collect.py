"""Manual bounded downloads. Resolved public IPs are pinned through TLS requests."""

import hashlib
import ipaddress
import socket
import time
from datetime import UTC, datetime
from urllib.parse import urljoin, urlsplit

import urllib3
from nextstep.models import Model
from pydantic import Field


class SourceSpec(Model):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    url: str
    format: str
    sponsor: str
    category: str = "unclassified"
    status: str = "candidate"
    expected_content_hash: str | None = None
    section_partitions: dict[str, list[dict]] = Field(default_factory=dict)
    program_bindings: dict[str, str] = Field(default_factory=dict)


class CollectedSource(Model):
    source: SourceSpec
    status: str
    fetched_at: datetime
    final_url: str | None = None
    content_hash: str | None = None
    artifact_key: str | None = None
    error: str | None = None


def validate_target(url):
    parsed = urlsplit(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 80, 443)
    ):
        raise ValueError("Only public HTTP(S) URLs on standard ports are allowed")
    addresses = list(
        dict.fromkeys(
            item[4][0]
            for item in socket.getaddrinfo(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        )
    )
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("Private or non-global network target is blocked")
    return parsed, addresses


def download(url, max_bytes=20 * 1024 * 1024, timeout=20):
    started = time.monotonic()
    for _ in range(6):
        parsed, addresses = validate_target(url)
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("Collection time limit")
        kwargs = {
            "host": addresses[0],
            "port": parsed.port or (443 if parsed.scheme == "https" else 80),
            "timeout": urllib3.Timeout(total=remaining),
            "retries": False,
        }
        if parsed.scheme == "https":
            pool = urllib3.HTTPSConnectionPool(
                **kwargs,
                server_hostname=parsed.hostname,
                assert_hostname=parsed.hostname,
                cert_reqs="CERT_REQUIRED",
            )
        else:
            pool = urllib3.HTTPConnectionPool(**kwargs)
        response = None
        try:
            path = (parsed.path or "/") + ("?" + parsed.query if parsed.query else "")
            response = pool.urlopen(
                "GET",
                path,
                headers={
                    "Host": parsed.netloc,
                    "User-Agent": "NextStepScholarshipResearch/0.1",
                    "Accept-Encoding": "identity",
                },
                redirect=False,
                preload_content=False,
            )
            if response.status in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                if not location:
                    raise ValueError("Redirect missing location")
                url = urljoin(url, location)
                continue
            if response.status != 200:
                raise ValueError(f"HTTP {response.status}")
            if int(response.headers.get("Content-Length", "0")) > max_bytes:
                raise ValueError("Source exceeds size limit")
            chunks = []
            size = 0
            for chunk in response.stream(65536, decode_content=True):
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError("Source exceeds size limit")
                if time.monotonic() - started > timeout:
                    raise TimeoutError("Collection time limit")
                chunks.append(chunk)
            return b"".join(chunks), url
        finally:
            if response is not None:
                response.close()
            pool.close()
    raise ValueError("Too many redirects")


def collect_source(source, store, fetcher=download):
    fetched = datetime.now(UTC)
    try:
        data, final_url = fetcher(source.url)
        digest = hashlib.sha256(data).hexdigest()
        key = f"originals/{source.id}/{digest}.{source.format}"
        store.put(key, data)
        result = CollectedSource(
            source=source,
            status="collected",
            fetched_at=fetched,
            final_url=final_url,
            content_hash=digest,
            artifact_key=key,
        )
    except Exception as exc:  # noqa: BLE001 - collection failures are data; avoid leaking network details
        result = CollectedSource(
            source=source, status="failed", fetched_at=fetched, error=type(exc).__name__
        )
    store.put(f"collection/{source.id}.json", result.model_dump_json(indent=2).encode())
    return result
