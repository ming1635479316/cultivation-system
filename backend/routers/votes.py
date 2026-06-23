"""
计算机修行录 - 投票路由
"""
from fastapi import APIRouter, HTTPException, Request

from models import VoteIn
from database import get_db
from middleware import get_user_id

router = APIRouter(prefix="/api/votes", tags=["votes"])


def _recalc_and_update(conn, target_type: str, target_id: int):
    """重新计算并更新投票目标的冗余分数。"""
    new_score = conn.execute(
        "SELECT COALESCE(SUM(value), 0) FROM votes WHERE target_type=? AND target_id=?",
        (target_type, target_id),
    ).fetchone()[0]

    table = "posts" if target_type == "post" else "comments"
    if target_type in ("post", "comment"):
        conn.execute(f"UPDATE {table} SET vote_score=? WHERE id=?", (new_score, target_id))
    return new_score


@router.post("")
def cast_vote(body: VoteIn, request: Request):
    uid = get_user_id(request)
    if body.value not in (-1, 1):
        raise HTTPException(400, "投票值必须为 1 或 -1")
    if body.target_type not in ("post", "comment"):
        raise HTTPException(400, "目标类型必须为 post 或 comment")

    with get_db() as conn:
        # 验证目标存在
        table = "posts" if body.target_type == "post" else "comments"
        target = conn.execute(f"SELECT id FROM {table} WHERE id=?", (body.target_id,)).fetchone()
        if not target:
            raise HTTPException(404, "投票目标不存在")

        existing = conn.execute(
            "SELECT id, value FROM votes WHERE user_id=? AND target_type=? AND target_id=?",
            (uid, body.target_type, body.target_id),
        ).fetchone()

        if existing:
            if existing["value"] == body.value:
                # 同值再次提交 → 取消投票
                conn.execute("DELETE FROM votes WHERE id=?", (existing["id"],))
            else:
                # 不同值 → 翻转投票
                conn.execute("UPDATE votes SET value=?, created_at=(datetime('now')) WHERE id=?",
                             (body.value, existing["id"]))
        else:
            conn.execute(
                "INSERT INTO votes (user_id, target_type, target_id, value) VALUES (?,?,?,?)",
                (uid, body.target_type, body.target_id, body.value),
            )

        new_score = _recalc_and_update(conn, body.target_type, body.target_id)

    return {"ok": True, "vote_score": new_score, "user_vote": body.value if not (existing and existing["value"] == body.value) else 0}
