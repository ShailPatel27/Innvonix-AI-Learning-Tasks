import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "platform.sqlite3"


@contextmanager
def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_database():
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT '',
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee' CHECK (role IN ('admin', 'employee')),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                description TEXT NOT NULL DEFAULT '',
                created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS group_memberships (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, group_id)
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                size_bytes INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS document_groups (
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
                PRIMARY KEY (document_id, group_id)
            );

            CREATE TABLE IF NOT EXISTS access_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                target TEXT NOT NULL DEFAULT '',
                details TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_group_memberships_user
                ON group_memberships(user_id, group_id);
            CREATE INDEX IF NOT EXISTS idx_document_groups_group
                ON document_groups(group_id, document_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_user
                ON conversations(user_id, updated_at);
            CREATE INDEX IF NOT EXISTS idx_audit_events_created
                ON audit_events(created_at);
            """
        )


def record_audit(db, actor_id: int | None, action: str, target: str = "", details: str = ""):
    db.execute(
        "INSERT INTO audit_events (actor_id, action, target, details, created_at) VALUES (?, ?, ?, ?, ?)",
        (actor_id, action, target, details, now_utc()),
    )


def get_user_groups(user_id: int) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            """
            SELECT g.id, g.name, g.description
            FROM groups g
            JOIN group_memberships gm ON gm.group_id = g.id
            WHERE gm.user_id = ?
            ORDER BY g.name
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]
