"""
计算机修行录 - 任务路由
"""
import json

from fastapi import APIRouter, HTTPException, Request

from models import TaskAction, now_iso, row_to_dict
from config import LEVEL_TASKS, get_task_reward
from database import get_db
from middleware import get_user_id
from services.stats import calc_stats, calc_progress
from services.events import record_event
from services.quiz import get_task_check, verify_task_answer

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/check/{level_id}/{task_idx}")
def get_check(level_id: int, task_idx: int, request: Request):
    """获取关卡验证题（不带答案），供前端弹出验证弹窗。"""
    get_user_id(request)  # 仅鉴权
    check = get_task_check(level_id, task_idx)
    if check:
        return {"has_check": True, "question": check["question"], "options": check["options"]}
    return {"has_check": False, "question": None, "options": None}


@router.post("/complete")
def complete_task(action: TaskAction, request: Request):
    """完成关卡任务。后端校验验证题答案并记录，返回更新后的 stats/progress。"""
    uid = get_user_id(request)
    key = f"{action.level_id}-{action.task_idx}"

    total = LEVEL_TASKS.get(action.level_id)
    if total is None or action.task_idx < 0 or action.task_idx >= total:
        raise HTTPException(400, "任务不存在")

    # 验证关卡答案（如果有验证题）
    check = get_task_check(action.level_id, action.task_idx)
    if check is not None:
        if action.answer is None:
            raise HTTPException(400, "此关卡需要先通过验证")
        if not verify_task_answer(action.level_id, action.task_idx, action.answer):
            raise HTTPException(400, "验证答案错误，请回顾知识点后重试")

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        completed_tasks = json.loads(user["completed_tasks"] or "[]")
        if key in completed_tasks:
            raise HTTPException(400, "任务已完成")

        level = user["level"]
        if action.level_id > level:
            raise HTTPException(400, "段位不足")

        completed_tasks.append(key)

        reward = get_task_reward(action.level_id)
        record_event(conn, uid, "task_done", value=reward, ref=key)

        conn.execute(
            "UPDATE users SET completed_tasks=?, updated_at=? WHERE id=?",
            (json.dumps(completed_tasks, ensure_ascii=False), now_iso(), uid),
        )

        events = [
            row_to_dict(r)
            for r in conn.execute("SELECT * FROM events WHERE user_id=?", (uid,)).fetchall()
        ]
        stats = calc_stats(level, events)
        progress = calc_progress(level, completed_tasks)

    return {
        "ok": True,
        "key": key,
        "reward": reward,
        "completedTasks": completed_tasks,
        "stats": stats,
        "progress": progress,
        "level": level,
    }


@router.post("/undo")
def undo_task(action: TaskAction, request: Request):
    """取消完成关卡任务，并删除对应事件。"""
    uid = get_user_id(request)
    key = f"{action.level_id}-{action.task_idx}"

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        completed_tasks = json.loads(user["completed_tasks"] or "[]")
        if key not in completed_tasks:
            raise HTTPException(400, "任务未完成")

        completed_tasks.remove(key)

        # 删除该任务对应的最新 task_done 事件
        conn.execute(
            """DELETE FROM events WHERE id = (
                SELECT id FROM events WHERE user_id=? AND type=? AND ref=? ORDER BY id DESC LIMIT 1
            )""",
            (uid, "task_done", key),
        )

        conn.execute(
            "UPDATE users SET completed_tasks=?, updated_at=? WHERE id=?",
            (json.dumps(completed_tasks, ensure_ascii=False), now_iso(), uid),
        )

        level = user["level"]
        events = [
            row_to_dict(r)
            for r in conn.execute("SELECT * FROM events WHERE user_id=?", (uid,)).fetchall()
        ]
        stats = calc_stats(level, events)
        progress = calc_progress(level, completed_tasks)

    return {
        "ok": True,
        "key": key,
        "completedTasks": completed_tasks,
        "stats": stats,
        "progress": progress,
        "level": level,
    }
