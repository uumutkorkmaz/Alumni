from html import escape

from datetime import date

from app.views.layout import (
    back_link,
    button,
    edit_header,
    filter_toolbar,
    form_card,
    new_button,
    page_hero,
    plural,
    render_page,
    row_actions,
    stat_tiles,
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


def render_announcement_list(announcements: list[dict], authors: list[dict]) -> str:
    rows = "".join(_row(a) for a in announcements) or (
        '<tr><td class="empty" colspan="5">No announcements yet. Publish the first one below.</td></tr>'
    )

    this_year = str(date.today().year)
    latest = max((a["created_at"] for a in announcements), default="")
    stats = stat_tiles([
        ("Announcements", len(announcements), "", ""),
        (f"In {this_year}", sum(1 for a in announcements if a["created_at"].startswith(this_year)), "", ""),
        ("Authors", len({a["author"] for a in announcements}), "", ""),
        ("Latest", latest[:10] or "&ndash;", "", ""),
    ], "Announcements in numbers")

    body = f"""
    {page_hero(
        "Notice board",
        "News for <em>graduates</em>",
        "Announcements from the department and the faculty: news, events and notices for MIS graduates.",
        new_button("New announcement") + button("Job postings", "/job-postings"),
    )}
    {stats}
    {filter_toolbar("announcements-table", plural(len(announcements), "announcement"))}
    <div class="table-wrap" data-reveal>
      <table id="announcements-table">
        <thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Published</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    {form_card("Publish an announcement", _announcement_form("/announcements", authors), "Visible to everyone")}
    """
    return render_page("Announcements", body, ACTIVE)


def render_announcement_detail(announcement: dict) -> str:
    a = announcement
    body = f"""
    {page_hero(
        f"Announcement #{a['id']}",
        escape(a['title']),
        "",
        button("Edit", f"/announcements/{a['id']}/edit", "primary") + button("All announcements", "/announcements"),
        meta=f'<span>By {escape(a["author"])}</span><span class="mono">{a["created_at"]}</span>',
        size="compact",
    )}
    <article class="card card-featured" data-reveal>
      <p class="content prose">{escape(a['content'])}</p>
    </article>
    {back_link("/announcements", "Back to announcements")}
    """
    return render_page(a["title"], body, ACTIVE, narrow=True)


def render_announcement_edit_form(announcement: dict, authors: list[dict]) -> str:
    a = announcement
    body = f"""
    {edit_header("announcement", f"Announcement #{a['id']}")}
    <section class="card card-featured">
      {_announcement_form(f"/announcements/{a['id']}/edit", authors, a)}
    </section>
    {back_link(f"/announcements/{a['id']}", "Back to the announcement")}
    """
    return render_page("Edit announcement", body, ACTIVE, narrow=True)


def _announcement_form(action: str, authors: list[dict], announcement: dict | None = None) -> str:
    a = announcement or {}

    def value(key: str) -> str:
        return escape(str(a.get(key, "")))

    author_options = "".join(
        f'<option value="{u["id"]}"{" selected" if u["id"] == a.get("author_id") else ""}>'
        f'{escape(u["name"])} ({u["role"]})</option>'
        for u in authors
    ) or '<option value="" disabled selected>No academic, staff or admin account yet</option>'
    submit_label = "Save changes" if announcement else "Publish"
    cancel = f'<a class="btn btn-ghost" href="/announcements/{a["id"]}">Cancel</a>' if announcement else ""
    return f"""
    <form class="form-grid" method="post" action="{action}">
      <div class="field"><label for="title">Title</label>
        <input id="title" type="text" name="title" value="{value('title')}" maxlength="200" required /></div>
      <div class="field"><label for="author_id">Author (academic, staff or admin)</label>
        <select id="author_id" name="author_id" required>{author_options}</select></div>
      <div class="field full"><label for="content">Content</label>
        <textarea id="content" name="content" rows="7" required>{value('content')}</textarea></div>
      <div class="form-actions"><button type="submit" class="btn btn-primary">{submit_label}</button>{cancel}</div>
    </form>
    """
