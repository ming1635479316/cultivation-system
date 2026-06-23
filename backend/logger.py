"""
计算机修行录 - 结构化日志
基于 Python logging 模块，输出 JSON 行格式便于后期分析。
"""
import json
import logging
import sys
import time
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON 行格式化器。"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exc"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """配置应用根日志。开发环境输出文本格式，生产环境 JSON。"""
    root = logging.getLogger("cultivation")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)

    # 简单判断：stdout 是 tty 则用可读格式，否则 JSON
    if sys.stderr.isatty():
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
    else:
        handler.setFormatter(JsonFormatter())

    root.addHandler(handler)
    return root


# 单例 logger
logger = setup_logging()


def log_request(method: str, path: str, status: int, duration_ms: float,
                user_id: int | None = None, client_ip: str = ""):
    """记录 HTTP 请求日志。"""
    extra = {
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 2),
    }
    if user_id is not None:
        extra["user_id"] = user_id
    if client_ip:
        extra["ip"] = client_ip

    if status >= 500:
        logger.error("request", extra={"extra_data": extra})
    elif status >= 400:
        logger.warning("request", extra={"extra_data": extra})
    else:
        logger.info("request", extra={"extra_data": extra})
