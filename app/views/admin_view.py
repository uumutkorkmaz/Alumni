"""The admin panel (ddd.md 4.1.4). A management area, so in English."""
from html import escape

from app.models.user import ROLE_LABELS, ROLES
from app.views.account_view import _device
from app.views.layout import initials, page_hero, render_page, section_head, stat_tiles

ACTIVE = "/admin"
TABS = [
    ("overview", "/admin", "Overview"),
    ("users", "/admin/users", "Users"),
    ("registrations", "/admin/registrations", "Registrations"),
    ("content", "/admin/content", "Content"),
    ("sessions", "/admin/sessions", "Sessions"),
    ("audit", "/admin/audit", "Audit log"),
]
STATUS_BADGE = {"active": "ok", "pending": "s-under_review", "rejected": "off", "suspended": "s-interview"}
APPLICATION_STATUSES = ["submitted", "under_review", "interview", "accepted", "rejected", "withdrawn"]


def role_badge(role: str) -> str:
    return f'<span class="badge role role-{role}">{ROLE_LABELS[role]}</span>'


def status_badge(status: str) -> str:
    return f'<span class="badge {STATUS_BADGE.get(status, "")}">{status}</span>'


def _flash(done: str, error: str) -> str:
    if error:
        return f'<div class="alert alert-error" role="alert">{escape(error)}</div>'
    if done:
        return f'<div class="alert alert-ok" role="status">{escape(done)}</div>'
    return ""


def admin_shell(tab: str, title: str, lead: str, content: str, pending: int = 0, done: str = "", error: str = "") -> str:
    """The panel's frame: a compact hero, the left-hand menu and the page's content."""
    links = "".join(
        f'<a href="{href}" class="admin-tab{" active" if key == tab else ""}"'
        f'{" aria-current=\"page\"" if key == tab else ""}>{label}'
        f'{f"<span class=\"admin-count\">{pending}</span>" if key == "registrations" and pending else ""}</a>'
        for key, href, label in TABS
    )
    body = f"""
    {page_hero("Admin panel", title, lead, size="compact")}
    <div class="admin-grid">
      <nav class="admin-nav" aria-label="Admin panel">{links}</nav>
      <div class="admin-main">{_flash(done, error)}{content}</div>
    </div>
    """
    return render_page("Admin · " + {k: l for k, _, l in TABS}.get(tab, "Panel"), body, ACTIVE, wide=True)


def _form(action: str, inner: str, confirm: str = "") -> str:
    on = f' onsubmit="return confirm(\'{confirm}\')"' if confirm else ""
    return f'<form method="post" action="{action}" class="inline-form"{on}>{inner}</form>'


def _button(label: str, kind: str = "ghost") -> str:
    return f'<button type="submit" class="btn btn-{kind} btn-sm">{label}</button>'


# --------------------------------------------------------------------------- overview
def render_admin_overview(data: dict, pending: int, recent: list[dict], done: str = "", error: str = "") -> str:
    active_users = sum(data["by_role"].values())
    stats = stat_tiles([
        ("Active accounts", active_users, "/admin/users?status=active", ""),
        ("Pending registrations", pending, "/admin/registrations", "waiting for you" if pending else ""),
        ("Open postings", data["open_postings"], "/admin/content#postings", f"of {data['postings']}"),
        ("Signed in now", data["sessions"], "/admin/sessions", "active sessions"),
    ], "Overview")
    biggest = max(data["by_role"].values()) or 1
    roles = "".join(
        f'<li><a href="/admin/users?role={r}">{role_badge(r)}</a>'
        f'<span class="bar"><span style="transform: scaleX({n / biggest:.3f})"></span></span><b>{n}</b></li>'
        for r, n in data["by_role"].items()
    )
    statuses = "".join(
        f'<li><a href="/admin/users?status={s}">{status_badge(s)}</a><b>{n}</b></li>'
        for s, n in data["by_status"].items()
    )
    content = f"""
    {stats}
    <div class="admin-two">
      <section class="card" data-reveal>
        <div class="card-head"><h2>Active people by role</h2><span class="label-mono">{active_users} accounts</span></div>
        <ul class="role-bars">{roles}</ul>
      </section>
      <section class="card" data-reveal>
        <div class="card-head"><h2>Accounts by status</h2><span class="label-mono">all</span></div>
        <ul class="status-list">{statuses}</ul>
        <p class="muted small-note" style="margin-top: 14px">{data['announcements']} announcements &middot; {data['applications']} applications</p>
      </section>
    </div>
    {section_head("Latest actions", "", ("Audit log", "/admin/audit"))}
    {_audit_table(recent)}
    """
    return admin_shell("overview", "Admin <em>panel</em>",
                       "Everything an admin manages, in one place: accounts and roles, registrations, content and sessions. Every change is written to the audit log.",
                       content, pending, done, error)


