import asyncio

from fastapi import APIRouter, HTTPException, Request
from nextstep.models import (
    AnswerResult,
    ChatTurn,
    Model,
    RetrievalRequest,
    StudentProfile,
)
from pydantic import Field, model_validator
from starlette.concurrency import run_in_threadpool

router = APIRouter()


class ChatRequest(Model):
    profile: StudentProfile
    request: RetrievalRequest
    history: list[ChatTurn] = Field(default_factory=list, max_length=6)

    @model_validator(mode="after")
    def bound_history(self):
        if sum(len(t.content) for t in self.history) > 8000:
            raise ValueError("Conversation history too long")
        return self


@router.post("/api/chat", response_model=AnswerResult)
async def chat(payload: ChatRequest, request: Request):
    repo = getattr(request.app.state, "repository", None)
    factory = getattr(request.app.state, "answer_factory", None)
    if repo is None or factory is None:
        raise HTTPException(
            503, "The answer service is unavailable. You can still browse the catalog."
        )
    # Never trust browser-provided corpus IDs or forwarded addresses.
    version = repo.active_version()
    if version is None:
        raise HTTPException(503, "No corpus has been published")
    try:
        request.app.state.rate_limiter.consume(
            request.client.host if request.client else "unknown"
        )
    except ValueError:
        raise HTTPException(429, "Request limit reached. Try again later.") from None
    pinned = payload.request.model_copy(update={"corpus_version": version})
    records = repo.list_scholarships(version)
    known = {r.id for r in records}
    if not set(pinned.program_ids).issubset(known):
        raise HTTPException(
            422, "One or more selected programs are no longer in the current catalog"
        )
    try:
        async with asyncio.timeout(30):
            return await run_in_threadpool(
                lambda: factory(version, records).answer_question(
                    payload.profile, pinned, payload.history
                )
            )
    except Exception:  # noqa: BLE001 - provider details/secrets never reach public responses
        raise HTTPException(
            503,
            "The answer could not be verified. Browse the catalog or consult the official source; no automatic retry was made.",
        ) from None
