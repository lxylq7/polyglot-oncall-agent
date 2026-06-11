# 定义所有 API 响应的数据结构
from pydantic import BaseModel
from typing import List, Optional


class RagQueryResponse(BaseModel):
    """RAG 查询响应"""
    answer: str
    sources: List[str]
    success: bool = True


class AgentChatResponse(BaseModel):
    """Agent 对话响应"""
    answer: str
    tool_used: Optional[List[str]] = None
    success: bool = True


class AIOpsResponse(BaseModel):
    """AIOps 运维响应"""
    report: str
    status: str
    success: bool = True
