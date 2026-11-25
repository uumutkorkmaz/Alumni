"""The signed-in person's own pages under /me (ddd.md 4.1.6). The menu on the left depends on the role:
students and graduates have applications and saved postings, posters have their postings, authors
their announcements; everyone has the overview, the profile and security."""
from html import escape

from app.models.user import APPLICANT_ROLES, AUTHOR_ROLES, POSTER_ROLES, ROLE_LABELS
from app.views.job_posting_view import EMPLOYMENT_TYPES, is_open
from app.views.layout import button, initials, page_hero, plural, render_page, section_head, stat_tiles

ACTIVE = "/me"
ALL = ("student", "alumni", "academic", "staff", "admin")
TABS = [
    ("overview", "/me", "Overview", ALL),
    ("profile", "/me/profile", "Profile", ALL),
    ("applications", "/me/applications", "My applications", APPLICANT_ROLES),
    ("saved", "/me/saved", "Saved postings", APPLICANT_ROLES),
    ("postings", "/me/postings", "My postings", POSTER_ROLES),
    ("announcements", "/me/announcements", "My announcements", AUTHOR_ROLES),
    ("security", "/me/security", "Security", ALL),
]
DECISIONS = ("submitted", "under_review", "interview", "accepted", "rejected")
PROFILE_LABELS = {"company": "Company", "job_title": "Job title", "city": "City", "linkedin_url": "LinkedIn", "bio": "About you"}


def tabs_for(role: str) -> list[tuple[str, str, str]]:
    return [(key, href, label) for key, href, label, roles in TABS if role in roles]


def _label(status: str) -> str:
    return status.replace("_", " ")


def _badge(status: str) -> str:
    return f'<span class="badge s-{status}">{_label(status)}</span>'


def _open_badge(p: dict) -> str:
    return '<span class="badge ok">Open</span>' if is_open(p) else '<span class="badge off">Closed</span>'


def _flash(done: str, error: str) -> str:
    if error:
        return f'<div class="alert alert-error" role="alert">{escape(error)}</div>'
    if done:
        return f'<div class="alert alert-ok" role="status">{escape(done)}</div>'
    return ""


def _post(action: str, inner: str, confirm: str = "") -> str:
    on = f' onsubmit="return confirm(\'{confirm}\')"' if confirm else ""
    return f'<form method="post" action="{action}" class="inline-form"{on}>{inner}</form>'


def _btn(label: str, kind: str = "ghost") -> str:
    return f'<button type="submit" class="btn btn-{kind} btn-sm">{label}</button>'


def _empty(text: str, cols: int) -> str:
    return f'<tr><td class="empty" colspan="{cols}">{text}</td></tr>'


def account_shell(user: dict, tab: str, title: str, lead: str, content: str, done: str = "", error: str = "") -> str:
    """The frame of every /me page: a compact hero, the person's menu and the page's content."""
    links = "".join(
        f'<a href="{href}" class="admin-tab{" active" if key == tab else ""}"'
        f'{" aria-current=\"page\"" if key == tab else ""}>{label}</a>'
        for key, href, label in tabs_for(user["role"])
    )
    pill = f"My account &middot; {ROLE_LABELS[user['role']]}"
    body = f"""
    {page_hero(pill, title, lead, size="compact")}
    <div class="admin-grid me-grid">
      <nav class="admin-nav" aria-label="My account">
        <a class="me-who" href="/users/{user['id']}" title="My public profile">
          <span class="avatar" aria-hidden="true">{initials(user['name'])}</span>
          <span><b>{escape(user['name'])}</b><small>See my public profile</small></span>
        </a>
        {links}
      </nav>
      <div class="admin-main">{_flash(done, error)}{content}</div>
    </div>
    """
    page = next((label for key, _, label in tabs_for(user["role"]) if key == tab), "My account")
    return render_page(f"My account · {page}", body, ACTIVE, wide=True)


# --------------------------------------------------------------------------- overview
def _completeness(profile: dict) -> tuple[int, list[str]]:
    keys = ["company", "job_title", "city", "linkedin_url", "bio"]
    missing = [PROFILE_LABELS[k] for k in keys if not profile.get(k)]
    return round(100 * (len(keys) - len(missing)) / len(keys)), missing


