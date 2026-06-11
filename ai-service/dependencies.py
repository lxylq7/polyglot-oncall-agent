# dependencies.py —— 全局共享实例

from clients.chroma_client import ChromaClient
from clients.dashscope_client import DashScopeClient
from clients.mcp_client import MCPClient
from service.agent_service import AgentService
from service.rag_service import RAGService

# 基础设施客户端（只创建一次）
chroma_client = ChromaClient()
dashscope_client = DashScopeClient()
mcp_client = MCPClient(url="http://localhost:8001/mcp")

# 业务服务
rag_service = RAGService(dashscope_client, chroma_client)
agent_service = AgentService(rag_service, dashscope_client, mcp_client)
