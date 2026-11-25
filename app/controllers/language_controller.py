from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import i18n


class LanguageController:
    """GET /lang/{tr|en}: remember the language for a year and go back to the page the visitor was on
    (only an address on this site; anything else goes to the home page)."""

    def __init__(self) -> None:
        self.router = APIRouter(tags=["Language"])
        self.router.add_api_route("/lang/{code}", self.choose, methods=["GET"])

    def choose(self, code: str, request: Request, next: str = "") -> RedirectResponse:
        if code not in i18n.LANGS:
            raise HTTPException(status_code=404, detail="Unknown language")
        back = next or request.headers.get("referer", "/")
        parts = urlsplit(back)
        same_site = not parts.netloc or parts.netloc == request.url.netloc
        path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        if not same_site or not path.startswith("/") or path.startswith("//") or path.startswith("/lang/"):
            path = "/"
        response = RedirectResponse(url=path, status_code=303)
        response.set_cookie(i18n.COOKIE, code, max_age=365 * 24 * 3600, samesite="lax", path="/")
        return response
