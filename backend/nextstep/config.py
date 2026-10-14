from decimal import Decimal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    live_calls_enabled: bool = False
    openai_run_budget_usd: Decimal = Field(default=Decimal('0'), ge=0)
    openai_total_budget_usd: Decimal = Field(default=Decimal('0'), ge=0)
    environment: str = 'development'
