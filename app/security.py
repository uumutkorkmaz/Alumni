"""Password hashing (ddd.md 4.1.2). Only the hash is stored, never the password.

scrypt is a slow, memory-hard hash from the standard library (hashlib), so no extra package is
needed. Each password gets its own random salt; the cost parameters are stored with the hash, so
they can be raised later without breaking old hashes. Format: scrypt$n$r$p$<salt b64>$<hash b64>
"""
import base64
import hashlib
import hmac
import os

N, R, P = 2**14, 8, 1  # CPU/memory cost (about 16 MB and a few dozen ms per hash)
SALT_BYTES = 16
KEY_BYTES = 32


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def hash_password(password: str) -> str:
    salt = os.urandom(SALT_BYTES)
    key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=N, r=R, p=P, dklen=KEY_BYTES)
    return f"scrypt${N}${R}${P}${_b64(salt)}${_b64(key)}"


def verify_password(password: str, stored: str | None) -> bool:
    """True if `password` matches the stored hash. For the login task; constant-time compare."""
    if not stored:
        return False
    try:
        scheme, n, r, p, salt_b64, key_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        salt, key = base64.b64decode(salt_b64), base64.b64decode(key_b64)
        candidate = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(key)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, key)
