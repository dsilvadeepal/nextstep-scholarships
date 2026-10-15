from decimal import Decimal
from types import SimpleNamespace

import pytest
from nextstep.config import Settings
from nextstep.db import metadata
from nextstep.limits import BudgetLedger
from nextstep.providers import ExtractedRecords, PaidModel
from sqlalchemy import create_engine


def test_no_global_trace_leak_and_usage_reconciled(tmp_path, monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    engine = create_engine(f"sqlite:///{tmp_path}/budget.db")
    metadata.create_all(engine)
    settings = Settings(
        live_calls_enabled=True,
        openai_api_key="fixture",
        pricing_effective_date="fixture-only",
        input_usd_per_million=Decimal(1),
        output_usd_per_million=Decimal(1),
    )
    ledger = BudgetLedger(engine, Decimal(1), Decimal(1), enabled=True)

    class Client:
        def __init__(self, **kwargs):
            pass

        def with_structured_output(self, *args, **kwargs):
            return self

        def invoke(self, *args, **kwargs):
            from langsmith.run_helpers import get_tracing_context

            assert get_tracing_context()["enabled"] is False
            return {
                "parsed": ExtractedRecords(records=[]),
                "raw": SimpleNamespace(
                    usage_metadata={"input_tokens": 10, "output_tokens": 10}
                ),
            }

    PaidModel(settings, ledger, Client).invoke(
        ExtractedRecords, "source instructions", {}
    )
    assert ledger.spent() == Decimal(".000020")


def test_paid_model_defaults_never_construct_a_client():
    def forbidden(**kwargs):
        raise AssertionError("network client constructed")

    with pytest.raises(ValueError, match="disabled"):
        PaidModel(Settings(_env_file=None), None, forbidden).invoke(
            ExtractedRecords, "", {}
        )


def test_pinecone_readiness_requires_searchable_manifest():
    from nextstep.providers import PineconeStore

    class Index:
        searchable = False

        def fetch(self, **kwargs):
            return SimpleNamespace(vectors={"c": SimpleNamespace(values=[1.0, 0.0])})

        def describe_index_stats(self):
            return SimpleNamespace(namespaces={"v": SimpleNamespace(vector_count=1)})

        def query(self, **kwargs):
            return SimpleNamespace(
                matches=[SimpleNamespace(id="c")] if self.searchable else []
            )

    store = object.__new__(PineconeStore)
    store.index = Index()
    assert store.ready("v", ["c"]) is False
    store.index.searchable = True
    assert store.ready("v", ["c"]) is True


def test_pinecone_constructor_matches_installed_sdk(monkeypatch):
    from nextstep.providers import PineconeStore

    class Client:
        def __init__(self, api_key, **kwargs):
            assert kwargs["timeout"] == 15 and kwargs["retry_config"].max_retries == 0

        def describe_index(self, name):
            return SimpleNamespace(dimension=1536, metric="cosine", host="fixture-host")

        def Index(self, *, host):
            return SimpleNamespace(host=host)

    monkeypatch.setattr("pinecone.Pinecone", Client)
    store = PineconeStore(
        Settings(
            _env_file=None,
            live_calls_enabled=True,
            pinecone_api_key="fixture",
            pinecone_index="fixture",
        ),
        None,
    )
    assert store.index.host == "fixture-host"
