import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.controllers.announcement_controller import AnnouncementController
from app.controllers.api_announcement_controller import ApiAnnouncementController
from app.controllers.api_application_controller import ApiApplicationController
from app.controllers.api_job_posting_controller import ApiJobPostingController
from app.controllers.api_user_controller import ApiUserController
from app.controllers.application_controller import ApplicationController
from app.controllers.job_posting_controller import JobPostingController
from app.controllers.user_controller import UserController
from app.database.stats import get_counts
from app.middleware.logger import log_requests
from app.middleware.not_found_guardian import not_found_guardian
from app.middleware.server_error_guardian import server_error_guardian
from app.views.error_view import render_generic_not_found_page
from app.views.layout import render_page

app = FastAPI(title="Alumni Tracking System")
# The middleware added last runs outermost. From the inside out: 404 guardian, 5xx guardian
# (it also catches a failure inside the 404 guardian), logger (it logs the final answer).
app.middleware("http")(not_found_guardian)
app.middleware("http")(server_error_guardian)
app.middleware("http")(log_requests)

if os.environ.get("DEBUG_ROUTES") == "1":
    # Test-only route to see the 5xx guardian at work; it exists only when DEBUG_ROUTES=1 in .env.
    @app.get("/api/debug/error", include_in_schema=False)
    def debug_error():
        raise RuntimeError("Test error raised on purpose by /api/debug/error")

APP_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

# The templates are page bodies only; render_page adds the shared navbar, stylesheet and footer.
INDEX_BODY = (APP_DIR / "templates" / "index.html").read_text(encoding="utf-8")
ABOUT_BODY = (APP_DIR / "templates" / "about.html").read_text(encoding="utf-8")

user_controller = UserController()
api_user_controller = ApiUserController()
app.include_router(user_controller.router)
app.include_router(api_user_controller.router)

announcement_controller = AnnouncementController()
api_announcement_controller = ApiAnnouncementController()
app.include_router(announcement_controller.router)
app.include_router(api_announcement_controller.router)

api_job_posting_controller = ApiJobPostingController()
app.include_router(api_job_posting_controller.router)
app.include_router(api_job_posting_controller.nested_router)

api_application_controller = ApiApplicationController()
app.include_router(api_application_controller.router)
app.include_router(api_application_controller.user_router)
app.include_router(api_application_controller.posting_router)

job_posting_controller = JobPostingController()
application_controller = ApplicationController()
app.include_router(job_posting_controller.router)
app.include_router(application_controller.router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    counts = get_counts()
    body = INDEX_BODY
    for name in ("users", "announcements", "job_postings", "applications"):
        body = body.replace("{{" + name + "}}", str(counts[name]) if counts else "&ndash;")
    return render_page("Home", body, "/")


@app.get("/about", response_class=HTMLResponse)
def read_about():
    return render_page("About", ABOUT_BODY, "/about", narrow=True)


@app.get("/404", response_class=HTMLResponse, include_in_schema=False)
def generic_not_found(path: str = ""):
    """The generic 404 page; invalid browser requests are redirected here (see not_found_guardian).
    It still answers 404, so nobody mistakes it for a real page."""
    return HTMLResponse(render_generic_not_found_page(path[:300]), status_code=404)


@app.get("/hello")
def read_hello():
    return "Hello, World!"


@app.get("/hello/{name}")
def read_hello_name(name: str):
    return f"Hello {name}"


@app.get("/sum/{number1}/{number2}")
def read_sum(number1: int, number2: int):
    return number1 + number2


@app.get("/api/health")
def read_health():
    return {"status": "ok"}


@app.get("/api/swagger", include_in_schema=False)
def read_swagger():
    return RedirectResponse(url="/docs")
