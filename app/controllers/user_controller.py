from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.models import user as user_model
from app.models.user import UserCreate, UserUpdate
from app.views.user_view import render_user_detail, render_user_edit_form, render_user_list


class UserController:
    """Independent controller: full CRUD for users under /users, managed through the HTML view layer."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/users", tags=["User"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("/{user_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{user_id}/edit", self.edit_form, methods=["GET"])
        self.router.add_api_route("/{user_id}/edit", self.update, methods=["POST"])
        self.router.add_api_route("/{user_id}/delete", self.delete, methods=["POST"])

    def list(self) -> HTMLResponse:
        """GET /users -> listing (R): renders the users table."""
        users = user_model.get_users()
        return HTMLResponse(render_user_list(users))

    def create(
        self,
        name: str = Form(...),
        email: str = Form(...),
        graduation_year: int = Form(...),
        department: str = Form(...),
    ) -> RedirectResponse:
        """POST /users -> creating (C): creates the user then redirects back to the listing."""
        try:
            data = UserCreate(
                name=name, email=email, graduation_year=graduation_year, department=department
            )
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors(include_url=False, include_context=False))
        user_model.create_user(data)
        return RedirectResponse(url="/users", status_code=303)

    def get(self, user_id: int) -> HTMLResponse:
        """GET /users/{id} -> detail page (R)."""
        user = user_model.get_user(user_id)
        return HTMLResponse(render_user_detail(user))

    def edit_form(self, user_id: int) -> HTMLResponse:
        """GET /users/{id}/edit -> pre-filled edit form."""
        user = user_model.get_user(user_id)
        return HTMLResponse(render_user_edit_form(user))

    def update(
        self,
        user_id: int,
        name: str = Form(...),
        email: str = Form(...),
        graduation_year: int = Form(...),
        department: str = Form(...),
    ) -> RedirectResponse:
        """POST /users/{id}/edit -> updating (U): HTML forms can't send PUT/PATCH,
        so the edit form submits here instead; redirects back to the detail page."""
        try:
            data = UserUpdate(
                name=name, email=email, graduation_year=graduation_year, department=department
            )
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=error.errors(include_url=False, include_context=False))
        user_model.partial_update_user(user_id, data)
        return RedirectResponse(url=f"/users/{user_id}", status_code=303)

    def delete(self, user_id: int) -> RedirectResponse:
        """POST /users/{id}/delete -> deleting (D): HTML forms can't send DELETE,
        so the delete button submits here instead; redirects back to the listing."""
        user_model.delete_user(user_id)
        return RedirectResponse(url="/users", status_code=303)
