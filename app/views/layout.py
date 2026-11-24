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
// Filter: <input data-filter="id1 id2"> hides the table rows / album cards ([data-filter-item]) of
// those elements whose text does not contain what was typed.
document.querySelectorAll('input[data-filter]').forEach(function (input) {
  var targets = input.dataset.filter.split(' ').map(function (id) { return document.getElementById(id); });
  input.addEventListener('input', function () {
    var q = input.value.trim().toLocaleLowerCase('tr');
    targets.forEach(function (target) {
      if (!target) return;
      target.querySelectorAll('tbody tr, [data-filter-item]').forEach(function (row) {
        row.hidden = q !== '' && row.textContent.toLocaleLowerCase('tr').indexOf(q) === -1;
      });
    });
  });
});

// View switch: buttons [data-view="album|table"] inside [data-views] show one of the elements named
// in their data-target and hide the other. The choice is remembered in this browser only.
document.querySelectorAll('[data-views]').forEach(function (group) {
  var buttons = group.querySelectorAll('[data-view]');
  function show(view) {
    buttons.forEach(function (b) {
      var on = b.dataset.view === view;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      document.getElementById(b.dataset.target).hidden = !on;
    });
    try { localStorage.setItem('view:' + location.pathname, view); } catch (e) {}
  }
  buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.dataset.view); }); });
  var saved = null;
  try { saved = localStorage.getItem('view:' + location.pathname); } catch (e) {}
  if (saved && group.querySelector('[data-view="' + saved + '"]')) show(saved);
  group.hidden = false;
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

  // Scroll film (home page, desktop only): a frame sequence drawn on a canvas. The scroll position
  // inside the section picks the frame; the shown position eases toward it and two neighbouring frames
  // are blended, so the motion stays smooth between frames. Frames load coarse first (every 16th,
  // then every 8th, ...), so scrolling works at once and gets finer while the rest arrives.
  var film = document.querySelector('[data-film]');
  if (film && window.matchMedia('(min-width: 900px)').matches && film.querySelector('canvas').getContext) {
    var canvas = film.querySelector('canvas'), ctx = canvas.getContext('2d');
    var steps = film.querySelectorAll('.film-step');
    var bar = film.querySelector('.film-progress span');
    var count = Number(film.dataset.frames), pattern = film.dataset.src;
    // 1920px frames only where they show: a canvas wider than 1400 device pixels (large or sharp
    // screens). Smaller screens take the 1280px set and download about 40 % less.
    var set = canvas.clientWidth * Math.min(window.devicePixelRatio || 1, 2) > 1400 ? '1080' : '720';
    var frames = new Array(count), loaded = new Array(count);
    var pos = 0, target = 0, drawn = -1, inView = true, ticking = false;
    var lastScroll = 0, idleTimer = 0, IDLE_MS = 140;
    film.classList.add('film--live');

    function url(i) { return pattern.replace('{set}', set).replace('{n}', String(i + 1).padStart(3, '0')); }
    var order = [], seen = {};
    [16, 8, 4, 2, 1].forEach(function (stride) {
      for (var i = 0; i < count; i += stride) if (!seen[i]) { seen[i] = 1; order.push(i); }
    });
    if (!seen[count - 1]) order.splice(1, 0, count - 1);   // the last frame early, too
    var next = 0, active = 0;
    function loadMore() {
      while (active < 6 && next < order.length) {
        (function (i) {
          var img = new Image();
          img.decoding = 'async';
          active++;
          img.onload = function () {
            (img.decode ? img.decode() : Promise.resolve()).catch(function () {}).then(function () {
              frames[i] = img; loaded[i] = true; active--;
              if (i === 0) { resize(); film.classList.add('film--ready'); }
              drawn = -1; schedule(); loadMore();
            });
          };
          img.onerror = function () { active--; loadMore(); };
          img.src = url(i);
        })(order[next++]);
      }
    }
    loadMore();

    function nearest(i) {
      for (var d = 0; d < count; d++) {
        if (i - d >= 0 && loaded[i - d]) return frames[i - d];
        if (i + d < count && loaded[i + d]) return frames[i + d];
      }
      return null;
    }
    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(canvas.clientWidth * dpr);
      canvas.height = Math.round(canvas.clientHeight * dpr);
      drawn = -1;
    }
    function cover(img, alpha) {
      var cw = canvas.width, ch = canvas.height, iw = img.naturalWidth, ih = img.naturalHeight;
      var scale = Math.max(cw / iw, ch / ih), w = iw * scale, h = ih * scale;
      ctx.globalAlpha = alpha;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';                 // best scaling when the frame is enlarged
      ctx.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
    }
    function draw() {
      var i = Math.floor(pos), frac = pos - i;
      var a = nearest(i), b = nearest(Math.min(count - 1, i + 1));
      if (!a) return;
      cover(a, 1);
      if (b && b !== a && frac > 0.02 && frac < 0.98) cover(b, frac);
      else if (b && frac >= 0.98) cover(b, 1);
      ctx.globalAlpha = 1;
      drawn = pos;
    }
    function progress() {
      var r = film.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      return total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
    }
    function tick() {
      ticking = false;
      var p = progress();
      target = p * (count - 1);
      // Blending two frames keeps motion smooth, but a still blend looks like a double image.
      // Once the scroll has stopped, settle on the nearest whole frame (at most half a frame away).
      if (performance.now() - lastScroll > IDLE_MS) target = Math.round(target);
      steps.forEach(function (s) {
        s.classList.toggle('is-active', p >= Number(s.dataset.from) && p < Number(s.dataset.to));
      });
      if (bar) bar.style.transform = 'scaleX(' + p + ')';
      pos += (target - pos) * 0.18;                       // gentle inertia
      if (Math.abs(target - pos) < 0.01) pos = target;
      if (pos !== drawn) draw();
      if (inView && pos !== target) schedule();
    }
    function schedule() { if (!ticking) { ticking = true; requestAnimationFrame(tick); } }
    window.addEventListener('scroll', function () {
      lastScroll = performance.now();
      schedule();
      clearTimeout(idleTimer);
      idleTimer = setTimeout(schedule, IDLE_MS + 20);     // wake up once more to settle on a whole frame
    }, { passive: true });
    window.addEventListener('resize', function () { resize(); schedule(); });
    new IntersectionObserver(function (e) { inView = e[0].isIntersecting; if (inView) schedule(); }).observe(film);
    schedule();
  }

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


