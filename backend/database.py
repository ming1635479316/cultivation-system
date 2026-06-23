"""
计算机修行录 - 数据库层
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from config import DB_PATH, MAX_EVENTS, MAX_MESSAGES


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
        cnt = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE user_id=?", (user_id,)
        ).fetchone()[0]
        if cnt > limit:
            conn.execute(
                f"DELETE FROM {table} WHERE user_id=? AND id NOT IN "
                f"(SELECT id FROM {table} WHERE user_id=? ORDER BY id DESC LIMIT {limit})",
                (user_id, user_id),
            )


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

        # 给旧 events 表添加 ref 字段
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(events)")]
        if "ref" not in cols:
            try:
                conn.execute("ALTER TABLE events ADD COLUMN ref TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # 给旧 tokens 表添加 expires_at 字段
        cols = [row["name"] for row in conn.execute("PRAGMA table_info(tokens)")]
        if "expires_at" not in cols:
            try:
                conn.execute("ALTER TABLE tokens ADD COLUMN expires_at TEXT")
                conn.commit()
                cols = [row["name"] for row in conn.execute("PRAGMA table_info(tokens)")]
            except sqlite3.OperationalError:
                pass

        # 迁移旧 user_old 数据
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
                        (_hash_password('admin'), d.get('name', '易'), d.get('avatar', '易'),
                         d.get('title', '修炼者'), d.get('level', 0), d.get('gender', ''),
                         d.get('age', ''), d.get('contact', ''), d.get('joined_date', '2026-06-13'),
                         d.get('specializations', '[]'), d.get('completed_tasks', '[]')))
            conn.execute("DROP TABLE IF EXISTS user_old")
            conn.execute("DROP TABLE IF EXISTS user")
        except sqlite3.OperationalError:
            pass

        # 清理过期 token
        if "expires_at" in cols:
            cleanup_expired_tokens(conn)


def _hash_password(pw: str) -> str:
    """数据库迁移用的哈希，避免循环导入"""
    import bcrypt
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
