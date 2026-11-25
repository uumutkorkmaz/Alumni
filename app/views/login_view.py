"""The login page (ddd.md 4.1.3). Public, so in Turkish."""
from html import escape

from app import devlogin
from app.views.layout import page_hero, render_page


def _dev_buttons() -> str:
    """TEMPORARY quick login, only with DEV_LOGIN=1 (ddd.md 4.1.4)."""
    if not devlogin.ENABLED:
        return ""
    buttons = "".join(
        f'<form method="post" action="/dev-login/{role}" class="inline-form">'
        f'<button type="submit" class="btn btn-ghost dev-role role-{role}">{label}</button></form>'
        for role, label in devlogin.BUTTON_LABELS.items()
    )
    return (
        '<section class="card dev-login" data-reveal>'
        '<div class="card-head"><h2>Test hesabıyla hızlı giriş</h2><span class="label-mono">Geçici &middot; DEV_LOGIN=1</span></div>'
        f'<div class="dev-buttons">{buttons}</div>'
        '<p class="muted small-note">Tıklayınca şifresiz olarak o rolün test hesabıyla girersin. Denemeler bitince kaldırılacak.</p>'
        "</section>"
    )


def render_login_page(email: str, next_url: str, error: str) -> str:
    alert = f'<div class="alert alert-error" role="alert">{escape(error)}</div>' if error else ""
    next_field = f'<input type="hidden" name="next" value="{escape(next_url)}" />' if next_url else ""
    note = (
        '<p class="muted small-note login-note">Bu sayfayı görmek için giriş yapmalısın.</p>'
        if next_url and next_url != "/"
        else ""
    )
    body = f"""
    {page_hero(
        "Giriş",
        "Hesabına <em>giriş yap</em>",
        "Öğrenci, mezun ya da İstanbul Üniversitesi personeli olarak kayıtlı hesabınla giriş yap.",
        size="compact",
    )}
    {_dev_buttons()}
    <section class="card card-featured login-card" data-reveal>
      {alert}{note}
      <form class="login-form" method="post" action="/login" novalidate>
        {next_field}
        <div class="field"><label for="email">E-posta</label>
          <input id="email" name="email" type="email" value="{escape(email)}" maxlength="255" autocomplete="email" required autofocus /></div>
        <div class="field"><label for="password">Şifre</label>
          <div class="password-wrap">
            <input id="password" name="password" type="password" maxlength="128" autocomplete="current-password" required />
            <button type="button" class="btn btn-ghost btn-sm" data-show-password aria-label="Şifreyi göster" data-t-show="Göster" data-t-hide="Gizle">Göster</button>
          </div></div>
        <label class="check"><input type="checkbox" name="remember" value="1" /> Beni hatırla (30 gün)</label>
        <div class="form-actions"><button type="submit" class="btn btn-primary">Giriş yap <span class="arrow" aria-hidden="true">&rarr;</span></button></div>
      </form>
      <hr class="divider" />
      <p class="switch-auth">Hesabın yok mu? <a href="/register">Kayıt ol</a></p>
    </section>
    <script>
    (function () {{
      var pw = document.getElementById('password'), b = document.querySelector('[data-show-password]');
      b.addEventListener('click', function () {{
        var show = pw.type === 'password';
        pw.type = show ? 'text' : 'password';
        b.textContent = show ? b.dataset.tHide : b.dataset.tShow;
      }});
    }})();
    </script>
    """
    return render_page("Giriş yap", body, "/login", narrow=True, lang="tr")
