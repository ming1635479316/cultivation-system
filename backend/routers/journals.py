"""
计算机修行录 - 感悟路由
"""
from fastapi import APIRouter, HTTPException, Request

from models import JournalIn, now_iso, row_to_dict
from database import get_db
from middleware import get_user_id

router = APIRouter(prefix="/api/journals", tags=["journals"])


@router.get("")
def list_journals(request: Request, page: int = 1, limit: int = 20):
    """分页获取感悟列表。"""
    uid = get_user_id(request)
    offset = (page - 1) * limit
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM journals WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
            (uid, limit, offset),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@router.post("")
def add_journal(journal: JournalIn, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO journals (user_id, title, body, date) VALUES (?, ?, ?, ?)",
            (uid, journal.title, journal.body, journal.date or now_iso()),
        )
        row = conn.execute("SELECT * FROM journals WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@router.delete("/{journal_id}")
def delete_journal(journal_id: int, request: Request):
    uid = get_user_id(request)
    with get_db() as conn:
        conn.execute("DELETE FROM journals WHERE id=? AND user_id=?", (journal_id, uid))
    return {"ok": True}
