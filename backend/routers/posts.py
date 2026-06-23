"""
计算机修行录 - 社区帖子路由
"""
import json

from fastapi import APIRouter, HTTPException, Request, Query

from models import PostIn, PostUpdateIn, row_to_dict, now_iso, json_dumps, json_loads
from database import get_db
from middleware import get_user_id
from services.events import record_event

router = APIRouter(prefix="/api/posts", tags=["posts"])


def _post_with_author(conn, row):
    """将帖子行附加作者信息。"""
    d = row_to_dict(row)
    d["tags"] = json_loads(d.get("tags", "[]"))
    author = conn.execute(
        "SELECT username, name, avatar, title, level FROM users WHERE id=?",
        (d["user_id"],)
    ).fetchone()
    if author:
        d["author"] = dict(author)
    return d


@router.get("")
def list_posts(
    request: Request,
    sort: str = Query("newest"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
):
    get_user_id(request)
    offset = (page - 1) * limit

    if sort == "hot":
        order = "(p.vote_score * 2 + p.comment_count) DESC, p.created_at DESC"
    elif sort == "questions":
        order = "p.created_at DESC"
        extra_where = " AND p.type='question'"
    elif sort == "articles":
        order = "p.created_at DESC"
        extra_where = " AND p.type='article'"
    else:  # newest
        order = "p.created_at DESC"
        extra_where = ""

    sql = (
        "SELECT p.* FROM posts p WHERE 1=1"
        + extra_where +
        f" ORDER BY {order} LIMIT ? OFFSET ?"
    )

    with get_db() as conn:
        rows = conn.execute(sql, (limit, offset)).fetchall()
        posts = [_post_with_author(conn, r) for r in rows]
    return {"posts": posts, "page": page, "sort": sort}


@router.post("")
def create_post(body: PostIn, request: Request):
    uid = get_user_id(request)
    tags_json = json_dumps(body.tags)

    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO posts (user_id, title, content, type, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (uid, body.title, body.content, body.type, tags_json, now_iso(), now_iso()),
        )
        post_id = cur.lastrowid
        record_event(conn, uid, "post_create", value={"theory": 2}, ref=f"post_{post_id}")

        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        result = _post_with_author(conn, row)
    return {"post": result}


@router.get("/{post_id}")
def get_post(post_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        if not row:
            raise HTTPException(404, "帖子不存在")
        post = _post_with_author(conn, row)

        # 当前用户是否已投票
        vote = conn.execute(
            "SELECT value FROM votes WHERE user_id=? AND target_type='post' AND target_id=?",
            (uid, post_id),
        ).fetchone()
        post["user_vote"] = vote["value"] if vote else 0

    return {"post": post}


@router.put("/{post_id}")
def update_post(post_id: int, body: PostUpdateIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        if not row:
            raise HTTPException(404, "帖子不存在")
        if row["user_id"] != uid:
            raise HTTPException(403, "只能编辑自己的帖子")

        updates = {}
        if body.title is not None:
            updates["title"] = body.title
        if body.content is not None:
            updates["content"] = body.content
        if body.tags is not None:
            updates["tags"] = json_dumps(body.tags)

        if updates:
            updates["updated_at"] = now_iso()
            set_clause = ", ".join(f"{k}=?" for k in updates)
            values = list(updates.values()) + [post_id]
            conn.execute(f"UPDATE posts SET {set_clause} WHERE id=?", values)

        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        result = _post_with_author(conn, row)
    return {"post": result}


@router.delete("/{post_id}")
def delete_post(post_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        if not row:
            raise HTTPException(404, "帖子不存在")
        if row["user_id"] != uid:
            raise HTTPException(403, "只能删除自己的帖子")

        conn.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
        conn.execute("DELETE FROM votes WHERE target_type='post' AND target_id=?", (post_id,))
        conn.execute("DELETE FROM posts WHERE id=?", (post_id,))
    return {"ok": True}
