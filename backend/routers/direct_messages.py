"""
计算机修行录 - 私信路由
"""
from fastapi import APIRouter, HTTPException, Request, Query

from models import DMIn, row_to_dict, now_iso
from database import get_db
from middleware import get_user_id

router = APIRouter(prefix="/api/dms", tags=["dms"])


@router.get("/conversations")
def list_conversations(request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        # 找到所有与我有私信往来的用户，取最新一条消息
        rows = conn.execute(
            """SELECT
                 CASE WHEN from_user_id=? THEN to_user_id ELSE from_user_id END AS other_id,
                 MAX(created_at) AS last_time,
                 SUM(CASE WHEN to_user_id=? AND is_read=0 THEN 1 ELSE 0 END) AS unread_count
               FROM direct_messages
               WHERE from_user_id=? OR to_user_id=?
               GROUP BY other_id
               ORDER BY last_time DESC""",
            (uid, uid, uid, uid),
        ).fetchall()

        conversations = []
        for r in rows:
            other = conn.execute(
                "SELECT id, username, name, avatar, title, level FROM users WHERE id=?",
                (r["other_id"],),
            ).fetchone()
            if not other:
                continue

            # 取最新一条消息预览
            last_msg = conn.execute(
                """SELECT content, created_at FROM direct_messages
                   WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?)
                   ORDER BY created_at DESC LIMIT 1""",
                (uid, r["other_id"], r["other_id"], uid),
            ).fetchone()

            conversations.append({
                "otherUser": dict(other),
                "lastTime": r["last_time"],
                "unreadCount": r["unread_count"] or 0,
                "lastMessage": last_msg["content"][:50] if last_msg else "",
            })
    return {"conversations": conversations}


@router.get("/{other_user_id}")
def get_messages(
    other_user_id: int,
    request: Request,
    since: str = Query(""),
    limit: int = Query(50, ge=1, le=100),
):
    uid = get_user_id(request)
    with get_db() as conn:
        # 标记对方发给我的消息为已读
        conn.execute(
            "UPDATE direct_messages SET is_read=1 WHERE to_user_id=? AND from_user_id=? AND is_read=0",
            (uid, other_user_id),
        )

        # 查询历史消息
        if since:
            rows = conn.execute(
                """SELECT * FROM direct_messages
                   WHERE ((from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?))
                   AND created_at > ?
                   ORDER BY created_at ASC""",
                (uid, other_user_id, other_user_id, uid, since),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM direct_messages
                   WHERE (from_user_id=? AND to_user_id=?) OR (from_user_id=? AND to_user_id=?)
                   ORDER BY created_at ASC LIMIT ?""",
                (uid, other_user_id, other_user_id, uid, limit),
            ).fetchall()

        messages = []
        for r in rows:
            d = row_to_dict(r)
            d["fromMe"] = d["from_user_id"] == uid
            messages.append(d)

    return {"messages": messages}


@router.post("/{other_user_id}")
def send_message(other_user_id: int, body: DMIn, request: Request):
    uid = get_user_id(request)
    if uid == other_user_id:
        raise HTTPException(400, "不能给自己发私信")

    with get_db() as conn:
        # 验证对方存在
        other = conn.execute("SELECT id FROM users WHERE id=?", (other_user_id,)).fetchone()
        if not other:
            raise HTTPException(404, "用户不存在")

        cur = conn.execute(
            "INSERT INTO direct_messages (from_user_id, to_user_id, content, created_at) VALUES (?,?,?,?)",
            (uid, other_user_id, body.content, now_iso()),
        )
        msg_id = cur.lastrowid
        row = conn.execute("SELECT * FROM direct_messages WHERE id=?", (msg_id,)).fetchone()

    d = row_to_dict(row)
    d["fromMe"] = True
    return {"message": d}
