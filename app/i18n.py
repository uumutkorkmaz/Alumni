"""Two languages for the pages: Turkish (tr, the default) and English (en). ddd.md 4.1.8.

How it works: the views write their text once (most pages in English; the home, about, login and
register pages in Turkish). Every page goes through `render_page`, which calls `translate_html` on the
finished HTML: each piece of text between tags, and the text of `placeholder`, `title`, `aria-label`,
`alt` and `confirm('...')`, is looked up in the catalogue of the chosen language (app/i18n_catalog.py)
and replaced when it is found. Sentences with a number or a name in them are matched by patterns.

What people type themselves (names, posting titles, announcements, text areas) is not in the
catalogue, so it stays as written. The JSON API and Swagger stay in English: they are for developers.
"""
import html as htmllib
import re
from contextvars import ContextVar

from app import i18n_catalog as cat

LANGS = ("tr", "en")
DEFAULT = "tr"
COOKIE = "lang"
current_lang: ContextVar[str] = ContextVar("current_lang", default=DEFAULT)


def lang() -> str:
    return current_lang.get()


def pick(tr: str, en: str) -> str:
    """For text built in code (not a fixed sentence): the Turkish or the English version."""
    return tr if lang() == "tr" else en


# --------------------------------------------------------------------------- the catalogue
_words: dict[str, dict[str, str]] = {}
_patterns: dict[str, list] = {}


def _load(target: str) -> None:
    if target in _words:
        return
    if target == "tr":
        words, patterns = dict(cat.EN_TO_TR), cat.EN_TO_TR_PATTERNS
    else:
        words, patterns = dict(cat.TR_TO_EN), cat.TR_TO_EN_PATTERNS
        # The login and registration messages already exist in both languages.
        from app.auth import MESSAGES as LOGIN
        from app.models.registration import MESSAGES as REGISTER
        for tr, en in list(LOGIN.values()) + list(REGISTER.values()):
            words.setdefault(" ".join(tr.split()), en)
    _words[target] = {" ".join(k.split()): v for k, v in words.items()}
    # A pattern starting with "!" applies only when every group is a known text.
    _patterns[target] = [
        (re.compile("^" + p.lstrip("!") + "$", re.S), r, p.startswith("!")) for p, r in patterns
    ]


def _lookup(key: str, target: str) -> str | None:
    """The translation of one normalised text, or None when it is not known."""
    words = _words[target]
    if key in words:
        return words[key]
    for pattern, repl, strict in _patterns[target]:
        m = pattern.match(key)
        if not m:
            continue
        groups = []
        for g in m.groups():
            g = g or ""
            known = _lookup(g, target) if g and not re.fullmatch(r"[\d\s.:#%/\-–]+", g) else None
            if strict and known is None and not re.fullmatch(r"[\d\s.:#%/\-–]*", g):
                break
            groups.append(known if known is not None else g)
        else:
            return repl.format(*groups)
    # "A · B · C": each part on its own (names and places stay as they are).
    for sep in (" · ", " — "):
        if sep in key:
            parts = key.split(sep)
            done = [_lookup(p, target) for p in parts]
            if any(d is not None for d in done):
                return sep.join(d if d is not None else p for d, p in zip(done, parts))
    # "A, B, C" and "A or B": only when every part is known.
    for sep, joiner in ((", ", ", "), (" or ", " ya da " if target == "tr" else " or ")):
        if sep in key:
            parts = key.split(sep)
            done = [_lookup(p, target) for p in parts]
            if all(d is not None for d in done):
                return joiner.join(done)
    return None


def translate_text(text: str, target: str | None = None, quote: bool = False) -> str:
    """One piece of HTML text in the target language (the current one by default); unchanged if unknown."""
    target = target or lang()
    _load(target)
    key = " ".join(htmllib.unescape(text).split())
    if not key:
        return text
    found = _lookup(key, target)
    if found is None:
        return text
    lead = text[: len(text) - len(text.lstrip())]
    tail = text[len(text.rstrip()):]
    return lead + htmllib.escape(found, quote=quote) + tail


_SKIP = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<textarea\b.*?</textarea>|<!--.*?-->)", re.S | re.I)
_TEXT = re.compile(r">([^<>]+)(?=<|$)")
# Texts a page script shows later (a label for the chosen role, "Show" / "Hide") wait in data-t-*,
# data-label-* and data-doc-* attributes, so they are translated with the page.
_ATTR = re.compile(r'(?<![\w-])(placeholder|title|aria-label|alt|data-t-[\w-]+|data-label-\w+|data-doc-\w+)="([^"]*)"')
_CONFIRM = re.compile(r"confirm\('([^']*)'\)")


def _confirm(m: re.Match, target: str) -> str:
    done = translate_text(m.group(1), target)
    return "confirm('" + done.replace("\\", "\\\\").replace("'", "\\'") + "')"


def _part(html: str, target: str) -> str:
    html = _TEXT.sub(lambda m: ">" + translate_text(m.group(1), target), html)
    html = _ATTR.sub(lambda m: f'{m.group(1)}="{translate_text(m.group(2), target, quote=True)}"', html)
    return _CONFIRM.sub(lambda m: _confirm(m, target), html)


def translate_html(html: str, target: str | None = None) -> str:
    """The whole page in the target language. Scripts, styles and text areas (what a person typed)
    are left as they are."""
    target = target or lang()
    _load(target)
    whole = cat.EN_TO_TR_HTML if target == "tr" else cat.TR_TO_EN_HTML
    for source, replacement in whole:  # headings with one <em> word, e.g. "My <em>profile</em>"
        html = html.replace(source, replacement)
    pieces = _SKIP.split(html)
    return "".join(p if _SKIP.fullmatch(p) else _part(p, target) for p in pieces)
