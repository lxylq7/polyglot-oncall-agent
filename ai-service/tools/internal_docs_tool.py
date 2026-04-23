#导入chromadb客户端
from clients.chroma_client import ChromaClient
#导入配置
from config import settings

#创建chromadb的客户端实例 ragservice也创建了一个 后续可以优化为同一个
_chroma_client = ChromaClient()


def query_internal_docs(query: str, top_k: int = None) -> dict:
    """
    查询内部文档知识库
    使用向量相似性搜索，从 ChromaDB 中检索与查询最相关的文档。
    对应 Java 中的 InternalDocsTools.queryInternalDocs()
    Args:
        query: 搜索查询，描述要查找的信息
               如 "CPU使用率过高的处理步骤"
        top_k: 返回的文档数量，默认从配置读取
    Returns:
        搜索结果字典，格式：
        {
            "status": "success",
            "results": [
                {
                    "id": "doc_0",
                    "content": "文档内容...",
                    "metadata": {"source": "cpu_high_usage.md"}
                }
            ]
        }
        如果没有找到结果：
        {
            "status": "no_results",
            "message": "No relevant documents found in the knowledge base."
        }
    """
    # 使用配置的 top_k，或传入的值
    actual_top_k = top_k or settings.rag_top_k

    try:
        #调用chromadb客户端搜索
        results = _chroma_client.search(query,top_k=actual_top_k)
        if not results:
            return {
                "status": "no_results",
                "message": "No relevant documents found in the knowledge base."
            }
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to query internal docs: {str(e)}"
        }

