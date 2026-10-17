"""Import frozen local manifest and liabilities; read Pinecone, never re-embed."""

import json
import os
from pathlib import Path

from nextstep.ledger_handoff import export_ledger, import_ledger
from nextstep.models import Chunk, Scholarship
from nextstep.providers import PineconeStore
from nextstep.repository import Repository
from pinecone import Pinecone
from sqlalchemy import create_engine

root = Path(__file__).resolve().parents[1]
url = os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(url)
repo = Repository(engine)
bundle = json.loads((root / "data/corpus-candidate-2026-10-16-v4.json").read_text())
version = bundle["version"]
records = [Scholarship.model_validate(r) for r in bundle["records"]]
chunks = [Chunk.model_validate(c) for c in bundle["chunks"]]
index = Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index("nextstep-scholarships")
for start in range(0, len(chunks), 100):
    batch = chunks[start : start + 100]
    result = index.fetch(namespace=version, ids=[c.id for c in batch])
    assert set(result.vectors) == {c.id for c in batch}, "Missing hosted vectors"
    for chunk in batch:
        actual = result.vectors[chunk.id].metadata
        expected = PineconeStore.metadata_for(version, chunk)
        assert all(actual.get(k) == v for k, v in expected.items()), (
            "Vector metadata mismatch"
        )
if not repo.is_ready(version):
    repo.stage_catalog(version, records)
    repo.stage_chunks(version, chunks)
    repo.freeze_manifest(version)
    repo.mark_ready(version)
assert {r.id for r in repo.list_scholarships(version)} == {r.id for r in records}
import_ledger(
    engine, json.loads((root / "artifacts/ledger-handoff-2026-10-17.json").read_text())
)
repo.activate_version(repo.active_version(), version)
from decimal import Decimal

rows = export_ledger(engine)["rows"]
print(
    {
        "active": repo.active_version(),
        "records": len(records),
        "chunks": len(chunks),
        "ledger_rows": len(rows),
        "liability": str(sum((Decimal(r["amount"]) for r in rows), Decimal(0))),
    }
)
