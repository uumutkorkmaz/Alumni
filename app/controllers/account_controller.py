from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import auth, policy
from app.models import account
from app.models import profile as profile_model
from app.models import registration as registration_model
from app.models.user import APPLICANT_ROLES, AUTHOR_ROLES, POSTER_ROLES
from app.views.account_view import (
    render_me_announcements,
    render_me_applications,
    render_me_overview,
    render_me_postings,
    render_me_profile,
    render_me_saved,
    render_me_security,
)


def _back(path: str, done: str = "", error: str = "") -> RedirectResponse:
    """Back to a page with a one-line result (or the reason it was refused)."""
    path, _, fragment = path.partition("#")
    sep = "&" if "?" in path else "?"
    query = f"error={quote(error[:200])}" if error else f"done={quote(done[:200])}"
    return RedirectResponse(url=f"{path}{sep}{query}" + (f"#{fragment}" if fragment else ""), status_code=303)


def _do(path: str, done: str, action) -> RedirectResponse:
    try:
        action()
    except HTTPException as error:
        return _back(path, error=str(error.detail))
    return _back(path, done=done)


def _safe(back: str, default: str) -> str:
    """Only this site's own job posting and /me pages as the place to go back to."""
    ok = back.startswith(("/me", "/job-postings")) and not back.startswith("//") and "\\" not in back
    return back if ok else default


def _hash(request: Request) -> str:
    return account.token_hash(request.cookies.get(auth.COOKIE_NAME))


