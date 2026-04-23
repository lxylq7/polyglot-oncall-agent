
from pydantic_settings import BaseSettings #自动读取环境变量 配置文件 不需要手写os.getenv()
from dotenv import load_dotenv

#第三方手动加载 加载配置文件
load_dotenv()

#定义配置类
class Settings(BaseSettings):
    #兜底的默认值 当环境变量 配置文件中没有时

    # DashScope API Key
    dashscope_api_key: str

    # ChromaDB Configuration 向量数据库
    chroma_persist_directory:str = "./chroma_db"
    chroma_db_collection_name:str = "document_chunks"

    # Rag Configuration 向量检索配置
    rag_top_k: int = 3
    rag_model: str = "qwen3-max"

    # Server Configuration 服务器配置
    server_port: int = 8000

    # Prometheus Configuration 普罗米修斯监控系统
    prometheus_url: str ="http://localhost:9090"
    prometheus_mock_enabled: bool = True  # 是否启用Prometheus模拟数据

    #指定从.env文件读取
    class Config:
        env_file = ".env"

#创建配置实例 供其他模块使用 如果不创建实例 每次都会加载一次配置文件 导致性能问题
settings = Settings()