# 计算机修行录

> 把编程学习映射成修炼体系——九段十级，以实际产出衡量境界。

## 特性

- **十级修炼**：入门 → 初段~九段，每段有技能树、关卡任务、考核题目
- **四维战力**：coding / project / theory / tools，从修炼事件日志动态计算
- **考核系统**：102 道题目，按段位分组，Fisher-Yates 洗牌抽题，服务端判卷
- **关卡验证**：每关设有验证题，答对才能完成，防止跳过
- **社交功能**：社区帖子（文章/问答）、评论、投票、私信
- **排行榜**：全站四维战力排名
- **多用户**：注册/登录、个人资料编辑、头像上传、感悟日记
- **深色/浅色**：跟随系统自动切换
- **突破动效**：段位晋升全屏特效

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.10+ / FastAPI / SQLite (WAL) / Uvicorn |
| 前端 | 原生 HTML / CSS / JavaScript (ES5) |
| 鉴权 | bcrypt 密码哈希 / Token (7天过期) |
| 部署 | 腾讯云轻量服务器 / systemd / UFW |

## 项目结构

```
cultivation-system/
├── backend/
│   ├── main.py              # FastAPI 应用入口、中间件、生命周期
│   ├── config.py            # 常量：段位表、战力表、事件配置
│   ├── database.py          # SQLite 连接、建表、迁移、清理
│   ├── models.py            # Pydantic 请求/响应模型
│   ├── middleware.py         # Token 鉴权、登录限流、API 限流
│   ├── logger.py            # 结构化 JSON 日志
│   ├── routers/
│   │   ├── auth.py          # 注册/登录/登出/注销账号
│   │   ├── state.py         # 状态同步、个人资料更新
│   │   ├── tasks.py         # 关卡完成/取消/验证
│   │   ├── quiz.py          # 考核出题/提交/判卷
│   │   ├── messages.py      # 系统消息 CRUD
│   │   ├── journals.py      # 感悟日记 CRUD
│   │   ├── posts.py         # 社区帖子 CRUD
│   │   ├── comments.py      # 评论（支持嵌套回复）
│   │   ├── votes.py         # 投票（赞/踩）
│   │   ├── users_public.py  # 用户搜索、公开主页
│   │   ├── direct_messages.py  # 私信
│   │   └── leaderboard.py   # 排行榜
│   └── services/
│       ├── quiz.py          # 题库(102题)、抽题、判卷、关卡验证题
│       ├── stats.py         # 四维战力计算、段位进度计算
│       └── events.py        # 事件记录
├── web/
│   ├── index.html           # 主页：段位卡片、任务弹窗、考核、突破动效
│   ├── login.html           # 登录/注册
│   ├── community.html       # 社区：帖子列表（最新/热门/问答/文章）
│   ├── post.html            # 帖子详情 + 评论
│   ├── profile.html         # 个人资料编辑
│   ├── user.html            # 他人公开主页
│   ├── messages.html        # 系统消息
│   ├── dms.html             # 私信对话
│   ├── leaderboard.html     # 全站排行榜
│   ├── wechat-guide.html    # 微信浏览器引导页
│   ├── css/style.css        # 全局样式（深色/浅色/响应式）
│   └── js-v3/
│       ├── api.js           # API 客户端（鉴权、超时、自动重定向）
│       ├── store.js         # 状态管理（缓存 + 服务端同步）
│       ├── constants.js     # 段位常量（名称、技能、资源）
│       ├── app.js           # 主页 UI（段位列表、弹窗、考核、突破）
│       └── social.js        # 社交共享模块（时间格式化、投票、评论）
├── requirements.txt
├── 修炼体系_v2.0.md          # 九段制设计文档
└── ISSUES.md                # 问题清单与修复记录
```

## API 端点

| 前缀 | 用途 |
|------|------|
| `/api/auth` | 注册、登录、登出、注销账号 |
| `/api/state` | 启动同步（全量状态） |
| `/api/tasks` | 关卡完成/取消/验证题获取 |
| `/api/quiz` | 考核出题、提交判卷 |
| `/api/messages` | 系统消息 CRUD |
| `/api/journals` | 感悟日记 CRUD |
| `/api/posts` | 社区帖子 CRUD |
| `/api/posts/{id}/comments` | 评论（嵌套回复） |
| `/api/votes` | 投票（赞/踩） |
| `/api/users` | 用户搜索、公开主页 |
| `/api/dms` | 私信对话 |
| `/api/leaderboard` | 全站排行榜 |
| `/api/health` | 健康检查 |

在线文档：http://115.159.216.45:8001/docs

## 部署

- **服务器**：腾讯云 4核 4GB Ubuntu 22.04
- **服务**：`systemd` 管理（`cultivation` 服务），端口 8001
- **更新**：`git pull` → `sudo systemctl restart cultivation`

## 快速开始

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py             # 开发模式（reload），访问 http://127.0.0.1:8001
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-13 | 单用户，前端 localStorage 为主 |
| v2.0 | 2026-06-16 | 九段制设计文档定稿 |
| v3.0 | 2026-06-23 | 模块化拆分、多用户、后端为唯一数据源 |
| v3.1 | 2026-06-23 | 结构化日志、限流、WAL 模式、账号删除、UTC 时间戳 |
| v3.2 | 2026-06-24 | 关卡验证后端化、输入长度限制、头像校验 |