def _posting_list(postings: list[dict], empty: str, saved_ids: set[int] | None = None) -> str:
    if not postings:
        return f'<p class="muted" style="margin:0">{empty}</p>'
    items = "".join(
        f'<li><a href="/job-postings/{p["id"]}">{escape(p["title"])}</a>'
        f'<span class="sub">{escape(p["company"])} &middot; {escape(p["city"])} &middot; '
        f'{EMPLOYMENT_TYPES.get(p["employment_type"], "")}'
        f'{" &middot; until " + p["deadline"] if p.get("deadline") else ""}</span></li>'
        for p in postings
    )
    return f'<ul class="me-list">{items}</ul>'


def render_me_overview(user: dict, profile: dict, data: dict, done: str = "", error: str = "") -> str:
    role = user["role"]
    tiles, blocks = [], []

    if role in APPLICANT_ROLES:
        apps = data["applications"]
        active = [a for a in apps if a["status"] in ("submitted", "under_review", "interview")]
        tiles += [
            ("My applications", len(apps), "/me/applications", "sent so far"),
            ("In progress", len(active), "/me/applications", "submitted, in review or interview"),
            ("Interviews", sum(a["status"] == "interview" for a in apps), "/me/applications", ""),
            ("Saved postings", len(data["saved"]), "/me/saved", "to come back to"),
        ]
        interviews = [a for a in apps if a["status"] == "interview"]
        if interviews:
            rows = "".join(
                f'<li><a href="/job-postings/{a["posting_id"]}">{escape(a["title"])}</a>'
                f'<span class="sub">{escape(a["company"])} &middot; invited to an interview</span></li>'
                for a in interviews
            )
            blocks.append(f'<section class="card card-featured" data-reveal><h2>Next step: interviews</h2><ul class="me-list">{rows}</ul></section>')
        blocks.append(
            '<section class="card" data-reveal>'
            + section_head("Open postings for you", link=("All postings", "/job-postings"))
            + _posting_list(data["suggestions"], "You have applied to or saved every open posting.")
            + "</section>"
        )

    if role in POSTER_ROLES:
        postings = data["postings"]
        tiles += [
            ("My open postings", sum(is_open(p) for p in postings), "/me/postings", plural(len(postings), "posting") + " in all"),
            ("Waiting for you", sum(p["waiting"] for p in postings), "/me/postings#received", "applications to decide"),
        ]
    if role in AUTHOR_ROLES:
        tiles.append(("My announcements", len(data["announcements"]), "/me/announcements", ""))
    if role == "admin":
        tiles.append(("Registrations", data.get("pending", 0), "/admin/registrations", "waiting for review"))
    if role == "staff":
        tiles.append(("Department postings", sum(p["department"] for p in data["postings"]), "/me/postings", "you manage these"))

    percent, missing = _completeness(profile)
    if missing:
        why = (
            "Graduates who share where they work help the department follow careers and help students find mentors."
            if role == "alumni" else "A complete profile helps people know who they are talking to."
        )
        blocks.insert(0, f"""
        <section class="card me-progress" data-reveal>
          <div class="card-head"><h2>Your profile is {percent}% complete</h2><a class="btn btn-ghost btn-sm" href="/me/profile">Complete it</a></div>
          <div class="bar" aria-hidden="true"><span style="width:{percent}%"></span></div>
          <p class="muted">{why} Missing: {", ".join(missing)}.</p>
        </section>""")

    shortcuts = []
    if role in APPLICANT_ROLES:
        shortcuts.append(button("Browse job postings", "/job-postings", "primary", arrow=True))
    if role in POSTER_ROLES:
        shortcuts.append(button("Publish a job posting", "/job-postings#new"))
    if role in AUTHOR_ROLES:
        shortcuts.append(button("Write an announcement", "/announcements#new"))
    if role == "admin":
        shortcuts.append(button("Admin panel", "/admin"))
    shortcuts.append(button("Edit my profile", "/me/profile"))

    content = (
        (stat_tiles(tiles, "My numbers") if tiles else "")
        + f'<div class="me-shortcuts">{"".join(shortcuts)}</div>'
        + "".join(blocks)
    )
    first = escape(user["name"].split()[0]) if user["name"].split() else escape(user["name"])
    lead = f"Last sign-in {profile['last_login_at']}" if profile.get("last_login_at") else "Welcome"
    return account_shell(user, "overview", f"Hello, <em>{first}</em>", lead, content, done, error)


