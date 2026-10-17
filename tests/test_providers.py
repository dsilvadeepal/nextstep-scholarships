from decimal import Decimal
from types import SimpleNamespace

import pytest
from langchain_core.runnables import RunnableLambda
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
            assert kwargs == {"method": "function_calling", "include_raw": True}
            return RunnableLambda(self.invoke)

        def invoke(self, prompt):
            from langsmith.run_helpers import get_tracing_context

            assert get_tracing_context()["enabled"] is False
            messages = prompt.to_messages()
            assert messages[0].content == "source instructions {literal}"
            assert messages[0].type == "system" and messages[1].type == "human"
            assert messages[1].content == '{"text": "student’s {literal}"}'
            return {
                "parsed": ExtractedRecords(records=[]),
                "raw": SimpleNamespace(
                    usage_metadata={"input_tokens": 10, "output_tokens": 10}
                ),
            }

    PaidModel(settings, ledger, Client).invoke(
        ExtractedRecords,
        "source instructions {literal}",
        {"text": "student’s {literal}"},
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


def test_extraction_wire_shape_normalizes_only_empty_lists_and_single_evidence_ids():
    parsed = ExtractedRecords.model_validate(
        {
            "records": [
                {
                    "id": "a",
                    "name": "Award",
                    "corpus_version": "staged",
                    "materials": None,
                    "field_evidence": {"name": "e1"},
                }
            ]
        }
    )
    assert parsed.records[0].materials == []
    assert parsed.records[0].field_evidence == {"name": ["e1"]}
    with pytest.raises(ValueError):
        ExtractedRecords.model_validate(
            {
                "records": [
                    {
                        "id": "a",
                        "name": "Award",
                        "corpus_version": "staged",
                        "materials": 42,
                    }
                ]
            }
        )


def test_vector_metadata_keeps_cycle_and_exact_source_provenance():
    from datetime import UTC, datetime

    from nextstep.models import Chunk, EvidenceRef
    from nextstep.providers import PineconeStore

    captured = []
    store = object.__new__(PineconeStore)
    store.index = SimpleNamespace(upsert=lambda **kwargs: captured.append(kwargs))
    ref = EvidenceRef(
        id="e",
        source_id="official-rules",
        document_version="sha256-original",
        section_id="p7",
        page=7,
        quote="Current juniors",
        start=4,
        end=19,
        url="https://example.org/rules.pdf",
        fetched_at=datetime(2026, 10, 14, tzinfo=UTC),
        title="Eligibility",
        cycle="2026–27 application; Fall 2028 entry",
    )
    chunk = Chunk(
        id="c",
        program_id="award",
        source_id="official-rules",
        corpus_version="v",
        text=ref.quote,
        heading="Eligibility",
        section_ids=["p7"],
        token_count=3,
        evidence=[ref],
        cycle=ref.cycle,
        information_status="source_checked",
        source_checked_at="2026-10-14",
        cycle_metadata={
            "application_cycle": "2026–27",
            "college_entry_year": 2028,
            "high_school_graduation_year": 2028,
        },
    )
    store.upsert("v", [chunk], [[1.0, 0.0]])
    metadata = captured[0]["vectors"][0]["metadata"]
    assert captured[0]["namespace"] == "v"
    assert metadata["source_url"] == ref.url
    assert metadata["document_hash"] == ref.document_version
    assert metadata["page_number"] == 7
    assert metadata["quote_start"] == 4 and metadata["quote_end"] == 19
    assert metadata["college_entry_year"] == 2028
    assert metadata["application_cycle"] == "2026–27"
    assert "award_academic_year" not in metadata
    assert metadata["information_status"] == "source_checked"
    assert metadata["source_checked_at"] == "2026-10-14"
    assert metadata["fetched_at"] == ref.fetched_at.isoformat()
    assert all(value is not None for value in metadata.values())


@pytest.mark.parametrize("failure", [None, "parse", "transport"])
def test_structured_chain_native_schema_and_failure_accounting(tmp_path, failure):
    from nextstep.rag.construction import Draft

    engine = create_engine(f"sqlite:///{tmp_path}/budget.db")
    metadata.create_all(engine)
    settings = Settings(
        _env_file=None,
        live_calls_enabled=True,
        openai_api_key="fixture",
        pricing_effective_date="fixture-only",
        input_usd_per_million=Decimal(1),
        output_usd_per_million=Decimal(1),
    )
    ledger = BudgetLedger(engine, Decimal(1), Decimal(1), enabled=True)
    calls = []

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["max_retries"] == 0

        def with_structured_output(self, schema, **kwargs):
            assert schema is Draft
            assert kwargs == {
                "method": "json_schema",
                "strict": True,
                "include_raw": True,
            }
            return RunnableLambda(self.invoke)

        def invoke(self, prompt):
            calls.append(prompt)
            if failure == "transport":
                raise TimeoutError("ambiguous provider response")
            return {
                "parsed": None if failure else Draft(claims=[], unanswered=[]),
                "parsing_error": ValueError("invalid") if failure else None,
                "raw": SimpleNamespace(
                    usage_metadata={"input_tokens": 10, "output_tokens": 10}
                ),
            }

    model = PaidModel(settings, ledger, Client)
    if failure:
        with pytest.raises(TimeoutError if failure == "transport" else ValueError):
            model.invoke(Draft, "instructions", {})
    else:
        parsed, usage = model.invoke(Draft, "instructions", {})
        assert isinstance(parsed, Draft)
        assert usage["input_tokens"] == 10
    assert len(calls) == 1
    assert ledger.spent() == Decimal(".025200" if failure == "transport" else ".000020")


def test_app_model_without_ledger_needs_no_prices_or_budget():
    settings = Settings(
        _env_file=None, live_calls_enabled=True, openai_api_key="fixture"
    )

    class Client:
        def __init__(self, **kwargs):
            pass

        def with_structured_output(self, *args, **kwargs):
            return RunnableLambda(
                lambda _: {
                    "parsed": ExtractedRecords(records=[]),
                    "raw": SimpleNamespace(
                        usage_metadata={"input_tokens": 10, "output_tokens": 10}
                    ),
                }
            )

    result, usage = PaidModel(settings, client_factory=Client).invoke(
        ExtractedRecords, "test", {}
    )
    assert result.records == []
    assert usage["input_tokens"] == 10
