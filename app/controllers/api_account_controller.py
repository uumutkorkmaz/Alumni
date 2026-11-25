from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel

from app import policy
from app.controllers.account_controller import _hash
from app.models import account
from app.models import profile as profile_model


class ProfileUpdate(BaseModel):
    company: str | None = None
    job_title: str | None = None
    city: str | None = None
    linkedin_url: str | None = None
    bio: str | None = None


class PasswordChange(BaseModel):
    current: str = ""
    new: str
    confirm: str


class ApiAccountController:
    """The signed-in person's own data as JSON, under /api/me (ddd.md 4.1.6). GET /api/me itself
    (who am I) is in ApiAuthController."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/me", tags=["ApiMyAccount"])
        r = self.router.add_api_route
        r("/profile", self.profile, methods=["GET"])
        r("/profile", self.update_profile, methods=["PATCH"])
        r("/applications", self.applications, methods=["GET"])
        r("/applications/{application_id}/withdraw", self.withdraw, methods=["POST"])
        r("/saved", self.saved, methods=["GET"])
        r("/saved/{posting_id}", self.save, methods=["PUT"], status_code=204)
        r("/saved/{posting_id}", self.unsave, methods=["DELETE"], status_code=204)
        r("/postings", self.postings, methods=["GET"])
        r("/received", self.received, methods=["GET"])
        r("/announcements", self.announcements, methods=["GET"])
        r("/sessions", self.sessions, methods=["GET"])
        r("/password", self.change_password, methods=["POST"])
        # Public profile sections and the CV (ddd.md 4.1.7). Month fields are "YYYY-MM".
        r("/profile/{kind}", self.add_entry, methods=["POST"], status_code=201)
        r("/profile/{kind}/{item_id}", self.change_entry, methods=["PUT"])
        r("/profile/{kind}/{item_id}", self.delete_entry, methods=["DELETE"], status_code=204)
        r("/cv", self.cv, methods=["GET"])
        r("/cv", self.upload_cv, methods=["POST"], status_code=201)
        r("/cv", self.remove_cv, methods=["DELETE"], status_code=204)

    def profile(self) -> dict:
        return account.profile(policy.actor()["id"])

    def update_profile(self, data: ProfileUpdate) -> dict:
        uid = policy.actor()["id"]
        current = account.profile(uid)
        merged = {**{k: current.get(k) or "" for k in account.PROFILE_FIELDS}, **data.model_dump(exclude_unset=True)}
        values, errors = account.clean_profile({k: v or "" for k, v in merged.items()})
        if errors:
            raise HTTPException(status_code=422, detail=errors)
        return account.update_profile(uid, values)

    def applications(self) -> list[dict]:
        return account.my_applications(policy.actor()["id"])

    def withdraw(self, application_id: int) -> dict:
        uid = policy.actor()["id"]
        account.withdraw(uid, application_id)
        return next(a for a in account.my_applications(uid) if a["id"] == application_id)

    def saved(self) -> list[dict]:
        return account.saved(policy.actor()["id"])

    def save(self, posting_id: int) -> Response:
        account.save(policy.actor()["id"], posting_id)
        return Response(status_code=204)

    def unsave(self, posting_id: int) -> Response:
        account.unsave(policy.actor()["id"], posting_id)
        return Response(status_code=204)

    def postings(self) -> list[dict]:
        user = policy.actor()
        return account.my_postings(user["id"], user["role"] in ("staff", "admin"))

    def received(self) -> list[dict]:
        user = policy.actor()
        return account.received(user["id"], user["role"] in ("staff", "admin"))

    def announcements(self) -> list[dict]:
        return account.my_announcements(policy.actor()["id"])

    def sessions(self, request: Request) -> list[dict]:
        return account.sessions(policy.actor()["id"], _hash(request))

    def change_password(self, data: PasswordChange, request: Request) -> dict:
        ended = account.change_password(policy.actor()["id"], data.current, data.new, data.confirm, _hash(request))
        return {"changed": True, "other_sessions_ended": ended}

    # ------------------------------------------------------------------ profile sections and CV
    def _clean(self, kind: str, data: dict) -> dict:
        if kind not in profile_model.TABLES:
            raise HTTPException(status_code=404, detail="Unknown profile section")
        values, errors = profile_model.clean(kind, {k: ("" if v is None else v if isinstance(v, bool) else str(v)) for k, v in data.items()})
        if errors:
            raise HTTPException(status_code=422, detail=errors)
        return values

    def add_entry(self, kind: str, data: dict) -> dict:
        uid = policy.actor()["id"]
        profile_model.add(uid, kind, self._clean(kind, data))
        return profile_model.sections(uid)

    def change_entry(self, kind: str, item_id: int, data: dict) -> dict:
        uid = policy.actor()["id"]
        profile_model.change(uid, kind, item_id, self._clean(kind, data))
        return profile_model.sections(uid)

    def delete_entry(self, kind: str, item_id: int) -> Response:
        profile_model.remove(policy.actor()["id"], kind, item_id)
        return Response(status_code=204)

    def cv(self) -> dict | None:
        return profile_model.current_cv(policy.actor()["id"])

    async def upload_cv(self, cv: UploadFile = File(...)) -> dict:
        uid = policy.actor()["id"]
        return profile_model.save_cv(uid, cv.filename or "cv.pdf", await cv.read(profile_model.MAX_CV_BYTES + 1))

    def remove_cv(self) -> Response:
        profile_model.remove_cv(policy.actor()["id"])
        return Response(status_code=204)
