"""
计算机修行录 - 排行榜路由
"""
from fastapi import APIRouter, Request

from database import get_db
from middleware import get_user_id

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("")
def get_leaderboard(request: Request):
    get_user_id(request)
    with get_db() as conn:
        rows = conn.execute(
            """SELECT
                 u.id, u.username, u.name, u.avatar, u.title, u.level,
                 u.joined_date,
                 COALESCE(SUM(
                     COALESCE(CAST(json_extract(e.value, '$.coding') AS INTEGER), 0) +
                     COALESCE(CAST(json_extract(e.value, '$.project') AS INTEGER), 0) +
                     COALESCE(CAST(json_extract(e.value, '$.theory') AS INTEGER), 0) +
                     COALESCE(CAST(json_extract(e.value, '$.tools') AS INTEGER), 0)
                 ), 0) AS total_stats
               FROM users u
               LEFT JOIN events e ON e.user_id = u.id
               WHERE u.id > 0
               GROUP BY u.id
               ORDER BY u.level DESC, total_stats DESC""",
        ).fetchall()

    board = []
    for i, r in enumerate(rows):
        board.append({
            "rank": i + 1,
            "id": r["id"],
            "username": r["username"],
            "name": r["name"],
            "avatar": r["avatar"],
            "title": r["title"],
            "level": r["level"],
            "totalStats": r["total_stats"],
            "joinedDate": r["joined_date"],
        })
    return {"leaderboard": board}
