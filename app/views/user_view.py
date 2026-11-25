from html import escape

from app import policy
from app.auth import me
from app.models.user import ROLE_LABELS, ROLES
from app.views.layout import (
    back_link,
    button,
    edit_header,
    filter_toolbar,
    form_card,
    initials,
    new_button,
    page_hero,
    plural,
    render_page,
    row_actions,
    section_head,
    stat_tiles,
)

ACTIVE = "/users"

# Students and graduates are the album; academic and administrative staff are listed apart.
ALBUM_ROLES = ("student", "alumni")


def role_badge(role: str) -> str:
    """A short mono badge with the role's own colour (DESIGN.md §2.4 / Role Badge)."""
    return f'<span class="badge role role-{role}">{ROLE_LABELS[role]}</span>'


def _year_text(user: dict) -> str:
    if user["graduation_year"] is None:
        return ""
    prefix = "Expected" if user["role"] == "student" else "Class of"
    return f"{prefix} {user['graduation_year']}"


def _row(user: dict) -> str:
    base = f"/users/{user['id']}"
    return (
        f'<tr><td class="id">#{user["id"]}</td>'
        f'<td><div class="cell-title"><span class="avatar" aria-hidden="true">{initials(user["name"])}</span>'
        f'<a href="{base}">{escape(user["name"])}</a></div></td>'
        f'<td class="muted">{escape(user["email"]) if user["email"] else "hidden"}</td>'
        f'<td>{role_badge(user["role"])}</td>'
        f'<td class="date">{user["graduation_year"] or "&ndash;"}</td><td>{escape(user["department"])}</td>'
        f'<td class="col-actions">{row_actions(base, "user", policy.can_edit_user(user), policy.can_delete_user())}</td></tr>'
    )


# Album (DESIGN.md §4, Album Card): the graduates as photos tossed on a table, after the tilted photo
# clusters of the San Rita reference. The "photo" is a spot of the campus film
# (app/static/film/thumbs/t01..t32.webp: the gate, the avenue, the Rectorate) with the graduate's
# initials on it; there are no portraits in the database. The picture comes from the id (a graduate
# always gets the same one); the scatter comes from the position, so neighbours never share an angle.
THUMBS = 32
TILTS = [-6, 5, -3, 7, -7, 3, -5, 6, 2, -4]            # degrees: enough to scatter, small enough that
                                                        # a neighbour never covers a name
SHIFT_X = [-8, 6, -4, 8, -6, 2, 6, -8, 4, -2]          # px
SHIFT_Y = [0, 22, 8, 30, 14, 4, 26, 10, 18, 2]         # px


def _card(user: dict, i: int) -> str:
    base = f"/users/{user['id']}"
    thumb = f"/static/film/thumbs/t{(user['id'] * 7) % THUMBS + 1:02d}.webp"
    k = i % len(TILTS)
    # Each photo lies on top of the one before it: the names sit on the left, so a card only ever
    # covers the empty right edge of its left neighbour.
    scatter = f"--tilt: {TILTS[k]}deg; --dx: {SHIFT_X[k]}px; --dy: {SHIFT_Y[k]}px; --z: {i + 1}"
    return (
        f'<li class="album-card" style="{scatter}" data-reveal data-filter-item>'
        f'<a class="album-photo" href="{base}">'
        f'<img src="{thumb}" alt="" loading="lazy" decoding="async" width="400" height="500" />'
        f'<span class="album-initials" aria-hidden="true">{initials(user["name"])}</span>'
        f'<span class="album-tag">#{user["id"]:02d}</span>'
        '<span class="album-caption">'
        f'<span class="album-name">{escape(user["name"])}</span>'
        f'<span class="album-meta">{"Student &middot; " if user["role"] == "student" else ""}'
        f'{_year_text(user)} &middot; {escape(user["department"])}</span>'
        f'<span class="album-mail">{escape(user["email"] or "")}</span>'
        "</span></a>"
        f'<div class="album-actions">{row_actions(base, "user", policy.can_edit_user(user), policy.can_delete_user())}</div>'
        "</li>"
    )


