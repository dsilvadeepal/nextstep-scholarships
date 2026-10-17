"""Archive an explicit official-source inventory; downloads only, no model calls."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from nextstep.ingest.collect import SourceSpec, collect_source
from nextstep.ingest.parse import parse_source
from nextstep.storage import LocalArtifactStore

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "artifacts/research/expansion-2026-10-16"


def collect(row):
    store = LocalArtifactStore(DEST)
    receipt_path = DEST / "collection" / f"{row['id']}.json"
    if receipt_path.exists():
        from nextstep.ingest.collect import CollectedSource

        receipt = CollectedSource.model_validate_json(receipt_path.read_text())
    else:
        receipt = collect_source(
            SourceSpec.model_validate(
                {k: row[k] for k in ("id", "url", "format", "sponsor", "category")}
            ),
            store,
        )
    result = {**row, "collection_status": receipt.status, "error": receipt.error}
    if receipt.status == "collected":
        try:
            doc = parse_source(receipt, store)
            store.put(
                f"normalized/{row['id']}.json", doc.model_dump_json(indent=2).encode()
            )
            result.update(
                parsed=True,
                sections=len(doc.sections),
                characters=sum(len(s.text) for s in doc.sections),
                content_hash=doc.content_hash,
                final_url=doc.url,
            )
        except Exception as exc:  # noqa: BLE001 - parsing failures are recorded as data
            result.update(parsed=False, error=type(exc).__name__)
    print(row["id"], result["collection_status"], result.get("sections", 0), flush=True)
    return result


if __name__ == "__main__":
    rows = json.loads(
        (ROOT / "data/expansion-source-inventory-2026-10-16.json").read_text()
    )
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(collect, rows))
    (DEST / "index.json").write_text(json.dumps(results, indent=2) + "\n")
