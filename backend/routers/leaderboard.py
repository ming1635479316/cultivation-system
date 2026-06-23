"""
计算机修行录 - 排行榜路由
"""
from fastapi import APIRouter, Request

from models import row_to_dict
from database import get_db
from middleware import get_user_id
from services.stats import calc_stats

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def get_leaderboard(request: Request):
    get_user_id(request)
    with get_db() as conn:
        users = conn.execute(
            "SELECT id, username, name, avatar, title, level, joined_date "
            "FROM users WHERE id > 0"
        ).fetchall()

        board = []
        for u in users:
            events = [
                row_to_dict(r) for r in
                conn.execute("SELECT * FROM events WHERE user_id=?", (u["id"],)).fetchall()
            ]
            stats = calc_stats(u["level"], events)
            total = sum(stats.values())
            board.append({
                "id": u["id"],
                "username": u["username"],
                "name": u["name"],
                "avatar": u["avatar"],
                "title": u["title"],
                "level": u["level"],
                "totalStats": total,
                "joinedDate": u["joined_date"],
            })

        board.sort(key=lambda x: (x["level"], x["totalStats"]), reverse=True)
        for i, entry in enumerate(board):
            entry["rank"] = i + 1

    return {"leaderboard": board}