def render_user_list(users: list[dict], pending: int = 0) -> str:
    rows = "".join(_row(u) for u in users) or (
        '<tr><td class="empty" colspan="7">No users yet. Add the first one below.</td></tr>'
    )
    album_users = [u for u in users if u["role"] in ALBUM_ROLES]
    others = [u for u in users if u["role"] not in ALBUM_ROLES]
    cards = "".join(_card(u, i) for i, u in enumerate(album_users)) or (
        '<li class="album-empty">No students or graduates yet. Add the first one below.</li>'
    )
    people = "".join(
        f'<li class="person" data-filter-item><span class="avatar" aria-hidden="true">{initials(u["name"])}</span>'
        f'<span class="person-text"><a href="/users/{u["id"]}">{escape(u["name"])}</a>'
        f'<span class="sub">{escape(u["department"])}</span></span>{role_badge(u["role"])}</li>'
        for u in others
    )
    staff_block = (
        f'{section_head("Faculty and staff", plural(len(others), "person").replace("persons", "people"))}'
        f'<ul class="people">{people}</ul>'
        if others
        else ""
    )
    graduates = [u for u in users if u["role"] == "alumni"]
    years = sorted({u["graduation_year"] for u in graduates})
    views = (
        '<div class="view-switch" data-views role="group" aria-label="View" hidden>'
        '<button type="button" data-view="album" data-target="users-album" aria-pressed="true">Album</button>'
        '<button type="button" data-view="table" data-target="users-table-wrap" aria-pressed="false">Table</button>'
        "</div>"
    )

    stats = stat_tiles([
        ("Graduates", len(graduates), "", f"classes {years[0]}–{years[-1]}" if len(years) > 1 else ""),
        ("Students", sum(1 for u in users if u["role"] == "student"), "", ""),
        ("Academics", sum(1 for u in users if u["role"] == "academic"), "", ""),
        ("Staff and admins", sum(1 for u in users if u["role"] in ("staff", "admin")), "", ""),
    ], "People in numbers")

    body = f"""
    {page_hero(
        "Directory &middot; Graduates",
        "The class <em>album</em>",
        "Istanbul University MIS students and graduates, with their class and department, and the academic and administrative staff who share opportunities with them. Switch to the table to see everyone with their role.",
        (new_button("New user") if policy.can_add_user() else "")
        + (button(f"Registrations to review ({pending})" if pending else "Registrations", "/admin/registrations")
           if policy.is_admin() else "")
        + button("Applications", "/applications"),
    )}
    {stats}
    {filter_toolbar("users-album users-table", plural(len(users), "user"), views)}
    <section class="album-band" id="users-album" aria-label="Class album">
      <p class="album-display" aria-hidden="true">Graduates</p>
      <ul class="album">{cards}</ul>
      {staff_block}
    </section>
    <div class="table-wrap" id="users-table-wrap" hidden>
      <table id="users-table">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Year</th><th>Department</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("Add user", _user_form(action="/users"), "Year required for students and graduates") if policy.can_add_user() else ""}
    """
    return render_page("Users", body, ACTIVE)


def _duration(months: int) -> str:
    years, rest = divmod(months, 12)
    parts = ([f"{years} yr{'s' if years > 1 else ''}"] if years else []) + ([f"{rest} mo"] if rest else [])
    return " ".join(parts) or "1 mo"


def _timeline(items: list[str]) -> str:
    return '<ol class="timeline">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def _experience(e: dict) -> str:
    when = f'{e["start"]} &ndash; {e["end"] or "now"} &middot; {_duration(e["months"])}'
    city = f' &middot; {escape(e["city"])}' if e.get("city") else ""
    desc = f'<p class="tl-desc">{escape(e["description"])}</p>' if e.get("description") else ""
    now = ' <span class="badge ok">now</span>' if not e["end"] else ""
    return (f'<div class="tl-title">{escape(e["title"])}{now}</div>'
            f'<div class="tl-sub">{escape(e["company"])}{city}</div><div class="tl-when mono">{when}</div>{desc}')


