from html import escape

from app.views.job_posting_view import is_open
from app import policy
from app.auth import me
from app.views.layout import (
    alert,
    button,
    delete_form,
    filter_toolbar,
    form_card,
    initials,
    new_button,
    page_hero,
    plural,
    render_page,
    section_head,
    stat_tiles,
)

ACTIVE = "/applications"
DASH = '<span class="muted">-</span>'

STATUSES = ["submitted", "under_review", "interview", "accepted", "rejected", "withdrawn"]


def _label(status: str) -> str:
    return status.replace("_", " ")


def _row(a: dict, users_by_id: dict[int, dict], postings_by_id: dict[int, dict]) -> str:
    user = users_by_id.get(a["user_id"])
    posting = postings_by_id.get(a["job_posting_id"])
    applicant = (
        f'<div class="cell-title"><span class="avatar" aria-hidden="true">{initials(user["name"])}</span>'
        f'<a href="/users/{user["id"]}">{escape(user["name"])}</a></div>'
        if user
        else f"User #{a['user_id']}"
    )
    job = (
        f'<a href="/job-postings/{posting["id"]}">{escape(posting["title"])}</a> '
        f'<span class="sub">{escape(posting["company"])}</span>'
        if posting
        else f"Posting #{a['job_posting_id']}"
    )
    options = "".join(
        f'<option value="{s}"{" selected" if s == a["status"] else ""}>{_label(s)}</option>' for s in STATUSES
    )
    # Who may change the status (ddd.md 4.1.3): staff, admin and the posting's owner decide; the
    # applicant may only withdraw.
    user = me()
    owner = (posting or {}).get("posted_by_user_id")
    if user and (user["role"] in ("staff", "admin") or user["id"] == owner):
        status_form = (
            f'<form class="inline-form" method="post" action="/applications/{a["id"]}/status">'
            f'<select name="status" aria-label="New status">{options}</select> '
            f'<button type="submit" class="btn btn-ghost btn-sm">Update</button></form>'
        )
    elif user and user["id"] == a["user_id"] and a["status"] != "withdrawn":
        status_form = (
            f'<form class="inline-form" method="post" action="/applications/{a["id"]}/status">'
            '<input type="hidden" name="status" value="withdrawn" />'
            '<button type="submit" class="btn btn-ghost btn-sm">Withdraw</button></form>'
        )
    else:
        status_form = '<span class="muted">&ndash;</span>'
    cover_letter = escape(a["cover_letter"] or "") or DASH
    delete = delete_form(f"/applications/{a['id']}/delete", "application") if policy.is_admin() else ""
    return (
        f'<tr><td class="id">#{a["id"]}</td><td>{applicant}</td><td>{job}</td>'
        f'<td><span class="badge s-{a["status"]}">{_label(a["status"])}</span></td>'
        f"<td>{status_form}</td>"
        f"<td>{cover_letter}</td>"
        f'<td class="date">{a["created_at"]}</td>'
        f'<td class="col-actions">{delete}</td></tr>'
    )


def _pipeline(applications: list[dict]) -> str:
    """One stage per status, with how many applications are in it (left to right: the usual path)."""
    counts = {s: 0 for s in STATUSES}
    for a in applications:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    stages = "".join(
        f'<div class="stage s-{s}" data-reveal><div class="label-mono">{_label(s)}</div>'
        f'<div class="num" data-count="{counts[s]}">{counts[s]}</div></div>'
        for s in STATUSES
    )
    return f'<section class="pipeline" aria-label="Applications by status">{stages}</section>'


def render_application_list(
    applications: list[dict], users: list[dict], postings: list[dict], error: str | None = None
) -> str:
    users_by_id = {u["id"]: u for u in users}
    postings_by_id = {p["id"]: p for p in postings}

    rows = "".join(_row(a, users_by_id, postings_by_id) for a in applications) or (
        '<tr><td class="empty" colspan="8">No applications yet. Create the first one below.</td></tr>'
    )

    posting_options = "".join(
        f'<option value="{p["id"]}">{escape(p["title"])} - {escape(p["company"])}'
        f'{"" if is_open(p) else " (closed)"}</option>'
        for p in postings
    )

    new_form = f"""
      <form class="form-grid" method="post" action="/applications">
        <div class="field"><span class="label-like">Applicant</span><p class="fixed-value">{escape(me()["name"]) if me() else ""} (you)</p></div>
        <div class="field"><label for="job_posting_id">Job posting</label>
          <select id="job_posting_id" name="job_posting_id" required>{posting_options}</select></div>
        <div class="field full"><label for="cover_letter">Cover letter (optional)</label>
          <textarea id="cover_letter" name="cover_letter" rows="4"></textarea></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Send application</button></div>
      </form>"""

    status_of = [a["status"] for a in applications]
    stats = stat_tiles([
        ("Applications", len(applications), "", ""),
        ("In progress", sum(1 for s in status_of if s in ("submitted", "under_review")), "", "submitted or under review"),
        ("Interviews", status_of.count("interview"), "", ""),
        ("Accepted", status_of.count("accepted"), "", ""),
    ], "Applications in numbers")

    body = f"""
    {page_hero(
        "Pipeline &middot; Applications",
        "Applications, <em>step by step</em>",
        "Who applied to which job posting, and where each application stands: from submitted to the final answer.",
        (new_button("New application") if policy.can_apply() else "") + button("Job postings", "/job-postings"),
    )}
    {alert(error)}
    {stats}
    {section_head("By status", "Six stages")}
    {_pipeline(applications)}
    {filter_toolbar("applications-table", plural(len(applications), "application"))}
    <div class="table-wrap" data-reveal>
      <table id="applications-table">
        <thead><tr><th>ID</th><th>Applicant</th><th>Job posting</th><th>Status</th><th>Change status</th><th>Cover letter</th><th>Applied</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("New application", new_form, "Only open postings accept applications") if policy.can_apply() else ""}
    """
    return render_page("Applications", body, ACTIVE)
