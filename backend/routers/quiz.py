"""
计算机修行录 - 考核路由
"""
import json

from fastapi import APIRouter, HTTPException, Request

from models import QuizSubmitIn, row_to_dict, now_iso
from database import get_db
from middleware import get_user_id
from services.quiz import pick_questions, get_questions_with_answers, grade_answers
from services.stats import calc_stats, calc_progress
from services.events import record_event
from config import LEVEL_TASKS

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.get("/questions/{level_id}")
def get_questions(level_id: int, request: Request):
    """返回指定段位的考核题目（不带答案）。"""
    get_user_id(request)  # 仅鉴权
    questions = pick_questions(level_id, 6)
    if not questions:
        raise HTTPException(404, "该段位暂无考核题目")
    return {"questions": questions}


@router.post("/submit")
def submit_quiz(body: QuizSubmitIn, request: Request):
    """提交考核答案，后端判卷并记录事件。"""
    uid = get_user_id(request)

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        # 重新抽取同样的题目（带答案）进行判卷
        # 注意：这里用固定种子确保和前端展示的题目一致
        # 方案：前端回传题目的 question 文本，后端匹配判卷
        full_questions = get_questions_with_answers(body.level_id, len(body.answers))
        if len(full_questions) != len(body.answers):
            raise HTTPException(400, "题目数量不匹配")

        result = grade_answers(full_questions, body.answers, body.level_id)

        # 记录每题正确的理论值
        quiz_correct_count = 0
        for i, r in enumerate(result["results"]):
            if r["is_correct"]:
                quiz_correct_count += 1
                record_event(conn, uid, "quiz_correct",
                             value={"theory": 2},
                             ref=f"quiz_{body.level_id}_{i}")

        # 通过考核
        level_up = False
        new_level = None
        if result["passed"]:
            record_event(conn, uid, "quiz_pass",
                         value={"coding": 10, "theory": 8},
                         ref=f"quiz_pass_{body.level_id}")

            # 如果考的是当前段位 → 自动突破
            current_level = user["level"]
            if body.level_id == current_level and current_level < 9:
                new_level = current_level + 1
                level_up = True
                conn.execute(
                    "UPDATE users SET level=?, updated_at=? WHERE id=?",
                    (new_level, now_iso(), uid),
                )

        # 重算属性
        level = user["level"]
        events = [
            row_to_dict(r)
            for r in conn.execute("SELECT * FROM events WHERE user_id=?", (uid,)).fetchall()
        ]
        completed_tasks = json.loads(user["completed_tasks"] or "[]")
        stats = calc_stats(level, events)
        progress = calc_progress(level, completed_tasks)

    return {
        "passed": result["passed"],
        "score": result["score"],
        "total": result["total"],
        "pass_score": result["pass_score"],
        "results": result["results"],
        "stats": stats,
        "progress": progress,
        "level_up": level_up,
        "new_level": new_level,
    }