def _education(e: dict) -> str:
    what = ", ".join(escape(x) for x in (e.get("degree"), e.get("field")) if x)
    desc = f'<p class="tl-desc">{escape(e["description"])}</p>' if e.get("description") else ""
    return (f'<div class="tl-title">{escape(e["school"])}</div>'
            + (f'<div class="tl-sub">{what}</div>' if what else "")
            + f'<div class="tl-when mono">{e["start_year"]} &ndash; {e["end_year"] or "now"}</div>{desc}')


def _certificate(c: dict) -> str:
    issued = f' &middot; <span class="mono">{c["issued"]}</span>' if c.get("issued") else ""
    link = (f' <a class="link-arrow" href="{escape(c["credential_url"])}" target="_blank" rel="noopener noreferrer">'
            'Show credential <span class="arrow" aria-hidden="true">&rarr;</span></a>') if c.get("credential_url") else ""
    return f'<div class="tl-title">{escape(c["name"])}</div><div class="tl-sub">{escape(c["issuer"])}{issued}</div>{link}'


def _profile_section(title: str, items: list, render, own: bool, empty: str, anchor: str) -> str:
    if items:
        inner = _timeline([render(i) for i in items])
    elif own:
        inner = f'<p class="muted" style="margin:0">{empty} <a href="/me/profile#{anchor}">Add it</a>.</p>'
    else:
        return ""
    return f'<section class="card pp-section" data-reveal><h2>{title}</h2>{inner}</section>'


def render_user_detail(user: dict, sections: dict | None = None, activity: dict | None = None) -> str:
    """The public profile (ddd.md 4.1.7), the way LinkedIn shows one: who the person is and what they
    do now, then about, experience, education and certificates, and on the side the contact details
    and what they published here. Every signed-in member sees it."""
    sections = sections or {"experiences": [], "educations": [], "certificates": []}
    activity = activity or {"postings": [], "announcements": []}
    viewer = me() or {}
    own = viewer.get("id") == user["id"]

    current = next((e for e in sections["experiences"] if not e["end"]), None)
    if user.get("job_title") or user.get("company"):
        headline = " at ".join(escape(v) for v in (user.get("job_title"), user.get("company")) if v)
    elif current:
        headline = f'{escape(current["title"])} at {escape(current["company"])}'
    else:
        headline = escape(user["department"])
    place = " &middot; ".join(x for x in (escape(user.get("city") or ""), escape(user["department"]) if headline != escape(user["department"]) else "") if x)

    actions = ""
    if own:
        actions += button("Edit my profile", "/me/profile", "primary")
    elif policy.can_edit_user(user):
        actions += button("Edit account", f"/users/{user['id']}/edit", "primary")
    if user.get("linkedin_url"):
        actions += f'<a class="btn btn-ghost" href="{escape(user["linkedin_url"])}" target="_blank" rel="noopener noreferrer">LinkedIn</a>'
    if user.get("email") and not own:
        actions += f'<a class="btn btn-ghost" href="mailto:{escape(user["email"])}">Email</a>'

    year = f" &middot; {_year_text(user)}" if user["graduation_year"] else ""
    head = f"""
    <section class="pp-head" data-reveal>
      <span class="pp-avatar" aria-hidden="true">{initials(user['name'])}</span>
      <div class="pp-who">
        <span class="pill">{ROLE_LABELS[user['role']]}{year}</span>
        <h1>{escape(user['name'])}</h1>
        <p class="pp-headline">{headline}</p>
        {f'<p class="pp-place">{place}</p>' if place else ""}
        <div class="cta">{actions}</div>
      </div>
    </section>"""

    about = ""
    if user.get("bio"):
        about = f'<section class="card card-featured pp-section" data-reveal><h2>About</h2><p class="content">{escape(user["bio"])}</p></section>'
    elif own:
        about = ('<section class="card pp-section" data-reveal><h2>About</h2><p class="muted" style="margin:0">'
                 'A few sentences about you. <a href="/me/profile">Write them</a>.</p></section>')
    main = (
        about
        + _profile_section("Experience", sections["experiences"], _experience, own, "No experience yet.", "experiences")
        + _profile_section("Education", sections["educations"], _education, own, "No education yet.", "educations")
        + _profile_section("Certificates", sections["certificates"], _certificate, own, "No certificates yet.", "certificates")
    )
    if not main:
        main = '<section class="card pp-section"><p class="muted" style="margin:0">Nothing shared on this profile yet.</p></section>'

    email = (f'<a href="mailto:{escape(user["email"])}">{escape(user["email"])}</a>' if user["email"]
             else '<span class="muted">Hidden: only staff, academics and the person see it</span>')
    details = f"""
      <section class="card" data-reveal>
        <dl class="dl">
          <dt>Email</dt><dd>{email}</dd>
          <dt>Role</dt><dd>{role_badge(user['role'])}</dd>
          {f'<dt>{"Expected graduation" if user["role"] == "student" else "Graduation year"}</dt><dd class="mono">{user["graduation_year"]}</dd>' if user["graduation_year"] else ""}
          <dt>Department</dt><dd>{escape(user['department'])}</dd>
          {f'<dt>City</dt><dd>{escape(user["city"])}</dd>' if user.get("city") else ""}
        </dl>
      </section>"""
    act = ""
    if activity["postings"]:
        act += "<h3>Job postings</h3><ul class=\"me-list\">" + "".join(
            f'<li><a href="/job-postings/{p["id"]}">{escape(p["title"])}</a><span class="sub">{escape(p["company"])}'
            f'{"" if p["is_active"] else " &middot; closed"}</span></li>' for p in activity["postings"]) + "</ul>"
    if activity["announcements"]:
        act += "<h3>Announcements</h3><ul class=\"me-list\">" + "".join(
            f'<li><a href="/announcements/{a["id"]}">{escape(a["title"])}</a><span class="sub mono">{a["created_at"]}</span></li>'
            for a in activity["announcements"]) + "</ul>"
    if act:
        act = f'<section class="card pp-activity" data-reveal><h2>Activity</h2>{act}</section>'

    body = f"""
    {head}
    <div class="detail-grid pp-grid">
      <div class="detail-main">{main}</div>
      <aside class="detail-side">{details}{act}</aside>
    </div>
    {back_link("/users", "Back to users")}
    """
    return render_page(user["name"], body, ACTIVE)


