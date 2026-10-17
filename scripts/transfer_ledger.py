"""Run with paid callers stopped. DATABASE_URL comes from environment, never CLI."""

import argparse
import json
import os
from pathlib import Path

from nextstep.ledger_handoff import export_ledger, import_ledger
from sqlalchemy import create_engine

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["export", "import"])
parser.add_argument("file", type=Path)
args = parser.parse_args()
url = os.environ["DATABASE_URL"]
if url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(url)
if args.action == "export":
    payload = export_ledger(engine)
    args.file.write_text(json.dumps(payload, indent=2))
    args.file.chmod(0o600)
else:
    import_ledger(engine, json.loads(args.file.read_text()))
    payload = export_ledger(engine)
from decimal import Decimal

print(
    {
        "records": len(payload["rows"]),
        "liability_usd": str(
            sum((Decimal(row["amount"]) for row in payload["rows"]), Decimal(0))
        ),
    }
)
