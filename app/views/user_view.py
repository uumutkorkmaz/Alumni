from html import escape

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
    stat_tiles,
)

ACTIVE = "/users"


def _row(user: dict) -> str:
    base = f"/users/{user['id']}"
    return (
        f'<tr><td class="id">#{user["id"]}</td>'
        f'<td><div class="cell-title"><span class="avatar" aria-hidden="true">{initials(user["name"])}</span>'
        f'<a href="{base}">{escape(user["name"])}</a></div></td>'
        f'<td class="muted">{escape(user["email"])}</td>'
        f'<td class="date">{user["graduation_year"]}</td><td>{escape(user["department"])}</td>'
        f'<td class="col-actions">{row_actions(base, "user")}</td></tr>'
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
        f'<span class="album-meta">Class of {user["graduation_year"]} &middot; {escape(user["department"])}</span>'
        f'<span class="album-mail">{escape(user["email"])}</span>'
        "</span></a>"
        f'<div class="album-actions">{row_actions(base, "user")}</div>'
        "</li>"
    )


def render_user_list(users: list[dict]) -> str:
    rows = "".join(_row(u) for u in users) or (
        '<tr><td class="empty" colspan="6">No users yet. Add the first one below.</td></tr>'
    )
    cards = "".join(_card(u, i) for i, u in enumerate(users)) or (
        '<li class="album-empty">No users yet. Add the first one below.</li>'
    )
    years = sorted({u["graduation_year"] for u in users})
    span = f"Classes {years[0]}–{years[-1]}" if len(years) > 1 else ""
    views = (
        '<div class="view-switch" data-views role="group" aria-label="View" hidden>'
        '<button type="button" data-view="album" data-target="users-album" aria-pressed="true">Album</button>'
        '<button type="button" data-view="table" data-target="users-table-wrap" aria-pressed="false">Table</button>'
        "</div>"
    )

    departments = {u["department"] for u in users}
    stats = stat_tiles([
        ("Graduates", len(users), "", ""),
        ("Classes", f"{years[0]}–{years[-1]}" if years else "&ndash;", "", f"{len(years)} graduating years" if years else ""),
        ("Departments", len(departments), "", ""),
        ("Newest class", years[-1] if years else "&ndash;", "", "", False),
    ], "Graduates in numbers")

    body = f"""
    {page_hero(
        "Directory &middot; Graduates",
        "The class <em>album</em>",
        "Every Istanbul University MIS graduate the system keeps, with their class and department. Open a photo to see the graduate; switch to the table to edit many at once.",
        new_button("New user") + button("Applications", "/applications"),
    )}
    {stats}
    {filter_toolbar("users-album users-table", plural(len(users), "user") + (f" &middot; {span}" if span else ""), views)}
    <section class="album-band" id="users-album" aria-label="Class album">
      <p class="album-display" aria-hidden="true">Graduates</p>
      <ul class="album">{cards}</ul>
    </section>
    <div class="table-wrap" id="users-table-wrap" hidden>
      <table id="users-table">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Class of</th><th>Department</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("Add user", _user_form(action="/users"), "All fields required")}
    """
    return render_page("Users", body, ACTIVE)


def render_user_detail(user: dict) -> str:
    body = f"""
    {page_hero(
        f"User #{user['id']} &middot; Class of {user['graduation_year']}",
        escape(user['name']),
        escape(user['department']),
        button("Edit", f"/users/{user['id']}/edit", "primary") + button("Applications", "/applications"),
        size="compact",
    )}
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        <dt>Email</dt><dd><a href="mailto:{escape(user['email'])}">{escape(user['email'])}</a></dd>
        <dt>Graduation year</dt><dd class="mono">{user['graduation_year']}</dd>
        <dt>Department</dt><dd>{escape(user['department'])}</dd>
      </dl>
    </section>
    {back_link("/users", "Back to users")}
    """
    return render_page(user["name"], body, ACTIVE, narrow=True)


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

    submit_label = "Save changes" if user else "Create user"
    cancel = f'<a class="btn btn-ghost" href="/users/{u["id"]}">Cancel</a>' if user else ""
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="name">Name</label>
        <input id="name" type="text" name="name" value="{value('name')}" maxlength="100" required autocomplete="name" /></div>
      <div class="field"><label for="email">Email</label>
        <input id="email" type="email" name="email" value="{value('email')}" maxlength="255" required autocomplete="email" /></div>
      <div class="field"><label for="graduation_year">Graduation year</label>
        <input id="graduation_year" type="number" name="graduation_year" value="{value('graduation_year')}" min="1950" max="2100" required /></div>
      <div class="field"><label for="department">Department</label>
        <input id="department" type="text" name="department" value="{value('department')}" maxlength="100" required /></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button>{cancel}</div>
    </form>
    """
