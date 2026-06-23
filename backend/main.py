"""
计算机修行录 - v3.0 模块化入口
FastAPI 应用组装、生命周期、中间件注册
"""
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import ALLOW_ORIGINS, WEB_DIR
from database import init_db
from routers import auth, state, tasks, messages, journals, quiz
from middleware import _get_client_ip, check_api_rate_limit
from logger import logger, log_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动", extra={"extra_data": {"version": "3.0.0"}})
    init_db()
    yield
    logger.info("应用关闭", extra={"extra_data": {"version": "3.0.0"}})


app = FastAPI(title="计算机修行录 API", version="3.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 中间件：日志 + 限流 + 禁用缓存
# ============================================================

# 不需要限流的路径
_RATE_LIMIT_SKIP = {"/api/health", "/docs", "/openapi.json", "/favicon.ico"}


@app.middleware("http")
async def middleware(request: Request, call_next):
    start = time.time()
    path = request.url.path
    client_ip = _get_client_ip(request)

    # 限流（跳过静态文件和健康检查）
    if path.startswith("/api/") and path not in _RATE_LIMIT_SKIP:
        try:
            check_api_rate_limit(client_ip)
        except Exception as e:
            return JSONResponse(
                status_code=429,
                content={"detail": str(e.detail) if hasattr(e, "detail") else "请求过于频繁"},
            )

    # 执行业务
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("未捕获异常", extra={"extra_data": {"path": path, "ip": client_ip}})
        raise

    duration = (time.time() - start) * 1000
    log_request(
        method=request.method,
        path=path,
        status=response.status_code,
        duration_ms=duration,
        client_ip=client_ip,
    )

    # 禁用缓存（微信浏览器会激进缓存，导致数据不同步）
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# 注册路由
app.include_router(auth.router)
app.include_router(state.router)
app.include_router(tasks.router)
app.include_router(messages.router)
app.include_router(journals.router)
app.include_router(quiz.router)


@app.get("/api/health")
def health():
    from config import DB_PATH
    return {"status": "ok", "db": os.path.exists(DB_PATH), "version": "3.0.0"}


# ============================================================
# 微信浏览器检测：打开链接前引导用户用系统浏览器
# ============================================================

WECHAT_GUIDE_PATH = os.path.join(WEB_DIR, "wechat-guide.html")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """根路径：微信浏览器返回引导页，普通浏览器正常进入。"""
    ua = request.headers.get("User-Agent", "")
    if "MicroMessenger" in ua and os.path.isfile(WECHAT_GUIDE_PATH):
        return HTMLResponse(
            content=open(WECHAT_GUIDE_PATH, "r", encoding="utf-8").read(),
            status_code=200,
        )
    # 普通浏览器 → 正常走静态文件
    if os.path.isfile(os.path.join(WEB_DIR, "index.html")):
        return HTMLResponse(
            content=open(os.path.join(WEB_DIR, "index.html"), "r", encoding="utf-8").read(),
            status_code=200,
        )
    return HTMLResponse(content="<h1>页面未找到</h1>", status_code=404)


# 静态文件挂载（必须在所有 API 路由之后）
if os.path.isdir(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    host, port = "0.0.0.0", 8001
    print(f"数据库: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cultivation.db')}")
    print(f"服务: http://{host}:{port}")
    print(f"文档: http://{host}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=True)
