"""
计算机修行录 - 消息路由
"""
from fastapi import APIRouter, HTTPException, Request

from models import MessageIn, now_iso, row_to_dict
from database import get_db, cleanup_old
from middleware import get_user_id

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("")
def list_messages(request: Request, page: int = 1, limit: int = 50):
    """分页获取消息列表。"""
    uid = get_user_id(request)
    offset = (page - 1) * limit
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM messages WHERE user_id=?
               ORDER BY pinned DESC, id DESC LIMIT ? OFFSET ?""",
            (uid, limit, offset),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@router.post("")
def add_message(msg: MessageIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (user_id, icon, text, time, unread, pinned) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, msg.icon, msg.text, msg.time or now_iso(), int(msg.unread), int(msg.pinned)),
        )
        cleanup_old(conn, uid)
        row = conn.execute("SELECT * FROM messages WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@router.put("/read-all")
def mark_all_read(request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("UPDATE messages SET unread=0 WHERE user_id=? AND unread=1", (uid,))
    return {"ok": True}


@router.put("/{msg_id}")
def update_message(msg_id: int, msg: MessageIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute(
            "UPDATE messages SET icon=?, text=?, time=?, unread=?, pinned=? WHERE id=? AND user_id=?",
            (msg.icon, msg.text, msg.time or now_iso(), int(msg.unread), int(msg.pinned), msg_id, uid),
        )
        row = conn.execute(
            "SELECT * FROM messages WHERE id=? AND user_id=?", (msg_id, uid)
        ).fetchone()
    return row_to_dict(row) if row else {"ok": False}


@router.delete("/{msg_id}")
def delete_message(msg_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("DELETE FROM messages WHERE id=? AND user_id=?", (msg_id, uid))
    return {"ok": True}
