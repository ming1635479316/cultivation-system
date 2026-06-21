"""
计算机修行录 - 后端服务
FastAPI + SQLite · v2.0 多用户版
"""

import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Railway 挂载持久卷，数据库文件放 /data 目录
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, "cultivation.db")

WEB_DIR = os.path.join(BASE_DIR, "..", "web")

MAX_EVENTS = 500
MAX_MESSAGES = 200


# ============================================================
# 应用生命周期
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="计算机修行录 API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 数据库
# ============================================================

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """建表 + 迁移"""
    # 迁移：用独立连接避免事务冲突
    migrations = [
        "ALTER TABLE user RENAME TO user_old",
        "ALTER TABLE events ADD COLUMN user_id INTEGER DEFAULT 1",
        "ALTER TABLE messages ADD COLUMN user_id INTEGER DEFAULT 1",
        "ALTER TABLE journals ADD COLUMN user_id INTEGER DEFAULT 1",
    ]
    for ddl in migrations:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(ddl)
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            pass

    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                name        TEXT    DEFAULT '',
                avatar      TEXT    DEFAULT '',
                title       TEXT    DEFAULT '修炼者',
                level       INTEGER DEFAULT 0,
                gender      TEXT    DEFAULT '',
                age         TEXT    DEFAULT '',
                contact     TEXT    DEFAULT '',
                joined_date TEXT    DEFAULT (date('now')),
                specializations TEXT DEFAULT '[]',
                completed_tasks TEXT DEFAULT '[]',
                updated_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tokens (
                token       TEXT    PRIMARY KEY,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                type        TEXT    NOT NULL,
                value       TEXT,
                created_at  TEXT    DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                icon        TEXT    DEFAULT '',
                text        TEXT    NOT NULL,
                time        TEXT    DEFAULT (datetime('now', 'localtime')),
                unread      INTEGER DEFAULT 1,
                pinned      INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS journals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                title       TEXT    NOT NULL,
                body        TEXT    NOT NULL,
                date        TEXT    DEFAULT (datetime('now', 'localtime'))
            );
        """)

        # 迁移旧数据：把 user_old 的数据迁到 users 表
        try:
            old = conn.execute("SELECT * FROM user_old WHERE id=1").fetchone()
            if old:
                d = dict(old)
                existing = conn.execute("SELECT id FROM users WHERE id=1").fetchone()
                if not existing:
                    conn.execute(
                        """INSERT INTO users (id, username, password, name, avatar, title, level,
                           gender, age, contact, joined_date, specializations, completed_tasks)
                           VALUES (1, 'admin', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (hash_password('admin'), d.get('name','易'), d.get('avatar','易'),
                         d.get('title','修炼者'), d.get('level',0), d.get('gender',''),
                         d.get('age',''), d.get('contact',''), d.get('joined_date','2026-06-13'),
                         d.get('specializations','[]'), d.get('completed_tasks','[]')))
            conn.execute("DROP TABLE IF EXISTS user_old")
            conn.execute("DROP TABLE IF EXISTS user")
        except sqlite3.OperationalError:
            pass


def cleanup_old(conn, user_id: int):
    """清理超量数据"""
    for table, limit in [("events", MAX_EVENTS), ("messages", MAX_MESSAGES)]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id=?", (user_id,)).fetchone()[0]
        if cnt > limit:
            conn.execute(
                f"DELETE FROM {table} WHERE user_id=? AND id NOT IN "
                f"(SELECT id FROM {table} WHERE user_id=? ORDER BY id DESC LIMIT {limit})",
                (user_id, user_id),
            )


# ============================================================
# 鉴权
# ============================================================

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_user_id(request: Request) -> int:
    """从请求头提取 token，返回 user_id"""
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "请先登录")
    with get_db() as conn:
        row = conn.execute("SELECT user_id FROM tokens WHERE token=?", (token,)).fetchone()
    if not row:
        raise HTTPException(401, "登录已过期，请重新登录")
    return row["user_id"]


# ============================================================
# Pydantic 模型
# ============================================================

