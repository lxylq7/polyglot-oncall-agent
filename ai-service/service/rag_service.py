#导入客户端
from clients.dashscope_client import DashScopeClient
from clients.chroma_client import ChromaClient
#导入配置
from config import settings

class RAGService:
    """RAG 检索增强生成服务"""
    def __init__(self):
        """初始化RAG服务 创建所需的客户端"""
        self.dashscope = DashScopeClient() #大模型数据库
        self.chroma = ChromaClient() #向量库数据库

    def query(self,question:str,history:list = None) -> dict:
        """
            执行 RAG 查询（非流式）
                完整流程：
                1. 在 ChromaDB 中搜索与问题最相似的文档
                2. 将检索到的文档拼接成上下文
                3. 将上下文和问题组合成提示词
                4. 调用大模型生成答案
                5. 返回答案和参考来源
            Args:
                question: 用户问题
                history: 对话历史（暂未使用，预留扩展）
            Returns:
                {"answer": "AI回答", "sources": ["参考文档1", "参考文档2"]}
        """
        #向量检索
        results = self.chroma.search(question,top_k=settings.rag_top_k)
        #如果没有找到相关文档
        if not results:
            return {
                "answer":"抱歉,知识库中没有相关信息",
                "sources":[]
            }
        # 构建上下文
        # 将检索到的文档格式化为  【参考资料1】内容\n【参考资料2】内容
        context = "\n".join([
            f"【参考资料{i + 1}】{result['content']}"
            for i, result in enumerate(results)
        ])
        #构建提示词
        prompt = f"""
        基于以下参考资料回答用户问题：
        参考资料：
        {context}
        用户问题：{question}
        请使用中文详细回答，确保答案准确引用参考资料。
                """.strip()

        #调用大模型生成答案
        answer = self.dashscope.generate(prompt)
        #返回结果
        return {
            "answer": answer,
            "sources": [result['content'] for result in results]
        }

    def query_stream(self,question:str,history:list = None) -> dict:
        """
        执行 RAG 查询（流式）

        与 query() 流程相同，但使用流式大模型调用
        适合前端实时展示 AI 的回答过程

        Args:
            question: 用户问题
            history: 对话历史

        Yields:
            每个生成的文本片段
        """
        #向量检索
        results = self.chroma.search(question,top_k=settings.rag_top_k)
        #如果没有找到相关文档
        if not results:
            yield "抱歉,知识库中没有相关信息"
            return
        # 构建上下文
        # 将检索到的文档格式化为  【参考资料1】内容\n【参考资料2】内容
        context = "\n".join([
            f"【参考资料{i + 1}】{result['content']}"
            for i, result in enumerate(results)
        ])
        #构建提示词
        prompt = f"""
        基于以下参考资料回答用户问题：
        参考资料：
        {context}
        用户问题：{question}
        请使用中文详细回答，确保答案准确引用参考资料。
                """.strip()

        #流式调用大模型生成答案
        for chunk in self.dashscope.generate(prompt):
            yield chunk

    def add_document(self,content:str,metadata:dict = None):
        """
        添加文档到知识库
        Args:
            content: 文档文本内容
            metadata: 文档元数据（如文件名、上传时间等）

        Returns:
            操作结果
        """
        if metadata is None:
            metadata = {}
            return self.chroma.add_documents([content],[metadata])
