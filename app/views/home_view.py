from html import escape

from app.views.layout import render_page

EMPLOYMENT_TYPES_TR = {
    "full_time": "Tam zamanlı",
    "part_time": "Yarı zamanlı",
    "internship": "Staj",
    "contract": "Sözleşmeli",
}

# Two sets of the same 160 frames: frames/1080/ (1920x1080) for large or sharp screens, frames/720/
# (1280x720) for the rest. The page script picks one by the canvas size in device pixels.
FILM_FRAMES = 160  # f001.webp ... f160.webp in each set

DB_DOWN = '<p class="muted home-empty">Veriler şu an yüklenemiyor: veritabanına ulaşılamıyor.</p>'


def _stat(href: str, value: str, label: str, note: str = "") -> str:
    """A linked counter tile; the number counts up once when the tile comes into view."""
    note_html = f'<div class="note">{note}</div>' if note else ""
    count = f' data-count="{value}"' if value.isdigit() else ""
    return (
        f'<a class="stat" href="{href}" data-reveal><div class="label">{label}</div>'
        f'<div class="num"{count}>{value}</div>{note_html}</a>'
    )


def _stats(counts: dict | None) -> str:
    def n(key: str) -> str:
        return str(counts[key]) if counts else "&ndash;"

    open_note = f"{counts['open_job_postings']} tanesi açık" if counts else ""
    return f"""
  <section class="stats" aria-label="Site özeti">
    {_stat("/users", n("users"), "Mezunlar")}
    {_stat("/job-postings", n("job_postings"), "İş ilanları", open_note)}
    {_stat("/applications", n("applications"), "Başvurular")}
    {_stat("/announcements", n("announcements"), "Duyurular")}
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
            f'<span class="home-item-side"><span class="badge info">{kind}</span>'
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

    # The scroll film (DESIGN.md §7): the campus walk from Beyazıt Square through the main gate to the
    # Rectorate plays forward as the page is scrolled, drawn frame by frame on a canvas (160 WebP frames).
    # Desktop only: on small screens, without JavaScript or under reduced motion it is a still picture
    # (the first frame) with the first caption.
    film = f"""
  <section class="film" data-film data-frames="{FILM_FRAMES}" data-src="/static/film/frames/{{set}}/f{{n}}.webp"
           aria-label="İstanbul Üniversitesi: ana kapıdan Rektörlüğe">
    <div class="film-stage">
      <img class="film-poster" src="/static/film/frames/720/f001.webp"
           srcset="/static/film/frames/720/f001.webp 1280w, /static/film/frames/1080/f001.webp 1920w"
           sizes="100vw" alt="" />
      <canvas class="film-canvas" aria-hidden="true"></canvas>
      <div class="film-shade" aria-hidden="true"></div>

      <div class="film-step hero is-active" data-from="0" data-to="0.3">
        <span class="pill">İstanbul Üniversitesi &middot; İktisat Fakültesi &middot; YBS</span>
        <h1>Mezunlar, iş ilanları ve başvurular <em>tek yerde</em></h1>
        <span class="faculty-line" aria-hidden="true"></span>
        <p class="lead">
          Alumni Tracking System, Yönetim Bilişim Sistemleri mezunlarını kaydeder,
          bölüm duyurularını ve mezunların paylaştığı iş ilanlarını yayınlar,
          başvuruları baştan sona takip eder.
        </p>
        <div class="cta">
          <a class="btn btn-primary" href="/job-postings">Açık ilanları gör <span class="arrow" aria-hidden="true">&rarr;</span></a>
          <a class="btn btn-ghost" href="/users">Mezunlar</a>
          <a class="btn btn-ghost" href="/announcements">Duyurular</a>
        </div>
        <span class="film-cue" aria-hidden="true">Kaydırın: kapıdan içeri girin</span>
      </div>

      <div class="film-step" data-from="0.36" data-to="0.66" aria-hidden="true">
        <span class="kicker">Beyazıt &middot; Ana kapı</span>
        <p class="film-title">Her mezun bir gün bu kapıdan geçti.</p>
        <p class="film-text">Mezuniyetten sonra da aynı ağın parçası: bölüm, duyurular ve fırsatlar burada.</p>
      </div>

      <div class="film-step" data-from="0.74" data-to="1.01" aria-hidden="true">
        <span class="kicker">Rektörlük</span>
        <p class="film-title">Ağ burada büyüyor.</p>
        <p class="film-text">Aşağıda: mezun sayıları, açık iş ilanları ve son duyurular.</p>
      </div>

      <div class="film-progress" aria-hidden="true"><span></span></div>
    </div>
  </section>
"""

    body = f"""
  {_stats(counts)}

  <section class="home-grid">
    <div class="card card-featured home-card" data-reveal>
      <div class="home-card-head">
        <h2>Açık iş ilanları</h2>
        <a class="link-arrow" href="/job-postings">Tüm ilanlar <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </div>
      {_postings(postings)}
    </div>
    <div class="card home-card" data-reveal>
      <div class="home-card-head">
        <h2>Son duyurular</h2>
        <a class="link-arrow" href="/announcements">Tüm duyurular <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </div>
      {_announcements(announcements)}
    </div>
  </section>

  <section class="how">
    <div class="section-head"><h2>Nasıl çalışır?</h2><span class="label-mono">Üç adım</span></div>
    <ol class="steps">
      <li class="step" data-reveal>
        <span class="step-num">1</span>
        <h3>Mezunlar kaydedilir</h3>
        <p>Her mezun adı, e-postası, mezuniyet yılı ve bölümüyle sisteme eklenir.</p>
        <a class="link-arrow" href="/users">Mezunlara git <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </li>
      <li class="step" data-reveal>
        <span class="step-num">2</span>
        <h3>İlanlar paylaşılır</h3>
        <p>Bölüm ya da mezunlar iş ve staj ilanı paylaşır; ilan son başvuru tarihine kadar açık kalır.</p>
        <a class="link-arrow" href="/job-postings">İlanlara git <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </li>
      <li class="step" data-reveal>
        <span class="step-num">3</span>
        <h3>Başvurular takip edilir</h3>
        <p>Mezunlar ilanlara başvurur; başvurunun durumu incelemeden mülakata ve sonuca kadar izlenir.</p>
        <a class="link-arrow" href="/applications">Başvurulara git <span class="arrow" aria-hidden="true">&rarr;</span></a>
      </li>
    </ol>
  </section>

  <p class="tech-strip">
    <span>FastAPI &middot; PostgreSQL &middot; SQLAlchemy &middot; Docker</span>
    <a href="/api/swagger">API dokümantasyonu</a>
    <a href="/about">Proje hakkında</a>
  </p>
"""
    return render_page("Home", body, "/", lang="tr", full_width=film)
