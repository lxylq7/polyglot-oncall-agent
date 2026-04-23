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

        #调用API
        response = dashscope.Generation.call(
            model=model_name,
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )

        #直接返回字符串
        return response.output.text

    def generate_stream(self, prompt: str, model: str = None):
        """流式：逐段返回"""
        model_name = model or settings.rag_model
        responses = dashscope.Generation.stream_call(
            model=model_name,
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )
        for response in responses:
            if response.output:
                yield response.output.text