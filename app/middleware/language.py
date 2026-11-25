"""The visitor's language for this request (ddd.md 4.1.8): the `lang` cookie (tr or en), Turkish when
there is none. The pages read it through app.i18n.lang()."""
from fastapi import Request

from app import i18n


async def language_middleware(request: Request, call_next):
    chosen = request.cookies.get(i18n.COOKIE)
    token = i18n.current_lang.set(chosen if chosen in i18n.LANGS else i18n.DEFAULT)
    try:
        return await call_next(request)
    finally:
        i18n.current_lang.reset(token)
