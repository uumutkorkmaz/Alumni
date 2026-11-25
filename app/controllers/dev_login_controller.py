from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import auth, devlogin


class DevLoginController:
    """TEMPORARY one-click login as a role's test account (ddd.md 4.1.4). main.py registers it only
    when DEV_LOGIN=1, so with the default 0 the route does not exist at all."""

    def __init__(self) -> None:
        self.router = APIRouter(tags=["DevLogin (temporary)"], include_in_schema=False)
        self.router.add_api_route("/dev-login/{role}", self.login_as, methods=["POST"])

    def login_as(self, role: str, request: Request) -> RedirectResponse:
        if role not in devlogin.TEST_ACCOUNTS:
            raise HTTPException(status_code=404, detail="No test account for this role")
        user_id = devlogin.ensure_test_account(role)
        auth.logout(request.cookies.get(auth.COOKIE_NAME))  # leave the current session, if any
        token, lifetime = auth.open_session(user_id, False, request.headers.get("user-agent"))
        response = RedirectResponse(url="/admin" if role == "admin" else "/", status_code=303)
        auth.set_cookie(response, token, lifetime, False)
        return response
