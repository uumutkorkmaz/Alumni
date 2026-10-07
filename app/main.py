from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from app.controllers.api_user_controller import ApiUserController
from app.controllers.user_controller import UserController

app = FastAPI(title="Alumni Tracking System")

TEMPLATES_DIR = Path(__file__).parent / "templates"
INDEX_HTML = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
ABOUT_HTML = (TEMPLATES_DIR / "about.html").read_text(encoding="utf-8")

user_controller = UserController()
api_user_controller = ApiUserController()
app.include_router(user_controller.router)
app.include_router(api_user_controller.router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return INDEX_HTML


@app.get("/about", response_class=HTMLResponse)
def read_about():
    return ABOUT_HTML


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
