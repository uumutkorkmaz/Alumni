PAGE_STYLE = """
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           background: #0b1120; color: #e2e8f0; margin: 0; padding: 40px 24px; }
    .wrap { max-width: 720px; margin: 0 auto; }
    h1 { margin-bottom: 24px; }
    a { color: #38bdf8; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 32px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #24314f; font-size: 14px; }
    th { color: #94a3b8; font-weight: 600; }
    form { display: grid; gap: 10px; max-width: 360px; }
    .inline-form { display: inline; margin: 0; }
    label { font-size: 13px; color: #94a3b8; }
    input { padding: 8px 10px; border-radius: 6px; border: 1px solid #24314f;
            background: #151f38; color: #e2e8f0; }
    button { padding: 6px 12px; border-radius: 8px; border: none;
             background: linear-gradient(120deg, #38bdf8, #a78bfa); color: #0b1120;
             font-weight: 600; cursor: pointer; }
    form.actions { display: flex; gap: 8px; max-width: none; }
    .danger { background: #f87171; }
    dl { display: grid; grid-template-columns: 160px 1fr; gap: 10px 16px; margin-bottom: 24px; }
    dt { color: #94a3b8; font-size: 13px; }
  </style>
"""


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  {PAGE_STYLE}
</head>
<body>
  <div class="wrap">
    {body}
  </div>
</body>
</html>"""


def render_user_list(users: list[dict]) -> str:
    rows = "".join(
        f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td>"
        f"<td>{u['graduation_year']}</td><td>{u['department']}</td>"
        f"<td>"
        f'<a href="/users/{u["id"]}">View</a> | '
        f'<a href="/users/{u["id"]}/edit">Edit</a> | '
        f'<form class="inline-form" method="post" action="/users/{u["id"]}/delete">'
        f'<button type="submit" class="danger">Delete</button></form>'
        f"</td></tr>"
        for u in users
    )
    if not rows:
        rows = '<tr><td colspan="6">No users yet.</td></tr>'

    body = f"""
    <h1>Users</h1>
    <table>
      <tr><th>ID</th><th>Name</th><th>Email</th><th>Graduation Year</th><th>Department</th><th>Actions</th></tr>
      {rows}
    </table>

    <h1>Add User</h1>
    {_user_form(action="/users")}
    """
    return _page("Users", body)


def render_user_detail(user: dict) -> str:
    body = f"""
    <h1>User #{user['id']}</h1>
    <dl>
      <dt>Name</dt><dd>{user['name']}</dd>
      <dt>Email</dt><dd>{user['email']}</dd>
      <dt>Graduation Year</dt><dd>{user['graduation_year']}</dd>
      <dt>Department</dt><dd>{user['department']}</dd>
    </dl>
    <a href="/users/{user['id']}/edit">Edit</a> |
    <a href="/users">Back to list</a>
    """
    return _page(f"User #{user['id']}", body)


def render_user_edit_form(user: dict) -> str:
    body = f"""
    <h1>Edit User #{user['id']}</h1>
    {_user_form(action=f"/users/{user['id']}/edit", user=user)}
    <p><a href="/users">Back to list</a></p>
    """
    return _page(f"Edit User #{user['id']}", body)


def _user_form(action: str, user: dict | None = None) -> str:
    name = user["name"] if user else ""
    email = user["email"] if user else ""
    graduation_year = user["graduation_year"] if user else ""
    department = user["department"] if user else ""
    submit_label = "Save" if user else "Create"

    return f"""
    <form method="post" action="{action}">
      <label>Name</label>
      <input type="text" name="name" value="{name}" required />
      <label>Email</label>
      <input type="email" name="email" value="{email}" required />
      <label>Graduation Year</label>
      <input type="number" name="graduation_year" value="{graduation_year}" required />
      <label>Department</label>
      <input type="text" name="department" value="{department}" required />
      <button type="submit">{submit_label}</button>
    </form>
    """