# --------------------------------------------------------------------------- profile
def _input(key: str, values: dict, errors: dict, hint: str = "", type_: str = "text", full: bool = False) -> str:
    value = escape(values.get(key) or "")
    err = f'<span class="field-error">{escape(errors[key])}</span>' if key in errors else ""
    hint_html = f'<span class="hint">{hint}</span>' if hint else ""
    if key == "bio":
        control = f'<textarea id="{key}" name="{key}" rows="4" maxlength="500">{value}</textarea>'
    else:
        control = f'<input id="{key}" name="{key}" type="{type_}" value="{value}" />'
    cls = "field" + (" full" if full else "") + (" has-error" if key in errors else "")
    return f'<div class="{cls}"><label for="{key}">{PROFILE_LABELS[key]}</label>{control}{hint_html}{err}</div>'


def render_me_profile(user: dict, profile: dict, values: dict | None = None, errors: dict | None = None,
                      done: str = "", error: str = "", sections: dict | None = None, cv: dict | None = None) -> str:
    values = values if values is not None else profile
    errors = errors or {}
    role = profile["role"]
    year_label = "Expected graduation" if role == "student" else "Graduation year"
    fixed = [
        ("Name", escape(profile["name"])),
        ("Email", escape(profile["email"])),
        ("Role", f'<span class="badge role role-{role}">{ROLE_LABELS[role]}</span>'),
        ("Department", escape(profile["department"])),
    ]
    if profile.get("graduation_year"):
        fixed.append((year_label, f'<span class="mono">{profile["graduation_year"]}</span>'))
    if profile.get("student_number"):
        fixed.append(("Student number", f'<span class="mono">{escape(profile["student_number"])}</span>'))
    if profile.get("title"):
        fixed.append(("Academic title", escape(profile["title"])))
    if profile.get("position"):
        fixed.append(("Position", escape(profile["position"])))
    fixed.append(("Member since", f'<span class="mono">{profile["created_at"]}</span>'))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in fixed)

    work_hint = {
        "alumni": "Where you work now: the department follows its graduates' careers with this.",
        "student": "An internship or part-time job, if you have one.",
    }.get(role, "Where you work (shown on your public profile).")
    form = f"""
      <form method="post" action="/me/profile" class="form-grid" novalidate>
        {_input("company", values, errors, work_hint)}
        {_input("job_title", values, errors)}
        {_input("city", values, errors)}
        {_input("linkedin_url", values, errors, "https://www.linkedin.com/in/...", "url")}
        {_input("bio", values, errors, "A few sentences: your interests, what you can help with. At most 500 characters.", full=True)}
        <div class="form-actions"><button type="submit" class="btn btn-primary">Save profile</button></div>
      </form>"""
    facts = "".join(f'<div class="me-fact"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in fixed)
    content = f"""
    <section class="card me-card" data-reveal>
      <div class="card-head"><h2>Account details</h2><span class="label-mono">checked at registration</span></div>
      <dl class="me-facts">{facts}</dl>
      <p class="hint me-note">These were checked against your document when your registration was approved.
      To correct one, ask the department staff or an admin.</p>
    </section>
    <section class="card me-card" data-reveal>
      <div class="card-head"><h2>Career profile</h2><span class="label-mono">you can change these</span></div>
      {form}
    </section>"""
    content += _cv_card(user, cv) + _profile_sections(sections or {})
    lead = f'What other members see about you. <a href="/users/{user["id"]}">See your public profile</a>.'
    return account_shell(user, "profile", "My <em>profile</em>", lead, content, done, error)


# --------------------------------------------------------------------------- applications
def render_me_applications(user: dict, applications: list[dict], done: str = "", error: str = "") -> str:
    counts = {s: 0 for s in ("submitted", "under_review", "interview", "accepted", "rejected", "withdrawn")}
    for a in applications:
        counts[a["status"]] += 1
    stages = "".join(
        f'<div class="stage s-{s}"><div class="label-mono">{_label(s)}</div><div class="num">{n}</div></div>'
        for s, n in counts.items()
    )
    rows = []
    for a in applications:
        actions = []
        if a["status"] in ("submitted", "under_review", "interview"):
            actions.append(_post(f"/me/applications/{a['id']}/withdraw", _btn("Withdraw"),
                                 "Withdraw this application? The poster will see it as withdrawn."))
        letter = escape(a["cover_letter"] or "")
        if a["status"] == "submitted":
            letter_cell = f"""<details class="me-letter"><summary>{letter[:60] + ("..." if len(letter) > 60 else "") if letter else "Add a letter"}</summary>
              <form method="post" action="/me/applications/{a['id']}/letter">
                <textarea name="cover_letter" rows="4" maxlength="5000" aria-label="Cover letter">{letter}</textarea>
                <button type="submit" class="btn btn-ghost btn-sm">Save letter</button></form></details>"""
        else:
            letter_cell = (letter[:80] + ("..." if len(letter) > 80 else "")) if letter else '<span class="muted">-</span>'
        rows.append(
            f'<tr><td><a href="/job-postings/{a["posting_id"]}">{escape(a["title"])}</a>'
            f'<span class="sub">{escape(a["company"])} &middot; {escape(a["city"])} &middot; by {escape(a["poster"])}</span>'
            + (f'<a class="cv-link" href="/cv/{a["cv_file_id"]}" target="_blank" rel="noopener">CV sent</a>' if a.get("cv_file_id") else "")
            + '</td>'
            f'<td>{_badge(a["status"])}<span class="sub mono">updated {a["updated_at"]}</span></td>'
            f"<td>{letter_cell}</td>"
            f'<td class="date">{a["created_at"]}</td>'
            f'<td class="col-actions"><div class="row-actions">{"".join(actions)}</div></td></tr>'
        )
    table = f"""
    <section class="pipeline" aria-label="My applications by status">{stages}</section>
    {section_head("Every application", plural(len(applications), "application"))}
    <div class="table-wrap"><table>
      <thead><tr><th>Posting</th><th>Status</th><th>Cover letter</th><th>Sent</th><th></th></tr></thead>
      <tbody>{"".join(rows) or _empty('You have not applied yet. <a href="/job-postings">Find a posting</a>.', 5)}</tbody>
    </table></div>
    <p class="hint">You can change the letter while the application is <b>submitted</b>, and withdraw until a decision is made.</p>"""
    return account_shell(user, "applications", "My <em>applications</em>", "Where each of your applications stands.", table, done, error)


# --------------------------------------------------------------------------- saved postings
def render_me_saved(user: dict, saved: list[dict], done: str = "", error: str = "") -> str:
    rows = "".join(
        f'<tr><td><a href="/job-postings/{p["id"]}">{escape(p["title"])}</a>'
        f'<span class="sub">{escape(p["company"])} &middot; {escape(p["city"])} &middot; {EMPLOYMENT_TYPES.get(p["employment_type"], "")}</span></td>'
        f'<td>{_open_badge(p)}</td>'
        f'<td class="mono">{p["deadline"] or "-"}</td>'
        f'<td>{_badge(p["applied_status"]) if p["applied_status"] else "<span class=muted>not yet</span>"}</td>'
        f'<td class="col-actions"><div class="row-actions">'
        f'{button("Apply", f"/job-postings/{p["id"]}#apply", "primary") if is_open(p) and not p["applied_status"] else ""}'
        f'{_post(f"/me/saved/{p["id"]}/remove", _btn("Remove") + "<input type=hidden name=back value=/me/saved>")}'
        "</div></td></tr>"
        for p in saved
    ) or _empty('Nothing saved yet. Use <b>Save</b> on a job posting to keep it here.', 5)
    content = f"""
    {section_head("Saved postings", plural(len(saved), "posting"))}
    <div class="table-wrap"><table>
      <thead><tr><th>Posting</th><th>Open</th><th>Deadline</th><th>My application</th><th></th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""
    return account_shell(user, "saved", "Saved <em>postings</em>", "Postings you keep to come back to.", content, done, error)


# --------------------------------------------------------------------------- my postings and the applications they received
def render_me_postings(user: dict, postings: list[dict], received: list[dict], done: str = "", error: str = "") -> str:
    rows = []
    for p in postings:
        toggle = _post(f"/me/postings/{p['id']}/active",
                       f'<input type="hidden" name="active" value="{0 if p["is_active"] else 1}" />'
                       + _btn("Close" if p["is_active"] else "Reopen"))
        who = '<span class="row-tag"><span class="badge">Department</span></span>' if p["department"] else ""
        rows.append(
            f'<tr><td>{who}<a href="/job-postings/{p["id"]}">{escape(p["title"])}</a>'
            f'<span class="sub">{escape(p["company"])} &middot; {escape(p["city"])}</span></td>'
            f'<td>{_open_badge(p)}<span class="sub mono">{"until " + p["deadline"] if p["deadline"] else "no deadline"}</span></td>'
            f'<td class="mono">{p["applications"]}</td>'
            f'<td class="mono">{p["waiting"]}</td>'
            f'<td class="mono">{p["interviews"]} / {p["accepted"]}</td>'
            f'<td class="col-actions"><div class="row-actions">{toggle}'
            f'<a class="btn btn-ghost btn-sm" href="/job-postings/{p["id"]}/edit">Edit</a></div></td></tr>'
        )
    rec_rows = []
    for a in received:
        options = "".join(f'<option value="{s}"{" selected" if s == a["status"] else ""}>{_label(s)}</option>' for s in DECISIONS)
        decide = (
            '<span class="muted">withdrawn by the applicant</span>' if a["status"] == "withdrawn" else
            _post(f"/me/received/{a['id']}/status",
                  f'<select name="status" aria-label="Decision">{options}</select> ' + _btn("Save"))
        )
        letter = escape(a["cover_letter"] or "")
        year = f" &middot; {a['graduation_year']}" if a["graduation_year"] else ""
        rec_rows.append(
            f'<tr><td><div class="cell-title"><span class="avatar" aria-hidden="true">{initials(a["applicant"])}</span>'
            f'<a href="/users/{a["applicant_id"]}">{escape(a["applicant"])}</a></div>'
            f'<span class="sub">{ROLE_LABELS[a["applicant_role"]]}{year} &middot; {escape(a["department"])}</span>'
            + (f'<a class="cv-link" href="/cv/{a["cv_file_id"]}" target="_blank" rel="noopener">Open CV</a>' if a.get("cv_file_id") else "")
            + '</td>'
            f'<td><a href="/job-postings/{a["job_posting_id"]}">{escape(a["title"])}</a></td>'
            f'<td>{_badge(a["status"])}</td>'
            f'<td>{(letter[:90] + ("..." if len(letter) > 90 else "")) if letter else "<span class=muted>-</span>"}</td>'
            f'<td class="col-actions">{decide}</td></tr>'
        )
    waiting = sum(a["status"] in ("submitted", "under_review") for a in received)
    content = f"""
    {section_head("My postings", plural(len(postings), "posting"), )}
    <div class="table-wrap"><table>
      <thead><tr><th>Posting</th><th>State</th><th>Applied</th><th>Waiting</th><th>Interview / accepted</th><th></th></tr></thead>
      <tbody>{"".join(rows) or _empty('You have not published a posting yet. <a href="/job-postings#new">Publish one</a>.', 6)}</tbody>
    </table></div>
    <div id="received" class="me-gap">{section_head("Applications received", f"{waiting} waiting for a decision")}</div>
    <div class="table-wrap"><table>
      <thead><tr><th>Applicant</th><th>Posting</th><th>Status</th><th>Cover letter</th><th>Decision</th></tr></thead>
      <tbody>{"".join(rec_rows) or _empty("No applications to your postings yet.", 5)}</tbody>
    </table></div>"""
    lead = "Your postings, and the people who applied to them."
    if user["role"] in ("staff", "admin"):
        lead += " The department's postings are here too: you manage them."
    return account_shell(user, "postings", "My <em>postings</em>", lead, content, done, error)


# --------------------------------------------------------------------------- my announcements
def render_me_announcements(user: dict, announcements: list[dict], done: str = "", error: str = "") -> str:
    rows = "".join(
        f'<tr><td><a href="/announcements/{a["id"]}">{escape(a["title"])}</a>'
        f'<span class="sub">{escape(a["content"][:110])}{"..." if len(a["content"]) > 110 else ""}</span></td>'
        f'<td class="date">{a["created_at"]}</td>'
        f'<td class="col-actions"><div class="row-actions"><a class="btn btn-ghost btn-sm" href="/announcements/{a["id"]}/edit">Edit</a>'
        f'{_post(f"/announcements/{a["id"]}/delete", _btn("Delete", "danger"), "Delete this announcement? This cannot be undone.")}'
        "</div></td></tr>"
        for a in announcements
    ) or _empty('You have not written an announcement yet. <a href="/announcements#new">Write one</a>.', 3)
    content = f"""
    {section_head("My announcements", plural(len(announcements), "announcement"), )}
    <div class="table-wrap"><table>
      <thead><tr><th>Announcement</th><th>Published</th><th></th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""
    return account_shell(user, "announcements", "My <em>announcements</em>", "What you have published for everyone.", content, done, error)


# --------------------------------------------------------------------------- security
def _device(agent: str | None) -> str:
    a = agent or ""
    browser = next((b for k, b in (("Edg", "Edge"), ("OPR", "Opera"), ("Chrome", "Chrome"), ("Firefox", "Firefox"),
                                   ("Safari", "Safari"), ("curl", "curl")) if k in a), "Unknown browser")
    system = next((s for k, s in (("Windows", "Windows"), ("Android", "Android"), ("iPhone", "iPhone"),
                                  ("Mac OS", "macOS"), ("Linux", "Linux")) if k in a), "")
    return browser + (f" on {system}" if system else "")


def render_me_security(user: dict, profile: dict, sessions: list[dict], done: str = "", error: str = "") -> str:
    has_password = profile["has_password"]
    current = (
        '<div class="field full"><label for="current">Current password</label>'
        '<input id="current" name="current" type="password" autocomplete="current-password" required /></div>'
        if has_password else
        '<p class="hint full">This account has no password yet (it was created by an admin). Choose one to sign in with it.</p>'
    )
    password_form = f"""
      <form method="post" action="/me/password" class="form-grid">
        {current}
        <div class="field"><label for="new">New password</label>
          <input id="new" name="new" type="password" autocomplete="new-password" minlength="8" maxlength="128" required />
          <span class="hint">At least 8 characters, with a letter and a digit.</span></div>
        <div class="field"><label for="confirm">New password again</label>
          <input id="confirm" name="confirm" type="password" autocomplete="new-password" required /></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary">{"Change password" if has_password else "Set password"}</button></div>
      </form>
      <p class="hint">Changing it signs you out everywhere else; this browser stays signed in.</p>"""

    rows = "".join(
        f'<tr><td>{_device(s["user_agent"])}{" <span class=\"badge ok\">this browser</span>" if s["current"] else ""}'
        f'<span class="sub mono">{escape((s["user_agent"] or "")[:70])}</span></td>'
        f'<td class="date">{s["created_at"]}</td><td class="date">{s["last_seen_at"]}</td><td class="date">{s["expires_at"]}</td>'
        f'<td class="col-actions">{"" if s["current"] else _post(f"/me/sessions/{s["id"]}/end", _btn("Sign out"))}</td></tr>'
        for s in sessions
    )
    others = sum(not s["current"] for s in sessions)
    end_others = _post("/me/sessions/end-others", _btn(f"Sign out the other {others}")) if others else ""

    if user["role"] == "admin":
        danger = '<p class="muted" style="margin:0">An admin account is removed by another admin in the admin panel.</p>'
    elif not has_password:
        danger = '<p class="muted" style="margin:0">Set a password first; you confirm the deletion with it.</p>'
    else:
        danger = """
        <form method="post" action="/me/delete" class="form-grid" onsubmit="return confirm('Delete your account and everything in it? This cannot be undone.')">
          <div class="field"><label for="delete_password">Your password</label>
            <input id="delete_password" name="password" type="password" autocomplete="current-password" required /></div>
          <div class="form-actions"><button type="submit" class="btn btn-danger">Delete my account</button></div>
        </form>
        <p class="hint">Your applications and saved postings are deleted with it; your postings and announcements stay, shown as the department's.</p>"""

    content = f"""
    <section class="card" data-reveal>
      <div class="card-head"><h2>Password</h2><span class="label-mono">{"set" if has_password else "not set yet"}</span></div>
      {password_form}
    </section>
    <div class="section-head me-gap"><h2>Where you are signed in</h2><div class="row-actions">{end_others}</div></div>
    <div class="table-wrap"><table>
      <thead><tr><th>Browser</th><th>Signed in</th><th>Last active</th><th>Ends</th><th></th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <section class="card me-danger" data-reveal>
      <div class="card-head"><h2>Delete my account</h2></div>
      {danger}
    </section>"""
    return account_shell(user, "security", "Sign-in &amp; <em>security</em>", "Your password and the browsers you are signed in on.", content, done, error)


# --------------------------------------------------------------------------- profile sections (ddd.md 4.1.7)
def _v(item: dict | None, key: str) -> str:
    value = (item or {}).get(key)
    return "" if value is None else escape(str(value))


def _f(label: str, control: str, full: bool = False, hint: str = "") -> str:
    hint_html = f'<span class="hint">{hint}</span>' if hint else ""
    return f'<div class="field{" full" if full else ""}"><label>{label}{control}</label>{hint_html}</div>'


def _section_fields(kind: str, item: dict | None = None) -> str:
    if kind == "experiences":
        current = item is not None and item.get("end") is None
        return (
            _f("Title", f'<input name="title" maxlength="120" required value="{_v(item, "title")}" placeholder="Data Analyst" />')
            + _f("Company", f'<input name="company" maxlength="150" required value="{_v(item, "company")}" />')
            + _f("City", f'<input name="city" maxlength="100" value="{_v(item, "city")}" />')
            + _f("Start", f'<input name="start_date" type="month" required value="{_v(item, "start")}" />')
            + _f("End", f'<input name="end_date" type="month" value="{_v(item, "end")}" />',
                 hint=f'<label class="check"><input type="checkbox" name="current" value="1"{" checked" if current else ""} /> I work here now</label>')
            + _f("What you do", f'<textarea name="description" rows="3" maxlength="1000">{_v(item, "description")}</textarea>', full=True)
        )
    if kind == "educations":
        return (
            _f("School", f'<input name="school" maxlength="150" required value="{_v(item, "school")}" placeholder="İstanbul Üniversitesi" />')
            + _f("Degree", f'<input name="degree" maxlength="100" value="{_v(item, "degree")}" placeholder="Lisans, Yüksek Lisans..." />')
            + _f("Field of study", f'<input name="field" maxlength="150" value="{_v(item, "field")}" placeholder="Yönetim Bilişim Sistemleri" />', full=True)
            + _f("Start year", f'<input name="start_year" type="number" min="1950" max="2100" required value="{_v(item, "start_year")}" />')
            + _f("End year", f'<input name="end_year" type="number" min="1950" max="2100" value="{_v(item, "end_year")}" />',
                 hint="Empty while you still study there.")
            + _f("Notes", f'<textarea name="description" rows="2" maxlength="1000">{_v(item, "description")}</textarea>', full=True)
        )
    return (
        _f("Certificate", f'<input name="name" maxlength="150" required value="{_v(item, "name")}" placeholder="Google Data Analytics" />')
        + _f("Issued by", f'<input name="issuer" maxlength="150" required value="{_v(item, "issuer")}" placeholder="Coursera" />')
        + _f("Issued", f'<input name="issued_on" type="month" value="{_v(item, "issued")}" />')
        + _f("Credential link", f'<input name="credential_url" type="url" maxlength="300" value="{_v(item, "credential_url")}" placeholder="https://..." />')
    )


SECTION_INFO = {
    "experiences": ("Experience", "Add experience", "Internships, jobs, volunteer work."),
    "educations": ("Education", "Add education", "Schools and programmes."),
    "certificates": ("Certificates", "Add certificate", "Courses and certificates you earned."),
}


def _item_line(kind: str, item: dict) -> str:
    if kind == "experiences":
        when = f'{item["start"]} &ndash; {item["end"] or "now"}'
        city = " &middot; " + escape(item["city"]) if item.get("city") else ""
        return (f'<b>{escape(item["title"])}</b><span class="sub">{escape(item["company"])}{city} '
                f'&middot; <span class="mono">{when}</span></span>')
    if kind == "educations":
        what = ", ".join(escape(x) for x in (item.get("degree"), item.get("field")) if x)
        when = f'{item["start_year"]} &ndash; {item["end_year"] or "now"}'
        return f'<b>{escape(item["school"])}</b><span class="sub">{what + " &middot; " if what else ""}<span class="mono">{when}</span></span>'
    issued = f' &middot; <span class="mono">{item["issued"]}</span>' if item.get("issued") else ""
    return f'<b>{escape(item["name"])}</b><span class="sub">{escape(item["issuer"])}{issued}</span>'


def _profile_sections(sections: dict) -> str:
    out = []
    for kind, (title, add_label, hint) in SECTION_INFO.items():
        items = sections.get(kind, [])
        rows = "".join(
            f"""<li class="pe-item"><div class="pe-text">{_item_line(kind, it)}</div>
              <div class="pe-actions">
                <details class="pe-edit"><summary class="btn btn-ghost btn-sm">Edit</summary>
                  <form method="post" action="/me/profile/{kind}/{it['id']}" class="form-grid">{_section_fields(kind, it)}
                    <div class="form-actions"><button type="submit" class="btn btn-primary btn-sm">Save</button></div></form>
                </details>
                {_post(f"/me/profile/{kind}/{it['id']}/delete", _btn("Delete", "danger"), "Delete this from your profile?")}
              </div></li>"""
            for it in items
        ) or f'<li class="pe-empty muted">{hint}</li>'
        count = f"{len(items)} {'entry' if len(items) == 1 else 'entries'}"
        out.append(f"""
        <section class="card pe-card" id="{kind}" data-reveal>
          <div class="card-head"><h2>{title}</h2><span class="label-mono">{count}</span></div>
          <ul class="pe-list">{rows}</ul>
          <details class="pe-add"><summary class="btn btn-ghost btn-sm">+ {add_label}</summary>
            <form method="post" action="/me/profile/{kind}" class="form-grid">{_section_fields(kind)}
              <div class="form-actions"><button type="submit" class="btn btn-primary btn-sm">Add</button></div></form>
          </details>
        </section>""")
    return '<div class="me-gap">' + section_head("Your story", "shown on your public profile") + "".join(out) + "</div>"


def cv_size(n: int) -> str:
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1048576:.1f} MB"


