# 修炼体系 · 问题清单

> v3.2 · 最后更新：2026-06-24

---

## 待处理

### P1 — 安全 / 数据完整性

| # | 问题 | 位置 | 建议 |
|---|------|------|------|
| P1-7 | 账号删除未级联清理社交数据 | `auth.py:86` 只删了 events/messages/journals/tokens，posts/comments/votes/dms 残留 | 补全级联删除 |
| P1-5 | 注册缺少限流 | `auth.py:18` register 无限流，可批量注册灌库 | 加 IP 频率限制 |

### P2 — 功能缺陷 / 性能

| # | 问题 | 位置 | 建议 |
|---|------|------|------|
| P2-1 | 排行榜 N+1 查询 | `leaderboard.py` 每个用户单独查 events | 预计算 stats 表 |
| P2-9 | `formatTime` 解析 UTC 时间戳失败 | `social.js:7` 对 `+00:00` 结尾的 ISO 串错误追加 `Z` | 修正时区解析逻辑 |
| P2-10 | DB 默认时间戳用本地时间 | `database.py` 所有 `DEFAULT datetime('now')` | 改为 `now_iso()` 显式写入 |
| P2-11 | journal_write 事件从未触发 | `journals.py` 写感悟没调 `record_event`，配置定义了奖励但没用 | `add_journal` 中补上 |
| P2-12 | 消息/感悟渲染未转义（XSS） | `profile.html:281` journal.body / `messages.html:69` msg.text 直接插 innerHTML | 加 `escapeHtml()` |

### P3 — 代码质量

| # | 问题 | 位置 | 建议 |
|---|------|------|------|
| P3-1 | `LoginIn` 字段无长度校验 | `models.py:19-21` | 加 min_length |
| P3-2 | `grade_submission` 死代码 | `services/quiz.py:146-155` | 删除 |
| P3-3 | `get_questions_with_answers` 死代码 | `services/quiz.py:158-183` | 删除 |
| P3-4 | profile 页 title 字段不暴露 | `profile.html` 表单缺 title | 加编辑项 |
| P3-5 | README 目录树 `requirements.txt` 路径写错 | 实际在 `backend/` 下 | 修正 |
| P3-6 | `backend/app.py` 孤儿文件 | 未被 import | 确认后可删 |
| P3-7 | `requirements.txt` 含未用的 `psycopg2-binary` | 项目用 SQLite | 删 |
| P3-8 | `VoteIn` 可用 Pydantic Literal 校验 | `models.py:116-119` 手写校验 | 改用 Literal |
| P3-9 | 排行榜同分排名不共享 | `leaderboard.py:44` | 密集排名 |
| P3-10 | favicon 部分页面缺失 | login/profile/messages.html | 统一 |

---

## 已修复（按版本）

### v3.2（2026-06-24）
- 关卡验证后端化（P1-1）、输入长度限制（P1-2）、头像校验（P1-3）
- 生产环境关闭 /docs（SHOW_DOCS 控制）
- admin 迁移密码不再输出日志

### v3.1（2026-06-23）
- WAL 模式、JSON 序列化、用户级联删除（基础表）、UTC now_iso()、结构化日志、API 限流、admin 密码环境变量

### v3.0（2026-06-23）
- bcrypt、Token 过期、CORS、事件校验、增量 API、后端计算 stats/progress、分页、健康检查、多用户迁移
