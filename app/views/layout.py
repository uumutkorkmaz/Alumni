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

# The AT mark (brand.md §3): Istanbul University green, Midnight Ink letters, a gold hairline.
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect x='.5' y='.5' width='31' height='31' rx='8.5' fill='%23439c86' stroke='%23b8860b' stroke-opacity='.6'/%3E"
    "%3Ctext x='16' y='21' font-size='13' font-weight='700' text-anchor='middle' fill='%230d1614' "
    "font-family='Arial'%3EAT%3C/text%3E%3C/svg%3E"
)

# Source Serif 4 (headings, numbers), Inter (interface), IBM Plex Mono (labels, ids). See DESIGN.md §3.
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@'
    "0,8..60,500;0,8..60,600;1,8..60,500&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500"
    '&display=swap" />'
)

# Behaviours shared by every page:
# 1. live filtering of a table by the text typed in an <input data-filter="table-id">;
# 2. scroll reveal: elements with data-reveal fade up once when they come into view (DESIGN.md §7);
# 3. count-up: numbers with data-count count from 0 when they come into view.
# Everything stays visible if the script never runs, and nothing moves under prefers-reduced-motion.
# (Delete confirmations are inline onsubmit handlers on the forms.)
SCRIPT = """
<script>
document.querySelectorAll('input[data-filter]').forEach(function (input) {
  var table = document.getElementById(input.dataset.filter);
  input.addEventListener('input', function () {
    var q = input.value.trim().toLocaleLowerCase('tr');
    table.querySelectorAll('tbody tr').forEach(function (row) {
      row.hidden = q !== '' && row.textContent.toLocaleLowerCase('tr').indexOf(q) === -1;
    });
  });
});

(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;

  function countUp(el) {
    var end = Number(el.dataset.count), t0 = performance.now(), dur = 900;
    if (!isFinite(end) || end <= 0) return;
    function tick(t) {
      var p = Math.min((t - t0) / dur, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 4)));
      if (p < 1) requestAnimationFrame(tick);
    }
    el.textContent = '0';
    requestAnimationFrame(tick);
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      e.target.querySelectorAll('[data-count]').forEach(countUp);
      io.unobserve(e.target);
    });
  }, { threshold: 0.15 });

  var groups = {};
  document.querySelectorAll('[data-reveal]').forEach(function (el) {
    var g = el.parentElement;
    var key = g.dataset.revealKey || (g.dataset.revealKey = String(Object.keys(groups).length));
    var i = groups[key] = (groups[key] === undefined ? 0 : groups[key] + 1);
    el.style.setProperty('--i', Math.min(i, 6));
    el.classList.add('reveal');
    io.observe(el);
  });
})();
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
      <a class="brand" href="/" aria-label="Alumni Tracking, home">
        <span class="brand-mark" aria-hidden="true">AT</span>
        <span class="brand-name"><b>Alumni Tracking</b><small>İÜ &middot; İKTİSAT &middot; YBS</small></span>
      </a>
      <nav class="nav-links" aria-label="Main">{links}</nav>
    </div>
  </header>"""


def render_page(title: str, body: str, active: str, narrow: bool = False, lang: str = "en") -> str:
    """Full HTML page: shared navbar, fonts, stylesheet, footer and script.
    `title` is plain text (escaped here). `lang="tr"` for Turkish pages, so upper-case labels write İ."""
    width = " narrow" if narrow else ""
    page_title = "Alumni Tracking System" if title == "Home" else f"{escape(title)} · Alumni Tracking"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0d1614" />
  <title>{page_title}</title>
  <link rel="icon" href="{FAVICON}" />
  {FONTS}
  <link rel="stylesheet" href="/static/app.css" />
</head>
<body>
  {render_nav(active)}
  <main class="container{width}">
    {body}
  </main>
  <footer class="site-footer">
    <span lang="en">YBSB3001 &mdash; Web Programming</span>
    <span lang="tr">İstanbul Üniversitesi &middot; İktisat Fakültesi &middot; Yönetim Bilişim Sistemleri</span>
  </footer>
  {SCRIPT}
</body>
</html>"""


def page_header(title: str, subtitle: str = "", action_html: str = "", kicker: str = "", line: bool = False) -> str:
    """Page title with an optional mono label above it, a line of text under it, the Faculty Line
    and a button on the right. `title`, `subtitle` and `kicker` are HTML (escape user data first)."""
    kick = f'<span class="kicker">{kicker}</span>' if kicker else ""
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    rule = '<span class="faculty-line" aria-hidden="true"></span>' if line else ""
    return f'<div class="page-header"><div>{kick}<h1>{title}</h1>{sub}{rule}</div>{action_html}</div>'


def edit_header(what: str, record: str) -> str:
    """Header of an edit page: a gold kicker ("Editing · User #3") marks that a record is being changed."""
    return (
        '<div class="page-header edit-head"><div>'
        f'<span class="kicker">Editing &middot; {record}</span>'
        f"<h1>Edit {what}</h1>"
        '<p class="subtitle">Change the fields and save. Nothing changes until you press Save changes.</p>'
        "</div></div>"
    )


def new_button(label: str) -> str:
    """Button that scrolls to the create form (the form card has id="new")."""
    return f'<a class="btn btn-primary" href="#new"><span aria-hidden="true">+</span> {escape(label)}</a>'


def back_link(href: str, label: str) -> str:
    return f'<a class="back-link" href="{href}"><span aria-hidden="true">&larr;</span> {escape(label)}</a>'


def form_card(title: str, inner: str, note: str = "", card_id: str = "new") -> str:
    """The create form under a list: a featured card with the Faculty Line on its top edge."""
    side = f'<span class="label-mono">{note}</span>' if note else ""
    return (
        f'<section class="card card-featured form-card" id="{card_id}" data-reveal>'
        f'<div class="card-head"><h2>{title}</h2>{side}</div>{inner}</section>'
    )


def initials(name: str) -> str:
    """Up to two initials for the avatar circle ("Ayşe Yılmaz" -> "AY")."""
    parts = [p for p in name.split() if p]
    letters = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")) if parts else "?"
    return escape(letters.upper())


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
