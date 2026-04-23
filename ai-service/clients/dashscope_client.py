import dashscope

from config import settings

class DashScopeClient:
    def __init__(self):
        """初始化DashScope客户端"""
        #设置api key
        dashscope.api_key = settings.dashscope_api_key
        print(f"✅ DashScope 初始化成功")

    def generate(self,prompt: str,model:str = None):
        """
        调用大模型生成回答（非流式）
        Args:
            prompt: 提示词（包含上下文和问题）
            model: 模型名称，默认为配置中的 rag_model
        Returns:
            str: 生成的回答文本
        """
        model_name = model or settings.rag_model

        #调用流式API
        responses = dashscope.Generation.call(
            model=model_name,
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )

        #遍历流式响应
        for response in responses:
            if response.output:
                #每次返回一个文本片段
                yield response.output.text
