import logging
import traceback
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import OperationalError

from app.middleware.not_found_guardian import read_detail, wants_html
from app.views.error_view import render_server_error_page

# The full error (with traceback) is written to logs/error.logs, not to the terminal, so errors
# can be read later; the client never sees internals. In Docker, ./logs is mounted from the project.
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
ERROR_LOG = LOG_DIR / "error.logs"
APP_DIR = Path(__file__).resolve().parents[1]
MIDDLEWARE_DIR = APP_DIR / "middleware"

class ReopeningFileHandler(RotatingFileHandler):
    """If error.logs is deleted while the app runs (e.g. to clear it), start a new file instead of
    writing into the deleted one."""

    def emit(self, record: logging.LogRecord) -> None:
        if self.stream is not None and not Path(self.baseFilename).exists():
            self.stream.close()
            self.stream = None  # the next write opens (creates) the file again
        LOG_DIR.mkdir(exist_ok=True)
        super().emit(record)


logger = logging.getLogger("alumni.errors")
logger.setLevel(logging.ERROR)
logger.propagate = False
if not logger.handlers:
    LOG_DIR.mkdir(exist_ok=True)
    # At 1 MB the file is renamed to error.logs.1 (up to 5 old files kept), so it never grows forever.
    handler = ReopeningFileHandler(ERROR_LOG, maxBytes=1_000_000, backupCount=5, encoding="utf-8", delay=True)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

STATUS_TEXT = {
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}
DEFAULT_REASON = {
    500: "Something went wrong on the server. This is our mistake, not yours; it has been logged with the error id below.",
    503: "The database is not reachable right now, so this request could not be completed. Please try again in a moment.",
}


def _answer(request: Request, status: int, reason: str, error_id: str) -> Response:
    title = STATUS_TEXT.get(status, "Server Error")
    if wants_html(request):
        page = render_server_error_page(status, title, reason, error_id, request.method, request.url.path)
        return HTMLResponse(page, status_code=status)
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "error": title,
            "reason": reason,
            "error_id": error_id,
            "method": request.method,
            "path": request.url.path,
        },
    )


def _log(request: Request, status: int, error_id: str, what: str, error: Exception | None = None) -> None:
    """One record per error in logs/error.logs: a header line, the cause, the traceback, a separator."""
    query = f"?{request.url.query}" if request.url.query else ""
    details = _where(error) if error else ""
    logger.error(
        f"{datetime.now():%Y-%m-%d %H:%M:%S}  ERROR {error_id}  {request.method} {request.url.path}{query}  {status}\n"
        f"cause: {what}\n{details}{'-' * 80}"
    )


def _where(error: Exception) -> str:
    """Where it failed, in a few lines: the frames of our own code (routes, controllers, models),
    the library frame where it finally broke, and the error message. Framework plumbing
    (Starlette, AnyIO, our middleware) is left out so the cause is easy to see."""
    frames = traceback.extract_tb(error.__traceback__)
    ours = [f for f in frames if f.filename.startswith(str(APP_DIR)) and not f.filename.startswith(str(MIDDLEWARE_DIR))]
    lines = ["where (our code):"]
    lines += [f"  {_short(f.filename)}:{f.lineno} in {f.name}: {f.line}" for f in ours] or ["  (not in our code)"]
    last = frames[-1] if frames else None
    if last is not None and last not in ours:
        lines.append(f"failed inside: {_short(last.filename)}:{last.lineno} in {last.name}")
    message = str(error).strip().splitlines()[0] if str(error).strip() else ""
    lines.append(f"error: {type(error).__module__}.{type(error).__name__}: {message}")
    return "\n".join(lines) + "\n"


def _short(filename: str) -> str:
    """app/models/user.py for our files, sqlalchemy/engine/base.py for libraries."""
    for marker in ("site-packages/", str(APP_DIR.parent) + "/"):
        if marker in filename:
            return filename.split(marker, 1)[1]
    return filename


async def server_error_guardian(request: Request, call_next) -> Response:
    """5xx guardian middleware: a server-side failure answers with a status, a reason and an error id,
    never with a traceback. The details are written to the terminal under the same error id."""
    error_id = uuid.uuid4().hex[:8]
    try:
        response = await call_next(request)
    except OperationalError as error:
        # The database server is another program; when it cannot be reached the answer is 503.
        _log(request, 503, error_id, f"database unreachable: {type(error).__name__}", error)
        return _answer(request, 503, DEFAULT_REASON[503], error_id)
    except Exception as error:
        _log(request, 500, error_id, f"{type(error).__name__}: {error}", error)
        return _answer(request, 500, DEFAULT_REASON[500], error_id)

    if response.status_code < 500:
        return response

    # A route answered 5xx on purpose: keep its own reason if it gave one.
    detail = await read_detail(response)
    _log(request, response.status_code, error_id, f"answered by the route: {detail or 'no detail'}")
    reason = detail or DEFAULT_REASON.get(response.status_code, DEFAULT_REASON[500])
    return _answer(request, response.status_code, reason, error_id)
