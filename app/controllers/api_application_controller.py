from fastapi import APIRouter

from app.models import application as application_model
from app.models.application import (
    ApplicationCreate,
    ApplicationUpdate,
    PostingApplicationCreate,
    UserApplicationCreate,
)


class ApiApplicationController:
    """JSON routes for applications (a user applying to a job posting).

    An application has two parents, so it is nested in two directions:
    - Direct:               /api/applications/{id}
    - Under a user:         /api/users/{user_id}/applications/{id}          ("my applications")
    - Under a job posting:  /api/job-postings/{posting_id}/applications/{id}  ("who applied to this posting")
    """

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/applications", tags=["ApiApplication"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("", self.list_all, methods=["GET"])
        self.router.add_api_route("/{application_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{application_id}", self.update, methods=["PATCH"])
        self.router.add_api_route("/{application_id}", self.delete, methods=["DELETE"])

        self.user_router = APIRouter(
            prefix="/api/users/{user_id}/applications", tags=["ApiApplication (nested under user)"]
        )
        self.user_router.add_api_route("", self.list_for_user, methods=["GET"])
        self.user_router.add_api_route("", self.create_for_user, methods=["POST"])
        self.user_router.add_api_route("/{application_id}", self.get_for_user, methods=["GET"])
        self.user_router.add_api_route("/{application_id}", self.delete_for_user, methods=["DELETE"])

        self.posting_router = APIRouter(
            prefix="/api/job-postings/{posting_id}/applications",
            tags=["ApiApplication (nested under job posting)"],
        )
        self.posting_router.add_api_route("", self.list_for_posting, methods=["GET"])
        self.posting_router.add_api_route("", self.create_for_posting, methods=["POST"])
        self.posting_router.add_api_route("/{application_id}", self.get_for_posting, methods=["GET"])
        self.posting_router.add_api_route("/{application_id}", self.update_for_posting, methods=["PATCH"])

    # Direct routes
    def create(self, data: ApplicationCreate) -> dict:
        return application_model.create_application(data.user_id, data.job_posting_id, data.cover_letter)

    def list_all(self) -> list[dict]:
        return application_model.get_applications()

    def get(self, application_id: int) -> dict:
        return application_model.get_application(application_id)

    def update(self, application_id: int, data: ApplicationUpdate) -> dict:
        return application_model.update_application(application_id, data)

    def delete(self, application_id: int) -> dict:
        application_model.delete_application(application_id)
        return {"message": "Application deleted", "id": application_id}

    # Nested under a user (the user in the path is the applicant)
    def list_for_user(self, user_id: int) -> list[dict]:
        return application_model.get_applications(user_id=user_id)

    def create_for_user(self, user_id: int, data: UserApplicationCreate) -> dict:
        return application_model.create_application(user_id, data.job_posting_id, data.cover_letter)

    def get_for_user(self, user_id: int, application_id: int) -> dict:
        return application_model.get_application(application_id, user_id=user_id)

    def delete_for_user(self, user_id: int, application_id: int) -> dict:
        application_model.delete_application(application_id, user_id=user_id)
        return {"message": "Application deleted", "id": application_id}

    # Nested under a job posting (the posting in the path is the one applied to)
    def list_for_posting(self, posting_id: int) -> list[dict]:
        return application_model.get_applications(job_posting_id=posting_id)

    def create_for_posting(self, posting_id: int, data: PostingApplicationCreate) -> dict:
        return application_model.create_application(data.user_id, posting_id, data.cover_letter)

    def get_for_posting(self, posting_id: int, application_id: int) -> dict:
        return application_model.get_application(application_id, job_posting_id=posting_id)

    def update_for_posting(self, posting_id: int, application_id: int, data: ApplicationUpdate) -> dict:
        return application_model.update_application(application_id, data, job_posting_id=posting_id)
