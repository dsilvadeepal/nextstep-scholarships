from dataclasses import dataclass
from decimal import Decimal

from nextstep.db import serialized, usage_ledger
from sqlalchemy import func, insert, select, update


@dataclass(frozen=True)
class Reservation:
    id: str
    amount: Decimal


class BudgetLedger:
    def __init__(self, engine, run_cap, total_cap, enabled=False, run_id="default"):
        self.engine, self.run_cap, self.total_cap = engine, run_cap, total_cap
        self.enabled, self.run_id = enabled, run_id

    def spent(self):
        with self.engine.connect() as conn:
            return conn.execute(
                select(func.coalesce(func.sum(usage_ledger.c.amount), 0))
            ).scalar_one()

    def reserve_budget(self, operation_id, estimated_usd):
        if not self.enabled or estimated_usd <= 0:
            raise ValueError("Paid calls disabled or invalid reservation")
        with serialized(self.engine) as conn:
            if conn.execute(
                select(usage_ledger.c.id).where(usage_ledger.c.id == operation_id)
            ).first():
                raise ValueError("Operation already reserved; do not replay paid work")
            total = conn.execute(
                select(func.coalesce(func.sum(usage_ledger.c.amount), 0))
            ).scalar_one()
            run = conn.execute(
                select(func.coalesce(func.sum(usage_ledger.c.amount), 0)).where(
                    usage_ledger.c.run_id == self.run_id
                )
            ).scalar_one()
            if (
                total + estimated_usd > self.total_cap
                or run + estimated_usd > self.run_cap
            ):
                raise ValueError("Approved budget exceeded")
            conn.execute(
                insert(usage_ledger).values(
                    id=operation_id,
                    run_id=self.run_id,
                    amount=estimated_usd,
                    status="reserved",
                )
            )
        return Reservation(operation_id, estimated_usd)

    def reconcile_budget(self, reservation_id, actual_usd):
        if actual_usd is not None and actual_usd < 0:
            raise ValueError("Negative usage")
        with serialized(self.engine) as conn:
            row = (
                conn.execute(
                    select(usage_ledger).where(usage_ledger.c.id == reservation_id)
                )
                .mappings()
                .one()
            )
            if row["status"] != "reserved":
                raise ValueError("Already reconciled")
            conn.execute(
                update(usage_ledger)
                .where(usage_ledger.c.id == reservation_id)
                .values(
                    amount=row["amount"] if actual_usd is None else actual_usd,
                    status="ambiguous" if actual_usd is None else "completed",
                )
            )


class RateLimiter:
    def __init__(self, engine, secret, per_minute=10, global_per_hour=100):
        self.engine, self.secret = engine, secret
        self.per_minute, self.global_per_hour = per_minute, global_per_hour

    def consume(self, client_address, now=None):
        import hashlib
        import hmac
        import time

        from nextstep.db import rate_counters
        from sqlalchemy import delete

        now = int(time.time() if now is None else now)
        client = hmac.new(
            self.secret.encode(),
            f"{now // 86400}:{client_address}".encode(),
            hashlib.sha256,
        ).hexdigest()
        keys = [
            (f"client:{client}:{now // 60}", self.per_minute),
            (f"global:{now // 3600}", self.global_per_hour),
        ]
        with serialized(self.engine) as conn:
            conn.execute(delete(rate_counters).where(rate_counters.c.expires < now))
            values = []
            for key, limit in keys:
                count = conn.execute(
                    select(rate_counters.c.count).where(rate_counters.c.key == key)
                ).scalar_one_or_none()
                if count is not None and count >= limit:
                    raise ValueError("Request limit reached. Try again later.")
                values.append((key, count))
            for key, count in values:
                if count is None:
                    conn.execute(
                        insert(rate_counters).values(
                            key=key, count=1, expires=now + 86400
                        )
                    )
                else:
                    conn.execute(
                        update(rate_counters)
                        .where(rate_counters.c.key == key)
                        .values(count=count + 1)
                    )
