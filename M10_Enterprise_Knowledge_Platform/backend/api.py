import asyncio
import json
import os
import re
import sqlite3
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from backend.database import (
    UPLOAD_DIR,
    connect,
    get_user_groups,
    initialize_database,
    now_utc,
    record_audit,
)
from backend.documents import extract_documents
from backend.rag import answer_question, delete_document_chunks, index_document
from backend.schemas import (
    ChatRequest,
    GroupCreateRequest,
    GroupMemberRequest,
    LoginRequest,
    SignupRequest,
)
from backend.security import hash_password, issue_session, revoke_session, user_for_token, verify_password

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / ".env")

app = FastAPI(title="Enterprise Knowledge Platform", version="1.0.0")
bearer_auth = HTTPBearer(auto_error=False)
app.mount(
    "/static",
    StaticFiles(directory=PROJECT_DIR / "frontend" / "static"),
    name="static",
)


def setup_platform():
    initialize_database()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if not admin_email or not admin_password:
        return
    if len(admin_password) < 8:
        raise RuntimeError("ADMIN_PASSWORD must be at least 8 characters long.")

    with connect() as db:
        existing = db.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
        if existing:
            db.execute(
                "UPDATE users SET role = 'admin', password_hash = ? WHERE id = ?",
                (hash_password(admin_password), existing["id"]),
            )
        else:
            db.execute(
                """
                INSERT INTO users (email, full_name, department, password_hash, role, created_at)
                VALUES (?, ?, 'Administration', ?, 'admin', ?)
                """,
                (
                    admin_email,
                    os.getenv("ADMIN_NAME", "Platform Administrator"),
                    hash_password(admin_password),
                    now_utc(),
                ),
            )


setup_platform()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_auth)],
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    user = user_for_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Your session has expired. Sign in again.")
    return user


def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Administrator access is required.")
    return user


def user_payload(user: dict) -> dict:
    groups = get_user_groups(user["id"])
    if user["role"] == "admin":
        with connect() as db:
            rows = db.execute(
                "SELECT id, name, description FROM groups ORDER BY name"
            ).fetchall()
        groups = [dict(row) for row in rows]
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "department": user["department"],
        "role": user["role"],
        "groups": groups,
    }


def accessible_document_ids(user: dict) -> set[str]:
    with connect() as db:
        if user["role"] == "admin":
            rows = db.execute("SELECT id FROM documents").fetchall()
        else:
            rows = db.execute(
                """
                SELECT DISTINCT d.id
                FROM documents d
                JOIN document_groups dg ON dg.document_id = d.id
                JOIN group_memberships gm ON gm.group_id = dg.group_id
                WHERE gm.user_id = ?
                """,
                (user["id"],),
            ).fetchall()
    return {row["id"] for row in rows}


def safe_conversation_messages(rows, allowed_document_ids: set[str]) -> list[dict]:
    messages = []
    for row in rows:
        sources = json.loads(row["sources_json"])
        restricted_sources = any(
            source.get("document_id") not in allowed_document_ids
            for source in sources
            if source.get("document_id")
        )
        content = row["content"]
        if row["role"] == "assistant" and restricted_sources:
            content = "This previous response is hidden because access to a cited document has changed."
            sources = []
        messages.append({"role": row["role"], "content": content, "sources": sources})
    return messages


