from html import escape

from app.views.layout import filter_toolbar, new_button, page_header, plural, render_page, row_actions

ACTIVE = "/users"


def _row(user: dict) -> str:
    base = f"/users/{user['id']}"
    return (
        f"<tr><td>{user['id']}</td><td><a href=\"{base}\">{escape(user['name'])}</a></td><td>{escape(user['email'])}</td>"
        f"<td>{user['graduation_year']}</td><td>{escape(user['department'])}</td>"
        f'<td class="col-actions">{row_actions(base, "user")}</td></tr>'
    )


def render_user_list(users: list[dict]) -> str:
    rows = "".join(_row(u) for u in users) or (
        '<tr><td class="empty" colspan="6">No users yet. Add the first one below.</td></tr>'
    )

    body = f"""
    {page_header("Users", "MIS graduates tracked by the system.", new_button("New user"))}
    {filter_toolbar("users-table", plural(len(users), "user"))}
    <div class="table-wrap">
      <table id="users-table">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Graduation year</th><th>Department</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <section class="card" id="new" style="margin-top: 32px">
      <h2>Add user</h2>
      {_user_form(action="/users")}
    </section>
    """
    return render_page("Users", body, ACTIVE)


def render_user_detail(user: dict) -> str:
    body = f"""
    {page_header(escape(user['name']), f"User #{user['id']}")}
    <section class="card">
      <dl class="dl">
        <dt>Email</dt><dd>{escape(user['email'])}</dd>
        <dt>Graduation year</dt><dd>{user['graduation_year']}</dd>
        <dt>Department</dt><dd>{escape(user['department'])}</dd>
      </dl>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/users/{user['id']}/edit">Edit</a>
      </div>
    </section>
    <a class="back-link" href="/users">&larr; Back to users</a>
    """
    return render_page(user["name"], body, ACTIVE, narrow=True)


def render_user_edit_form(user: dict) -> str:
    body = f"""
    {page_header("Edit user", f"User #{user['id']}")}
    <section class="card">
      {_user_form(action=f"/users/{user['id']}/edit", user=user)}
    </section>
    <a class="back-link" href="/users">&larr; Back to users</a>
    """
    return render_page("Edit user", body, ACTIVE, narrow=True)


def _user_form(action: str, user: dict | None = None) -> str:
    u = user or {}

    def value(key: str) -> str:
        return escape(str(u.get(key, "")))

    submit_label = "Save changes" if user else "Create user"
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="name">Name</label>
        <input id="name" type="text" name="name" value="{value('name')}" maxlength="100" required /></div>
      <div class="field"><label for="email">Email</label>
        <input id="email" type="email" name="email" value="{value('email')}" maxlength="255" required /></div>
      <div class="field"><label for="graduation_year">Graduation year</label>
        <input id="graduation_year" type="number" name="graduation_year" value="{value('graduation_year')}" min="1950" max="2100" required /></div>
      <div class="field"><label for="department">Department</label>
        <input id="department" type="text" name="department" value="{value('department')}" maxlength="100" required /></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button></div>
    </form>
    """
