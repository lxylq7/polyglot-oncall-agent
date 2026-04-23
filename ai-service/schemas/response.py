#定义所有api请求的数据结构
#导入pydantic的basemodel 所有数据类型的基类
from pydantic import BaseModel
#导入类型提示
from typing import List,Optional

#Rag查询响应
#当/api/rag/query返回结果时 响应体必须是这个结构
class RagQueryResponse(BaseModel):
    #answer AI生成的回答
    answer: str
    #sources 参考的文档来源列表
    sources: List[str]
    #success 是否成功 默认True
    success: bool = True

#Agent对话响应
#当/api/agent/chat返回结果时 响应体必须是这个结构
class AgentChatResponse(BaseModel):
    # answer AI生成的回答
    answer: str
    #tool_used 使用了哪个工具
    tool_used: Optional[str] = None
    #success 是否成功 默认True
    success: bool = True

#AIOps运维响应
#当/api/agent/aiops返回结果时 响应体必须是这个结构
class AIOpsResponse(BaseModel):
    #report 生成的告警分析报告
    report: str
    #status 任务状态
    status: str
    #success 是否成功 默认True
    success: bool = True
