"""
计算机修行录 - 状态路由（只读启动同步）
"""
from fastapi import APIRouter, Request

from models import StateOut, row_to_dict, user_row_to_dict
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
