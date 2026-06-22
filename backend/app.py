"""
计算机修行录 - 后端服务
FastAPI + SQLite · v2.0 多用户版
"""

import hashlib
import json
import os
import secrets
import sqlite3
import bcrypt
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 生产环境可通过 DATA_DIR 把数据库挂在持久卷，例如 /data
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, "cultivation.db")

WEB_DIR = os.path.join(BASE_DIR, "..", "web")

MAX_EVENTS = 500
MAX_MESSAGES = 200

# 允许前端写入的 event 类型；不在白名单内的会被过滤
VALID_EVENT_TYPES = {
    "task_done", "quiz_pass", "resource_read", "tool_unlock", "config_file", "journal_write"
}

# 每个段位的任务数量（与前端 data.js 保持一致）
LEVEL_TASKS = {
    0: 0, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 2, 9: 0,
}

# 事件对四维属性的贡献（与前端 EVENT_CONFIG 保持一致）
EVENT_CONFIG = {
    "task_done": {"coding": 0, "project": 0, "tools": 0},
    "quiz_pass": {"coding": 10, "theory": 8},
    "quiz_correct": {"theory": 2},
    "resource_read": {"theory": 3},
    "tool_unlock": {"tools": 8},
    "config_file": {"tools": 5},
    "journal_write": {"coding": 3, "theory": 5},
}


def get_task_reward(level_id: int) -> dict[str, int]:
    """关卡任务奖励（与前端 getTaskReward 保持一致）。"""
    if level_id <= 1:
        return {"coding": 5, "project": 2}
    if level_id == 2:
        return {"coding": 8, "project": 4}
    if level_id == 3:
        return {"coding": 10, "project": 5, "tools": 3}
    return {"coding": 12, "project": 8, "tools": 5}


def get_base_stats(level: int) -> dict[str, int]:
    """段位基础属性（与前端 getBaseStats 保持一致）。"""
    return {
        "coding": level * 8,
        "project": level * 6,
        "theory": level * 7,
        "tools": level * 6,
    }


def calc_stats(level: int, events: list[dict]) -> dict[str, int]:
    """后端计算四维属性，与前端 calcStats 保持一致。"""
    stats = get_base_stats(level)
    for e in events:
        cfg = EVENT_CONFIG.get(e.get("type"))
        if not cfg:
            continue
        value = e.get("value") or {}
        for stat, base in cfg.items():
            stats[stat] = stats.get(stat, 0) + value.get(stat, base)
    for k in stats:
        stats[k] = max(0, min(100, round(stats[k])))
    return stats


def calc_progress(level: int, completed_tasks: list[str]) -> int:
    """后端计算段位进度，与前端 calcProgress 保持一致。"""
    total = LEVEL_TASKS.get(level, 0)
    if total == 0:
        return 100
    done = sum(1 for t in completed_tasks if t.startswith(f"{level}-"))
    return round((done / total) * 100)


# 安全：CORS 来源通过环境变量配置，默认只允许本地开发地址
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "")
if CORS_ORIGINS:
    ALLOW_ORIGINS = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
