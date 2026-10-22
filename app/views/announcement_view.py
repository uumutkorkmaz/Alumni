from html import escape

from app.views.layout import filter_toolbar, new_button, page_header, plural, render_page, row_actions

ACTIVE = "/announcements"


def _row(a: dict) -> str:
    base = f"/announcements/{a['id']}"
    return (
        f"<tr><td>{a['id']}</td>"
        f'<td><a href="{base}">{escape(a["title"])}</a></td>'
        f"<td>{escape(a['author'])}</td><td class=\"nowrap\">{a['created_at']}</td>"
        f'<td class="col-actions">{row_actions(base, "announcement")}</td></tr>'
    )


def render_announcement_list(announcements: list[dict]) -> str:
    rows = "".join(_row(a) for a in announcements) or (
        '<tr><td class="empty" colspan="5">No announcements yet. Publish the first one below.</td></tr>'
    )

    body = f"""
    {page_header("Announcements", "News and notices for graduates.", new_button("New announcement"))}
    {filter_toolbar("announcements-table", plural(len(announcements), "announcement"))}
    <div class="table-wrap">
      <table id="announcements-table">
        <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Created</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <section class="card" id="new" style="margin-top: 32px">
      <h2>Add announcement</h2>
      {_announcement_form(action="/announcements")}
    </section>
    """
    return render_page("Announcements", body, ACTIVE)


def render_announcement_detail(announcement: dict) -> str:
    a = announcement
    body = f"""
    <article>
      <h1>{escape(a['title'])}</h1>
      <p class="meta"><span>#{a['id']}</span><span>{escape(a['author'])}</span><span>{a['created_at']}</span></p>
    </article>
    <section class="card" style="margin-top: 24px">
      <p class="content">{escape(a['content'])}</p>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/announcements/{a['id']}/edit">Edit</a>
      </div>
    </section>
    <a class="back-link" href="/announcements">&larr; Back to announcements</a>
    """
    return render_page(a["title"], body, ACTIVE, narrow=True)


def render_announcement_edit_form(announcement: dict) -> str:
    a = announcement
    body = f"""
    {page_header("Edit announcement", f"Announcement #{a['id']}")}
    <section class="card">
      {_announcement_form(action=f"/announcements/{a['id']}/edit", announcement=a)}
    </section>
    <a class="back-link" href="/announcements">&larr; Back to announcements</a>
    """
    return render_page("Edit announcement", body, ACTIVE, narrow=True)


def _announcement_form(action: str, announcement: dict | None = None) -> str:
    a = announcement or {}

    def value(key: str) -> str:
        return escape(str(a.get(key, "")))

    submit_label = "Save changes" if announcement else "Publish"
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="title">Title</label>
        <input id="title" type="text" name="title" value="{value('title')}" maxlength="200" required /></div>
      <div class="field"><label for="author">Author</label>
        <input id="author" type="text" name="author" value="{value('author')}" maxlength="100" required /></div>
      <div class="field full"><label for="content">Content</label>
        <textarea id="content" name="content" required>{value('content')}</textarea></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button></div>
    </form>
    """
