#导入RAG服务
from sqlalchemy.ext.asyncio import result
from streamlit.elements import alert

from service.rag_service import RAGService
#导入工具
from tools import date_time_tool
from tools import query_metrics_tool
#导入大模型客户端
from clients.dashscope_client import DashScopeClient

from tools.date_time_tool import get_current_date, get_current_datetime
from tools.query_metrics_tool import query_prometheus_alerts


class AgentService:
    def __init__(self):
        self.rag_service = RAGService()
        self.dashscope = DashScopeClient()

    def chat(self,question:str) -> dict:
        """
            Agent 对话逻辑
                根据用户问题中的关键词，判断是否需要调用工具：
                - 包含"时间"/"几点" → 调用时间工具
                - 包含"告警"/"监控" → 调用告警查询工具
                - 包含"文档"/"知识" → 调用 RAG 服务
                - 其他 → 直接调用大模型回答
            Args:
                question: 用户问题
            Returns:
                    "answer": "回答", "tool_used": "使用的工具名称"}
        """
        #判断是否需要调用工具
        if "时间" in question or "几点" in question:
            #调用时间工具'
            result = get_current_datetime()
            return {
                "answer": result,
                "tool_used": "date_time_tool"
            }

        #判断是否需要调用告警工具
        elif "告警" in question or "监控" in question:
            #调用告警查询工具
            alerts = query_prometheus_alerts()
            if alerts.get("success"):
                #提取告警名称列表
                names = [a["alerts_name"] for a in alerts["alerts"]]
                return {
                    "answer": f"当前活跃告警：{', '.join(names)}",
                    "tool_used": "alerts"
                }
            else:
                return {
                    "answer": f"查询告警失败：{alerts.get('error')}",
                    "tool_used": "alerts"
                }

        #判断是否需要调用RAG服务
        elif "文档" in question or "知识" in question:
            result = self.rag_service.query(question)
            return {
                "answer": result,
                "tool_used": "rag_service"
            }

        #其他情况 直接调用大模型回答
        else:
            answer = self.dashscope.generate(question)
            return {
                "answer": answer,
                "tool_used": None
            }