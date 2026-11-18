from html import escape

from app.views.layout import render_page

EMPLOYMENT_TYPES_TR = {
    "full_time": "Tam zamanlı",
    "part_time": "Yarı zamanlı",
    "internship": "Staj",
    "contract": "Sözleşmeli",
}

DB_DOWN = '<p class="muted home-empty">Veriler şu an yüklenemiyor: veritabanına ulaşılamıyor.</p>'


def _stat(href: str, value: str, label: str, note: str = "") -> str:
    note_html = f'<div class="note">{note}</div>' if note else ""
    return (
        f'<a class="stat" href="{href}"><div class="num">{value}</div>'
        f'<div class="label">{label}</div>{note_html}</a>'
    )


def _stats(counts: dict | None) -> str:
    def n(key: str) -> str:
        return str(counts[key]) if counts else "&ndash;"

    open_note = f"{counts['open_job_postings']} tanesi açık" if counts else ""
    return f"""
  <section class="stats" aria-label="Site özeti">
    {_stat("/users", n("users"), "Mezun")}
    {_stat("/job-postings", n("job_postings"), "İş ilanı", open_note)}
    {_stat("/applications", n("applications"), "Başvuru")}
    {_stat("/announcements", n("announcements"), "Duyuru")}
  </section>"""


def _postings(postings: list[dict] | None) -> str:
    if postings is None:
        return DB_DOWN
    if not postings:
        return '<p class="muted home-empty">Şu an açık iş ilanı yok.</p>'
    items = []
    for p in postings:
        deadline = f"Son başvuru {p['deadline'].isoformat()}" if p["deadline"] else "Süresiz"
        kind = EMPLOYMENT_TYPES_TR.get(p["employment_type"], escape(p["employment_type"]))
        items.append(
            f'<li><a class="home-item" href="/job-postings/{p["id"]}">'
            f'<span class="home-item-title">{escape(p["title"])}</span>'
            f'<span class="home-item-meta">{escape(p["company"])} &middot; {escape(p["city"])}</span>'
            f'<span class="home-item-side"><span class="badge s-submitted">{kind}</span>'
            f'<span class="home-item-date">{deadline}</span></span></a></li>'
        )
    return f'<ul class="home-list">{"".join(items)}</ul>'


def _announcements(announcements: list[dict] | None) -> str:
    if announcements is None:
        return DB_DOWN
    if not announcements:
        return '<p class="muted home-empty">Henüz duyuru yok.</p>'
    items = "".join(
        f'<li><a class="home-item" href="/announcements/{a["id"]}">'
        f'<span class="home-item-title">{escape(a["title"])}</span>'
        f'<span class="home-item-meta">{escape(a["author"])} &middot; {a["created_at"]:%Y-%m-%d}</span></a></li>'
        for a in announcements
    )
    return f'<ul class="home-list">{items}</ul>'


def render_home(data: dict | None) -> str:
    """Home page: what the system does, live counters, newest open job postings, latest announcements
    and how it works. `data` is None when the database cannot be read; the page still opens."""
    counts = data["counts"] if data else None
    postings = data["postings"] if data else None
    announcements = data["announcements"] if data else None

    body = f"""
  <section class="hero">
    <span class="pill">İstanbul Üniversitesi &middot; YBS Mezun Ağı</span>
    <h1>Mezunlar, iş ilanları ve başvurular <span>tek yerde</span></h1>
    <p class="lead">
      Alumni Tracking System, Yönetim Bilişim Sistemleri mezunlarını kaydeder,
      bölüm duyurularını ve mezunların paylaştığı iş ilanlarını yayınlar,
      başvuruları baştan sona takip eder.
    </p>
    <div class="cta">
      <a class="btn btn-primary" href="/job-postings">Açık ilanları gör</a>
      <a class="btn btn-ghost" href="/users">Mezunlar</a>
      <a class="btn btn-ghost" href="/announcements">Duyurular</a>
    </div>
  </section>

  {_stats(counts)}

  <section class="home-grid">
    <div class="card home-card">
      <div class="home-card-head">
        <h2>Açık iş ilanları</h2>
        <a href="/job-postings">Tüm ilanlar &rarr;</a>
      </div>
      {_postings(postings)}
    </div>
    <div class="card home-card">
      <div class="home-card-head">
        <h2>Son duyurular</h2>
        <a href="/announcements">Tüm duyurular &rarr;</a>
      </div>
      {_announcements(announcements)}
    </div>
  </section>

  <section class="how">
    <h2 class="section-title">Nasıl çalışır?</h2>
    <ol class="steps">
      <li class="step">
        <span class="step-num">1</span>
        <h3>Mezunlar kaydedilir</h3>
        <p>Her mezun adı, e-postası, mezuniyet yılı ve bölümüyle sisteme eklenir.</p>
        <a href="/users">Mezunlara git &rarr;</a>
      </li>
      <li class="step">
        <span class="step-num">2</span>
        <h3>İlanlar paylaşılır</h3>
        <p>Bölüm ya da mezunlar iş ve staj ilanı paylaşır; ilan son başvuru tarihine kadar açık kalır.</p>
        <a href="/job-postings">İlanlara git &rarr;</a>
      </li>
      <li class="step">
        <span class="step-num">3</span>
        <h3>Başvurular takip edilir</h3>
        <p>Mezunlar ilanlara başvurur; başvurunun durumu incelemeden mülakata ve sonuca kadar izlenir.</p>
        <a href="/applications">Başvurulara git &rarr;</a>
      </li>
    </ol>
  </section>

  <p class="tech-strip">
    FastAPI &middot; PostgreSQL &middot; SQLAlchemy &middot; Docker
    &nbsp;|&nbsp; <a href="/api/swagger">API dokümantasyonu</a>
    &nbsp;|&nbsp; <a href="/about">Proje hakkında</a>
  </p>
"""
    return render_page("Home", body, "/")
