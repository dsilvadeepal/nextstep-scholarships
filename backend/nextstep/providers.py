"""Provider adapters are inert until explicit access, pricing and budget configuration."""

import json
from decimal import Decimal
from typing import Protocol
from uuid import uuid4

import tiktoken
from nextstep.models import Condition, Scholarship
from pydantic import BaseModel, Field, model_validator


class ExtractionModel(Protocol):
    def extract(self, section_text: str) -> dict: ...


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    def upsert(self, version, chunks, vectors): ...


class ExtractedRecords(BaseModel):
    records: list[Scholarship]

    @model_validator(mode="before")
    @classmethod
    def normalize_wire_collections(cls, data):
        # Only repair equivalent JSON collection shapes, never content or evidence.
        import copy

        data = copy.deepcopy(data)
        if not isinstance(data, dict) or not isinstance(data.get("records"), list):
            return data
        for record in data["records"]:
            if not isinstance(record, dict):
                continue
            for field in ("materials", "conditions", "evidence"):
                if field in record and record[field] is None:
                    record[field] = []
            refs = record.get("field_evidence")
            if isinstance(refs, dict):
                record["field_evidence"] = {
                    field: [ids] if isinstance(ids, str) else ids
                    for field, ids in refs.items()
                }
        return data


class UnitCondition(Condition):
    evidence: list[str]
    children: list["UnitCondition"] = Field(default_factory=list)


class UnitScholarship(Scholarship):
    deadline: str | None = None
    opens: str | None = None
    evidence: list[str]
    conditions: list[UnitCondition] = Field(default_factory=list)


class UnitRecords(ExtractedRecords):
    records: list[UnitScholarship]


class PaidModel:
    def __init__(self, settings, ledger, client_factory=None):
        self.settings, self.ledger, self.client_factory = (
            settings,
            ledger,
            client_factory,
        )

    def invoke(self, schema, instructions, payload, max_output=1200):
        settings = self.settings
        if not settings.live_calls_enabled or not settings.openai_api_key:
            raise ValueError("Live OpenAI calls are disabled or unconfigured")
        if (
            not settings.pricing_effective_date
            or settings.input_usd_per_million is None
            or settings.output_usd_per_million is None
        ):
            raise ValueError("Approved current provider prices required")
        encoded = json.dumps(payload, default=str, ensure_ascii=False)
        count = len(
            tiktoken.get_encoding("cl100k_base").encode(
                instructions + encoded + json.dumps(schema.model_json_schema())
            )
        )
        if count > 22000:
            raise ValueError("Model input exceeds bounded context")
        # Reserve the entire bounded input allowance, including tool/message framing.
        estimate = (
            Decimal(24000) * settings.input_usd_per_million
            + Decimal(max_output) * settings.output_usd_per_million
        ) / Decimal(1000000)
        reservation = self.ledger.reserve_budget(str(uuid4()), estimate)
        try:
            if self.client_factory is None:
                from langchain_openai import ChatOpenAI

                factory = ChatOpenAI
            else:
                factory = self.client_factory
            client = factory(
                model=settings.answer_model,
                api_key=settings.openai_api_key,
                temperature=0,
                max_tokens=max_output,
                timeout=30,
                max_retries=0,
            )
            from langsmith import tracing_context

            with tracing_context(enabled=False):
                output = client.with_structured_output(
                    schema, method="function_calling", include_raw=True
                ).invoke(
                    [("system", instructions), ("human", encoded)],
                    config={"callbacks": []},
                )
            usage = output["raw"].usage_metadata
            actual = (
                Decimal(usage["input_tokens"]) * settings.input_usd_per_million
                + Decimal(usage["output_tokens"]) * settings.output_usd_per_million
            ) / Decimal(1000000)
            self.ledger.reconcile_budget(reservation.id, actual)
        except Exception:
            # Reconcile only if still pending; completed calls remain charged even if parsing fails.
            try:
                self.ledger.reconcile_budget(reservation.id, None)
            except ValueError:
                pass
            raise
        if output.get("parsing_error") or output.get("parsed") is None:
            raise ValueError("Provider structured output did not validate")
        return output["parsed"], {"model": settings.answer_model, **usage}

    def extract(self, section_text):
        from nextstep.ingest.extract import (
            EXTRACTION_INSTRUCTIONS,
            expand_unit_evidence,
            source_units,
        )
        from nextstep.models import NormalizedDocument

        document = NormalizedDocument.model_validate_json(section_text)
        units = source_units(document)
        payload = {
            "source_id": document.source_id,
            "url": document.url,
            "evidence_units": [{"id": ref.id, "text": ref.quote} for ref in units],
        }
        result, _ = self.invoke(UnitRecords, EXTRACTION_INSTRUCTIONS, payload, 4000)
        return expand_unit_evidence(result.model_dump(mode="json"), units)


