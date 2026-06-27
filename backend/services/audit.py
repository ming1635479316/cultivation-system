"""
计算机修行录 - 安全审计服务
记录所有认证相关事件，与用户可见 events 表隔离，永不过期清理。
"""
import json

from config import VALID_AUDIT_EVENT_TYPES
from models import now_iso


def record_audit(conn, user_id: int | None, event_type: str,
                 ip: str = "", detail: dict | None = None) -> int:
    """写入审计事件，校验类型合法性，返回事件 ID。"""
    if event_type not in VALID_AUDIT_EVENT_TYPES:
        raise ValueError(f"非法审计事件类型: {event_type}")

    cur = conn.execute(
        "INSERT INTO audit_events (user_id, event_type, ip, detail, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, event_type, ip,
         json.dumps(detail, ensure_ascii=False) if detail else None,
         now_iso()),
    )
    return cur.lastrowid
