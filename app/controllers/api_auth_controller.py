from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import auth


class LoginBody(BaseModel):
    email: str
    password: str
    remember: bool = False


class ApiAuthController:
    """Login and logout for API clients (Postman, Swagger) (ddd.md 4.1.3). The session is the same
    HttpOnly cookie as on the pages: Postman keeps it and sends it with the next requests."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api", tags=["ApiAuth"])
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/me", self.me, methods=["GET"])

    def login(self, request: Request, body: LoginBody):
        try:
            token, user, lifetime = auth.login(body.email, body.password, body.remember, request.headers.get("user-agent"))
        except auth.LoginError as error:
            status = 429 if error.code == "throttled" else 401 if error.code == "invalid" else 403
            detail = auth.message(error.code, "en")
            if error.code == "rejected" and error.reason:
                detail += f" Reason: {error.reason}"
            return JSONResponse({"detail": detail}, status_code=status)
        response = JSONResponse({"message": "Signed in", "user": user})
        auth.set_cookie(response, token, lifetime, body.remember)
        return response

    def logout(self, request: Request):
        auth.logout(request.cookies.get(auth.COOKIE_NAME))
        response = JSONResponse({"message": "Signed out"})
        auth.clear_cookie(response)
        return response

    def me(self) -> dict:
        user = auth.me()
        if user is None:  # the middleware already answers 401; kept for safety
            raise HTTPException(status_code=401, detail="Not signed in")
        return user