else:
    ALLOW_ORIGINS = [
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

# 登录失败次数限制（内存级，单机够用；多实例请用 Redis）
_LOGIN_ATTEMPTS = {}


def _get_client_ip(request: Request) -> str:
    """优先取 X-Forwarded-For，适用于反向代理后。"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_login_rate_limit(client_ip: str):
    """5 分钟内同一 IP 最多 5 次登录尝试。"""
    now = datetime.now(timezone.utc)
    attempts = _LOGIN_ATTEMPTS.get(client_ip, [])
    attempts = [t for t in attempts if now - t < timedelta(minutes=5)]
    if len(attempts) >= 5:
        raise HTTPException(429, "登录尝试过多，请 5 分钟后再试")
    attempts.append(now)
    _LOGIN_ATTEMPTS[client_ip] = attempts


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
    allow_origins=ALLOW_ORIGINS,
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
                created_at  TEXT    DEFAULT (datetime('now')),
                expires_at  TEXT    NOT NULL DEFAULT (datetime('now', '+7 days'))
            );

            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                type        TEXT    NOT NULL,
                value       TEXT,
                ref         TEXT,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                icon        TEXT    DEFAULT '',
                text        TEXT    NOT NULL,
                time        TEXT    DEFAULT (datetime('now')),
                unread      INTEGER DEFAULT 1,
                pinned      INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS journals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL DEFAULT 1,
                title       TEXT    NOT NULL,
                body        TEXT    NOT NULL,
                date        TEXT    DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
            CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id);
        """)

        # 给旧 events 表添加 ref 字段（如果还没有）
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(events)")]
        if "ref" not in cols:
            try:
                conn.execute("ALTER TABLE events ADD COLUMN ref TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # 给旧 tokens 表添加 expires_at 字段（如果还没有）
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(tokens)")]
        if "expires_at" not in cols:
            try:
                conn.execute(
                    "ALTER TABLE tokens ADD COLUMN expires_at TEXT"
                )
                conn.commit()
                cols = [row["name"] for row in conn.execute("PRAGMA table_info(tokens)")]
            except sqlite3.OperationalError:
                pass

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

        # 清理过期 token（确保列存在后再执行）
        if "expires_at" in cols:
            cleanup_expired_tokens(conn)


def cleanup_expired_tokens(conn: sqlite3.Connection):
    """清理过期 token（兼容无时区字符串，按 UTC 处理）"""
    rows = conn.execute("SELECT token, expires_at FROM tokens").fetchall()
    now = datetime.now(timezone.utc)
    for token, expires_at in rows:
        if not expires_at:
            continue
        try:
            exp = datetime.fromisoformat(expires_at)
        except ValueError:
            continue
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < now:
            conn.execute("DELETE FROM tokens WHERE token=?", (token,))


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
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    """验证密码，兼容旧版 SHA256。"""
    # bcrypt 哈希以 $2 开头
    if hashed.startswith("$"):
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    # 兼容旧版 SHA256
    return hashed == hashlib.sha256(pw.encode()).hexdigest()


def get_user_id(request: Request) -> int:
    """从请求头提取 token，返回 user_id，并检查是否过期。"""
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "请先登录")
    with get_db() as conn:
        row = conn.execute("SELECT user_id, expires_at FROM tokens WHERE token=?", (token,)).fetchone()
        if not row:
            raise HTTPException(401, "登录已过期，请重新登录")
        if row["expires_at"]:
            exp = datetime.fromisoformat(row["expires_at"])
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                conn.execute("DELETE FROM tokens WHERE token=?", (token,))
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


class TaskAction(BaseModel):
    level_id: int = Field(..., ge=0, le=9)
    task_idx: int = Field(..., ge=0)


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
def login(body: LoginIn, request: Request):
    client_ip = _get_client_ip(request)
    _check_login_rate_limit(client_ip)
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (body.username,),
        ).fetchone()
        if not user or not verify_password(body.password, user["password"]):
            raise HTTPException(401, "用户名或密码错误")

        # 旧版 SHA256 密码自动升级为 bcrypt
        if not user["password"].startswith("$"):
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hash_password(body.password), user["id"]),
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        conn.execute(
            "INSERT INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user["id"], expires_at.isoformat()),
        )
        cleanup_expired_tokens(conn)

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
        if ev.get("ref") is None:
            ev.pop("ref", None)
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

        # 基本校验：level 必须是整数 0~9
        level = u.get("level", 0)
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 0
        if level < 0 or level > 9:
            level = 0

        conn.execute(
            """UPDATE users SET name=?, avatar=?, title=?, level=?, gender=?, age=?,
               contact=?, joined_date=?, specializations=?, completed_tasks=?, updated_at=?
               WHERE id=?""",
            (
                u.get("name", ""),
                u.get("avatar", ""),
                u.get("title", "修炼者"),
                level,
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

        # 事件：只接受白名单内的类型，过滤掉非法类型
        conn.execute("DELETE FROM events WHERE user_id=?", (uid,))
        for e in state.events:
            ev_type = e.get("type")
            if ev_type not in VALID_EVENT_TYPES:
                continue
            conn.execute(
                "INSERT INTO events (user_id, id, type, value, ref, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (uid, e.get("id"), ev_type,
                 json.dumps(e.get("value", {}), ensure_ascii=False) if e.get("value") else None,
                 e.get("ref"),
                 e.get("date") or e.get("created_at", now_iso())),
            )

        # 消息
        conn.execute("DELETE FROM messages WHERE user_id=?", (uid,))
        for m in state.messages:
            conn.execute(
                "INSERT INTO messages (user_id, id, icon, text, time, unread, pinned) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uid, m.get("id"), m.get("icon", ""), m["text"],
                 m.get("time", now_iso()),
                 int(m.get("unread", True)), int(m.get("pinned", False))),
            )

        # 感悟
        conn.execute("DELETE FROM journals WHERE user_id=?", (uid,))
        for j in state.journals:
            conn.execute(
                "INSERT INTO journals (user_id, id, title, body, date) VALUES (?, ?, ?, ?, ?)",
                (uid, j.get("id"), j["title"], j["body"],
                 j.get("date", now_iso())),
            )

        cleanup_old(conn, uid)

    return {"ok": True, "lastModified": now_ts}


