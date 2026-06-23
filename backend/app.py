"""
计算机修行录 - 兼容入口（服务器 systemd 使用 uvicorn app:app）
实际逻辑已迁移至 main.py
"""
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
