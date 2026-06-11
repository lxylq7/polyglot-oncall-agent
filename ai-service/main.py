# 导入FastAPI框架
from fastapi import FastAPI
# 导入CORS中间件，允许跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 导入路由模块
from routers import rag, agent
# 导入配置
from config import settings
from contextlib import asynccontextmanager
import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动 MCP Server（后台线程，端口 8001）
    from mcp_server import mcp

    mcp_thread = threading.Thread(
        target=mcp.run,
        kwargs={"transport": "streamable-http"},
        daemon=True,
    )
    mcp_thread.start()
    print("MCP Server started on port 8001")

    yield

    # 关闭时 daemon 线程随进程退出自动清理
    print("MCP Server shutting down...")


# 创建FastAPI应用实例
app = FastAPI(
    title="SuperBizAgent AI Service",
    description="AI Service for RAG and AI Agent operations",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Service"}


# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=False,
    )
