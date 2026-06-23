"""
计算机修行录 - Pydantic 模型
"""
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


# ---- 请求模型 ----

class RegisterIn(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=4, max_length=64)


class LoginIn(BaseModel):
    username: str
    password: str


class MessageIn(BaseModel):
    icon: str = ""
    text: str
    time: str | None = None
    unread: bool = True
    pinned: bool = False


class JournalIn(BaseModel):
    title: str
    body: str
    date: str | None = None


class TaskAction(BaseModel):
    level_id: int = Field(..., ge=0, le=9)
    task_idx: int = Field(..., ge=0)


class QuizSubmitIn(BaseModel):
    level_id: int = Field(..., ge=0, le=9)
    answers: list[int]  # 每题选中的选项索引


class ProfileUpdateIn(BaseModel):
    name: str | None = None
    avatar: str | None = None
    title: str | None = None
    gender: str | None = None
    age: str | None = None
    contact: str | None = None


# ---- 响应模型 ----

class AuthOut(BaseModel):
    token: str
    user: dict[str, Any]


class StateOut(BaseModel):
    user: dict[str, Any]
    events: list[dict[str, Any]]
    messages: list[dict[str, Any]]
    journals: list[dict[str, Any]]
    lastModified: str = ""
    stats: dict[str, int] | None = None
    progress: int | None = None


class QuizQuestionOut(BaseModel):
    id: int
    level: int
    category: str
    question: str
    options: list[str]


class QuizResultOut(BaseModel):
    passed: bool
    score: int
    total: int
    pass_score: int
    results: list[dict[str, Any]]
    stats: dict[str, int] | None = None
    progress: int | None = None
    level_up: bool = False
    new_level: int | None = None


# ---- 辅助函数 ----

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dumps(obj: Any) -> str:
    """序列化为 JSON 字符串，确保有效 JSON。"""
    return json.dumps(obj, ensure_ascii=False)


def json_loads(s: Any) -> Any:
    """安全地从字符串/已有对象解析 JSON。"""
    if s is None:
        return None
    if isinstance(s, (list, dict)):
        return s
    if isinstance(s, str):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s
    return s


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    for key in ("specializations", "completed_tasks", "value"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except json.JSONDecodeError:
                # 损坏的 JSON 保持原值，上游可自行处理
                pass
    for key in ("unread", "pinned"):
        if key in d:
            d[key] = bool(d[key])
    return d


def user_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = row_to_dict(row)
    d.pop("password", None)
    if "joined_date" in d:
        d["joinedDate"] = d.pop("joined_date")
    if "completed_tasks" in d:
        d["completedTasks"] = d.pop("completed_tasks")
    return d
