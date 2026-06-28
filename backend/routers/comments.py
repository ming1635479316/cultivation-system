"""
计算机修行录 - 评论路由
"""
from fastapi import APIRouter, HTTPException, Request

from models import CommentIn, row_to_dict, now_iso
from database import get_db
from middleware import get_user_id, _get_client_ip
from services.events import record_event
from services.ip_geo import get_ip_province

router = APIRouter(prefix="/api/posts/{post_id}/comments", tags=["comments"])


def _comment_with_author(conn, row):
    """将评论行附加作者信息。"""
    d = row_to_dict(row)
    author = conn.execute(
        "SELECT id, username, name, avatar, title, level FROM users WHERE id=?",
        (d["user_id"],)
    ).fetchone()
    if author:
        d["author"] = dict(author)
    # IP 属地
    ip = d.get("ip", "")
    d["ip_province"] = get_ip_province(ip) if ip else ""
    return d


@router.get("")
def list_comments(post_id: int, request: Request):
    get_user_id(request)
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.*, u.id AS author_id, u.username, u.name, u.avatar, u.title, u.level
               FROM comments c JOIN users u ON c.user_id = u.id
               WHERE c.post_id=? ORDER BY c.created_at ASC""",
            (post_id,),
        ).fetchall()

        all_comments = []
        for r in rows:
            d = row_to_dict(r)
            d["author"] = {
                "id": r["author_id"], "username": r["username"], "name": r["name"],
                "avatar": r["avatar"], "title": r["title"], "level": r["level"],
            }
            # IP 属地
            ip = d.get("ip", "")
            d["ip_province"] = get_ip_province(ip) if ip else ""
            all_comments.append(d)

        # 组装嵌套结构（1 级）
        parents = [c for c in all_comments if c.get("parent_id") is None]
        children = [c for c in all_comments if c.get("parent_id") is not None]
        children_by_parent = {}
        for child in children:
            pid = child["parent_id"]
            if pid not in children_by_parent:
                children_by_parent[pid] = []
            children_by_parent[pid].append(child)

        for p in parents:
            p["replies"] = children_by_parent.get(p["id"], [])

    return {"comments": parents}


@router.post("")
def create_comment(post_id: int, body: CommentIn, request: Request):
    uid = get_user_id(request)
    client_ip = _get_client_ip(request) or "unknown"
    with get_db() as conn:
        # 验证帖子存在
        post = conn.execute("SELECT id FROM posts WHERE id=?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(404, "帖子不存在")

        # 验证 parent_id 存在且属于同一帖子
        parent_id = body.parent_id
        if parent_id is not None:
            parent = conn.execute(
                "SELECT id, post_id FROM comments WHERE id=?", (parent_id,)
            ).fetchone()
            if not parent or parent["post_id"] != post_id:
                raise HTTPException(400, "父评论不存在或不属于此帖子")

        cur = conn.execute(
            "INSERT INTO comments (user_id, post_id, parent_id, content, ip, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, post_id, parent_id, body.content, client_ip, now_iso()),
        )
        comment_id = cur.lastrowid

        conn.execute("UPDATE posts SET comment_count = comment_count + 1 WHERE id=?", (post_id,))
        record_event(conn, uid, "comment_create", value={"theory": 1}, ref=f"comment_{comment_id}")

        row = conn.execute("SELECT * FROM comments WHERE id=?", (comment_id,)).fetchone()
        return {"comment": _comment_with_author(conn, row)}


@router.delete("/{comment_id}")
def delete_comment(post_id: int, comment_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM comments WHERE id=?", (comment_id,)).fetchone()
        if not row:
            raise HTTPException(404, "评论不存在")
        if row["user_id"] != uid:
            raise HTTPException(403, "只能删除自己的评论")

        # 删除子评论 + 自身
        deleted = 1
        child_rows = conn.execute(
            "SELECT id FROM comments WHERE parent_id=?", (comment_id,)
        ).fetchall()
        for cr in child_rows:
            conn.execute("DELETE FROM comments WHERE id=?", (cr["id"],))
            deleted += 1
        conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
        conn.execute(
            "UPDATE posts SET comment_count = MAX(0, comment_count - ?) WHERE id=?",
            (deleted, post_id),
        )
    return {"ok": True}
