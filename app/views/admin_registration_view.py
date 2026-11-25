"""The admin's review queue of registrations (ddd.md 4.1.2). A management page, so in English."""
from html import escape

from app.models.user import ROLE_LABELS
from app.views.layout import button, initials, page_hero, render_page, section_head, stat_tiles
from app.views.user_view import role_badge

ACTIVE = "/users"
TYPE_LABELS = {"application/pdf": "PDF", "image/jpeg": "JPG", "image/png": "PNG"}


def _size(n: int | None) -> str:
    if not n:
        return ""
    if n < 1024:
        return f"{n} bytes"
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def _card(r: dict) -> str:
    facts = [("Email", escape(r["email"])), ("Department", escape(r["department"]))]
    if r["role"] in ("student", "alumni"):
        facts.append(("Expected graduation" if r["role"] == "student" else "Graduation year", str(r["graduation_year"])))
        facts.append(("Student number", escape(r["student_number"] or "–")))
    if r["role"] == "academic":
        facts.append(("Title", escape(r["title"] or "")))
    if r["role"] == "staff":
        facts.append(("Position", escape(r["position"] or "")))
    facts.append(("Registered", r["created_at"]))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    if r["has_file"]:
        doc = (
            f'<a class="btn btn-ghost btn-sm" href="/admin/registrations/{r["id"]}/document" target="_blank" rel="noopener">'
            f'Open document &middot; {TYPE_LABELS.get(r["content_type"], "")} {_size(r["size_bytes"])}</a>'
            f'<span class="sub">{escape(r["original_name"])}</span>'
        )
    else:
        doc = '<span class="muted">No document file</span>'
    name = escape(r["name"])
    return f"""
    <article class="card review-card" data-reveal>
      <header class="review-head">
        <span class="avatar" aria-hidden="true">{initials(r["name"])}</span>
        <div><h3>{name}</h3><span class="sub">Account #{r["id"]} &middot; {ROLE_LABELS[r["role"]]}</span></div>
        {role_badge(r["role"])}
      </header>
      <dl class="dl">{dl}</dl>
      <div class="review-doc">{doc}</div>
      <div class="review-actions">
        <form method="post" action="/admin/registrations/{r["id"]}/approve" class="inline-form">
          <input type="hidden" name="name" value="{name}" />
          <button type="submit" class="btn btn-primary btn-sm">Approve</button>
        </form>
        <form method="post" action="/admin/registrations/{r["id"]}/reject" class="reject-form">
          <input type="hidden" name="name" value="{name}" />
          <input type="text" name="reason" required minlength="3" maxlength="300"
                 placeholder="Reason, e.g. the document is not readable" aria-label="Reason for rejecting {name}" />
          <button type="submit" class="btn btn-danger btn-sm">Reject</button>
        </form>
      </div>
    </article>"""


def render_registrations(pending: list[dict], done: str = "", name: str = "") -> str:
    by_role = {role: sum(1 for r in pending if r["role"] == role) for role in ("student", "alumni", "academic", "staff")}
    stats = stat_tiles(
        [("Pending", len(pending), "", "waiting for a decision")]
        + [(ROLE_LABELS[role] + "s" if role != "staff" else "Staff", n, "", "") for role, n in by_role.items() if role != "alumni"]
        + [("Graduates", by_role["alumni"], "", "")],
        "Pending registrations",
    )
    notice = ""
    if done in ("approved", "rejected"):
        what = "approved: the account is active" if done == "approved" else "rejected: the person sees the reason"
        notice = (
            f'<div class="alert alert-ok" role="status">{escape(name) or "The registration"} was {what}. '
            "The document file was deleted.</div>"
        )
    cards = "".join(_card(r) for r in pending) or (
        '<section class="card"><p class="muted" style="margin: 0">No registrations are waiting. '
        'New ones appear here as soon as someone registers.</p></section>'
    )
    body = f"""
    {page_hero(
        "Admin &middot; Registrations",
        "Registrations to <em>review</em>",
        "Check each document against the details typed in, then approve the account or reject it with a reason. The file is deleted after the decision.",
        button("Registration page", "/register") + button("Users", "/users"),
    )}
    {notice}
    <div class="alert alert-warn" role="note">Until the login task, this page is open like the other management pages. Afterwards only admins reach it, and the reviewer is recorded.</div>
    {stats}
    {section_head("Waiting for a decision", f"{len(pending)} pending")}
    <div class="review-list">{cards}</div>
    """
    return render_page("Registrations", body, ACTIVE)
