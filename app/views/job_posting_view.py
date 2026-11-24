from datetime import date
from html import escape

from app.views.layout import (
    alert,
    back_link,
    button,
    edit_header,
    filter_toolbar,
    form_card,
    new_button,
    page_hero,
    plural,
    render_page,
    row_actions,
    section_head,
    stat_tiles,
)

ACTIVE = "/job-postings"
DASH = '<span class="muted">-</span>'
NONE = '<span class="muted">none</span>'
NO_DESCRIPTION = '<span class="muted">No description. Use the application link below.</span>'

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
        f'<tr><td class="id">#{posting["id"]}</td>'
        f'<td><a href="{base}">{escape(posting["title"])}</a>'
        f'<span class="sub">{escape(posting["company"])}</span></td>'
        f"<td>{escape(posting['city'])}</td>"
        f'<td class="nowrap">{_type_label(posting)}</td>'
        f'<td class="date">{posting["deadline"] or DASH}</td>'
        f"<td>{_status_badge(posting)}</td>"
        f"<td>{_user_link(posting['posted_by_user_id'], users_by_id)}</td>"
        f'<td class="col-actions">{row_actions(base, "job posting")}</td></tr>'
    )


def render_job_posting_list(
    postings: list[dict], users: list[dict], error: str | None = None, values: dict | None = None
) -> str:
    """`error` and `values` are set when a submitted form was refused: the message and what was typed."""
    users_by_id = {u["id"]: u for u in users}
    rows = "".join(_row(p, users_by_id) for p in postings) or (
        '<tr><td class="empty" colspan="8">No job postings yet. Add the first one below.</td></tr>'
    )
    open_count = sum(1 for p in postings if is_open(p))

    error_box = alert(f"The job posting was not saved. {error}") if error else ""
    stats = stat_tiles([
        ("Postings", len(postings), "", ""),
        ("Open", open_count, "", "accepting applications"),
        ("Closed", len(postings) - open_count, "", ""),
        ("Internships", sum(1 for p in postings if p["employment_type"] == "internship"), "", ""),
    ], "Job postings in numbers")
    body = f"""
    {page_hero(
        "Careers &middot; Postings",
        "Jobs and <em>internships</em>",
        "Positions shared by the department and by graduates. A posting stays open until its deadline, or until it is closed.",
        new_button("New job posting") + button("Applications", "/applications"),
    )}
    {error_box}
    {stats}
    {filter_toolbar("postings-table", f"{plural(len(postings), 'posting')} &middot; {open_count} open")}
    <div class="table-wrap" data-reveal>
      <table id="postings-table">
        <thead><tr><th>ID</th><th>Title &middot; Company</th><th>City</th><th>Type</th><th>Deadline</th><th>Status</th><th>Posted by</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("Add a job posting", _posting_form("/job-postings", users, values), "Description or link required")}
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
        f'<td class="date">{a["created_at"]}</td></tr>'
        for a in applications
    ) or '<tr><td class="empty" colspan="4">Nobody has applied yet.</td></tr>'

    if is_open(posting):
        options = "".join(f'<option value="{u["id"]}">{escape(u["name"])} (#{u["id"]})</option>' for u in users)
        apply_form = f"""
      <form class="form-grid" method="post" action="/job-postings/{posting['id']}/apply">
        <div class="field full"><label for="user_id">Applicant</label>
          <select id="user_id" name="user_id" required>{options}</select></div>
        <div class="field full"><label for="cover_letter">Cover letter (optional)</label>
          <textarea id="cover_letter" name="cover_letter" rows="4"></textarea></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Send application</button></div>
      </form>"""
    else:
        apply_form = '<p class="muted" style="margin: 0">This posting is closed, so nobody can apply to it.</p>'

    body = f"""
    {page_hero(
        f"Job posting #{posting['id']} &middot; {_type_label(posting)}",
        escape(posting['title']),
        "",
        (button("Apply", "#apply", "primary", arrow=True) if is_open(posting) else "")
        + button("Edit", f"/job-postings/{posting['id']}/edit")
        + button("All job postings", "/job-postings"),
        meta=f"<span>{escape(posting['company'])}</span><span>{escape(posting['city'])}</span>{_status_badge(posting)}",
        size="compact",
    )}
    {alert(error)}

    <div class="detail-grid">
      <div class="detail-main">
        <section class="card card-featured" data-reveal>
          <h2>About the role</h2>
          <p class="content">{escape(posting['description']) if posting['description'] else NO_DESCRIPTION}</p>
        </section>

        {section_head("Applicants", plural(len(applications), "application"))}
        <div class="table-wrap" data-reveal>
          <table>
            <thead><tr><th>Applicant</th><th>Status</th><th>Cover letter</th><th>Applied</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>

      <aside class="detail-side">
        <section class="card" data-reveal>
          <dl class="dl">
            <dt>Company</dt><dd>{escape(posting['company'])} &middot; {escape(posting['city'])}</dd>
            <dt>Posted by</dt><dd>{_user_link(posting['posted_by_user_id'], users_by_id)}</dd>
            <dt>Deadline</dt><dd class="mono">{posting['deadline'] or NONE}</dd>
            <dt>Apply at</dt><dd>{_external_link(posting['application_url'])}</dd>
            <dt>Created</dt><dd class="mono">{posting['created_at']}</dd>
          </dl>
        </section>
        <section class="card card-featured" id="apply" data-reveal>
          <h2>Apply</h2>
          {apply_form}
        </section>
      </aside>
    </div>
    {back_link("/job-postings", "Back to job postings")}
    """
    return render_page(posting["title"], body, ACTIVE)


def render_job_posting_edit_form(posting: dict, users: list[dict], error: str | None = None) -> str:
    error_box = alert(f"The changes were not saved. {error}") if error else ""
    body = f"""
    {error_box}
    {edit_header("job posting", f"Job posting #{posting['id']}")}
    <section class="card card-featured">
      {_posting_form(f"/job-postings/{posting['id']}/edit", users, posting, editing=True)}
    </section>
    {back_link(f"/job-postings/{posting['id']}", "Back to the job posting")}
    """
    return render_page("Edit job posting", body, ACTIVE, narrow=True)


def _posting_form(action: str, users: list[dict], values: dict | None = None, editing: bool = False) -> str:
    p = values or {}

    def value(key: str) -> str:
        return escape(str(p.get(key) or ""))

    type_options = "".join(
        f'<option value="{key}"{" selected" if p.get("employment_type") == key else ""}>{label}</option>'
        for key, label in EMPLOYMENT_TYPES.items()
    )
    owner_options = '<option value="">Department (no user)</option>' + "".join(
        f'<option value="{u["id"]}"{" selected" if str(p.get("posted_by_user_id")) == str(u["id"]) else ""}>'
        f'{escape(u["name"])} (#{u["id"]})</option>'
        for u in users
    )
    checked = " checked" if p.get("is_active", True) else ""
    submit_label = "Save changes" if editing else "Create job posting"
    cancel = f'<a class="btn btn-ghost" href="/job-postings/{p["id"]}">Cancel</a>' if editing else ""

    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field full"><label for="title">Title (max 120 characters)</label>
        <input id="title" type="text" name="title" value="{value('title')}" maxlength="120" required /></div>
      <div class="field"><label for="company">Company</label>
        <input id="company" type="text" name="company" value="{value('company')}" maxlength="150" required /></div>
      <div class="field"><label for="city">City</label>
        <input id="city" type="text" name="city" value="{value('city')}" maxlength="150" required /></div>
      <div class="field"><label for="employment_type">Employment type</label>
        <select id="employment_type" name="employment_type" required>{type_options}</select></div>
      <div class="field"><label for="posted_by_user_id">Posted by</label>
        <select id="posted_by_user_id" name="posted_by_user_id">{owner_options}</select></div>
      <p class="muted small-note">Fill in <b>at least one</b> of Description and Application URL. You may fill in both.</p>
      <div class="field full"><label for="description">Description (optional if an application URL is given)</label>
        <textarea id="description" name="description">{value('description')}</textarea></div>
      <div class="field"><label for="application_url">Application URL (optional if a description is given)</label>
        <input id="application_url" type="url" name="application_url" value="{value('application_url')}" maxlength="500" placeholder="https://" /></div>
      <div class="field"><label for="deadline">Deadline (optional)</label>
        <input id="deadline" type="date" name="deadline" value="{value('deadline')}" /></div>
      <div class="field full"><label class="check"><input type="checkbox" name="is_active"{checked} /> Active (accepting applications)</label></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button>{cancel}</div>
    </form>
    """
