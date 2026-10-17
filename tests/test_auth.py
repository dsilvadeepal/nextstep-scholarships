import pytest
from fastapi import HTTPException
from nextstep.auth import AdminIdentity, authorize


def test_forged_or_missing_identity_denied():
    for identity in [None, {"sub": "owner"}, "owner"]:
        with pytest.raises(HTTPException) as exc:
            authorize(identity, {"owner"})
        assert exc.value.status_code == 401


def test_verified_identity_must_be_allowlisted():
    with pytest.raises(HTTPException) as exc:
        authorize(AdminIdentity(subject="other"), {"owner"})
    assert exc.value.status_code == 403
    assert authorize(AdminIdentity(subject="owner"), {"owner"}).subject == "owner"