# --------------------------------------------------------------------------- users
def render_admin_users(users: list[dict], filters: dict, me: dict, pending: int, done: str = "", error: str = "") -> str:
    back = "/admin/users" + (
        "?" + "&".join(f"{k}={escape(v)}" for k, v in filters.items() if v) if any(filters.values()) else "")
    role_filter = '<option value="">All roles</option>' + "".join(
        f'<option value="{r}"{" selected" if filters["role"] == r else ""}>{ROLE_LABELS[r]}</option>' for r in ROLES)
    status_filter = '<option value="">All statuses</option>' + "".join(
        f'<option value="{s}"{" selected" if filters["status"] == s else ""}>{s}</option>'
        for s in ("active", "pending", "rejected", "suspended"))
    rows = []
    for u in users:
        is_me = u["id"] == me["id"]
        hidden = f'<input type="hidden" name="back" value="{back}" />'
        if is_me:
            role_cell = f'{role_badge(u["role"])} <span class="muted small-note">you</span>'
            actions = '<span class="muted small-note">Your own account</span>'
        else:
            options = "".join(f'<option value="{r}"{" selected" if r == u["role"] else ""}>{ROLE_LABELS[r]}</option>' for r in ROLES)
            role_cell = _form(f'/admin/users/{u["id"]}/role',
                              f'{hidden}<select name="role" aria-label="Role of {escape(u["name"])}">{options}</select>{_button("Save")}')
            if u["status"] == "active":
                toggle = _form(f'/admin/users/{u["id"]}/status',
                               f'{hidden}<input type="hidden" name="status" value="suspended" />{_button("Suspend")}',
                               f'Suspend {escape(u["name"])}? They are signed out and cannot sign in.')
            elif u["status"] == "suspended":
                toggle = _form(f'/admin/users/{u["id"]}/status',
                               f'{hidden}<input type="hidden" name="status" value="active" />{_button("Reactivate", "primary")}')
            elif u["status"] == "pending":
                toggle = '<a class="btn btn-ghost btn-sm" href="/admin/registrations">Review</a>'
            else:
                toggle = ""
            end = (_form(f'/admin/users/{u["id"]}/sessions/end', f'{hidden}{_button(f"Sign out ({u["sessions"]})")}')
                   if u["sessions"] else "")
            delete = _form(f'/admin/users/{u["id"]}/delete', f'{hidden}{_button("Delete", "danger")}',
                           f'Delete {escape(u["name"])} and everything that belongs to them? This cannot be undone.')
            actions = f'<div class="row-actions">{toggle}{end}{delete}</div>'
        rows.append(
            f'<tr><td class="id">#{u["id"]}</td>'
            f'<td><div class="cell-title"><span class="avatar" aria-hidden="true">{initials(u["name"])}</span>'
            f'<span><a href="/users/{u["id"]}">{escape(u["name"])}</a><span class="sub">{escape(u["email"])}</span></span></div></td>'
            f'<td>{role_cell}</td>'
            f'<td>{status_badge(u["status"])}<span class="sub mono">{"last in " + u["last_login_at"] if u["last_login_at"] else ("never signed in" if u["has_password"] else "no password yet")}</span></td>'
            f'<td class="col-actions">{actions}</td></tr>'
        )
    table = "".join(rows) or '<tr><td class="empty" colspan="5">No account matches the filter.</td></tr>'
    content = f"""
    <form class="admin-filter" method="get" action="/admin/users">
      <select name="role" aria-label="Role">{role_filter}</select>
      <select name="status" aria-label="Status">{status_filter}</select>
      <input type="search" name="q" value="{escape(filters['q'])}" placeholder="Name or email" aria-label="Search" />
      <button type="submit" class="btn btn-ghost btn-sm">Filter</button>
      <a class="link-arrow" href="/admin/users">Clear</a>
    </form>
    <p class="muted small-note admin-rules">You cannot change your own role, suspend or delete yourself, and the last active admin keeps the role. A role change or a suspension signs the account out.</p>
    <div class="table-wrap" data-reveal>
      <table>
        <thead><tr><th>ID</th><th>Account</th><th>Role</th><th>Status</th><th></th></tr></thead>
        <tbody>{table}</tbody>
      </table>
    </div>
    """
    return admin_shell("users", "Accounts and <em>roles</em>",
                       f"{len(users)} accounts in every status. Change a role, suspend or reactivate an account, end its sessions or delete it.",
                       content, pending, done, error)


