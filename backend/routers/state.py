"""
计算机修行录 - 状态路由（只读启动同步 + 个人资料更新）
"""
from fastapi import APIRouter, Request

from models import StateOut, ProfileUpdateIn, row_to_dict, user_row_to_dict, now_iso
from database import get_db
from middleware import get_user_id
from services.stats import calc_stats, calc_progress

router = APIRouter(prefix="/api", tags=["state"])


@router.get("/state", response_model=StateOut)
def get_state(request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        events_rows = conn.execute(
            "SELECT * FROM events WHERE user_id=? ORDER BY id", (uid,)
        ).fetchall()
        messages_rows = conn.execute(
            "SELECT * FROM messages WHERE user_id=? ORDER BY pinned DESC, id DESC", (uid,)
        ).fetchall()
        journals_rows = conn.execute(
            "SELECT * FROM journals WHERE user_id=? ORDER BY id DESC", (uid,)
        ).fetchall()

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

    # 后端计算 stats 和 progress
    level = user_data.get("level", 0)
    completed = user_data.get("completedTasks", [])
    stats = calc_stats(level, events_data)
    progress = calc_progress(level, completed)

    return StateOut(
        user=user_data,
        events=events_data,
        messages=[row_to_dict(r) for r in messages_rows],
        journals=[row_to_dict(r) for r in journals_rows],
        lastModified=last_modified,
        stats=stats,
        progress=progress,
    )


@router.put("/user/profile")
def update_profile(body: ProfileUpdateIn, request: Request):
    """更新个人资料（名字、头像、性别、年龄、联系方式）。"""
    uid = get_user_id(request)
    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.avatar is not None:
        updates["avatar"] = body.avatar
    if body.title is not None:
        updates["title"] = body.title
    if body.gender is not None:
        updates["gender"] = body.gender
    if body.age is not None:
        updates["age"] = body.age
    if body.contact is not None:
        updates["contact"] = body.contact

    if not updates:
        return {"ok": True}

    updates["updated_at"] = now_iso()

    set_clause = ", ".join(f"{k}=?" for k in updates.keys())
    values = list(updates.values()) + [uid]

    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", values)
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

    return {"ok": True, "user": user_row_to_dict(user)}
