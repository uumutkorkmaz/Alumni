"""The registration pages (ddd.md 4.1.2). Public pages, so in Turkish (brand.md, Voice)."""
from html import escape

from app.models.registration import ACADEMIC_TITLES, DOCUMENTS, STAFF_EMAIL_DOMAIN, STUDENT_EMAIL_DOMAIN
from app.views.layout import button, page_hero, render_page

ACTIVE = "/register"

ROLE_CARDS = [
    ("student", "Öğrenci", f"@{STUDENT_EMAIL_DOMAIN} e-postasıyla"),
    ("alumni", "Mezun", "Kendi e-postanla"),
    ("academic", "Akademisyen", f"@{STAFF_EMAIL_DOMAIN} e-postasıyla"),
    ("staff", "İdari personel", f"@{STAFF_EMAIL_DOMAIN} e-postasıyla"),
]
EMAIL_HINTS = {
    "student": f"ad.soyad@{STUDENT_EMAIL_DOMAIN}",
    "alumni": "ornek@gmail.com",
    "academic": f"ad.soyad@{STAFF_EMAIL_DOMAIN}",
    "staff": f"ad.soyad@{STAFF_EMAIL_DOMAIN}",
}
DEPARTMENTS = [
    "Yönetim Bilişim Sistemleri",
    "İktisat",
    "İşletme",
    "Çalışma Ekonomisi ve Endüstri İlişkileri",
    "Maliye",
    "Ekonometri",
    "Bölüm Sekreterliği",
    "Kariyer Merkezi",
    "Dekanlık",
    "Mezunlar Derneği",
]


def _field(name: str, label: str, control: str, errors: dict, hint: str = "", roles: str = "",
           full: bool = False, labels: dict | None = None) -> str:
    """One labelled field with its hint and error. `roles` limits it to some roles (the page
    script hides it for the others); `labels` gives another label per role."""
    error = errors.get(name, "")
    cls = "field" + (" full" if full else "") + (" has-error" if error else "")
    attrs = f' data-roles="{roles}"' if roles else ""
    if labels:
        attrs += "".join(f' data-label-{r}="{escape(t)}"' for r, t in labels.items())
    hint_html = f'<span class="hint" id="{name}-hint">{hint}</span>' if hint else ""
    error_html = f'<span class="field-error" id="{name}-error" role="alert">{escape(error)}</span>' if error else ""
    return (
        f'<div class="{cls}"{attrs}><label for="{name}" data-label>{escape(label)}</label>'
        f"{control}{hint_html}{error_html}</div>"
    )


def _input(name: str, values: dict, errors: dict, type_: str = "text", **attrs) -> str:
    value = escape(str(values.get(name, "") or ""))
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items() if v is not None)
    invalid = f' aria-invalid="true" aria-describedby="{name}-error"' if name in errors else ""
    keep = f' value="{value}"' if type_ != "password" else ""
    return f'<input id="{name}" name="{name}" type="{type_}"{keep}{extra}{invalid} />'