class OpenAIEmbeddingProvider:
    def __init__(self, settings, ledger):
        self.settings, self.ledger = settings, ledger
        self.model, self.dimensions = (
            settings.embedding_model,
            settings.embedding_dimensions,
        )

    def embed(self, texts):
        settings = self.settings
        if (
            not settings.live_calls_enabled
            or not settings.openai_api_key
            or settings.embedding_usd_per_million is None
            or not settings.pricing_effective_date
        ):
            raise ValueError("Embedding access/pricing/budget not enabled")
        from openai import OpenAI

        tokens = sum(
            len(tiktoken.get_encoding("cl100k_base").encode(t, disallowed_special=()))
            for t in texts
        )
        if tokens > 20000:
            raise ValueError("Embedding batch exceeds limit")
        reserve = self.ledger.reserve_budget(
            str(uuid4()),
            Decimal(tokens) * settings.embedding_usd_per_million / Decimal(1000000),
        )
        try:
            result = OpenAI(
                api_key=settings.openai_api_key, max_retries=0, timeout=30
            ).embeddings.create(
                model=self.model, input=texts, dimensions=self.dimensions
            )
            self.ledger.reconcile_budget(
                reserve.id,
                Decimal(result.usage.total_tokens)
                * settings.embedding_usd_per_million
                / Decimal(1000000),
            )
            return [
                item.embedding
                for item in sorted(result.data, key=lambda item: item.index)
            ]
        except Exception:
            try:
                self.ledger.reconcile_budget(reserve.id, None)
            except ValueError:
                pass
            raise


class PineconeStore:
    def __init__(self, settings, embeddings):
        if (
            not settings.live_calls_enabled
            or not settings.pinecone_api_key
            or not settings.pinecone_index
        ):
            raise ValueError("Pinecone access is not enabled")
        from pinecone import Pinecone, RetryConfig

        self.client = Pinecone(
            api_key=settings.pinecone_api_key,
            timeout=15,
            retry_config=RetryConfig(max_retries=0),
        )
        description = self.client.describe_index(settings.pinecone_index)
        if (
            description.dimension != settings.embedding_dimensions
            or description.metric != "cosine"
        ):
            raise ValueError("Pinecone index configuration mismatch")
        self.index = self.client.Index(host=description.host)
        self.embeddings = embeddings

    def upsert(self, version, chunks, vectors):
        for start in range(0, len(chunks), 50):
            batch = [
                {
                    "id": c.id,
                    "values": v,
                    "metadata": self.metadata_for(version, c),
                }
                for c, v in zip(
                    chunks[start : start + 50], vectors[start : start + 50], strict=True
                )
            ]
            self.index.upsert(vectors=batch, namespace=version)

    @staticmethod
    def metadata_for(version, chunk):
        if chunk.corpus_version != version:
            raise ValueError("Vector metadata must match the corpus namespace")
        result = {
            "program_id": chunk.program_id,
            "source_id": chunk.source_id,
            "corpus_version": version,
            "text": chunk.text,
            "heading": chunk.heading,
            "section_ids": chunk.section_ids,
            "cycle": chunk.cycle,
            "information_status": chunk.information_status,
            "source_checked_at": chunk.source_checked_at.isoformat()
            if chunk.source_checked_at
            else None,
            **chunk.cycle_metadata.model_dump(exclude_none=True),
        }
        if chunk.evidence:
            ref = chunk.evidence[0]
            result.update(
                source_url=ref.url,
                document_hash=ref.document_version,
                fetched_at=ref.fetched_at.isoformat(),
                source_title=ref.title,
                page_number=ref.page,
                quote_start=ref.start,
                quote_end=ref.end,
                evidence_ids=[r.id for r in chunk.evidence],
            )
        # Pinecone metadata has no null type. Omission represents unknown facts.
        return {key: value for key, value in result.items() if value is not None}

    def ready(self, version, ids):
        # Eventual consistency is not guessed: failed readiness is explicitly retried by the operator.
        found = set()
        probes = []
        for start in range(0, len(ids), 100):
            response = self.index.fetch(ids=ids[start : start + 100], namespace=version)
            found.update(response.vectors)
            if response.vectors:
                probes.append(next(iter(response.vectors.values())).values)
        if found != set(ids):
            return False
        stats = self.index.describe_index_stats()
        namespace = stats.namespaces.get(version)
        if namespace is None or namespace.vector_count != len(ids):
            return False
        for vector in probes:
            response = self.index.query(
                namespace=version,
                vector=vector,
                top_k=1,
                filter={"corpus_version": {"$eq": version}},
                include_metadata=False,
            )
            if not response.matches or any(m.id not in found for m in response.matches):
                return False
        return bool(probes)

    def search(self, question, version, program_id, limit):
        # Request-scoped adapter: reuse one query embedding across program filters.
        if getattr(self, "_query_text", None) != question:
            self._query_vector = self.embeddings.embed([question])[0]
            self._query_text = question
        query = self._query_vector
        filters = {"corpus_version": {"$eq": version}}
        if program_id:
            filters["program_id"] = {"$eq": program_id}
        response = self.index.query(
            namespace=version,
            vector=query,
            top_k=limit,
            filter=filters,
            include_metadata=False,
        )
        return [match.id for match in response.matches]
