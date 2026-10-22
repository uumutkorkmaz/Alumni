from html import escape

NAV_LINKS = [
    ("/", "Home"),
    ("/about", "About"),
    ("/users", "Users"),
    ("/announcements", "Announcements"),
    ("/job-postings", "Job Postings"),
    ("/applications", "Applications"),
    ("/docs", "API Docs"),
]

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%2338bdf8'/%3E%3Ctext x='16' y='22' font-size='15' "
    "font-weight='800' text-anchor='middle' fill='%230b1120' font-family='Arial'%3EAT%3C/text%3E%3C/svg%3E"
)

# Two small behaviours shared by every page: live filtering of a table by the text typed in an
# <input data-filter="table-id">. (Delete confirmations are inline onsubmit handlers on the forms.)
SCRIPT = """
<script>
document.querySelectorAll('input[data-filter]').forEach(function (input) {
  var table = document.getElementById(input.dataset.filter);
  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    table.querySelectorAll('tbody tr').forEach(function (row) {
      row.hidden = q !== '' && row.textContent.toLowerCase().indexOf(q) === -1;
    });
  });
});
</script>
"""


def render_nav(active: str) -> str:
    active_attr = ' class="active" aria-current="page"'
    links = "".join(
        f'<a href="{href}"{active_attr if href == active else ""}>{label}</a>' for href, label in NAV_LINKS
    )
    return f"""
  <header class="site-nav">
    <div class="nav-inner">
      <a class="brand" href="/"><span class="brand-mark">AT</span>Alumni Tracking</a>
      <nav class="nav-links" aria-label="Main">{links}</nav>
    </div>
  </header>"""


def render_page(title: str, body: str, active: str, narrow: bool = False) -> str:
    """Full HTML page: shared navbar, stylesheet, footer. `title` is plain text (escaped here)."""
    width = " narrow" if narrow else ""
    page_title = "Alumni Tracking System" if title == "Home" else f"{escape(title)} · Alumni Tracking"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0b1120" />
  <title>{page_title}</title>
  <link rel="icon" href="{FAVICON}" />
  <link rel="stylesheet" href="/static/app.css" />
</head>
<body>
  {render_nav(active)}
  <main class="container{width}">
    {body}
  </main>
  <footer class="site-footer">YBSB3001 &mdash; Web Programming</footer>
  {SCRIPT}
</body>
</html>"""


def page_header(title: str, subtitle: str = "", action_html: str = "") -> str:
    """Page title with an optional line of text under it and an optional button on the right."""
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    return f'<div class="page-header"><div><h1>{title}</h1>{sub}</div>{action_html}</div>'


def new_button(label: str) -> str:
    """Button that scrolls to the create form (the form card has id="new")."""
    return f'<a class="btn btn-primary" href="#new">+ {escape(label)}</a>'


def delete_form(action: str, what: str) -> str:
    """Small delete button; the browser asks for confirmation before the POST is sent."""
    return (
        f'<form class="inline-form" method="post" action="{action}" '
        f'onsubmit="return confirm(\'Delete this {what}? This cannot be undone.\')">'
        f'<button type="submit" class="btn btn-danger btn-sm">Delete</button></form>'
    )


def row_actions(base: str, what: str) -> str:
    """Edit / Delete buttons for a table row (the row's title is already a link to the detail page).
    `base` is e.g. /users/3."""
    return (
        '<div class="row-actions">'
        f'<a class="btn btn-ghost btn-sm" href="{base}/edit">Edit</a>'
        f"{delete_form(base + '/delete', what)}"
        "</div>"
    )


def filter_toolbar(table_id: str, count_text: str) -> str:
    """Row above a table: how many rows there are, and a box that filters them as you type."""
    return (
        '<div class="toolbar">'
        f'<span class="count">{count_text}</span>'
        f'<input class="filter" type="search" placeholder="Filter this list..." '
        f'aria-label="Filter this list" data-filter="{table_id}" />'
        "</div>"
    )


def alert(message: str | None) -> str:
    return f'<div class="alert alert-error" role="alert">{escape(message)}</div>' if message else ""


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"
