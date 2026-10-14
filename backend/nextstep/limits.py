from dataclasses import dataclass
from decimal import Decimal
from sqlalchemy import select, insert, update, func
from nextstep.db import usage_ledger, serialized

@dataclass(frozen=True)
class Reservation:
    id: str
    amount: Decimal

class BudgetLedger:
    def __init__(self, engine, run_cap, total_cap, enabled=False, run_id='default'):
        self.engine, self.run_cap, self.total_cap = engine, run_cap, total_cap
        self.enabled, self.run_id = enabled, run_id

    def spent(self):
        with self.engine.connect() as conn:
            return conn.execute(select(func.coalesce(func.sum(usage_ledger.c.amount), 0))).scalar_one()

    def reserve_budget(self, operation_id, estimated_usd):
        if not self.enabled or estimated_usd <= 0:
            raise ValueError('Paid calls disabled or invalid reservation')
        with serialized(self.engine) as conn:
            if conn.execute(select(usage_ledger.c.id).where(usage_ledger.c.id == operation_id)).first():
                raise ValueError('Operation already reserved; do not replay paid work')
            total = conn.execute(select(func.coalesce(func.sum(usage_ledger.c.amount), 0))).scalar_one()
            run = conn.execute(select(func.coalesce(func.sum(usage_ledger.c.amount), 0)).where(usage_ledger.c.run_id == self.run_id)).scalar_one()
            if total + estimated_usd > self.total_cap or run + estimated_usd > self.run_cap:
                raise ValueError('Approved budget exceeded')
            conn.execute(insert(usage_ledger).values(id=operation_id, run_id=self.run_id, amount=estimated_usd, status='reserved'))
        return Reservation(operation_id, estimated_usd)

    def reconcile_budget(self, reservation_id, actual_usd):
        if actual_usd is not None and actual_usd < 0:
            raise ValueError('Negative usage')
        with serialized(self.engine) as conn:
            row = conn.execute(select(usage_ledger).where(usage_ledger.c.id == reservation_id)).mappings().one()
            if row['status'] != 'reserved':
                raise ValueError('Already reconciled')
            conn.execute(update(usage_ledger).where(usage_ledger.c.id == reservation_id).values(amount=row['amount'] if actual_usd is None else actual_usd, status='ambiguous' if actual_usd is None else 'completed'))
