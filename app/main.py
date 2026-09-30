from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Alumni Tracking System")

users: list[dict] = []


class UserCreate(BaseModel):
    name: str
    email: str
    graduation_year: int
    department: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    graduation_year: int | None = None
    department: str | None = None

TEMPLATES_DIR = Path(__file__).parent / "templates"
INDEX_HTML = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
ABOUT_HTML = (TEMPLATES_DIR / "about.html").read_text(encoding="utf-8")


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


@app.post("/api/users")
def create_user(user: UserCreate):
    new_user = {"id": len(users) + 1, **user.model_dump()}
    users.append(new_user)
    return new_user


@app.get("/api/users")
def list_users():
    return users


def find_user(user_id: int) -> dict:
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return find_user(user_id)


@app.put("/api/users/{user_id}")
def replace_user(user_id: int, user: UserCreate):
    existing = find_user(user_id)
    existing.update(user.model_dump())
    return existing


@app.patch("/api/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    existing = find_user(user_id)
    existing.update(user.model_dump(exclude_unset=True))
    return existing


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    existing = find_user(user_id)
    users.remove(existing)
    return {"message": "User deleted", "id": user_id}