def _cv_card(user: dict, cv: dict | None) -> str:
    if user["role"] not in APPLICANT_ROLES:
        return ""
    if cv:
        now = (
            f'<div class="cv-now"><div><a href="/cv/{cv["id"]}" target="_blank" rel="noopener">{escape(cv["original_name"])}</a>'
            f'<span class="sub mono">{cv_size(cv["size_bytes"])} &middot; uploaded {cv["uploaded_at"]}</span></div>'
            + _post("/me/cv/remove", _btn("Remove"), "Remove your CV? Applications you already sent keep theirs.")
            + "</div>"
        )
    else:
        now = '<p class="muted" style="margin:0 0 12px">No CV yet. Upload one and attach it when you apply.</p>'
    return f"""
    <section class="card cv-card me-gap" id="cv" data-reveal>
      <div class="card-head"><h2>CV</h2><span class="label-mono">seen by you, staff and the posters you apply to</span></div>
      {now}
      <form method="post" action="/me/cv" enctype="multipart/form-data" class="cv-upload">
        <input type="file" name="cv" accept="application/pdf,.pdf" required aria-label="CV file (PDF)" />
        <button type="submit" class="btn btn-ghost btn-sm">{"Replace CV" if cv else "Upload CV"}</button>
      </form>
      <p class="hint">PDF, at most 5 MB. A new CV replaces this one; applications you already sent keep the CV they were sent with.</p>
    </section>"""
