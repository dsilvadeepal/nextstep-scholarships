from decimal import Decimal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    live_calls_enabled: bool = False
    openai_run_budget_usd: Decimal = Field(default=Decimal(0), ge=0)
    openai_total_budget_usd: Decimal = Field(default=Decimal(0), ge=0)
    environment: str = "development"
    database_url: str | None = None
    session_secret: str | None = None
    public_origin: str = "http://127.0.0.1:8014"
    oidc_client_id: str | None = None
    oidc_issuer: str = "https://replit.com/oidc"
    admin_subjects: list[str] = Field(default_factory=list)
    rate_secret: str | None = None
    openai_api_key: str | None = None
    answer_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    pinecone_api_key: str | None = None
    pinecone_index: str | None = None
    app_storage_bucket_id: str | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str = "nextstep-fictional-evals"
    pricing_effective_date: str | None = None
    input_usd_per_million: Decimal | None = None
    output_usd_per_million: Decimal | None = None
    embedding_usd_per_million: Decimal | None = None

    @model_validator(mode="after")
    def validate_production(self):
        if self.environment == "production":
            if not self.database_url or not self.database_url.startswith("postgresql"):
                raise ValueError(
                    "Production requires an explicitly configured PostgreSQL database"
                )
            if (
                not self.public_origin.startswith("https://")
                or not self.rate_secret
                or len(self.rate_secret) < 32
            ):
                raise ValueError(
                    "Production requires HTTPS public origin and stable rate secret"
                )
            if (
                not self.session_secret
                or len(self.session_secret) < 32
                or not self.oidc_client_id
                or not self.admin_subjects
            ):
                raise ValueError(
                    "Production requires verified owner identity configuration"
                )
        for amount in [
            self.input_usd_per_million,
            self.output_usd_per_million,
            self.embedding_usd_per_million,
        ]:
            if amount is not None and (not amount.is_finite() or amount < 0):
                raise ValueError("Provider prices must be finite and nonnegative")
        return self
