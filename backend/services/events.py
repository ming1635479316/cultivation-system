"""
计算机修行录 - 事件写入服务
"""
import json
from config import VALID_EVENT_TYPES
from models import now_iso


def record_event(conn, user_id: int, event_type: str, value: dict | None = None,
                 ref: str | None = None) -> int:
    """统一事件写入，校验类型合法性，返回事件 ID。"""
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"非法事件类型: {event_type}")

    cur = conn.execute(
        "INSERT INTO events (user_id, type, value, ref, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, event_type,
         json.dumps(value, ensure_ascii=False) if value else None,
         ref, now_iso()),
    )
    return cur.lastrowid