def render_register_page(values: dict, errors: dict) -> str:
    role = values.get("role", "")
    cards = "".join(
        f'<label class="role-card">'
        f'<input type="radio" name="role" value="{key}"{" checked" if key == role else ""} required />'
        f'<span class="role-card-title">{title}</span><span class="role-card-sub">{sub}</span></label>'
        for key, title, sub in ROLE_CARDS
    )
    role_error = (
        f'<span class="field-error" role="alert">{escape(errors["role"])}</span>' if "role" in errors else ""
    )
    title_options = '<option value="">Unvan seçin</option>' + "".join(
        f'<option{" selected" if values.get("title") == t else ""}>{t}</option>' for t in ACADEMIC_TITLES
    )
    datalist = "".join(f'<option value="{d}"></option>' for d in DEPARTMENTS)
    summary = (
        '<div class="alert alert-error" role="alert">'
        f"Kayıt gönderilmedi: {len(errors)} alanda düzeltme gerekiyor. Şifreleri ve belgeyi yeniden girin.</div>"
        if errors
        else ""
    )
    consent_checked = " checked" if values.get("consent") else ""
    doc_hints = "".join(f' data-doc-{r}="{escape(t)}"' for r, t in DOCUMENTS.items())

    form = f"""
    <form class="register-form" method="post" action="/register" enctype="multipart/form-data" novalidate
          data-register data-email-hints='{escape(str(EMAIL_HINTS).replace("'", '"'))}'>
      {summary}
      <fieldset class="role-picker">
        <legend>Kim olarak kayıt oluyorsun?</legend>
        <div class="role-cards">{cards}</div>
        {role_error}
      </fieldset>

      <div class="form-grid">
        {_field("name", "Ad soyad", _input("name", values, errors, maxlength=100, autocomplete="name", required="required"), errors)}
        {_field("email", "E-posta", _input("email", values, errors, "email", maxlength=255, autocomplete="email", required="required", placeholder="ornek@gmail.com"), errors,
                hint="Rolüne göre: öğrenciler öğrenci e-postası, personel kurumsal e-posta kullanır.")}
        {_field("password", "Şifre", '<div class="password-wrap">' + _input("password", values, errors, "password", minlength=8, maxlength=128, autocomplete="new-password", required="required") + '<button type="button" class="btn btn-ghost btn-sm" data-show-password aria-label="Şifreyi göster">Göster</button></div><div class="strength" aria-hidden="true"><span></span></div>', errors,
                hint="En az 8 karakter; en az bir harf ve bir rakam.")}
        {_field("password_confirm", "Şifre tekrar", _input("password_confirm", values, errors, "password", maxlength=128, autocomplete="new-password", required="required"), errors)}
        {_field("department", "Bölüm", _input("department", values, errors, maxlength=100, list="departments", required="required"), errors,
                labels={"staff": "Birim"})}
        {_field("graduation_year", "Mezuniyet yılı", _input("graduation_year", values, errors, "number", min=1950, max=2100, inputmode="numeric"), errors,
                roles="student alumni", labels={"student": "Beklenen mezuniyet yılı", "alumni": "Mezuniyet yılı"})}
        {_field("student_number", "Öğrenci numarası", _input("student_number", values, errors, inputmode="numeric", maxlength=20, pattern="[0-9]*"), errors,
                roles="student alumni", labels={"student": "Öğrenci numarası", "alumni": "Öğrenci numarası (isteğe bağlı)"})}
        {_field("title", "Unvan", f'<select id="title" name="title">{title_options}</select>', errors, roles="academic")}
        {_field("position", "Görev", _input("position", values, errors, maxlength=100, placeholder="örn. Bölüm sekreteri"), errors, roles="staff")}
      </div>
      <datalist id="departments">{datalist}</datalist>

      <div class="field full{' has-error' if 'document' in errors else ''}">
        <span class="label-like">Belge</span>
        <label class="dropzone" for="document" data-dropzone{doc_hints}>
          <input id="document" name="document" type="file" accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" required />
          <span class="dropzone-title" data-file-name>Belgeni seç ya da buraya sürükle</span>
          <span class="dropzone-sub" data-doc-hint>PDF, JPG ya da PNG &middot; en fazla 5 MB</span>
        </label>
        {f'<span class="field-error" role="alert">{escape(errors["document"])}</span>' if "document" in errors else ""}
      </div>

      <div class="field full{' has-error' if 'consent' in errors else ''}">
        <label class="check consent">
          <input type="checkbox" name="consent" value="1"{consent_checked} required />
          <span>Bilgilerimin ve yüklediğim belgenin, İstanbul Üniversitesi YBS mezun takip sistemi kapsamında
          hesabımın doğrulanması amacıyla işlenmesini kabul ediyorum. Belge, inceleme bittikten sonra silinir.</span>
        </label>
        {f'<span class="field-error" role="alert">{escape(errors["consent"])}</span>' if "consent" in errors else ""}
      </div>

      <div class="form-actions"><button type="submit" class="btn btn-primary">Kaydı gönder <span class="arrow" aria-hidden="true">&rarr;</span></button></div>
      <p class="switch-auth">Hesabın var mı? <a href="/login">Giriş yap</a></p>
    </form>"""

    side = f"""
    <aside class="register-side">
      <section class="card" data-reveal>
        <h2>Nasıl çalışır?</h2>
        <ol class="mini-steps">
          <li><span class="step-num">1</span><div><b>Rolünü seç, bilgilerini gir.</b><p>Rolüne uygun e-posta adresiyle.</p></div></li>
          <li><span class="step-num">2</span><div><b>Belgeni yükle.</b><p>Öğrenci belgesi, mezun belgesi ya da personel kartı.</p></div></li>
          <li><span class="step-num">3</span><div><b>Yönetici onaylar.</b><p>Onaydan sonra hesabın açılır; belgen silinir.</p></div></li>
        </ol>
      </section>
      <section class="card" data-reveal>
        <h2>Hangi e-posta?</h2>
        <dl class="dl compact">
          <dt>Öğrenci</dt><dd>@{STUDENT_EMAIL_DOMAIN}</dd>
          <dt>Mezun</dt><dd>Kendi e-postan</dd>
          <dt>Akademisyen</dt><dd>@{STAFF_EMAIL_DOMAIN}</dd>
          <dt>İdari personel</dt><dd>@{STAFF_EMAIL_DOMAIN}</dd>
        </dl>
        <p class="muted small-note" style="margin-top: 14px">Yönetici hesabı kayıtla açılmaz; yöneticiler tarafından verilir.</p>
      </section>
    </aside>"""

    body = f"""
    {page_hero(
        "Mezun ağına katıl",
        "Hesabını <em>oluştur</em>",
        "Öğrenci, mezun ya da İstanbul Üniversitesi personeli olarak kayıt ol. Belgeni yükle; yönetici onaylayınca hesabın açılır.",
        button("Hesabım var, giriş yap", "/login"),
        size="compact",
    )}
    <div class="register-grid">
      <section class="card card-featured" data-reveal>{form}</section>
      {side}
    </div>
    {REGISTER_SCRIPT}
    """
    return render_page("Kayıt ol", body, ACTIVE, lang="tr")


