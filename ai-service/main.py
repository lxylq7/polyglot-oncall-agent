# 导入FastAPI框架
from fastapi import FastAPI
# 导入CORS中间件 允许跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 导入路由模块
from routers import rag,agent
# 导入配置
from config import settings

# 创建FastAPI应用实例
app = FastAPI(
    title="SuperBizAgent AI Service",
    description="AI Service for RAG and AI Agent operations",
    version="1.0.0"
)

# 添加CORS中间件
# 允许前端 SpringBoot的9900端口跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源（生产环境应限制）
    allow_credentials=True,    # 允许携带凭证
    allow_methods=["*"],       # 允许所有 HTTP 方法
    allow_headers=["*"],       # 允许所有请求头
)

# 注册路由
# prefix: API 路径前缀
# tags: 在 API 文档中的分组标签
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])

# 健康检查接口
# 用于 Spring Boot 检测 Python 服务是否正常运行
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Service"}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",                      # 应用路径
        host="0.0.0.0",                  # 监听所有网络接口
        port=settings.server_port,       # 从配置读取端口
        reload=True                      # 开发模式：代码修改后自动重启
    )