def valid_email(email: str) -> bool:
    return re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) is not None


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(PROJECT_DIR / "frontend" / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest):
    email = request.email.strip().lower()
    if not valid_email(email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if len(request.password) < 8:
        raise HTTPException(status_code=422, detail="Password must contain at least 8 characters.")
    if not request.full_name.strip():
        raise HTTPException(status_code=422, detail="Enter your name.")

    try:
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO users (email, full_name, department, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, 'employee', ?)
                """,
                (
                    email,
                    request.full_name.strip(),
                    request.department.strip(),
                    hash_password(request.password),
                    now_utc(),
                ),
            )
            user_id = cursor.lastrowid
            record_audit(db, user_id, "signup", str(user_id))
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from error

    token = issue_session(user_id)
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return {"access_token": token, "token_type": "bearer", "user": user_payload(dict(user))}


@app.post("/auth/login")
def login(request: LoginRequest):
    email = request.email.strip().lower()
    failed_login = False
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None or not verify_password(request.password, row["password_hash"]):
            record_audit(db, None, "login_failed", "")
            failed_login = True
            user = None
        else:
            record_audit(db, row["id"], "login", str(row["id"]))
            user = dict(row)
    if failed_login:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")

    token = issue_session(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": user_payload(user)}


@app.post("/auth/logout")
def logout(
    user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_auth),
):
    revoke_session(credentials.credentials)
    with connect() as db:
        record_audit(db, user["id"], "logout", str(user["id"]))
    return {"message": "Signed out."}


@app.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return user_payload(user)


@app.get("/groups")
def list_groups(user: dict = Depends(get_current_user)):
    with connect() as db:
        if user["role"] == "admin":
            rows = db.execute(
                """
                SELECT g.id, g.name, g.description, COUNT(gm.user_id) AS member_count
                FROM groups g LEFT JOIN group_memberships gm ON gm.group_id = g.id
                GROUP BY g.id ORDER BY g.name
                """
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT g.id, g.name, g.description
                FROM groups g JOIN group_memberships gm ON gm.group_id = g.id
                WHERE gm.user_id = ? ORDER BY g.name
                """,
                (user["id"],),
            ).fetchall()
    return [dict(row) for row in rows]


@app.post("/groups", status_code=status.HTTP_201_CREATED)
def create_group(request: GroupCreateRequest, admin: dict = Depends(require_admin)):
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Group name cannot be empty.")
    try:
        with connect() as db:
            cursor = db.execute(
                "INSERT INTO groups (name, description, created_by, created_at) VALUES (?, ?, ?, ?)",
                (name, request.description.strip(), admin["id"], now_utc()),
            )
            group_id = cursor.lastrowid
            record_audit(db, admin["id"], "group_created", str(group_id), name)
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="A group with this name already exists.") from error
    return {"id": group_id, "name": name, "description": request.description.strip()}


