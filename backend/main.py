"""
计算机修行录 - v3.0 模块化入口
FastAPI 应用组装、生命周期、中间件注册
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import ALLOW_ORIGINS, WEB_DIR
from database import init_db
from routers import auth, state, tasks, messages, journals, quiz


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="计算机修行录 API", version="3.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# 静态文件挂载（必须在所有 API 路由之后）
if os.path.isdir(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")


if __name__ == "__main__":
    import uvicorn
    host, port = "0.0.0.0", 8001
    print(f"数据库: {__import__('os').path.join(os.path.dirname(os.path.abspath(__file__)), 'cultivation.db')}")
    print(f"服务: http://{host}:{port}")
    print(f"文档: http://{host}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=True)
