from html import escape

from app.views.layout import page_header, render_page

# Where to send the user back to, by the first part of the path.
SECTIONS = {
    "users": ("/users", "Users"),
    "announcements": ("/announcements", "Announcements"),
    "job-postings": ("/job-postings", "Job Postings"),
    "applications": ("/applications", "Applications"),
}


def render_server_error_page(
    status: int, title: str, reason: str, error_id: str, method: str, path: str
) -> str:
    first = path.strip("/").split("/")[0]
    section = SECTIONS.get(first)
    # A link can only repeat a GET; after a failed form (POST) go back to the list instead.
    retry_url = path if method == "GET" else (section[0] if section else "/")
    body = f"""
    {page_header(f"{status} · {escape(title)}", "The server could not complete this request.")}
    <section class="card">
      <dl class="dl">
        <dt>Reason</dt><dd>{escape(reason)}</dd>
        <dt>Error id</dt><dd><code>{escape(error_id)}</code> (give this number if you report the problem)</dd>
        <dt>Request</dt><dd><code>{escape(method)} {escape(path)}</code></dd>
      </dl>
      <div class="detail-actions">
        <a class="btn btn-primary" href="{escape(retry_url)}">Try again</a>
        <a class="btn btn-ghost" href="/">Home</a>
      </div>
    </section>
    """
    return render_page(title, body, active=section[0] if section else "", narrow=True)


def render_generic_not_found_page(requested: str) -> str:
    """The generic 404 page at /404: invalid browser requests are redirected here."""
    links = "".join(
        f'<a class="btn btn-ghost" href="{url}">{label}</a>' for url, label in SECTIONS.values()
    )
    asked = (
        f'<p class="muted" style="margin-bottom: 16px">You asked for <code>{escape(requested)}</code>.</p>'
        if requested
        else ""
    )
    body = f"""
    {page_header("404 · Page not found", "This address does not exist on the site.")}
    <section class="card">
      {asked}
      <p>The link may be mistyped, or the page may have moved. These pages exist:</p>
      <div class="detail-actions">{links}</div>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/">Go to the home page</a>
        <a class="btn btn-ghost" href="/api/swagger">API documentation</a>
      </div>
    </section>
    """
    return render_page("Page not found", body, active="", narrow=True)


def render_not_found_page(method: str, path: str, reason: str) -> str:
    first = path.strip("/").split("/")[0]
    section = SECTIONS.get(first)
    back = f'<a class="btn btn-ghost" href="{section[0]}">Back to {section[1]}</a>' if section else ""
    body = f"""
    {page_header("404 · Not found", "The page or record you asked for is not here.")}
    <section class="card">
      <dl class="dl">
        <dt>Reason</dt><dd>{escape(reason)}</dd>
        <dt>Request</dt><dd><code>{escape(method)} {escape(path)}</code></dd>
      </dl>
      <div class="detail-actions">
        <a class="btn btn-primary" href="/">Home</a>
        {back}
      </div>
    </section>
    """
    return render_page("Not found", body, active=section[0] if section else "", narrow=True)
