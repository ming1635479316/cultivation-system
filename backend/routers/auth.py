"""
计算机修行录 - 认证路由
"""
import json
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Request

from models import RegisterIn, LoginIn, PasswordChangeIn, AuthOut, user_row_to_dict, now_iso
from database import get_db, cleanup_expired_tokens
from middleware import hash_password, verify_password, check_login_rate_limit, check_register_rate_limit, check_password_change_rate_limit, _get_client_ip, get_user_id
from services.audit import record_audit

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

        record_audit(conn, user_id, "register", ip=_get_client_ip(request),
                     detail={"username": body.username})

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
            if user:
                record_audit(conn, user["id"], "login_failure", ip=client_ip,
                             detail={"username": body.username, "reason": "wrong_password"})
            else:
                record_audit(conn, None, "login_failure", ip=client_ip,
                             detail={"username": body.username, "reason": "user_not_found"})
            conn.commit()  # 审计必须在 raise 前提交，否则被回滚
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

        record_audit(conn, user["id"], "login_success", ip=client_ip,
                     detail={"username": body.username})

    return AuthOut(token=token, user=user_row_to_dict(user))


@router.post("/logout")
def logout(request: Request):
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if token:
        with get_db() as conn:
            conn.execute("DELETE FROM tokens WHERE token=?", (token,))
    return {"ok": True}


@router.post("/change-password")
def change_password(body: PasswordChangeIn, request: Request):
    """修改当前用户密码（需验证旧密码），修改后所有旧 token 失效。"""
    uid = get_user_id(request)
    client_ip = _get_client_ip(request)
    check_password_change_rate_limit(client_ip)

    with get_db() as conn:
        user = conn.execute(
            "SELECT password FROM users WHERE id=?", (uid,)
        ).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")

        if not verify_password(body.old_password, user["password"]):
            record_audit(conn, uid, "password_change", ip=client_ip,
                         detail={"success": False, "reason": "old_password_mismatch"})
            conn.commit()  # 审计必须在 raise 前提交
            raise HTTPException(400, "旧密码错误")

        if body.old_password == body.new_password:
            raise HTTPException(400, "新密码不能与旧密码相同")

        conn.execute(
            "UPDATE users SET password=?, updated_at=? WHERE id=?",
            (hash_password(body.new_password), now_iso(), uid),
        )

        # 使所有旧 token 失效，强制重新登录
        conn.execute("DELETE FROM tokens WHERE user_id=?", (uid,))

        record_audit(conn, uid, "password_change", ip=client_ip,
                     detail={"success": True})

    return {"ok": True, "message": "密码修改成功，请重新登录"}


@router.delete("/account")
def delete_account(request: Request):
    """删除当前用户账号及其所有数据（级联删除）。"""
    uid = get_user_id(request)
    client_ip = _get_client_ip(request)
    with get_db() as conn:
        # 记录审计（必须在删除用户前）
        user_info = conn.execute(
            "SELECT username FROM users WHERE id=?", (uid,)
        ).fetchone()
        record_audit(conn, uid, "account_delete", ip=client_ip,
                     detail={"username": user_info["username"] if user_info else str(uid)})

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
