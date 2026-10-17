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
    import time

    settings = request.app.state.settings
    session = request.scope.get("session", {})
    if (
        not getattr(request.app.state, "auth_configured", False)
        or session.get("expires", 0) <= time.time()
    ):
        raise HTTPException(401, "Verified sign-in required")
    if (
        request.method not in ("GET", "HEAD")
        and request.headers.get("origin") != settings.public_origin
    ):
        raise HTTPException(403, "Origin rejected")
    return authorize(
        AdminIdentity(subject=session.get("sub", "")), set(settings.admin_subjects)
    )


def install_auth(app, settings):
    import time

    from authlib.integrations.starlette_client import OAuth
    from fastapi.responses import RedirectResponse
    from starlette.middleware.sessions import SessionMiddleware

    configured = bool(
        (settings.environment != "production" or settings.hosted_admin_enabled)
        and settings.oidc_client_id
        and settings.session_secret
        and settings.admin_subjects
    )
    app.state.auth_configured = configured
    if configured:
        if settings.oidc_issuer != "https://replit.com/oidc":
            raise ValueError("Only the approved Replit issuer is supported")
        if len(settings.session_secret) < 32:
            raise ValueError("Session secret must contain at least 32 characters")
        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.session_secret,
            https_only=settings.environment == "production",
            same_site="lax",
            max_age=3600,
        )
        oauth = OAuth()
        oauth.register(
            "replit",
            client_id=settings.oidc_client_id,
            token_endpoint_auth_method="none",
            server_metadata_url=settings.oidc_issuer
            + "/.well-known/openid-configuration",
            client_kwargs={"scope": "openid profile", "code_challenge_method": "S256"},
        )
        app.state.oauth = oauth

    @app.get("/api/auth/status")
    def auth_status(request: Request):
        session = request.scope.get("session", {})
        return {
            "configured": configured,
            "authenticated": bool(
                session.get("sub") in settings.admin_subjects
                and session.get("expires", 0) > time.time()
            ),
        }

    @app.get("/api/auth/login")
    async def login(request: Request):
        if not configured:
            raise HTTPException(503, "Replit identity is not configured")
        return await app.state.oauth.replit.authorize_redirect(
            request, settings.public_origin + "/api/auth/callback"
        )

    @app.get("/api/auth/callback")
    async def callback(request: Request):
        if not configured:
            raise HTTPException(503, "Replit identity is not configured")
        try:
            # Authlib validates state, nonce, issuer, audience, signature and expiry.
            token = await app.state.oauth.replit.authorize_access_token(request)
            claims = token["userinfo"]
            identity = authorize(
                AdminIdentity(subject=claims["sub"]), set(settings.admin_subjects)
            )
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001 - discard provider errors without token logging
            raise HTTPException(401, "Sign-in could not be verified") from None
        request.session.clear()
        request.session.update(
            {
                "sub": identity.subject,
                "expires": min(float(claims["exp"]), time.time() + 3600),
            }
        )
        return RedirectResponse("/?admin=1")

    @app.post("/api/auth/logout")
    def logout(request: Request):
        if request.headers.get("origin") != settings.public_origin:
            raise HTTPException(403, "Origin rejected")
        if configured:
            request.session.clear()
        return {"status": "signed_out"}
