from html import escape

from app.views.job_posting_view import is_open
from app.views.layout import alert, delete_form, filter_toolbar, page_header, plural, render_page

ACTIVE = "/applications"
DASH = '<span class="muted">-</span>'

STATUSES = ["submitted", "under_review", "interview", "accepted", "rejected", "withdrawn"]


def _label(status: str) -> str:
    return status.replace("_", " ")


def _row(a: dict, users_by_id: dict[int, dict], postings_by_id: dict[int, dict]) -> str:
    user = users_by_id.get(a["user_id"])
    posting = postings_by_id.get(a["job_posting_id"])
    applicant = (
        f'<a href="/users/{user["id"]}">{escape(user["name"])}</a>' if user else f"User #{a['user_id']}"
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
        f"<tr><td>{a['id']}</td><td>{applicant}</td><td>{job}</td>"
        f'<td><span class="badge s-{a["status"]}">{_label(a["status"])}</span></td>'
        f"<td>{status_form}</td>"
        f"<td>{cover_letter}</td>"
        f"<td class=\"nowrap\">{a['created_at']}</td>"
        f'<td class="col-actions">{delete}</td></tr>'
    )


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

    body = f"""
    {alert(error)}
    {page_header("Applications", "Who applied to which job posting.")}
    {filter_toolbar("applications-table", plural(len(applications), "application"))}
    <div class="table-wrap">
      <table id="applications-table">
        <thead><tr><th>ID</th><th>Applicant</th><th>Job posting</th><th>Status</th><th>Change status</th><th>Cover letter</th><th>Applied</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <section class="card" id="new" style="margin-top: 32px">
      <h2>New application</h2>
      <form class="form-grid" method="post" action="/applications">
        <div class="field"><label for="user_id">Applicant</label>
          <select id="user_id" name="user_id" required>{user_options}</select></div>
        <div class="field"><label for="job_posting_id">Job posting</label>
          <select id="job_posting_id" name="job_posting_id" required>{posting_options}</select></div>
        <div class="field full"><label for="cover_letter">Cover letter (optional)</label>
          <textarea id="cover_letter" name="cover_letter"></textarea></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Apply</button></div>
      </form>
    </section>
    """
    return render_page("Applications", body, ACTIVE)
