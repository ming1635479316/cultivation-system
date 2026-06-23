"""
计算机修行录 - 配置常量
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, "cultivation.db")
WEB_DIR = os.path.join(BASE_DIR, "..", "web")

MAX_EVENTS = 500
MAX_MESSAGES = 200

# 允许前端写入的 event 类型（白名单）
VALID_EVENT_TYPES = {
    "task_done", "quiz_pass", "resource_read", "tool_unlock", "config_file", "journal_write"
}

# 每个段位的任务数量（与前端 data.js 保持一致）
LEVEL_TASKS = {
    0: 0, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 3, 8: 2, 9: 0,
}

# 事件对四维属性的贡献
EVENT_CONFIG = {
    "task_done":     {"coding": 0, "project": 0, "tools": 0},
    "quiz_pass":     {"coding": 10, "theory": 8},
    "quiz_correct":  {"theory": 2},
    "resource_read": {"theory": 3},
    "tool_unlock":   {"tools": 8},
    "config_file":   {"tools": 5},
    "journal_write": {"coding": 3, "theory": 5},
}

# CORS 来源
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "")
if CORS_ORIGINS:
    ALLOW_ORIGINS = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
else:
    ALLOW_ORIGINS = [
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]


def get_task_reward(level_id: int) -> dict[str, int]:
    """关卡任务奖励（与前端 getTaskReward 保持一致）。"""
    if level_id <= 1:
        return {"coding": 5, "project": 2}
    if level_id == 2:
        return {"coding": 8, "project": 4}
    if level_id == 3:
        return {"coding": 10, "project": 5, "tools": 3}
    return {"coding": 12, "project": 8, "tools": 5}


def get_base_stats(level: int) -> dict[str, int]:
    """段位基础属性（与前端 getBaseStats 保持一致）。"""
    return {
        "coding": level * 8,
        "project": level * 6,
        "theory": level * 7,
        "tools": level * 6,
    }