# --------------------------------------------------------------------------- content
def render_admin_content(announcements, postings, applications, users, pending, done="", error="") -> str:
    names = {u["id"]: u["name"] for u in users}
    titles = {p["id"]: p["title"] for p in postings}

    def delete(kind: str, item_id: int, what: str) -> str:
        return _form(f"/admin/content/{kind}/{item_id}/delete", _button("Delete", "danger"),
                     f"Delete this {what}? This cannot be undone.")

    ann_rows = "".join(
        f'<tr><td class="id">#{a["id"]}</td><td><a href="/announcements/{a["id"]}">{escape(a["title"])}</a></td>'
        f'<td>{escape(a["author"])}</td><td class="date">{a["created_at"]}</td>'
        f'<td class="col-actions"><div class="row-actions"><a class="btn btn-ghost btn-sm" href="/announcements/{a["id"]}/edit">Edit</a>'
        f'{delete("announcements", a["id"], "announcement")}</div></td></tr>'
        for a in announcements) or '<tr><td class="empty" colspan="5">No announcements.</td></tr>'

    def posting_row(p: dict) -> str:
        toggle = _form(f'/admin/content/postings/{p["id"]}/active',
                       f'<input type="hidden" name="active" value="{"0" if p["is_active"] else "1"}" />'
                       f'{_button("Close" if p["is_active"] else "Reopen", "ghost" if p["is_active"] else "primary")}')
        owner = names.get(p["posted_by_user_id"], "Department") if p["posted_by_user_id"] else "Department"
        state = '<span class="badge ok">active</span>' if p["is_active"] else '<span class="badge off">closed</span>'
        return (f'<tr><td class="id">#{p["id"]}</td><td><a href="/job-postings/{p["id"]}">{escape(p["title"])}</a>'
                f'<span class="sub">{escape(p["company"])}</span></td><td>{escape(owner)}</td><td>{state}</td>'
                f'<td class="date">{p["deadline"] or "–"}</td>'
                f'<td class="col-actions"><div class="row-actions">{toggle}'
                f'<a class="btn btn-ghost btn-sm" href="/job-postings/{p["id"]}/edit">Edit</a>'
                f'{delete("postings", p["id"], "job posting")}</div></td></tr>')

    post_rows = "".join(posting_row(p) for p in postings) or '<tr><td class="empty" colspan="6">No job postings.</td></tr>'

    def app_row(a: dict) -> str:
        options = "".join(f'<option value="{s}"{" selected" if s == a["status"] else ""}>{s.replace("_", " ")}</option>'
                          for s in APPLICATION_STATUSES)
        status = _form(f'/admin/content/applications/{a["id"]}/status',
                       f'<select name="status" aria-label="Status">{options}</select>{_button("Save")}')
        return (f'<tr><td class="id">#{a["id"]}</td><td>{escape(names.get(a["user_id"], f"User #{a["user_id"]}"))}</td>'
                f'<td>{escape(titles.get(a["job_posting_id"], f"Posting #{a["job_posting_id"]}"))}</td>'
                f'<td><span class="badge s-{a["status"]}">{a["status"].replace("_", " ")}</span></td>'
                f'<td>{status}</td><td class="col-actions">{delete("applications", a["id"], "application")}</td></tr>')

    app_rows = "".join(app_row(a) for a in applications) or '<tr><td class="empty" colspan="6">No applications.</td></tr>'
    content = f"""
    <div id="announcements">{section_head("Announcements", f"{len(announcements)} in all")}</div>
    <div class="table-wrap" data-reveal><table>
      <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Published</th><th></th></tr></thead>
      <tbody>{ann_rows}</tbody></table></div>
    <div id="postings">{section_head("Job postings", f"{len(postings)} in all")}</div>
    <div class="table-wrap" data-reveal><table>
      <thead><tr><th>ID</th><th>Title &middot; Company</th><th>Posted by</th><th>State</th><th>Deadline</th><th></th></tr></thead>
      <tbody>{post_rows}</tbody></table></div>
    <div id="applications">{section_head("Applications", f"{len(applications)} in all")}</div>
    <div class="table-wrap" data-reveal><table>
      <thead><tr><th>ID</th><th>Applicant</th><th>Job posting</th><th>Status</th><th>Change status</th><th></th></tr></thead>
      <tbody>{app_rows}</tbody></table></div>
    """
    return admin_shell("content", "All the <em>content</em>",
                       "Every announcement, job posting and application: open or close postings, decide applications, delete anything; edit through each record's own page.",
                       content, pending, done, error)


