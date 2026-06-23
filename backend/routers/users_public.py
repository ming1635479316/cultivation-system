"""
计算机修行录 - 公开用户路由（搜索 + 个人主页）
"""
from fastapi import APIRouter, HTTPException, Request, Query

from models import row_to_dict, user_row_to_dict, json_loads
from database import get_db
from middleware import get_user_id
from services.stats import calc_stats, calc_progress

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/search")
def search_users(request: Request, q: str = Query("", min_length=1, max_length=32)):
    get_user_id(request)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, username, name, avatar, title, level FROM users WHERE username LIKE ? LIMIT 20",
            (f"%{q}%",),
        ).fetchall()
    return {"users": [dict(r) for r in rows]}


@router.get("/{user_id}")
def get_public_profile(user_id: int, request: Request):
    get_user_id(request)
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        user_data = user_row_to_dict(user)

        # 计算战力
        events = [
            row_to_dict(r)
            for r in conn.execute("SELECT * FROM events WHERE user_id=?", (user_id,)).fetchall()
        ]
        stats = calc_stats(user_data.get("level", 0), events)

        # 最近帖子
        posts = []
        post_rows = conn.execute(
            """SELECT id, title, type, vote_score, comment_count, created_at
               FROM posts WHERE user_id=? ORDER BY created_at DESC LIMIT 5""",
            (user_id,),
        ).fetchall()
        for pr in post_rows:
            d = dict(pr)
            d["tags"] = json_loads(d.get("tags", "[]"))
            posts.append(d)

    return {"user": user_data, "stats": stats, "recentPosts": posts}
