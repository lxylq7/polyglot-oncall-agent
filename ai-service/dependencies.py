#dependencies.py 全局共享实例

from clients.chroma_client import ChromaClient
from clients.dashscope_client import DashScopeClient
from service.agent_service import AgentService
from service.rag_service import RAGService

#只创建一次
chroma_client = ChromaClient()
dashscope_client = DashScopeClient()
rag_service = RAGService(dashscope_client,chroma_client)
agent_service = AgentService(rag_service,dashscope_client)
