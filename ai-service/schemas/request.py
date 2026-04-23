#定义所有api请求的数据结构
#导入pydantic的basemodel 所有数据类型的基类
from pydantic import BaseModel
#导入类型提示
from typing import List,Optional

#Rag查询请求
#当前端调用 /api/rag/query 时 请求体必须是这个结构
class RagQueryRequest(BaseModel):
    #question 问题 必须有
    question: str
    #对话历史 可选 默认为None
    history: Optional[List[dict]] = None

#Agent对话请求
#当前端调用 /api/agent/chat 时 请求体必须是这个结构
class AgentChatRequest(BaseModel):
    #session_id 会话id 用于区分不同用户
    session_id: str
    #question 用户的问题
    question: str
    #history 对话历史 可选 默认为None
    history: Optional[List[dict]] = None

#AIOps运维请求
#当前端调用 /api/agent/aiops时 请求体必须是这个结构
class AIOpsRequest(BaseModel):
    #task 任务类型 默认为"analyze_alerts 分析告警
    task: str = "analyze_alerts"