# --------------------------------------------------------------------------- sessions
def render_admin_sessions(sessions: list[dict], me: dict, pending: int, done: str = "", error: str = "") -> str:
    rows = "".join(
        f'<tr><td><a href="/users/{s["user_id"]}">{escape(s["name"])}</a>'
        f'{" <span class=\"muted small-note\">you</span>" if s["user_id"] == me["id"] else ""}</td>'
        f'<td>{role_badge(s["role"])}</td><td class="date">{s["created_at"]}</td><td class="date">{s["last_seen_at"]}</td>'
        f'<td class="date">{s["expires_at"]}</td><td class="ua" title="{escape(s["user_agent"] or "")}">{_device(s["user_agent"])}</td>'
        f'<td class="col-actions">{_form(f"/admin/sessions/{s["id"]}/end", _button("End"))}</td></tr>'
        for s in sessions) or '<tr><td class="empty" colspan="7">Nobody is signed in.</td></tr>'
    content = f"""
    <div class="table-wrap" data-reveal><table>
      <thead><tr><th>User</th><th>Role</th><th>Signed in</th><th>Last seen</th><th>Expires</th><th>Browser</th><th></th></tr></thead>
      <tbody>{rows}</tbody></table></div>
    """
    return admin_shell("sessions", "Who is <em>signed in</em>",
                       "Every session that has not expired. Ending a session signs that browser out at once.",
                       content, pending, done, error)


# --------------------------------------------------------------------------- audit
def _audit_table(entries: list[dict]) -> str:
    rows = "".join(
        f'<tr><td class="date">{e["created_at"]}</td><td>{escape(e["admin_name"])}</td>'
        f'<td><span class="badge plain-badge">{e["action"].replace("_", " ")}</span></td>'
        f'<td class="mono">{e["target_type"]}{f" #{e["target_id"]}" if e["target_id"] else ""}</td>'
        f'<td>{escape(e["details"] or "")}</td></tr>'
        for e in entries) or '<tr><td class="empty" colspan="5">No changes yet.</td></tr>'
    return (f'<div class="table-wrap" data-reveal><table><thead><tr><th>When</th><th>Admin</th><th>Action</th>'
            f'<th>Target</th><th>Details</th></tr></thead><tbody>{rows}</tbody></table></div>')


def render_admin_audit(entries: list[dict], pending: int) -> str:
    return admin_shell("audit", "Audit <em>log</em>",
                       "Every change made in the panel, newest first: who did what, to which record, and when. The log stays even when the record or the admin is deleted.",
                       _audit_table(entries), pending)
