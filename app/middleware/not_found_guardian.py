import json
from urllib.parse import quote

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.views.error_view import render_not_found_page

FRAMEWORK_DEFAULT = "Not Found"  # what FastAPI/Starlette say when no route matches
GENERIC_404_PAGE = "/404"


async def read_body(response: Response) -> bytes:
    """The whole body of a streamed answer (it can be read only once)."""
    return b"".join([chunk async for chunk in response.body_iterator])


def detail_of(body: bytes) -> str | None:
    """The 'detail' of an answer, e.g. "User not found" raised by a model."""
    try:
        detail = json.loads(body).get("detail")
    except (ValueError, AttributeError):
        return body.decode(errors="replace").strip() or None
    return detail if isinstance(detail, str) else None


async def read_detail(response: Response) -> str | None:
    return detail_of(await read_body(response))


def _route_matched(request: Request) -> bool:
    return "route" in request.scope  # set by FastAPI when a route matched the path


def _reason(request: Request, detail: str | None) -> str:
    method, path = request.method, request.url.path

    if path.startswith("/static/"):
        return f"The file {path} does not exist."
    if not _route_matched(request) and (detail is None or detail == FRAMEWORK_DEFAULT):
        return f"No route matches {method} {path}. Check the address; every API route is listed at /api/swagger."

    # A route matched, so the address is right but the record in it does not exist.
    params = request.scope.get("path_params") or {}
    where = ", ".join(f"{name}={value}" for name, value in params.items())
    what = detail if detail and detail != FRAMEWORK_DEFAULT else "Nothing was found"
    return f"{what} ({where})." if where else f"{what}."


def wants_html(request: Request) -> bool:
    """Browser pages get an HTML page; the JSON API and other clients get JSON."""
    return not request.url.path.startswith("/api/") and "text/html" in request.headers.get("accept", "")


def _only_path_errors(body: bytes) -> bool:
    """True when a 422 is about the address itself (e.g. /users/abc), not about a form or a JSON body."""
    try:
        errors = json.loads(body).get("detail")
    except (ValueError, AttributeError):
        return False
    return isinstance(errors, list) and bool(errors) and all(
        isinstance(e, dict) and (e.get("loc") or [None])[0] == "path" for e in errors
    )


def _redirect_to_generic_404(request: Request) -> RedirectResponse:
    """Invalid browser request -> the generic 404 page. GET stays GET (302); after a form POST,
    303 makes the browser load the page with GET."""
    asked = request.url.path + (f"?{request.url.query}" if request.url.query else "")
    status = 302 if request.method in ("GET", "HEAD") else 303
    return RedirectResponse(f"{GENERIC_404_PAGE}?path={quote(asked, safe='')}", status_code=status)


async def not_found_guardian(request: Request, call_next) -> Response:
    """404 guardian middleware.

    - Invalid browser requests (no route matches, or the address itself is malformed, like /users/abc)
      are redirected to the generic 404 page.
    - Every other 404 leaves the app with a reason saying why nothing was found: an HTML page with the
      reason for browsers (e.g. /users/999), JSON for the API.
    """
    response = await call_next(request)

    if request.url.path == GENERIC_404_PAGE:
        return response  # the generic 404 page answers 404 itself; it is the destination, not an error

    if response.status_code == 422 and wants_html(request):
        body = await read_body(response)
        if _only_path_errors(body):
            return _redirect_to_generic_404(request)
        # A form or body error: give the original answer back unchanged (its body was read above).
        return Response(body, status_code=422, headers=dict(response.headers))

    if response.status_code != 404:
        return response

    body = await read_body(response)
    if wants_html(request) and not _route_matched(request) and not request.url.path.startswith("/static/"):
        return _redirect_to_generic_404(request)

    reason = _reason(request, detail_of(body))
    if wants_html(request):
        return HTMLResponse(render_not_found_page(request.method, request.url.path, reason), status_code=404)
    return JSONResponse(
        status_code=404,
        content={
            "status": 404,
            "error": "Not Found",
            "reason": reason,
            "method": request.method,
            "path": request.url.path,
        },
    )
