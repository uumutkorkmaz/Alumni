from html import escape

from app.views.job_posting_view import is_open
from app.views.layout import alert, delete_form, filter_toolbar, form_card, initials, new_button, page_header, plural, render_page

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
    status_form = (
        f'<form class="inline-form" method="post" action="/applications/{a["id"]}/status">'
        f'<select name="status" aria-label="New status">{options}</select> '
        f'<button type="submit" class="btn btn-ghost btn-sm">Update</button></form>'
    )
    cover_letter = escape(a["cover_letter"] or "") or DASH
    delete = delete_form(f"/applications/{a['id']}/delete", "application")
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

    user_options = "".join(f'<option value="{u["id"]}">{escape(u["name"])} (#{u["id"]})</option>' for u in users)
    posting_options = "".join(
        f'<option value="{p["id"]}">{escape(p["title"])} - {escape(p["company"])}'
        f'{"" if is_open(p) else " (closed)"}</option>'
        for p in postings
    )

    new_form = f"""
      <form class="form-grid" method="post" action="/applications">
        <div class="field"><label for="user_id">Applicant</label>
          <select id="user_id" name="user_id" required>{user_options}</select></div>
        <div class="field"><label for="job_posting_id">Job posting</label>
          <select id="job_posting_id" name="job_posting_id" required>{posting_options}</select></div>
        <div class="field full"><label for="cover_letter">Cover letter (optional)</label>
          <textarea id="cover_letter" name="cover_letter" rows="4"></textarea></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Send application</button></div>
      </form>"""

    body = f"""
    {alert(error)}
    {page_header("Applications", "Who applied to which job posting, and where each application stands.", new_button("New application"), kicker="Pipeline · Applications", line=True)}
    {_pipeline(applications)}
    {filter_toolbar("applications-table", plural(len(applications), "application"))}
    <div class="table-wrap" data-reveal>
      <table id="applications-table">
        <thead><tr><th>ID</th><th>Applicant</th><th>Job posting</th><th>Status</th><th>Change status</th><th>Cover letter</th><th>Applied</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("New application", new_form, "Only open postings accept applications")}
    """
    return render_page("Applications", body, ACTIVE)
