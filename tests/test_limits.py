from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from sqlalchemy import create_engine
from nextstep.db import metadata
from nextstep.limits import BudgetLedger

def test_reservations_cannot_exceed_cap_and_timeout_retains_cost(tmp_path):
    engine = create_engine(f'sqlite:///{tmp_path}/usage.db')
    metadata.create_all(engine)
    ledger = BudgetLedger(engine, Decimal('1'), Decimal('1'), enabled=True)
    def reserve(key):
        try:
            return ledger.reserve_budget(key, Decimal('.7'))
        except ValueError:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(reserve, ['a', 'b']))
    assert sum(r is not None for r in results) == 1
    reservation = next(r for r in results if r is not None)
    ledger.reconcile_budget(reservation.id, None)
    assert ledger.spent() == Decimal('.7')

def test_paid_calls_fail_closed(tmp_path):
    import pytest
    engine = create_engine(f'sqlite:///{tmp_path}/usage.db')
    metadata.create_all(engine)
    with pytest.raises(ValueError):
        BudgetLedger(engine, Decimal('10'), Decimal('10')).reserve_budget('a', Decimal('.1'))