def render_register_done() -> str:
    body = f"""
    {page_hero(
        "Başvuru alındı",
        "Başvurun <em>alındı</em>",
        "Bilgilerin ve belgen yöneticiye ulaştı. Belgen incelenip onaylandığında hesabın açılacak.",
        button("Ana sayfa", "/", "primary", arrow=True) + button("İş ilanlarına göz at", "/job-postings"),
        size="compact",
    )}
    <section class="card card-featured" data-reveal>
      <ol class="mini-steps">
        <li><span class="step-num">&#10003;</span><div><b>Kayıt ve belge alındı.</b><p>Şifren güvenli biçimde (hash olarak) saklandı.</p></div></li>
        <li><span class="step-num">2</span><div><b>Yönetici belgeni inceliyor.</b><p>Onaylanınca hesabın aktif olur; reddedilirse nedeni yazılır.</p></div></li>
        <li><span class="step-num">3</span><div><b>Giriş.</b><p>Onaydan sonra e-postan ve şifrenle <a href="/login">giriş yap</a>.</p></div></li>
      </ol>
    </section>
    """
    return render_page("Başvuru alındı", body, ACTIVE, narrow=True, lang="tr")


# The page's own behaviour: show the fields of the chosen role, change labels and hints, password
# strength and show/hide, and the chosen file's name. Without JavaScript every field stays visible and
# the server checks everything anyway.
REGISTER_SCRIPT = """
<script>
(function () {
  var form = document.querySelector('[data-register]');
  if (!form) return;
  var hints = JSON.parse(form.dataset.emailHints || '{}');
  var email = form.querySelector('#email');
  var drop = form.querySelector('[data-dropzone]');
  var docHint = form.querySelector('[data-doc-hint]');

  function applyRole() {
    var checked = form.querySelector('input[name="role"]:checked');
    var role = checked ? checked.value : '';
    form.dataset.role = role;
    form.querySelectorAll('[data-roles]').forEach(function (field) {
      var on = role !== '' && field.dataset.roles.split(' ').indexOf(role) !== -1;
      field.hidden = !on;
      field.querySelectorAll('input, select').forEach(function (el) { el.disabled = !on; });
    });
    form.querySelectorAll('.field').forEach(function (field) {
      var label = field.querySelector('[data-label]');
      if (!label) return;
      if (!label.dataset.base) label.dataset.base = label.textContent;
      label.textContent = (role && field.dataset['label' + role.charAt(0).toUpperCase() + role.slice(1)]) || label.dataset.base;
    });
    if (role && hints[role]) email.placeholder = hints[role];
    if (role && drop.dataset['doc' + role.charAt(0).toUpperCase() + role.slice(1)]) {
      docHint.textContent = drop.dataset['doc' + role.charAt(0).toUpperCase() + role.slice(1)] + ' \\u00b7 PDF, JPG ya da PNG \\u00b7 en fazla 5 MB';
    }
  }
  form.querySelectorAll('input[name="role"]').forEach(function (r) { r.addEventListener('change', applyRole); });
  applyRole();

  var pw = form.querySelector('#password');
  var bar = form.querySelector('.strength span');
  pw.addEventListener('input', function () {
    var v = pw.value, score = 0;
    if (v.length >= 8) score++;
    if (/[A-Za-z\\u00c7\\u011e\\u0130\\u00d6\\u015e\\u00dc\\u00e7\\u011f\\u0131\\u00f6\\u015f\\u00fc]/.test(v) && /\\d/.test(v)) score++;
    if (v.length >= 12) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;
    bar.style.transform = 'scaleX(' + (score / 4) + ')';
    bar.dataset.level = String(score);
  });
  var toggle = form.querySelector('[data-show-password]');
  toggle.addEventListener('click', function () {
    var show = pw.type === 'password';
    pw.type = show ? 'text' : 'password';
    toggle.textContent = show ? 'Gizle' : 'G\\u00f6ster';
    toggle.setAttribute('aria-label', show ? '\\u015eifreyi gizle' : '\\u015eifreyi g\\u00f6ster');
  });

  var file = form.querySelector('#document');
  var fileName = form.querySelector('[data-file-name]');
  file.addEventListener('change', function () {
    fileName.textContent = file.files.length ? file.files[0].name : 'Belgeni se\\u00e7 ya da buraya s\\u00fcr\\u00fckle';
    drop.classList.toggle('has-file', file.files.length > 0);
  });
  ['dragenter', 'dragover'].forEach(function (e) { drop.addEventListener(e, function () { drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (e) { drop.addEventListener(e, function () { drop.classList.remove('is-over'); }); });
})();
</script>
"""
