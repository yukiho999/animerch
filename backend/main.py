# ============================================
# 桐桐的吃谷日记 — FastAPI 入口
# ============================================
import os
import sys
from contextlib import asynccontextmanager

# 把 backend 父目录加入 path，解决 uvicorn 启动时找不到 backend 模块的问题
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from backend.database import engine, Base
from backend.routers import ip, merch, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时建表（如不存在）"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="桐桐的吃谷日记",
    description="聚合国内社交媒体平台上官方发布的周边发行通知",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 — prefix 已在各 router 中定义
app.include_router(ip.router)
app.include_router(merch.router)
app.include_router(admin.router)
app.include_router(admin.page_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# ── 图片代理：绕过微博 CDN Referer 防盗链 ──

@app.get("/api/proxy/image")
async def proxy_image(url: str = Query(..., description="原始图片URL")):
    """后端代理获取图片，绕过微博 CDN 的 Referer 检查"""
    headers = {
        "Referer": "https://m.weibo.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            content_type = resp.headers.get("content-type", "image/jpeg")
            return StreamingResponse(
                content=resp.iter_bytes(),
                status_code=resp.status_code,
                media_type=content_type,
                headers={"Cache-Control": "public, max-age=86400"},
            )
    except Exception:
        from fastapi.responses import Response
        return Response(status_code=404)
