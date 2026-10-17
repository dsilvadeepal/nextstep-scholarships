"""Offline, idempotent liability transfer; never overwrites hosted spending."""

from decimal import Decimal

from nextstep.db import serialized, usage_ledger
from sqlalchemy import insert, select


def export_ledger(engine):
    with serialized(engine) as conn:
        rows = (
            conn.execute(select(usage_ledger).order_by(usage_ledger.c.id))
            .mappings()
            .all()
        )
        if any(row["status"] == "reserved" for row in rows):
            raise ValueError("Wait for outstanding reservations before transferring")
        return {
            "schema": 1,
            "rows": [dict(row, amount=str(row["amount"])) for row in rows],
        }


def import_ledger(engine, payload):
    if payload.get("schema") != 1:
        raise ValueError("Unsupported ledger format")
    rows = payload["rows"]
    seen = set()
    validated = []
    for row in rows:
        amount = Decimal(row["amount"])
        if (
            not amount.is_finite()
            or amount < 0
            or row["status"] not in ("completed", "ambiguous")
            or row["id"] in seen
        ):
            raise ValueError("Invalid liability record")
        seen.add(row["id"])
        validated.append(
            {k: row[k] for k in ("id", "run_id", "status")} | {"amount": amount}
        )
    with serialized(engine) as conn:
        for row in validated:
            existing = (
                conn.execute(select(usage_ledger).where(usage_ledger.c.id == row["id"]))
                .mappings()
                .first()
            )
            if existing and dict(existing) != row:
                raise ValueError("Ledger conflict: no records changed")
            if not existing:
                conn.execute(insert(usage_ledger).values(**row))
    return len(validated)
