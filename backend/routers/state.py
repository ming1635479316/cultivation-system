"""
计算机修行录 - 状态路由（只读启动同步 + 个人资料更新）
"""
import base64
import re

from fastapi import APIRouter, HTTPException, Request

from models import StateOut, ProfileUpdateIn, row_to_dict, user_row_to_dict, now_iso
from database import get_db
from middleware import get_user_id
from services.stats import calc_stats, calc_progress

router = APIRouter(prefix="/api", tags=["state"])

# 头像最大原始尺寸：256KB（base64 解码后）
AVATAR_MAX_RAW_BYTES = 256 * 1024
# 允许的头像 MIME 类型
AVATAR_ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}


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
        _validate_avatar(body.avatar)
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


def _validate_avatar(avatar: str):
    """校验头像：空字符串表示删除，否则必须是有效的 data URI 且尺寸合规。"""
    if not avatar or not avatar.strip():
        return  # 允许清空头像

    # 必须是 data URI 格式
    if not avatar.startswith("data:"):
        raise HTTPException(400, "头像格式无效，需要 data URI")

    # 提取 MIME 类型
    mime_match = re.match(r"data:([^;]+);base64,", avatar)
    if not mime_match:
        raise HTTPException(400, "头像格式无效，需要 base64 编码")

    mime_type = mime_match.group(1)
    if mime_type not in AVATAR_ALLOWED_TYPES:
        raise HTTPException(
            400,
            f"不支持的图片格式：{mime_type}，仅支持 PNG、JPEG、WebP",
        )

    # 解码并校验大小
    try:
        b64_data = avatar.split(",", 1)[1]
        raw_bytes = base64.b64decode(b64_data, validate=True)
    except Exception:
        raise HTTPException(400, "头像 base64 解码失败")

    if len(raw_bytes) > AVATAR_MAX_RAW_BYTES:
        raise HTTPException(
            400,
            f"头像文件过大（{len(raw_bytes)} bytes），最大允许 {AVATAR_MAX_RAW_BYTES} bytes",
        )

    if len(raw_bytes) == 0:
        raise HTTPException(400, "头像数据为空")