def render_user_edit_form(user: dict) -> str:
    body = f"""
    {edit_header("user", f"User #{user['id']}")}
    <section class="card card-featured">
      {_user_form(action=f"/users/{user['id']}/edit", user=user)}
    </section>
    {back_link(f"/users/{user['id']}", "Back to the user")}
    """
    return render_page("Edit user", body, ACTIVE, narrow=True)


def _user_form(action: str, user: dict | None = None) -> str:
    u = user or {}

    def value(key: str) -> str:
        return escape(str(u.get(key, "")))

    current = u.get("role", "alumni")
    # Only an admin gives any role; staff add students and graduates; otherwise the role stays.
    if policy.is_admin():
        allowed = ROLES
    elif user is None:
        allowed = ("student", "alumni")
    else:
        allowed = (current,)
    role_options = "".join(
        f'<option value="{r}"{" selected" if r == current else ""}>{ROLE_LABELS[r]}</option>' for r in allowed
    )
    submit_label = "Save changes" if user else "Create user"
    cancel = f'<a class="btn btn-ghost" href="/users/{u["id"]}">Cancel</a>' if user else ""
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="name">Name</label>
        <input id="name" type="text" name="name" value="{value('name')}" maxlength="100" required autocomplete="name" /></div>
      <div class="field"><label for="email">Email</label>
        <input id="email" type="email" name="email" value="{value('email')}" maxlength="255" required autocomplete="email" /></div>
      <div class="field"><label for="role">Role</label>
        <select id="role" name="role" required>{role_options}</select></div>
      <div class="field"><label for="graduation_year">Graduation year (required for students and graduates)</label>
        <input id="graduation_year" type="number" name="graduation_year" value="{value('graduation_year') if u.get('graduation_year') else ''}" min="1950" max="2100" /></div>
      <div class="field"><label for="department">Department</label>
        <input id="department" type="text" name="department" value="{value('department')}" maxlength="100" required /></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button>{cancel}</div>
    </form>
    """
