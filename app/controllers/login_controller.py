import re

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import auth
from app.views.login_view import render_login_page


def safe_next(target: str | None) -> str:
    """Where to go after signing in: only a path on this site (no "//evil.com", no full URL)."""
    if target and target.startswith("/") and not target.startswith("//") and not re.match(r"^/\\", target):
        return target[:300]
    return "/"


class LoginController:
    """Login and logout through the HTML pages (ddd.md 4.1.3). Public, in Turkish."""

    def __init__(self) -> None:
        self.router = APIRouter(tags=["Login"])
        self.router.add_api_route("/login", self.form, methods=["GET"])
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])

    def form(self, next: str = "") -> HTMLResponse:
        if auth.me():
            return RedirectResponse(url=safe_next(next), status_code=303)
        return HTMLResponse(render_login_page(email="", next_url=safe_next(next) if next else "", error=""))

    def login(
        self,
        request: Request,
        email: str = Form(""),
        password: str = Form(""),
        remember: str = Form(""),
        next: str = Form(""),
    ):
        remember_me = remember.lower() in ("1", "on", "true")
        try:
            token, _user, lifetime = auth.login(email, password, remember_me, request.headers.get("user-agent"))
        except auth.LoginError as error:
            text = auth.message(error.code)
            if error.code == "rejected" and error.reason:
                text += f" Neden: {error.reason}"
            status = 429 if error.code == "throttled" else 401 if error.code == "invalid" else 403
            return HTMLResponse(
                render_login_page(email=email, next_url=safe_next(next) if next else "", error=text),
                status_code=status,
            )
        response = RedirectResponse(url=safe_next(next), status_code=303)
        auth.set_cookie(response, token, lifetime, remember_me)
        return response

    def logout(self, request: Request) -> RedirectResponse:
        auth.logout(request.cookies.get(auth.COOKIE_NAME))
        response = RedirectResponse(url="/", status_code=303)
        auth.clear_cookie(response)
        return response
