from datetime import date
from html import escape

from app.views.layout import alert, filter_toolbar, new_button, page_header, plural, render_page, row_actions

ACTIVE = "/job-postings"
DASH = '<span class="muted">-</span>'
NONE = '<span class="muted">none</span>'

EMPLOYMENT_TYPES = {
    "full_time": "Full time",
    "part_time": "Part time",
    "internship": "Internship",
    "contract": "Contract",
}


def is_open(posting: dict) -> bool:
    """Same rule the API uses: a posting is closed when inactive or past its deadline."""
    if not posting["is_active"]:
        return False
    deadline = posting["deadline"]
    return deadline is None or date.fromisoformat(deadline) >= date.today()


def _status_badge(posting: dict) -> str:
    return '<span class="badge ok">Open</span>' if is_open(posting) else '<span class="badge off">Closed</span>'


def _type_label(posting: dict) -> str:
    return EMPLOYMENT_TYPES.get(posting["employment_type"], escape(posting["employment_type"]))


def _user_link(user_id: int | None, users_by_id: dict[int, dict]) -> str:
    if user_id is None:
        return '<span class="muted">Department</span>'
    user = users_by_id.get(user_id)
    name = escape(user["name"]) if user else f"User #{user_id}"
    return f'<a href="/users/{user_id}">{name}</a>'


def _external_link(url: str | None) -> str:
    if not url:
        return DASH
    safe = escape(url)
    if url.startswith(("http://", "https://")):
        return f'<a href="{safe}" target="_blank" rel="noopener noreferrer">{safe}</a>'
    return safe


def _row(posting: dict, users_by_id: dict[int, dict]) -> str:
    base = f"/job-postings/{posting['id']}"
    return (
        f"<tr><td>{posting['id']}</td>"
        f'<td><a href="{base}">{escape(posting["title"])}</a></td>'
        f"<td>{escape(posting['company'])}</td>"
        f"<td>{escape(posting['location'])}</td>"
        f"<td>{_type_label(posting)}</td>"
        f"<td class=\"nowrap\">{posting['deadline'] or DASH}</td>"
        f"<td>{_status_badge(posting)}</td>"
        f"<td>{_user_link(posting['posted_by_user_id'], users_by_id)}</td>"
        f'<td class="col-actions">{row_actions(base, "job posting")}</td></tr>'
    )


def render_job_posting_list(postings: list[dict], users: list[dict]) -> str:
    users_by_id = {u["id"]: u for u in users}
    rows = "".join(_row(p, users_by_id) for p in postings) or (
        '<tr><td class="empty" colspan="9">No job postings yet. Add the first one below.</td></tr>'
    )
    open_count = sum(1 for p in postings if is_open(p))

    body = f"""
    {page_header("Job Postings", "Jobs and internships shared with graduates.", new_button("New job posting"))}
    {filter_toolbar("postings-table", f"{plural(len(postings), 'posting')} &middot; {open_count} open")}
    <div class="table-wrap">
      <table id="postings-table">
        <thead><tr><th>ID</th><th>Title</th><th>Company</th><th>Location</th><th>Type</th><th>Deadline</th><th>Status</th><th>Posted by</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <section class="card" id="new" style="margin-top: 32px">
      <h2>Add job posting</h2>
      {_posting_form("/job-postings", users)}
    </section>
    """
    return render_page("Job Postings", body, ACTIVE)


