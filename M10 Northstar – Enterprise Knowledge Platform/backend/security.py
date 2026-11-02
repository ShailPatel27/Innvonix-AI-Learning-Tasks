import base64
import hashlib
import hmac
import secrets
import time

from backend.database import connect, now_utc

SESSION_LIFETIME_SECONDS = 30 * 24 * 60 * 60


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return "scrypt${}${}${}${}${}".format(
        2**14,
        8,
        1,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, n, r, p, encoded_salt, encoded_digest = stored_hash.split("$", 5)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def issue_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as db:
        db.execute("DELETE FROM access_sessions WHERE expires_at <= ?", (time.time(),))
        db.execute(
            "INSERT INTO access_sessions (token_hash, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token_hash, user_id, time.time() + SESSION_LIFETIME_SECONDS, now_utc()),
        )
    return token


def user_for_token(token: str):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as db:
        row = db.execute(
            """
            SELECT u.id, u.email, u.full_name, u.department, u.role
            FROM access_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (token_hash, time.time()),
        ).fetchone()
        if row:
            db.execute(
                "UPDATE access_sessions SET expires_at = ? WHERE token_hash = ?",
                (time.time() + SESSION_LIFETIME_SECONDS, token_hash),
            )
    return dict(row) if row else None


def revoke_session(token: str):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as db:
        db.execute("DELETE FROM access_sessions WHERE token_hash = ?", (token_hash,))
