"""
计算机修行录 - 认证路由
"""
import json
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Request

from models import RegisterIn, LoginIn, AuthOut, user_row_to_dict
from database import get_db, cleanup_expired_tokens
from middleware import hash_password, verify_password, check_login_rate_limit, check_register_rate_limit, _get_client_ip, get_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthOut)
def register(body: RegisterIn, request: Request):
    check_register_rate_limit(_get_client_ip(request))
    with get_db() as conn:
        exists = conn.execute(
            "SELECT id FROM users WHERE username=?", (body.username,)
        ).fetchone()
        if exists:
            raise HTTPException(400, "用户名已被注册")

        cur = conn.execute(
            "INSERT INTO users (username, password, name, avatar) VALUES (?, ?, ?, ?)",
            (body.username, hash_password(body.password), body.username, body.username[:2]),
        )
        user_id = cur.lastrowid

        token = secrets.token_urlsafe(32)
        conn.execute("INSERT INTO tokens (token, user_id) VALUES (?, ?)", (token, user_id))

        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    return AuthOut(token=token, user=user_row_to_dict(user))


@router.post("/login", response_model=AuthOut)
def login(body: LoginIn, request: Request):
    client_ip = _get_client_ip(request)
    check_login_rate_limit(client_ip)

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=?", (body.username,),
        ).fetchone()
        if not user or not verify_password(body.password, user["password"]):
            raise HTTPException(401, "用户名或密码错误")

        # 旧版 SHA256 密码自动升级为 bcrypt
        if not user["password"].startswith("$"):
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hash_password(body.password), user["id"]),
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        conn.execute(
            "INSERT INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user["id"], expires_at.isoformat()),
        )
        cleanup_expired_tokens(conn)

    return AuthOut(token=token, user=user_row_to_dict(user))


@router.post("/logout")
def logout(request: Request):
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if token:
        with get_db() as conn:
            conn.execute("DELETE FROM tokens WHERE token=?", (token,))
    return {"ok": True}


@router.delete("/account")
def delete_account(request: Request):
    """删除当前用户账号及其所有数据（级联删除）。"""
    uid = get_user_id(request)
    with get_db() as conn:
        # 手动级联删除（SQLite 不支持 ALTER TABLE 添加 CASCADE）
        # 注意顺序：先删引用 posts 的 comments，再删 posts
        for table in ["comments", "votes"]:
            conn.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM posts WHERE user_id=?", (uid,))
        conn.execute(
            "DELETE FROM direct_messages WHERE from_user_id=? OR to_user_id=?",
            (uid, uid),
        )
        for table in ["events", "messages", "journals", "tokens"]:
            conn.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
    return {"ok": True, "deleted": uid}