class RegisterIn(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=4, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class AuthOut(BaseModel):
    token: str
    user: dict[str, Any]


class StateOut(BaseModel):
    user: dict[str, Any]
    events: list[dict[str, Any]]
    messages: list[dict[str, Any]]
    journals: list[dict[str, Any]]
    lastModified: str = ""


class MessageIn(BaseModel):
    icon: str = ""
    text: str
    time: str | None = None
    unread: bool = True
    pinned: bool = False


class JournalIn(BaseModel):
    title: str
    body: str
    date: str | None = None


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    for key in ("specializations", "completed_tasks", "value"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except json.JSONDecodeError:
                pass
    for key in ("unread", "pinned"):
        if key in d:
            d[key] = bool(d[key])
    return d


def user_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = row_to_dict(row)
    # 移除敏感字段
    d.pop("password", None)
    # 驼峰转换
    if "joined_date" in d:
        d["joinedDate"] = d.pop("joined_date")
    if "completed_tasks" in d:
        d["completedTasks"] = d.pop("completed_tasks")
    return d


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# 认证 API
# ============================================================

@app.post("/api/auth/register", response_model=AuthOut)
def register(body: RegisterIn):
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM users WHERE username=?", (body.username,)).fetchone()
        if exists:
            raise HTTPException(400, "用户名已被注册")

        cur = conn.execute(
            "INSERT INTO users (username, password, name, avatar) VALUES (?, ?, ?, ?)",
            (body.username, hash_password(body.password), body.username, body.username[:2]),
        )
        user_id = cur.lastrowid

        token = secrets.token_urlsafe(32)
        conn.execute("INSERT INTO tokens (token, user_id) VALUES (?, ?)", (token, user_id))

        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    return AuthOut(token=token, user=user_row_to_dict(user))


@app.post("/api/auth/login", response_model=AuthOut)
def login(body: LoginIn):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (body.username, hash_password(body.password)),
        ).fetchone()
        if not user:
            raise HTTPException(401, "用户名或密码错误")

        token = secrets.token_urlsafe(32)
        conn.execute("INSERT INTO tokens (token, user_id) VALUES (?, ?)", (token, user["id"]))

    return AuthOut(token=token, user=user_row_to_dict(user))


@app.post("/api/auth/logout")
def logout(request: Request):
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if token:
        with get_db() as conn:
            conn.execute("DELETE FROM tokens WHERE token=?", (token,))
    return {"ok": True}


# ============================================================
# 数据 API（全部需要登录）
# ============================================================

@app.get("/api/state", response_model=StateOut)
def get_state(request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        events_rows = conn.execute("SELECT * FROM events WHERE user_id=? ORDER BY id", (uid,)).fetchall()
        messages_rows = conn.execute("SELECT * FROM messages WHERE user_id=? ORDER BY pinned DESC, id DESC", (uid,)).fetchall()
        journals_rows = conn.execute("SELECT * FROM journals WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()

    user_data = user_row_to_dict(user) if user else {}
    last_modified = user_data.get("updated_at", "")

    events_data = []
    for r in events_rows:
        ev = row_to_dict(r)
        if "created_at" in ev:
            ev["date"] = ev.pop("created_at")
        events_data.append(ev)

    return StateOut(
        user=user_data,
        events=events_data,
        messages=[row_to_dict(r) for r in messages_rows],
        journals=[row_to_dict(r) for r in journals_rows],
        lastModified=last_modified,
    )


@app.post("/api/state")
def save_state(state: StateOut, request: Request):
    uid = get_user_id(request)
    now_ts = now_iso()

    with get_db() as conn:
        u = state.user
        conn.execute(
            """UPDATE users SET name=?, avatar=?, title=?, level=?, gender=?, age=?,
               contact=?, joined_date=?, specializations=?, completed_tasks=?, updated_at=?
               WHERE id=?""",
            (
                u.get("name", ""),
                u.get("avatar", ""),
                u.get("title", "修炼者"),
                u.get("level", 0),
                u.get("gender", ""),
                u.get("age", ""),
                u.get("contact", ""),
                u.get("joinedDate") or u.get("joined_date", ""),
                json.dumps(u.get("specializations", []), ensure_ascii=False),
                json.dumps(u.get("completedTasks") or u.get("completed_tasks", []), ensure_ascii=False),
                now_ts,
                uid,
            ),
        )

        # 事件
        conn.execute("DELETE FROM events WHERE user_id=?", (uid,))
        for e in state.events:
            conn.execute(
                "INSERT INTO events (user_id, id, type, value, created_at) VALUES (?, ?, ?, ?, ?)",
                (uid, e.get("id"), e["type"],
                 json.dumps(e.get("value", {}), ensure_ascii=False) if e.get("value") else None,
                 e.get("date") or e.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            )

        # 消息
        conn.execute("DELETE FROM messages WHERE user_id=?", (uid,))
        for m in state.messages:
            conn.execute(
                "INSERT INTO messages (user_id, id, icon, text, time, unread, pinned) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uid, m.get("id"), m.get("icon", ""), m["text"],
                 m.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                 int(m.get("unread", True)), int(m.get("pinned", False))),
            )

        # 感悟
        conn.execute("DELETE FROM journals WHERE user_id=?", (uid,))
        for j in state.journals:
            conn.execute(
                "INSERT INTO journals (user_id, id, title, body, date) VALUES (?, ?, ?, ?, ?)",
                (uid, j.get("id"), j["title"], j["body"],
                 j.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            )

        cleanup_old(conn, uid)

    return {"ok": True, "lastModified": now_ts}


@app.post("/api/messages")
def add_message(msg: MessageIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (user_id, icon, text, time, unread, pinned) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, msg.icon, msg.text, msg.time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             int(msg.unread), int(msg.pinned)),
        )
        cleanup_old(conn, uid)
        row = conn.execute("SELECT * FROM messages WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.put("/api/messages/{msg_id}")
def update_message(msg_id: int, msg: MessageIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute(
            "UPDATE messages SET icon=?, text=?, time=?, unread=?, pinned=? WHERE id=? AND user_id=?",
            (msg.icon, msg.text, msg.time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             int(msg.unread), int(msg.pinned), msg_id, uid),
        )
        row = conn.execute("SELECT * FROM messages WHERE id=? AND user_id=?", (msg_id, uid)).fetchone()
    return row_to_dict(row) if row else {"ok": False}


@app.delete("/api/messages/{msg_id}")
def delete_message(msg_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE id=? AND user_id=?", (msg_id, uid))
    return {"ok": True}


@app.put("/api/messages/read-all")
def mark_all_read(request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("UPDATE messages SET unread=0 WHERE user_id=? AND unread=1", (uid,))
    return {"ok": True}


@app.post("/api/journals")
def add_journal(journal: JournalIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO journals (user_id, title, body, date) VALUES (?, ?, ?, ?)",
            (uid, journal.title, journal.body,
             journal.date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        row = conn.execute("SELECT * FROM journals WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.delete("/api/journals/{journal_id}")
def delete_journal(journal_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("DELETE FROM journals WHERE id=? AND user_id=?", (journal_id, uid))
    return {"ok": True}


@app.get("/api/health")
def health():
    return {"status": "ok", "db": os.path.exists(DB_PATH), "version": "2.0.0"}


# 静态文件
if os.path.isdir(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    host, port = "0.0.0.0", 8001
    print(f"数据库: {DB_PATH}")
    print(f"服务: http://{host}:{port}")
    print(f"文档: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)
