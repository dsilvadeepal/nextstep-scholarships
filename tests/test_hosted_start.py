import importlib.util
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location(
    "hosted_start", Path(__file__).parents[1] / "scripts/start_hosted.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_production_needs_no_ledger_or_price_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://unused")
    monkeypatch.setenv("SESSION_SECRET", "s" * 32)
    monkeypatch.setattr(module, "create_engine", lambda _: None)
    monkeypatch.setattr(
        module,
        "Repository",
        lambda _: SimpleNamespace(active_version=lambda: "candidate-2026-10-16-v4"),
    )
    settings = module.verified_settings()
    assert settings.live_calls_enabled
    assert not settings.hosted_admin_enabled
    assert settings.input_usd_per_million is None
