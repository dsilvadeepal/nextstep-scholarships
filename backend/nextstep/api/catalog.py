from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request
from nextstep.matching import match_catalog
from nextstep.models import Scenario, StudentProfile
from pydantic import BaseModel

router = APIRouter()


class MatchRequest(BaseModel):
    profile: StudentProfile
    scenario: Scenario | None = None


@router.post("/api/matches")
def matches(payload: MatchRequest, request: Request):
    repo = getattr(request.app.state, "repository", None)
    if repo is None:
        raise HTTPException(503, "Scholarship catalog is not connected yet")
    version = repo.active_version()
    if version is None:
        raise HTTPException(503, "No scholarship corpus has been published yet")
    profile = payload.profile
    if payload.scenario:
        profile = StudentProfile.model_validate(
            {**profile.model_dump(), **payload.scenario.overrides}
        )
    records = repo.list_scholarships(version)
    return {
        "corpus_version": version,
        "matches": match_catalog(
            records, profile, datetime.now(ZoneInfo("America/New_York")).date()
        ),
        "scholarships": records,
        "coverage": {
            "program_count": len(records),
            "note": "Collection is not comprehensive; automatically extracted rules are provisional.",
        },
    }
