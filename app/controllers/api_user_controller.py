from fastapi import APIRouter

from app.models import user as user_model
from app.models.user import UserCreate, UserUpdate


class ApiUserController:
    """Independent controller: exposes user CRUD operations as REST API routes under /api/users."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/users", tags=["ApiUser"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("", self.list, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.replace, methods=["PUT"])
        self.router.add_api_route("/{user_id}", self.update, methods=["PATCH"])
        self.router.add_api_route("/{user_id}", self.delete, methods=["DELETE"])

    def create(self, data: UserCreate) -> dict:
        return user_model.create_user(data)

    def list(self) -> list[dict]:
        return user_model.get_users()

    def get(self, user_id: int) -> dict:
        return user_model.get_user(user_id)

    def replace(self, user_id: int, data: UserCreate) -> dict:
        return user_model.update_user(user_id, data)

    def update(self, user_id: int, data: UserUpdate) -> dict:
        return user_model.partial_update_user(user_id, data)

    def delete(self, user_id: int) -> dict:
        user_model.delete_user(user_id)
        return {"message": "User deleted", "id": user_id}