def render_page(
    title: str, body: str, active: str, narrow: bool = False, lang: str = "en", full_width: str = ""
) -> str:
    """Full HTML page: shared navbar, fonts, stylesheet, footer and script.
    `title` is plain text (escaped here). `lang="tr"` for Turkish pages, so upper-case labels write İ.
    `full_width` is HTML placed edge to edge between the navbar and the page container (the home film)."""
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
  {full_width}
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


def page_hero(
    pill: str, title: str, lead: str = "", actions: str = "", meta: str = "", size: str = "page"
) -> str:
    """The home page hero, for every other page (DESIGN.md §5, Page patterns): the ledger grid behind,
    a gold pill, a large serif title (wrap one phrase in <em> for the gold italic), the Faculty Line,
    a lead and the page's buttons, all centred. `size` is "page" (lists, About) or "compact" (details,
    edit and error pages). All arguments are HTML: escape user data before passing it."""
    meta_html = f'<p class="meta">{meta}</p>' if meta else ""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    cta = f'<div class="cta">{actions}</div>' if actions else ""
    return (
        f'<section class="hero hero--{size}">'
        f'<span class="pill">{pill}</span>'
        f"<h1>{title}</h1>{meta_html}"
        '<span class="faculty-line" aria-hidden="true"></span>'
        f"{lead_html}{cta}"
        "</section>"
    )


def button(label: str, href: str, kind: str = "ghost", arrow: bool = False) -> str:
    """A link styled as a button. `label` is HTML."""
    tail = ' <span class="arrow" aria-hidden="true">&rarr;</span>' if arrow else ""
    return f'<a class="btn btn-{kind}" href="{href}">{label}{tail}</a>'


def stat_tiles(items: list[tuple], label: str = "Summary") -> str:
    """The home page counter tiles. Each item is (label, value, href, note[, counts]); href and note may
    be "". A whole-number value counts up from 0 when the tile comes into view (pass counts=False for a
    year, which should not count); a text value (a span, a word) is shown as it is, in a smaller size.
    Tiles with a link lift under the pointer."""
    tiles = []
    for item in items:
        name, value, href, note, counts = (list(item) + ["", "", True])[:5]
        value = str(value)
        number = value.isdigit()
        if number and not counts:
            number = False
        count = f' data-count="{value}"' if number else ""
        num_class = "num" if number else "num num-text"
        note_html = f'<div class="note">{note}</div>' if note else ""
        inner = f'<div class="label">{name}</div><div class="{num_class}"{count}>{value}</div>{note_html}'
        if href:
            tiles.append(f'<a class="stat" href="{href}" data-reveal>{inner}</a>')
        else:
            tiles.append(f'<div class="stat" data-reveal>{inner}</div>')
    return f'<section class="stats" aria-label="{label}">{"".join(tiles)}</section>'


def section_head(title: str, label: str = "", link: tuple | None = None) -> str:
    """A section title as on the home page: serif heading, and on the right a mono label or an arrow link
    given as (text, href)."""
    right = f'<span class="label-mono">{label}</span>' if label else ""
    if link:
        right = (
            f'<a class="link-arrow" href="{link[1]}">{link[0]} '
            '<span class="arrow" aria-hidden="true">&rarr;</span></a>'
        )
    return f'<div class="section-head"><h2>{title}</h2>{right}</div>'


def edit_header(what: str, record: str) -> str:
    """Header of an edit page: the compact hero, its pill saying which record is being changed."""
    return page_hero(
        f"Editing &middot; {record}",
        f"Edit <em>{what}</em>",
        "Change the fields and save. Nothing changes until you press Save changes.",
        size="compact",
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


def filter_toolbar(table_id: str, count_text: str, extra_html: str = "") -> str:
    """Row above a table: how many rows there are, and a box that filters them as you type.
    `table_id` may name several elements, separated by spaces (e.g. an album and a table)."""
    return (
        '<div class="toolbar">'
        f'<span class="count">{count_text}</span>'
        '<div class="toolbar-right">'
        f"{extra_html}"
        f'<input class="filter" type="search" placeholder="Filter this list..." '
        f'aria-label="Filter this list" data-filter="{table_id}" />'
        "</div></div>"
    )


def alert(message: str | None) -> str:
    return f'<div class="alert alert-error" role="alert">{escape(message)}</div>' if message else ""


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"
