from html import escape

from app.views.layout import (
    back_link,
    edit_header,
    filter_toolbar,
    form_card,
    initials,
    new_button,
    page_header,
    plural,
    render_page,
    row_actions,
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


def render_user_list(users: list[dict]) -> str:
    rows = "".join(_row(u) for u in users) or (
        '<tr><td class="empty" colspan="6">No users yet. Add the first one below.</td></tr>'
    )
    years = sorted({u["graduation_year"] for u in users})
    span = f"Classes {years[0]}–{years[-1]}" if len(years) > 1 else ""

    body = f"""
    {page_header("Users", "MIS graduates tracked by the system.", new_button("New user"), kicker="Directory · Graduates", line=True)}
    {filter_toolbar("users-table", plural(len(users), "user") + (f" &middot; {span}" if span else ""))}
    <div class="table-wrap" data-reveal>
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
    <div class="profile">
      <span class="avatar lg" aria-hidden="true">{initials(user['name'])}</span>
      <div>
        <span class="kicker">User #{user['id']} &middot; Class of {user['graduation_year']}</span>
        <h1>{escape(user['name'])}</h1>
      </div>
    </div>
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        <dt>Email</dt><dd><a href="mailto:{escape(user['email'])}">{escape(user['email'])}</a></dd>
        <dt>Graduation year</dt><dd class="mono">{user['graduation_year']}</dd>
        <dt>Department</dt><dd>{escape(user['department'])}</dd>
      </dl>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/users/{user['id']}/edit">Edit</a>
        <a class="btn btn-ghost" href="/applications">Applications</a>
      </div>
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