def render_job_posting_detail(
    posting: dict, users: list[dict], applications: list[dict], error: str | None = None
) -> str:
    users_by_id = {u["id"]: u for u in users}
    rows = "".join(
        f"<tr><td>{_user_link(a['user_id'], users_by_id)}</td>"
        f'<td><span class="badge s-{a["status"]}">{a["status"].replace("_", " ")}</span></td>'
        f"<td>{escape(a['cover_letter'] or '') or DASH}</td>"
        f"<td class=\"nowrap\">{a['created_at']}</td></tr>"
        for a in applications
    ) or '<tr><td class="empty" colspan="4">Nobody has applied yet.</td></tr>'

    if is_open(posting):
        options = "".join(f'<option value="{u["id"]}">{escape(u["name"])} (#{u["id"]})</option>' for u in users)
        apply_form = f"""
      <form class="form-grid" method="post" action="/job-postings/{posting['id']}/apply">
        <div class="field full"><label for="user_id">Applicant</label>
          <select id="user_id" name="user_id" required>{options}</select></div>
        <div class="field full"><label for="cover_letter">Cover letter (optional)</label>
          <textarea id="cover_letter" name="cover_letter"></textarea></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Apply</button></div>
      </form>"""
    else:
        apply_form = '<p class="muted">This posting is closed, so nobody can apply to it.</p>'

    body = f"""
    {alert(error)}
    <h1>{escape(posting['title'])}</h1>
    <p class="meta">
      <span>{escape(posting['company'])}</span><span>{escape(posting['location'])}</span>
      <span>{_type_label(posting)}</span>{_status_badge(posting)}
    </p>

    <section class="card" style="margin-top: 24px">
      <p class="content">{escape(posting['description'])}</p>
      <dl class="dl" style="margin-top: 20px">
        <dt>Posted by</dt><dd>{_user_link(posting['posted_by_user_id'], users_by_id)}</dd>
        <dt>Deadline</dt><dd>{posting['deadline'] or NONE}</dd>
        <dt>Apply at</dt><dd>{_external_link(posting['application_url'])}</dd>
        <dt>Created</dt><dd>{posting['created_at']}</dd>
      </dl>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/job-postings/{posting['id']}/edit">Edit</a>
        <a class="btn btn-ghost" href="/applications">Manage all applications</a>
      </div>
    </section>

    <h2 class="section-title">Applicants ({len(applications)})</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Applicant</th><th>Status</th><th>Cover letter</th><th>Applied</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <section class="card" style="margin-top: 32px">
      <h2>Apply to this posting</h2>
      {apply_form}
    </section>
    <a class="back-link" href="/job-postings">&larr; Back to job postings</a>
    """
    return render_page(posting["title"], body, ACTIVE)


def render_job_posting_edit_form(posting: dict, users: list[dict]) -> str:
    body = f"""
    {page_header("Edit job posting", f"Job posting #{posting['id']}")}
    <section class="card">
      {_posting_form(f"/job-postings/{posting['id']}/edit", users, posting)}
    </section>
    <a class="back-link" href="/job-postings">&larr; Back to job postings</a>
    """
    return render_page("Edit job posting", body, ACTIVE, narrow=True)


def _posting_form(action: str, users: list[dict], posting: dict | None = None) -> str:
    p = posting or {}

    def value(key: str) -> str:
        return escape(str(p.get(key) or ""))

    type_options = "".join(
        f'<option value="{key}"{" selected" if p.get("employment_type") == key else ""}>{label}</option>'
        for key, label in EMPLOYMENT_TYPES.items()
    )
    owner_options = '<option value="">Department (no user)</option>' + "".join(
        f'<option value="{u["id"]}"{" selected" if p.get("posted_by_user_id") == u["id"] else ""}>'
        f'{escape(u["name"])} (#{u["id"]})</option>'
        for u in users
    )
    checked = " checked" if p.get("is_active", True) else ""
    submit_label = "Save changes" if posting else "Create job posting"

    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field full"><label for="title">Title</label>
        <input id="title" type="text" name="title" value="{value('title')}" maxlength="200" required /></div>
      <div class="field"><label for="company">Company</label>
        <input id="company" type="text" name="company" value="{value('company')}" maxlength="150" required /></div>
      <div class="field"><label for="location">Location</label>
        <input id="location" type="text" name="location" value="{value('location')}" maxlength="150" required /></div>
      <div class="field"><label for="employment_type">Employment type</label>
        <select id="employment_type" name="employment_type" required>{type_options}</select></div>
      <div class="field"><label for="posted_by_user_id">Posted by</label>
        <select id="posted_by_user_id" name="posted_by_user_id">{owner_options}</select></div>
      <div class="field full"><label for="description">Description</label>
        <textarea id="description" name="description" required>{value('description')}</textarea></div>
      <div class="field"><label for="application_url">Application URL (optional)</label>
        <input id="application_url" type="url" name="application_url" value="{value('application_url')}" maxlength="500" placeholder="https://" /></div>
      <div class="field"><label for="deadline">Deadline (optional)</label>
        <input id="deadline" type="date" name="deadline" value="{value('deadline')}" /></div>
      <div class="field full"><label class="check"><input type="checkbox" name="is_active"{checked} /> Active (accepting applications)</label></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button></div>
    </form>
    """
