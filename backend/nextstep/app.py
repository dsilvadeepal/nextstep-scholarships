from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from nextstep.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="NextStep Scholarships")
    from nextstep.middleware import BodyLimitMiddleware

    app.add_middleware(BodyLimitMiddleware)
    app.state.settings = settings or Settings()
    settings = app.state.settings
    from nextstep.auth import install_auth

    install_auth(app, settings)
    from nextstep.api.admin import router as admin_router

    app.include_router(admin_router)
    if settings.database_url:
        import secrets

        from nextstep.limits import RateLimiter
        from nextstep.repository import Repository
        from sqlalchemy import create_engine

        engine = create_engine(settings.database_url, pool_pre_ping=True)
        app.state.repository = Repository(engine)
        app.state.rate_limiter = RateLimiter(
            engine, settings.rate_secret or secrets.token_hex(32)
        )
    from fastapi.responses import JSONResponse
    from sqlalchemy.exc import SQLAlchemyError

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        return JSONResponse(
            {"detail": "Catalog database is unavailable"}, status_code=503
        )

    from nextstep.api.catalog import router

    app.include_router(router)
    from nextstep.api.chat import router as chat_router

    app.include_router(chat_router)
    if settings.database_url and settings.live_calls_enabled:
        from nextstep.limits import BudgetLedger
        from nextstep.providers import OpenAIEmbeddingProvider, PaidModel, PineconeStore
        from nextstep.rag.answer import AnswerService
        from nextstep.rag.retrieve import Retriever

        ledger = BudgetLedger(
            engine,
            settings.openai_run_budget_usd,
            settings.openai_total_budget_usd,
            enabled=settings.live_calls_enabled,
            run_id="public-chat",
        )

        def answer_factory(version, records):
            embeddings = OpenAIEmbeddingProvider(settings, ledger)
            return AnswerService(
                Retriever(
                    app.state.repository.get_chunks(version),
                    PineconeStore(settings, embeddings),
                ),
                PaidModel(settings, ledger),
                records,
            )

        app.state.answer_factory = answer_factory
        from nextstep.evals.service import EvaluationService

        app.state.eval_execute = EvaluationService(settings, app.state.repository)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.api_route(
        "/api/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE"],
        include_in_schema=False,
    )
    def missing_api(path: str):
        from fastapi import HTTPException

        raise HTTPException(404, "API route not found")

    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="ui")
    return app


app = create_app()
