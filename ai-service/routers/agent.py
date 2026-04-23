from fastapi import APIRouter,HTTPException
from schemas.response import AgentChatResponse
from schemas.request import AgentChatRequest
from dependencies import agent_service
#导入SSE流式响应支持
from sse_starlette.sse import EventSourceResponse
# 导入异步 IO
import asyncio

#创建路由对象
router = APIRouter()

#初始化Agent服务 全局单例 改用全局唯一实例
#agent_service = AgentService()

@router.post("/chat",response_model=AgentChatResponse)
async def agent_chat(request:AgentChatRequest):
    """
        Agent 对话接口（非流式）
        接收用户问题，Agent 自动判断是否需要调用工具，返回答案
        请求体：{"session_id": "test", "question": "现在几点了？"}
        响应体：{"answer": "当前时间是：2026-04-23 14:30:00", "tool_used": "datetime", "success": true}
    """
    try:
        result = agent_service.chat(request.question)
        return AgentChatResponse(
            answer=result["answer"],
            tool_used=result["tool_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.post("/chat_stream")
async def agent_chat_stream(request:AgentChatRequest):
    """
    Agent 流式对话接口
    接收用户问题，流式返回 AI 生成的答案
    请求体：{"session_id": "test", "question": "你好"}
    响应：SSE 事件流
    """
    async def event_generator():
        #先获取完整答案
        result = agent_service.chat(request.question)
        answer = result["answer"]
        #将答案分成字符 每次输出50个
        for i in range(0,len(answer),50):
            chunk = answer[i:i+50]
            yield {"data":chunk}
            await asyncio.sleep(0.1)