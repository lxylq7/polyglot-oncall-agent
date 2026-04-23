import chromadb

from config import settings
from chromadb.config import Settings as ChromaSettings

class ChromaClient:
    def __init__(self):
        #创建持久化客户端
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory, #文件存储位置
            settings=ChromaSettings(anonymized_telemetry=False) #anonymized_telemetry 禁用匿名遥测(软件在后台自动,悄悄发送给开发者的使用数据)
        )
        #创建一个向量数据表 有则直接使用 无则创建
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_db_collection_name
        )
        print(f"✅ ChromaDB 初始化成功")

    #添加文档 把文档存进去 不用我们手动向量化 documents文档内容 metadatas元数据(存附加信息,比如文件名,页码,来源等) ids文档编号
    def add_documents(self,documents:list,metadatas:list = None,ids: list = None):
        """添加文档到集合"""
        #如果没有提供元数据 创建空列表
        if metadatas is None:
            metadatas = [{} for _ in documents]
        #如果没有提供id 自动生成
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        #调用ChromaDB API添加文档 ChromaDB会自动向量化文档
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        return {"success":True,"count":len(documents)}

    def search(self,query_text:str,top_k:int = 3) -> list:
        """搜索相似文档"""
        #query_text 要搜索的文档列表 n_results 返回的文本数量
        results = self.collection.query(query_text=[query_text],n_results=top_k)

        #格式化结果 便于使用
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id":results["ids"][0][i],
                "document":results["documents"][0][i],
                "metadata":results["metadatas"][0][i] if results["metadatas"]
                else {}
            })
        return formatted_results

    def get_state(self):
        """获取集合统计信息"""
        return {"count":self.collection.count(),"name":self.collection.name}