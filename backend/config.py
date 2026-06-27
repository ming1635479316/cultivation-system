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
    "task_done", "quiz_pass", "quiz_correct", "resource_read", "tool_unlock", "config_file",
    "journal_write", "post_create", "comment_create"
}

# 安全审计事件类型（与用户可见 events 表隔离，永不过期清理）
VALID_AUDIT_EVENT_TYPES = {
    "login_success",
    "login_failure",
    "register",
    "password_change",
    "account_delete",
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
    "post_create":   {"theory": 2},
    "comment_create": {"theory": 1},
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


# 段位基础战力表（四维：coding/project/theory/tools）
_BASE_STATS_TABLE = {
    0:  (2,   1,   2,   1),    # 入门    ~6
    1:  (30,  20,  25,  20),   # 初段    ~95
    2:  (120, 80,  100, 80),   # 二段    ~380
    3:  (400, 300, 350, 300),  # 三段    ~1350
    4:  (1200, 900, 1100, 900),# 四段    ~4100
    5:  (3000, 2200, 2700, 2200), # 五段 ~10100
    6:  (7000, 5500, 6500, 5500), # 六段 ~24500
    7:  (15000, 12000, 14000, 12000), # 七段 ~53000
    8:  (32000, 25000, 29000, 25000), # 八段 ~111000
    9:  (80000, 65000, 75000, 65000), # 九段 ~285000
}


# 段位战力倍率（用于事件加成缩放）
_POWER_SCALE_MAP = {0:1, 1:3, 2:12, 3:40, 4:120, 5:300, 6:700, 7:1500, 8:3200, 9:8000}


def get_power_scale(level: int) -> int:
    return _POWER_SCALE_MAP.get(min(level, 9), 1)


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
    """段位基础属性（硬编码表，已含倍率）。"""
    lv = min(level, 9)
    c, p, t, tl = _BASE_STATS_TABLE.get(lv, (0, 0, 0, 0))
    return {"coding": c, "project": p, "theory": t, "tools": tl}