@app.post("/api/tasks/complete")
def complete_task(action: TaskAction, request: Request):
    """完成关卡任务。后端校验并记录，防止前端伪造。"""
    uid = get_user_id(request)
    key = f"{action.level_id}-{action.task_idx}"

    total = LEVEL_TASKS.get(action.level_id)
    if total is None or action.task_idx < 0 or action.task_idx >= total:
        raise HTTPException(400, "任务不存在")

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        completed_tasks = json.loads(user["completed_tasks"] or "[]")
        if key in completed_tasks:
            raise HTTPException(400, "任务已完成")

        level = user["level"]
        if action.level_id > level:
            raise HTTPException(400, "段位不足")

        completed_tasks.append(key)

        reward = get_task_reward(action.level_id)
        conn.execute(
            "INSERT INTO events (user_id, type, value, ref, created_at) VALUES (?, ?, ?, ?, ?)",
            (uid, "task_done", json.dumps(reward, ensure_ascii=False), key, now_iso()),
        )

        conn.execute(
            "UPDATE users SET completed_tasks=?, updated_at=? WHERE id=?",
            (json.dumps(completed_tasks, ensure_ascii=False), now_iso(), uid),
        )

        events = [row_to_dict(r) for r in conn.execute("SELECT * FROM events WHERE user_id=?", (uid,)).fetchall()]
        stats = calc_stats(level, events)
        progress = calc_progress(level, completed_tasks)

    return {
        "ok": True,
        "key": key,
        "reward": reward,
        "completedTasks": completed_tasks,
        "stats": stats,
        "progress": progress,
        "level": level,
    }


@app.post("/api/tasks/undo")
def undo_task(action: TaskAction, request: Request):
    """取消完成关卡任务，并删除对应事件。"""
    uid = get_user_id(request)
    key = f"{action.level_id}-{action.task_idx}"

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        completed_tasks = json.loads(user["completed_tasks"] or "[]")
        if key not in completed_tasks:
            raise HTTPException(400, "任务未完成")

        completed_tasks.remove(key)

        # 删除该任务对应的最新 task_done 事件
        conn.execute(
            """DELETE FROM events WHERE id = (
                SELECT id FROM events WHERE user_id=? AND type=? AND ref=? ORDER BY id DESC LIMIT 1
            )""",
            (uid, "task_done", key),
        )

        conn.execute(
            "UPDATE users SET completed_tasks=?, updated_at=? WHERE id=?",
            (json.dumps(completed_tasks, ensure_ascii=False), now_iso(), uid),
        )

        level = user["level"]
        events = [row_to_dict(r) for r in conn.execute("SELECT * FROM events WHERE user_id=?", (uid,)).fetchall()]
        stats = calc_stats(level, events)
        progress = calc_progress(level, completed_tasks)

    return {
        "ok": True,
        "key": key,
        "completedTasks": completed_tasks,
        "stats": stats,
        "progress": progress,
        "level": level,
    }


@app.post("/api/messages")
def add_message(msg: MessageIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (user_id, icon, text, time, unread, pinned) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, msg.icon, msg.text, msg.time or now_iso(),
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
            (msg.icon, msg.text, msg.time or now_iso(),
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
             journal.date or now_iso()),
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
