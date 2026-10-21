from fastapi import APIRouter

from app.models import job_posting as job_posting_model
from app.models.job_posting import JobPostingBase, JobPostingCreate, JobPostingUpdate


class ApiJobPostingController:
    """JSON routes for job postings, in two shapes.

    Direct routes treat a posting as a resource of its own: /api/job-postings/{id}.
    Nested routes reach it through its owner, mirroring users -> job_postings:
    /api/users/{user_id}/job-postings/{id}.
    """

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/job-postings", tags=["ApiJobPosting"])
        self.router.add_api_route("", self.create, methods=["POST"])
        self.router.add_api_route("", self.list_all, methods=["GET"])
        self.router.add_api_route("/{posting_id}", self.get, methods=["GET"])
        self.router.add_api_route("/{posting_id}", self.replace, methods=["PUT"])
        self.router.add_api_route("/{posting_id}", self.update, methods=["PATCH"])
        self.router.add_api_route("/{posting_id}", self.delete, methods=["DELETE"])

        self.nested_router = APIRouter(
            prefix="/api/users/{user_id}/job-postings", tags=["ApiJobPosting (nested under user)"]
        )
        self.nested_router.add_api_route("", self.list_for_user, methods=["GET"])
        self.nested_router.add_api_route("", self.create_for_user, methods=["POST"])
        self.nested_router.add_api_route("/{posting_id}", self.get_for_user, methods=["GET"])
        self.nested_router.add_api_route("/{posting_id}", self.delete_for_user, methods=["DELETE"])

    # Direct routes
    def create(self, data: JobPostingCreate) -> dict:
        return job_posting_model.create_job_posting(data)

    def list_all(self) -> list[dict]:
        return job_posting_model.get_job_postings()

    def get(self, posting_id: int) -> dict:
        return job_posting_model.get_job_posting(posting_id)

    def replace(self, posting_id: int, data: JobPostingCreate) -> dict:
        return job_posting_model.update_job_posting(posting_id, data)

    def update(self, posting_id: int, data: JobPostingUpdate) -> dict:
        return job_posting_model.partial_update_job_posting(posting_id, data)

    def delete(self, posting_id: int) -> dict:
        job_posting_model.delete_job_posting(posting_id)
        return {"message": "Job posting deleted", "id": posting_id}

    # Nested routes (the user in the path is the owner)
    def list_for_user(self, user_id: int) -> list[dict]:
        return job_posting_model.get_job_postings(user_id)

    def create_for_user(self, user_id: int, data: JobPostingBase) -> dict:
        return job_posting_model.create_job_posting_for_user(user_id, data)

    def get_for_user(self, user_id: int, posting_id: int) -> dict:
        return job_posting_model.get_job_posting(posting_id, user_id)

    def delete_for_user(self, user_id: int, posting_id: int) -> dict:
        job_posting_model.delete_job_posting(posting_id, user_id)
        return {"message": "Job posting deleted", "id": posting_id}
