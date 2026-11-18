from html import escape

from app.views.layout import (
    back_link,
    edit_header,
    filter_toolbar,
    form_card,
    new_button,
    page_header,
    plural,
    render_page,
    row_actions,
)

ACTIVE = "/announcements"


def _excerpt(text: str, limit: int = 110) -> str:
    """First line of the content, cut at a word boundary."""
    line = " ".join(text.split())
    if len(line) <= limit:
        return escape(line)
    return escape(line[:limit].rsplit(" ", 1)[0]) + "&hellip;"


def _row(a: dict) -> str:
    base = f"/announcements/{a['id']}"
    return (
        f'<tr><td class="id">#{a["id"]}</td>'
        f'<td><a href="{base}">{escape(a["title"])}</a><span class="excerpt">{_excerpt(a.get("content") or "")}</span></td>'
        f"<td>{escape(a['author'])}</td><td class=\"date\">{a['created_at']}</td>"
        f'<td class="col-actions">{row_actions(base, "announcement")}</td></tr>'
    )


def render_announcement_list(announcements: list[dict]) -> str:
    rows = "".join(_row(a) for a in announcements) or (
        '<tr><td class="empty" colspan="5">No announcements yet. Publish the first one below.</td></tr>'
    )

    body = f"""
    {page_header("Announcements", "News and notices for graduates.", new_button("New announcement"), kicker="Notice board", line=True)}
    {filter_toolbar("announcements-table", plural(len(announcements), "announcement"))}
    <div class="table-wrap" data-reveal>
      <table id="announcements-table">
        <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Published</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("Publish an announcement", _announcement_form(action="/announcements"), "Visible to everyone")}
    """
    return render_page("Announcements", body, ACTIVE)


def render_announcement_detail(announcement: dict) -> str:
    a = announcement
    body = f"""
    <header class="article-head">
      <span class="kicker">Announcement #{a['id']}</span>
      <h1>{escape(a['title'])}</h1>
      <p class="meta"><span>By {escape(a['author'])}</span><span class="mono">{a['created_at']}</span></p>
      <span class="faculty-line" aria-hidden="true"></span>
    </header>
    <article class="card" data-reveal>
      <p class="content prose">{escape(a['content'])}</p>
      <hr class="divider" />
      <div class="detail-actions" style="margin-top: 0">
        <a class="btn btn-primary" href="/announcements/{a['id']}/edit">Edit</a>
        <a class="btn btn-ghost" href="/announcements">All announcements</a>
      </div>
    </article>
    {back_link("/announcements", "Back to announcements")}
    """
    return render_page(a["title"], body, ACTIVE, narrow=True)


def render_announcement_edit_form(announcement: dict) -> str:
    a = announcement
    body = f"""
    {edit_header("announcement", f"Announcement #{a['id']}")}
    <section class="card card-featured">
      {_announcement_form(action=f"/announcements/{a['id']}/edit", announcement=a)}
    </section>
    {back_link(f"/announcements/{a['id']}", "Back to the announcement")}
    """
    return render_page("Edit announcement", body, ACTIVE, narrow=True)


def _announcement_form(action: str, announcement: dict | None = None) -> str:
    a = announcement or {}

    def value(key: str) -> str:
        return escape(str(a.get(key, "")))

    submit_label = "Save changes" if announcement else "Publish"
    cancel = f'<a class="btn btn-ghost" href="/announcements/{a["id"]}">Cancel</a>' if announcement else ""
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="title">Title</label>
        <input id="title" type="text" name="title" value="{value('title')}" maxlength="200" required /></div>
      <div class="field"><label for="author">Author</label>
        <input id="author" type="text" name="author" value="{value('author')}" maxlength="100" required /></div>
      <div class="field full"><label for="content">Content</label>
        <textarea id="content" name="content" rows="7" required>{value('content')}</textarea></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button>{cancel}</div>
    </form>
    """
