from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from nextstep.auth import install_auth, require_admin
from nextstep.config import Settings
from nextstep.db import metadata, usage_ledger
from nextstep.ledger_handoff import export_ledger, import_ledger
from sqlalchemy import create_engine, insert, select


def production(**kwargs):
    return Settings(
        _env_file=None,
        environment="production",
        database_url="postgresql://unused",
        public_origin="https://demo.example",
        rate_secret="r" * 32,
        **kwargs,
    )


def test_production_admin_disabled_even_with_credentials():
    settings = production(
        oidc_client_id="unused", session_secret="s" * 32, admin_subjects=["owner"]
    )
    app = FastAPI()
    app.state.settings = settings
    install_auth(app, settings)
    from fastapi import Depends

    @app.get("/admin", dependencies=[Depends(require_admin)])
    def admin():
        return {"secret": True}

    client = TestClient(app)
    assert client.get("/api/auth/status").json() == {
        "configured": False,
        "authenticated": False,
    }
    assert client.get("/admin").status_code == 401
    assert client.get("/api/auth/login").status_code == 503
    with pytest.raises(ValueError):
        production(hosted_admin_enabled=True)


def test_transfer_idempotent_preserves_hosted_and_rolls_back_conflicts():
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    row = {"id": "local", "run_id": "demo", "status": "ambiguous", "amount": ".25"}
    payload = {"schema": 1, "rows": [row]}
    import_ledger(engine, payload)
    import_ledger(engine, payload)
    with engine.begin() as conn:
        conn.execute(
            insert(usage_ledger).values(
                id="hosted", run_id="chat", status="completed", amount=".1"
            )
        )
    assert len(export_ledger(engine)["rows"]) == 2
    with pytest.raises(ValueError):
        import_ledger(
            engine, {"schema": 1, "rows": [dict(row, id="new"), dict(row, amount=".5")]}
        )
    with engine.connect() as conn:
        assert conn.execute(
            select(usage_ledger.c.amount).where(usage_ledger.c.id == "local")
        ).scalar_one() == Decimal(".25")
    assert len(export_ledger(engine)["rows"]) == 2
    with engine.begin() as conn:
        conn.execute(
            insert(usage_ledger).values(
                id="pending", run_id="x", status="reserved", amount=".1"
            )
        )
    with pytest.raises(ValueError):
        export_ledger(engine)
