NAV_LINKS = [
    ("/", "Home"),
    ("/about", "About"),
    ("/users", "Users"),
    ("/announcements", "Announcements"),
    ("/docs", "API Docs"),
]

NAV_STYLE = """
  <style>
    nav { display: flex; align-items: center; justify-content: space-between;
          max-width: 1080px; margin: 0 auto 40px; }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; }
    .brand-mark { width: 32px; height: 32px; border-radius: 9px;
                  background: linear-gradient(135deg, #38bdf8, #a78bfa);
                  display: flex; align-items: center; justify-content: center;
                  font-size: 15px; font-weight: 800; color: #0b1120; }
    nav .nav-links { display: flex; gap: 28px; font-size: 14px; }
    nav .nav-links a { color: #94a3b8; text-decoration: none; transition: color 0.15s ease; }
    nav .nav-links a:hover, nav .nav-links a.active { color: #e2e8f0; }
    @media (max-width: 720px) {
      nav { flex-direction: column; gap: 14px; }
      nav .nav-links { gap: 16px; font-size: 13px; flex-wrap: wrap; justify-content: center; }
    }
  </style>
"""


def render_nav(active: str) -> str:
    active_attr = ' class="active"'
    links = "".join(
        f'<a href="{href}"{active_attr if href == active else ""}>{label}</a>'
        for href, label in NAV_LINKS
    )
    return f"""
  <nav>
    <div class="brand"><span class="brand-mark">AT</span>Alumni Tracking</div>
    <div class="nav-links">{links}</div>
  </nav>"""
