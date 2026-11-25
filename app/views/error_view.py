from html import escape

from app.views.layout import button, page_hero, render_page

# Where to send the user back to, by the first part of the path.
SECTIONS = {
    "users": ("/users", "Users"),
    "announcements": ("/announcements", "Announcements"),
    "job-postings": ("/job-postings", "Job Postings"),
    "applications": ("/applications", "Applications"),
}


def _error_head(code: int, title: str, subtitle: str, actions: str = "") -> str:
    """The compact hero of every other page; the pill carries the code (DESIGN.md §4, Error Page)."""
    return page_hero(f"Error {code}", escape(title), subtitle, actions, size="compact")


def render_server_error_page(
    status: int, title: str, reason: str, error_id: str, method: str, path: str
) -> str:
    first = path.strip("/").split("/")[0]
    section = SECTIONS.get(first)
    # A link can only repeat a GET; after a failed form (POST) go back to the list instead.
    retry_url = path if method == "GET" else (section[0] if section else "/")
    body = f"""
    {_error_head(status, title, "The server could not complete this request. This is our mistake, not yours.",
                 button("Try again", escape(retry_url), "primary") + button("Home", "/"))}
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        <dt>Reason</dt><dd>{escape(reason)}</dd>
        <dt>Error id</dt><dd><code>{escape(error_id)}</code> <span class="muted">(give this number if you report the problem)</span></dd>
        <dt>Request</dt><dd><code>{escape(method)} {escape(path)}</code></dd>
      </dl>
    </section>
    """
    return render_page(title, body, active=section[0] if section else "", narrow=True)


def render_generic_not_found_page(requested: str) -> str:
    """The generic 404 page at /404: invalid browser requests are redirected here."""
    links = "".join(
        f'<a class="btn btn-ghost btn-sm" href="{url}">{label}</a>' for url, label in SECTIONS.values()
    )
    asked = (
        f'<dt>Requested</dt><dd><code>{escape(requested)}</code></dd>'
        if requested
        else ""
    )
    body = f"""
    {_error_head(404, "Page not found", "This address does not exist on the site.",
                 button("Go to the home page", "/", "primary") + button("API documentation", "/api/swagger"))}
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        {asked}
        <dt>Reason</dt><dd>The link may be mistyped, or the page may have moved.</dd>
        <dt>Pages</dt><dd><div class="section-links">{links}</div></dd>
      </dl>
    </section>
    """
    return render_page("Page not found", body, active="", narrow=True)


def render_forbidden_page(method: str, path: str, reason: str) -> str:
    """403: signed in, but this role may not do this (ddd.md 4.1.3, auth middleware)."""
    first = path.strip("/").split("/")[0]
    section = SECTIONS.get(first)
    back = f'<a class="btn btn-ghost" href="{section[0]}">Back to {section[1]}</a>' if section else ""
    body = f"""
    {_error_head(403, "Not allowed", "You are signed in, but your role may not do this.",
                 button("Home", "/", "primary") + back)}
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        <dt>Reason</dt><dd>{escape(reason)}</dd>
        <dt>Request</dt><dd><code>{escape(method)} {escape(path)}</code></dd>
      </dl>
    </section>
    """
    return render_page("Not allowed", body, active=section[0] if section else "", narrow=True)


def render_not_found_page(method: str, path: str, reason: str) -> str:
    first = path.strip("/").split("/")[0]
    section = SECTIONS.get(first)
    back = f'<a class="btn btn-ghost" href="{section[0]}">Back to {section[1]}</a>' if section else ""
    body = f"""
    {_error_head(404, "Not found", "The page or record you asked for is not here.",
                 button("Home", "/", "primary") + back)}
    <section class="card card-featured" data-reveal>
      <dl class="dl">
        <dt>Reason</dt><dd>{escape(reason)}</dd>
        <dt>Request</dt><dd><code>{escape(method)} {escape(path)}</code></dd>
      </dl>
    </section>
    """
    return render_page("Not found", body, active=section[0] if section else "", narrow=True)
