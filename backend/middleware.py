"""
计算机修行录 - 鉴权中间件 + 速率限制
"""
import hashlib
import bcrypt
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request, Depends

from database import get_db

# 登录失败次数限制（内存级，单机够用）
_LOGIN_ATTEMPTS: dict[str, list[datetime]] = {}

# 通用 API 速率限制（按 IP：时间窗口 + 计数）
_RATE_WINDOW: dict[str, list[datetime]] = {}
_RATE_LIMIT = 120       # 每 IP 每分钟最多请求数
_RATE_WINDOW_SEC = 60   # 滑动窗口秒数


def _get_client_ip(request: Request) -> str:
    """优先取 X-Forwarded-For，适用于反向代理后。"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_login_rate_limit(client_ip: str):
    """5 分钟内同一 IP 最多 5 次登录尝试。"""
    now = datetime.now(timezone.utc)
    attempts = _LOGIN_ATTEMPTS.get(client_ip, [])
    attempts = [t for t in attempts if now - t < timedelta(minutes=5)]
    if len(attempts) >= 5:
        raise HTTPException(429, "登录尝试过多，请 5 分钟后再试")
    attempts.append(now)
    _LOGIN_ATTEMPTS[client_ip] = attempts


# 注册限流（独立于登录限流）
_REGISTER_ATTEMPTS: dict[str, list[datetime]] = {}
_REGISTER_LIMIT = 3      # 每 IP 每小时最多注册次数
_REGISTER_WINDOW_H = 1   # 注册限流窗口（小时）


def check_register_rate_limit(client_ip: str):
    """1 小时内同一 IP 最多 _REGISTER_LIMIT 次注册。"""
    now = datetime.now(timezone.utc)
    attempts = _REGISTER_ATTEMPTS.get(client_ip, [])
    attempts = [t for t in attempts if now - t < timedelta(hours=_REGISTER_WINDOW_H)]
    if len(attempts) >= _REGISTER_LIMIT:
        raise HTTPException(429, "注册过于频繁，请 1 小时后再试")
    attempts.append(now)
    _REGISTER_ATTEMPTS[client_ip] = attempts


# 密码修改限流（独立于登录限流）
_PASSWORD_CHANGE_ATTEMPTS: dict[str, list[datetime]] = {}
_PASSWORD_CHANGE_LIMIT = 3      # 每 IP 每小时最多修改密码次数
_PASSWORD_CHANGE_WINDOW_H = 1   # 密码修改限流窗口（小时）


def check_password_change_rate_limit(client_ip: str):
    """1 小时内同一 IP 最多 _PASSWORD_CHANGE_LIMIT 次密码修改。"""
    now = datetime.now(timezone.utc)
    attempts = _PASSWORD_CHANGE_ATTEMPTS.get(client_ip, [])
    attempts = [t for t in attempts if now - t < timedelta(hours=_PASSWORD_CHANGE_WINDOW_H)]
    if len(attempts) >= _PASSWORD_CHANGE_LIMIT:
        raise HTTPException(429, "密码修改过于频繁，请 1 小时后再试")
    attempts.append(now)
    _PASSWORD_CHANGE_ATTEMPTS[client_ip] = attempts


def check_api_rate_limit(client_ip: str):
    """滑动窗口限流：每分钟每 IP 最多 _RATE_LIMIT 次请求。"""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=_RATE_WINDOW_SEC)
    timestamps = _RATE_WINDOW.get(client_ip, [])
    timestamps = [t for t in timestamps if t > window_start]
    if len(timestamps) >= _RATE_LIMIT:
        raise HTTPException(429, "请求过于频繁，请稍后再试")
    timestamps.append(now)
    _RATE_WINDOW[client_ip] = timestamps


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    """验证密码，兼容旧版 SHA256。"""
    if hashed.startswith("$"):
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    return hashed == hashlib.sha256(pw.encode()).hexdigest()


def get_user_id(request: Request) -> int:
    """从请求头提取 token，返回 user_id，检查是否过期。"""
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "请先登录")
    with get_db() as conn:
        row = conn.execute(
            "SELECT user_id, expires_at FROM tokens WHERE token=?", (token,)
        ).fetchone()
        if not row:
            raise HTTPException(401, "登录已过期，请重新登录")
        if row["expires_at"]:
            exp = datetime.fromisoformat(row["expires_at"])
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                conn.execute("DELETE FROM tokens WHERE token=?", (token,))
                raise HTTPException(401, "登录已过期，请重新登录")
    return row["user_id"]