@app.post("/groups/{group_id}/members", status_code=status.HTTP_201_CREATED)
def add_group_member(
    group_id: int,
    request: GroupMemberRequest,
    admin: dict = Depends(require_admin),
):
    with connect() as db:
        if db.execute("SELECT 1 FROM groups WHERE id = ?", (group_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Group not found.")
        member = db.execute(
            "SELECT id, email FROM users WHERE id = ?", (request.user_id,)
        ).fetchone()
        if member is None:
            raise HTTPException(status_code=404, detail="User not found.")
        db.execute(
            "INSERT OR IGNORE INTO group_memberships (user_id, group_id, created_at) VALUES (?, ?, ?)",
            (request.user_id, group_id, now_utc()),
        )
        record_audit(db, admin["id"], "group_member_added", str(group_id), member["email"])
    return {"message": f"{member['email']} is now a member of this group."}


@app.delete("/groups/{group_id}/members/{user_id}")
def remove_group_member(group_id: int, user_id: int, admin: dict = Depends(require_admin)):
    with connect() as db:
        db.execute(
            "DELETE FROM group_memberships WHERE group_id = ? AND user_id = ?",
            (group_id, user_id),
        )
        record_audit(db, admin["id"], "group_member_removed", str(group_id), str(user_id))
    return {"message": "Group membership removed."}


@app.get("/admin/users")
def admin_list_users(admin: dict = Depends(require_admin)):
    with connect() as db:
        users = db.execute(
            "SELECT id, email, full_name, department, role, created_at FROM users ORDER BY full_name"
        ).fetchall()
        memberships = db.execute(
            """
            SELECT gm.user_id, g.id AS group_id, g.name AS group_name
            FROM group_memberships gm JOIN groups g ON g.id = gm.group_id
            ORDER BY g.name
            """
        ).fetchall()
    groups_by_user: dict[int, list[dict]] = {}
    for membership in memberships:
        groups_by_user.setdefault(membership["user_id"], []).append(
            {"id": membership["group_id"], "name": membership["group_name"]}
        )
    return [
        {**dict(user), "groups": groups_by_user.get(user["id"], [])}
        for user in users
    ]


@app.get("/admin/audit")
def admin_audit_log(admin: dict = Depends(require_admin)):
    with connect() as db:
        rows = db.execute(
            """
            SELECT a.id, u.email AS actor, a.action, a.target, a.details, a.created_at
            FROM audit_events a LEFT JOIN users u ON u.id = a.actor_id
            ORDER BY a.id DESC LIMIT 100
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: Annotated[list[UploadFile], File()],
    group_ids: Annotated[list[int], Form()],
    user: dict = Depends(get_current_user),
):
    selected_groups = sorted(set(group_ids))
    if not selected_groups:
        raise HTTPException(status_code=422, detail="Share the document with at least one group.")

    with connect() as db:
        placeholders = ",".join("?" for _ in selected_groups)
        existing_groups = db.execute(
            f"SELECT id, name FROM groups WHERE id IN ({placeholders})", selected_groups
        ).fetchall()
        if len(existing_groups) != len(selected_groups):
            raise HTTPException(status_code=404, detail="One or more selected groups do not exist.")
        if user["role"] != "admin":
            memberships = {
                row["group_id"]
                for row in db.execute(
                    "SELECT group_id FROM group_memberships WHERE user_id = ?",
                    (user["id"],),
                ).fetchall()
            }
            if not set(selected_groups).issubset(memberships):
                raise HTTPException(status_code=403, detail="You can share files only with your groups.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    output = []
    for upload in files:
        filename = Path((upload.filename or "document.txt").replace("\\", "/")).name
        content = await upload.read(25 * 1024 * 1024 + 1)
        if not content:
            raise HTTPException(status_code=400, detail=f"{filename} is empty.")
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"{filename} exceeds the 25 MB limit.")

        try:
            pages = extract_documents(filename, content)
        except (ValueError, UnicodeError) as error:
            raise HTTPException(status_code=400, detail=f"{filename}: {error}") from error
        except Exception as error:
            raise HTTPException(status_code=400, detail=f"Could not read {filename}: {error}") from error

        document_id = str(uuid4())
        stored_path = UPLOAD_DIR / f"{document_id}{Path(filename).suffix.lower()}"
        try:
            chunk_count = await asyncio.to_thread(
                index_document, document_id, filename, selected_groups, pages
            )
        except RuntimeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"Could not index {filename}: {error}") from error

        try:
            stored_path.write_bytes(content)
            with connect() as db:
                db.execute(
                    """
                    INSERT INTO documents (id, filename, stored_path, uploaded_by, size_bytes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (document_id, filename, str(stored_path), user["id"], len(content), now_utc()),
                )
                db.executemany(
                    "INSERT INTO document_groups (document_id, group_id) VALUES (?, ?)",
                    [(document_id, group_id) for group_id in selected_groups],
                )
                record_audit(
                    db,
                    user["id"],
                    "document_uploaded",
                    document_id,
                    f"{filename}; groups={','.join(map(str, selected_groups))}",
                )
        except Exception as error:
            await asyncio.to_thread(delete_document_chunks, document_id)
            stored_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"Could not save {filename}: {error}") from error

        output.append(
            {
                "id": document_id,
                "filename": filename,
                "chunks": chunk_count,
                "shared_with": [group["name"] for group in existing_groups],
            }
        )
    return {"documents": output}


@app.get("/documents")
def list_documents(user: dict = Depends(get_current_user)):
    with connect() as db:
        if user["role"] == "admin":
            rows = db.execute(
                """
                SELECT d.id, d.filename, d.uploaded_by, d.size_bytes, d.created_at,
                       u.full_name AS uploader,
                       GROUP_CONCAT(g.name, ', ') AS shared_groups
                FROM documents d
                LEFT JOIN users u ON u.id = d.uploaded_by
                LEFT JOIN document_groups dg ON dg.document_id = d.id
                LEFT JOIN groups g ON g.id = dg.group_id
                GROUP BY d.id ORDER BY d.created_at DESC
                """
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT DISTINCT d.id, d.filename, d.uploaded_by, d.size_bytes, d.created_at,
                       u.full_name AS uploader,
                       GROUP_CONCAT(DISTINCT g.name) AS shared_groups
                FROM documents d
                JOIN document_groups dg ON dg.document_id = d.id
                JOIN group_memberships gm ON gm.group_id = dg.group_id AND gm.user_id = ?
                LEFT JOIN users u ON u.id = d.uploaded_by
                LEFT JOIN groups g ON g.id = dg.group_id
                GROUP BY d.id ORDER BY d.created_at DESC
                """,
                (user["id"],),
            ).fetchall()
    return [
        {**dict(row), "can_delete": user["role"] == "admin" or row["uploaded_by"] == user["id"]}
        for row in rows
    ]


@app.delete("/documents/{document_id}")
def delete_document(document_id: str, user: dict = Depends(get_current_user)):
    with connect() as db:
        row = db.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        if user["role"] != "admin" and row["uploaded_by"] != user["id"]:
            raise HTTPException(status_code=403, detail="Only the uploader or an administrator can delete this document.")
        filename = row["filename"]
        stored_path = Path(row["stored_path"])

    try:
        delete_document_chunks(document_id)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    with connect() as db:
        db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        record_audit(db, user["id"], "document_deleted", document_id, filename)
    stored_path.unlink(missing_ok=True)
    return {"message": f"Deleted {filename}."}


@app.get("/conversations")
def list_conversations(user: dict = Depends(get_current_user)):
    with connect() as db:
        rows = db.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE user_id = ? ORDER BY updated_at DESC",
            (user["id"],),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    with connect() as db:
        conversation = db.execute(
            "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user["id"]),
        ).fetchone()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        rows = db.execute(
            "SELECT role, content, sources_json FROM conversation_messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
    return safe_conversation_messages(rows, accessible_document_ids(user))


@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, user: dict = Depends(get_current_user)):
    with connect() as db:
        cursor = db.execute(
            "DELETE FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user["id"]),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        record_audit(db, user["id"], "conversation_deleted", conversation_id)
    return {"message": "Conversation deleted."}


@app.post("/chat")
def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    groups = get_user_groups(user["id"])
    if user["role"] == "admin":
        with connect() as db:
            group_ids = [row["id"] for row in db.execute("SELECT id FROM groups").fetchall()]
    else:
        group_ids = [group["id"] for group in groups]

    conversation_id = request.conversation_id or str(uuid4())
    with connect() as db:
        if request.conversation_id:
            conversation = db.execute(
                "SELECT id FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user["id"]),
            ).fetchone()
            if conversation is None:
                raise HTTPException(status_code=404, detail="Conversation not found.")
        else:
            db.execute(
                "INSERT INTO conversations (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, user["id"], request.question[:80], now_utc(), now_utc()),
            )

        history_rows = db.execute(
            "SELECT role, content, sources_json FROM conversation_messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 8",
            (conversation_id,),
        ).fetchall()
    history = safe_conversation_messages(
        list(reversed(history_rows)), accessible_document_ids(user)
    )

    try:
        answer, sources = answer_question(request.question, history, group_ids)
    except ValueError as error:
        if not request.conversation_id:
            with connect() as db:
                db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        raise HTTPException(status_code=409, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"The AI service could not answer: {error}") from error

    with connect() as db:
        db.executemany(
            """
            INSERT INTO conversation_messages (conversation_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (conversation_id, "user", request.question, "[]", now_utc()),
                (conversation_id, "assistant", answer, json.dumps(sources), now_utc()),
            ],
        )
        db.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now_utc(), conversation_id),
        )
        record_audit(db, user["id"], "chat_query", conversation_id)

    return {"conversation_id": conversation_id, "answer": answer, "sources": sources}
