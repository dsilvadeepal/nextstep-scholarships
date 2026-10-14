"""Fail closed until a supported identity verifier is configured.

AdminIdentity is created only by a server-side verifier, never from request JSON.
"""

from dataclasses import dataclass

from fastapi import HTTPException, Request


@dataclass(frozen=True)
class AdminIdentity:
    subject: str


def authorize(identity, allowed_subjects):
    if not isinstance(identity, AdminIdentity):
        raise HTTPException(401, "Verified sign-in required")
    if identity.subject not in allowed_subjects:
        raise HTTPException(403, "Owner access required")
    return identity


async def require_admin(request: Request) -> AdminIdentity:
    # No identity header or client-supplied subject is trusted.
    raise HTTPException(401, "Admin identity integration is not configured")
