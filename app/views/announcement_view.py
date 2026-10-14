from html import escape

from app.views.layout import NAV_STYLE, render_nav
from app.views.user_view import PAGE_STYLE

EXTRA_STYLE = """
  <style>
    textarea { padding: 8px 10px; border-radius: 6px; border: 1px solid #24314f;
               background: #151f38; color: #e2e8f0; min-height: 100px; font-family: inherit; }
    .content { white-space: pre-wrap; line-height: 1.6; }
    .meta { color: #94a3b8; font-size: 13px; margin-bottom: 16px; }
  </style>
"""


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(title)}</title>
  {PAGE_STYLE}
  {EXTRA_STYLE}
  {NAV_STYLE}
</head>
<body>
  {render_nav("/announcements")}
  <div class="wrap">
    {body}
  </div>
</body>
</html>"""


def render_announcement_list(announcements: list[dict]) -> str:
    rows = "".join(
        f"<tr><td>{a['id']}</td><td>{escape(a['title'])}</td><td>{escape(a['author'])}</td>"
        f"<td>{a['created_at']}</td>"
        f"<td>"
        f'<a href="/announcements/{a["id"]}">View</a> | '
        f'<a href="/announcements/{a["id"]}/edit">Edit</a> | '
        f'<form class="inline-form" method="post" action="/announcements/{a["id"]}/delete">'
        f'<button type="submit" class="danger">Delete</button></form>'
        f"</td></tr>"
        for a in announcements
    )
    if not rows:
        rows = '<tr><td colspan="5">No announcements yet.</td></tr>'

    body = f"""
    <h1>Announcements</h1>
    <table>
      <tr><th>ID</th><th>Title</th><th>Author</th><th>Created</th><th>Actions</th></tr>
      {rows}
    </table>

    <h1>Add Announcement</h1>
    {_announcement_form(action="/announcements")}
    """
    return _page("Announcements", body)


def render_announcement_detail(announcement: dict) -> str:
    a = announcement
    body = f"""
    <h1>{escape(a['title'])}</h1>
    <p class="meta">#{a['id']} &middot; {escape(a['author'])} &middot; {a['created_at']}</p>
    <p class="content">{escape(a['content'])}</p>
    <p>
      <a href="/announcements/{a['id']}/edit">Edit</a> |
      <a href="/announcements">Back to list</a>
    </p>
    """
    return _page(a["title"], body)


def render_announcement_edit_form(announcement: dict) -> str:
    a = announcement
    body = f"""
    <h1>Edit Announcement #{a['id']}</h1>
    {_announcement_form(action=f"/announcements/{a['id']}/edit", announcement=a)}
    <p><a href="/announcements">Back to list</a></p>
    """
    return _page(f"Edit Announcement #{a['id']}", body)


def _announcement_form(action: str, announcement: dict | None = None) -> str:
    title = escape(announcement["title"]) if announcement else ""
    content = escape(announcement["content"]) if announcement else ""
    author = escape(announcement["author"]) if announcement else ""
    submit_label = "Save" if announcement else "Create"

    return f"""
    <form method="post" action="{action}">
      <label>Title</label>
      <input type="text" name="title" value="{title}" required />
      <label>Content</label>
      <textarea name="content" required>{content}</textarea>
      <label>Author</label>
      <input type="text" name="author" value="{author}" required />
      <button type="submit">{submit_label}</button>
    </form>
    """