class AccountController:
    """The signed-in person's own pages under /me (ddd.md 4.1.6). Everything here works on the
    signed-in user only: no id of another account is ever taken from the address or the form."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/me", tags=["My account"])
        r = self.router.add_api_route
        r("", self.overview, methods=["GET"])
        r("/profile", self.profile, methods=["GET"])
        r("/profile", self.save_profile, methods=["POST"])
        r("/applications", self.applications, methods=["GET"])
        r("/applications/{application_id}/withdraw", self.withdraw, methods=["POST"])
        r("/applications/{application_id}/letter", self.letter, methods=["POST"])
        r("/saved", self.saved, methods=["GET"])
        r("/saved/{posting_id}", self.save, methods=["POST"])
        r("/saved/{posting_id}/remove", self.unsave, methods=["POST"])
        r("/postings", self.postings, methods=["GET"])
        r("/postings/{posting_id}/active", self.set_posting_active, methods=["POST"])
        r("/received/{application_id}/status", self.decide, methods=["POST"])
        r("/announcements", self.announcements, methods=["GET"])
        r("/security", self.security, methods=["GET"])
        r("/password", self.change_password, methods=["POST"])
        r("/sessions/end-others", self.end_other_sessions, methods=["POST"])
        r("/sessions/{session_id}/end", self.end_session, methods=["POST"])
        r("/delete", self.delete_account, methods=["POST"])
        # The public profile's sections and the CV (ddd.md 4.1.7)
        r("/profile/{kind}", self.add_entry, methods=["POST"])
        r("/profile/{kind}/{item_id}", self.change_entry, methods=["POST"])
        r("/profile/{kind}/{item_id}/delete", self.delete_entry, methods=["POST"])
        r("/cv", self.upload_cv, methods=["POST"])
        r("/cv/remove", self.remove_cv, methods=["POST"])

    # ------------------------------------------------------------------ overview and profile
    def overview(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        role, uid = user["role"], user["id"]
        data = {
            "applications": account.my_applications(uid) if role in APPLICANT_ROLES else [],
            "saved": account.saved(uid) if role in APPLICANT_ROLES else [],
            "suggestions": account.suggestions(uid) if role in APPLICANT_ROLES else [],
            "postings": account.my_postings(uid, role in ("staff", "admin")) if role in POSTER_ROLES else [],
            "announcements": account.my_announcements(uid) if role in AUTHOR_ROLES else [],
            "pending": registration_model.pending_count() if role == "admin" else 0,
        }
        return HTMLResponse(render_me_overview(user, account.profile(uid), data, done, error))

    def profile(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        return HTMLResponse(render_me_profile(user, account.profile(user["id"]), done=done, error=error,
                                              sections=profile_model.sections(user["id"]),
                                              cv=profile_model.current_cv(user["id"])))

    async def save_profile(self, request: Request) -> HTMLResponse:
        user = policy.actor()
        form = await request.form()
        values, errors = account.clean_profile({k: str(v) for k, v in form.items()})
        if errors:
            page = render_me_profile(user, account.profile(user["id"]), values, errors,
                                     error="The profile was not saved: check the marked fields.",
                                     sections=profile_model.sections(user["id"]), cv=profile_model.current_cv(user["id"]))
            return HTMLResponse(page, status_code=422)
        account.update_profile(user["id"], values)
        return _back("/me/profile", done="Profile saved. It shows on your public profile.")

    # ------------------------------------------------------------------ profile sections and the CV
    async def _entry(self, request: Request, kind: str, item_id: int | None) -> RedirectResponse:
        uid = policy.actor()["id"]
        back = f"/me/profile#{kind}"
        if kind not in profile_model.TABLES:
            raise HTTPException(status_code=404, detail="Unknown profile section")
        form = {k: str(v) for k, v in (await request.form()).items()}
        values, errors = profile_model.clean(kind, form)
        if errors:
            return _back(back, error="Not saved: " + " ".join(errors.values()))
        if item_id is None:
            return _do(back, "Added to your profile.", lambda: profile_model.add(uid, kind, values))
        return _do(back, "Saved.", lambda: profile_model.change(uid, kind, item_id, values))

    async def add_entry(self, request: Request, kind: str) -> RedirectResponse:
        return await self._entry(request, kind, None)

    async def change_entry(self, request: Request, kind: str, item_id: int) -> RedirectResponse:
        return await self._entry(request, kind, item_id)

    def delete_entry(self, kind: str, item_id: int) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do(f"/me/profile#{kind}", "Deleted from your profile.", lambda: profile_model.remove(uid, kind, item_id))

    async def upload_cv(self, cv: UploadFile = File(...)) -> RedirectResponse:
        uid = policy.actor()["id"]
        content = await cv.read(profile_model.MAX_CV_BYTES + 1)
        return _do("/me/profile#cv", "CV saved. Attach it when you apply.",
                   lambda: profile_model.save_cv(uid, cv.filename or "cv.pdf", content))

    def remove_cv(self) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do("/me/profile#cv", "CV removed.", lambda: profile_model.remove_cv(uid))

    # ------------------------------------------------------------------ applications and saved postings
    def applications(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        return HTMLResponse(render_me_applications(user, account.my_applications(user["id"]), done, error))

    def withdraw(self, application_id: int) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do("/me/applications", "Application withdrawn.", lambda: account.withdraw(uid, application_id))

    def letter(self, application_id: int, cover_letter: str = Form("")) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do("/me/applications", "Cover letter saved.", lambda: account.edit_cover_letter(uid, application_id, cover_letter))

    def saved(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        return HTMLResponse(render_me_saved(user, account.saved(user["id"]), done, error))

    def save(self, posting_id: int, back: str = Form("/me/saved")) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do(_safe(back, "/me/saved"), "Saved. Find it under My account, Saved postings.", lambda: account.save(uid, posting_id))

    def unsave(self, posting_id: int, back: str = Form("/me/saved")) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do(_safe(back, "/me/saved"), "Removed from your saved postings.", lambda: account.unsave(uid, posting_id))

    # ------------------------------------------------------------------ postings and the applications they received
    def postings(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        department = user["role"] in ("staff", "admin")
        return HTMLResponse(render_me_postings(
            user, account.my_postings(user["id"], department), account.received(user["id"], department), done, error))

    def set_posting_active(self, posting_id: int, active: str = Form(...)) -> RedirectResponse:
        user, on = policy.actor(), active == "1"
        return _do("/me/postings", "Posting opened." if on else "Posting closed: nobody can apply now.",
                   lambda: account.set_posting_active(user, posting_id, on))

    def decide(self, application_id: int, status: str = Form(...)) -> RedirectResponse:
        user = policy.actor()
        return _do("/me/postings#received", "Decision saved; the applicant sees it on their page.",
                   lambda: account.decide(user, application_id, status))

    # ------------------------------------------------------------------ announcements
    def announcements(self, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        return HTMLResponse(render_me_announcements(user, account.my_announcements(user["id"]), done, error))

    # ------------------------------------------------------------------ security
    def security(self, request: Request, done: str = "", error: str = "") -> HTMLResponse:
        user = policy.actor()
        return HTMLResponse(render_me_security(
            user, account.profile(user["id"]), account.sessions(user["id"], _hash(request)), done, error))

    def change_password(self, request: Request, current: str = Form(""), new: str = Form(""),
                        confirm: str = Form("")) -> RedirectResponse:
        user = policy.actor()
        try:
            ended = account.change_password(user["id"], current, new, confirm, _hash(request))
        except HTTPException as error:
            return _back("/me/security", error=str(error.detail))
        others = f" {ended} other session(s) were signed out." if ended else ""
        return _back("/me/security", done="Password saved." + others)

    def end_session(self, session_id: int) -> RedirectResponse:
        uid = policy.actor()["id"]
        return _do("/me/security", "That browser was signed out.", lambda: account.end_session(uid, session_id))

    def end_other_sessions(self, request: Request) -> RedirectResponse:
        n = account.end_other_sessions(policy.actor()["id"], _hash(request))
        return _back("/me/security", done=f"{n} other session(s) signed out; this browser stays signed in.")

    def delete_account(self, password: str = Form("")) -> RedirectResponse:
        user = policy.actor()
        try:
            account.delete_account(user, password)
        except HTTPException as error:
            return _back("/me/security", error=str(error.detail))
        response = RedirectResponse(url="/", status_code=303)
        auth.clear_cookie(response)  # its sessions went with the account
        return response


class CvController:
    """GET /cv/{id} (and /api/cv/{id}): the PDF, for its owner, staff, admins and the poster of a
    posting it was sent to (ddd.md 4.1.7). Anyone else gets 404."""

    def __init__(self) -> None:
        self.router = APIRouter(tags=["My account"])
        self.router.add_api_route("/cv/{cv_id}", self.download, methods=["GET"])
        self.router.add_api_route("/api/cv/{cv_id}", self.download, methods=["GET"], tags=["ApiMyAccount"])
        self.router.add_api_route("/api/users/{user_id}/profile", self.public_profile, methods=["GET"], tags=["ApiUser"])

    def public_profile(self, user_id: int) -> dict:
        """The public profile as JSON: the user (email hidden by the usual rule), sections, activity."""
        from app.models import user as user_model
        user = policy.hide_emails([user_model.get_user(user_id)])[0]
        return {"user": user, **profile_model.sections(user_id), "activity": profile_model.activity(user_id)}

    def download(self, cv_id: int) -> FileResponse:
        path, name = profile_model.cv_for_download(cv_id, policy.actor())
        return FileResponse(path, media_type="application/pdf", filename=name, content_disposition_type="inline",
                            headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"})
