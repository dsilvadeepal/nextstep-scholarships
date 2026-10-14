import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from nextstep.models import StudentProfile
from nextstep.config import Settings
from nextstep.app import create_app


def test_profile_limits_and_unknowns():
    assert StudentProfile().gpa is None
    assert StudentProfile().grade is None
    with pytest.raises(ValidationError):
        StudentProfile(prospective_colleges=["a", "b", "c", "d"])
    profile = StudentProfile(
        gpa={"value": 3.4, "scale": 4, "type": "unweighted", "estimated": True}
    )
    assert profile.gpa.estimated is True


def test_health_excludes_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-secret")
    client = TestClient(create_app())
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/nonexistent").status_code == 404


def test_paid_calls_default_disabled():
    assert Settings(_env_file=None).live_calls_enabled is False
