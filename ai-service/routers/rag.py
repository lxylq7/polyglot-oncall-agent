#导入FastAPI的路由类
from fastapi import HTTPException,APIRouter
#导入请求和响应模型
from schemas.response import RagQueryResponse
from schemas.request import RagQueryRequest
from service import rag_service
#导入RAG服务
from service.rag_service import RAGService
#导入SSE流式响应支持
from sse_starlette.sse import EventSourceResponse
# 导入异步 IO
import asyncio

#创建路由对象 后续所有接口都注册在这个对象上
router = APIRouter()

#初始化RAG服务 全局单例
rag_service = RAGService()

@router.post("/query",response_model=RagQueryResponse)
async def rag_query(request:RagQueryRequest):
    """
        RAG 问答接口（非流式）
        接收用户问题，返回 AI 生成的答案
        请求体：{"question": "什么是向量数据库？", "history": []}
        响应体：{"answer": "向量数据库是...", "sources": ["参考文档1"], "success": true}
    """
    try:
        #调用RAG服务
        result = rag_service.query(request.question,request.history)
        #构造响应对象
        return RagQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        #出错时
        raise HTTPException(status_code=500,detail=str(e))

@router.post("/query_stream")
async def rag_query_stream(request:RagQueryRequest):
    """
        RAG 流式问答接口
        接收用户问题，流式返回 AI 生成的答案（SSE 格式）
        请求体：{"question": "什么是向量数据库？", "history": []}
        响应：SSE 事件流，每个事件包含一段文本
    """
    #定义异步生成器函数
    async def event_generator():
        #遍历流式响应的每个文本片段
        for chunk in rag_service.query_stream(request.question,request.history):
            #发送sse事件
            yield {"data":chunk}
            #短暂延迟 避免发送过快
            await asyncio.sleep(0.01)

    #返回SSE响应
    return EventSourceResponse(event_generator())

#原来是文件上传接口 功能在java端实现 这里写接受内容接口 由java端传过来
@router.post("/add_document")
async def add_document(request: dict):
    """
    接收文档内容并存入 ChromaDB
    由 Spring Boot 调用，不需要前端直接调用
    请求体：{"content": "文档内容...", "metadata": {"filename": "xxx.txt"}}
    """
    content = request.get("content", "")
    metadata = request.get("metadata", {})
    result = rag_service.add_document(content, metadata)
    return {"success": True, "message": "文档已添加到知识库"}


@router.get("/stats")
async def get_stats():
    """
    知识库统计接口
    返回知识库中的文档数量等信息
    响应：{"count": 10, "name": "document_chunks"}
    """
    return rag_service.chroma.get_state()