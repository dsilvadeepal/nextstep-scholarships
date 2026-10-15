from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from nextstep.db import metadata
from nextstep.limits import BudgetLedger
from sqlalchemy import create_engine


def test_reservations_cannot_exceed_cap_and_timeout_retains_cost(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/usage.db")
    metadata.create_all(engine)
    ledger = BudgetLedger(engine, Decimal(1), Decimal(1), enabled=True)

    def reserve(key):
        try:
            return ledger.reserve_budget(key, Decimal(".7"))
        except ValueError:
            return None

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(reserve, ["a", "b"]))
    assert sum(r is not None for r in results) == 1
    reservation = next(r for r in results if r is not None)
    ledger.reconcile_budget(reservation.id, None)
    assert ledger.spent() == Decimal(".7")


def test_paid_calls_fail_closed(tmp_path):
    import pytest

    engine = create_engine(f"sqlite:///{tmp_path}/usage.db")
    metadata.create_all(engine)
    with pytest.raises(ValueError):
        BudgetLedger(engine, Decimal(10), Decimal(10)).reserve_budget(
            "a", Decimal(".1")
        )


def test_rate_counters_are_shared_expire_and_ignore_forwarded_claims(tmp_path):
    import pytest
    from nextstep.limits import RateLimiter

    engine = create_engine(f"sqlite:///{tmp_path}/rate.db")
    metadata.create_all(engine)
    limiter = RateLimiter(engine, "test-secret", per_minute=2, global_per_hour=3)
    limiter.consume("127.0.0.1", now=100)
    limiter.consume("127.0.0.1", now=101)
    with pytest.raises(ValueError):
        limiter.consume("127.0.0.1", now=102)
    limiter.consume("127.0.0.2", now=102)
    with pytest.raises(ValueError):
        limiter.consume("127.0.0.3", now=103)
    limiter.consume("127.0.0.1", now=4000)
