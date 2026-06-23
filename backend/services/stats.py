"""
计算机修行录 - 属性与进度计算
"""
from config import EVENT_CONFIG, LEVEL_TASKS, get_base_stats


def calc_stats(level: int, events: list[dict]) -> dict[str, int]:
    """从段位 + 事件日志计算四维属性。"""
    stats = get_base_stats(level)
    for e in events:
        cfg = EVENT_CONFIG.get(e.get("type"))
        if not cfg:
            continue
        value = e.get("value") or {}
        for stat, base in cfg.items():
            stats[stat] = stats.get(stat, 0) + value.get(stat, base)
    for k in stats:
        stats[k] = max(0, min(100, round(stats[k])))
    return stats


def calc_progress(level: int, completed_tasks: list[str]) -> int:
    """计算段位进度。"""
    total = LEVEL_TASKS.get(level, 0)
    if total == 0:
        return 100
    done = sum(1 for t in completed_tasks if t.startswith(f"{level}-"))
    return round((done / total) * 100)
