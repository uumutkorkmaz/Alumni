import logging
import sys
import time
from datetime import datetime

from fastapi import Request, Response

# One line per request on the terminal (stdout, so `docker compose logs api` shows it too):
#   time      method route status duration
#   10:20:30  POST /api/users 201 18 ms
logger = logging.getLogger("alumni.requests")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def _write(started_at: datetime, method: str, path: str, status: int, started: float) -> None:
    duration_ms = round((time.perf_counter() - started) * 1000)
    logger.info(f"{started_at:%H:%M:%S}  {method} {path} {status} {duration_ms} ms")


async def log_requests(request: Request, call_next) -> Response:
    """Logger middleware: runs around every request, before and after the route's controller."""
    started_at = datetime.now()
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # An unhandled error still gets a line (500), then the error goes on to FastAPI as before.
        _write(started_at, request.method, request.url.path, 500, started)
        raise
    _write(started_at, request.method, request.url.path, response.status_code, started)
    return response
