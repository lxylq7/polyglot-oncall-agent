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

        try:
            response = dashscope.Generation.call(
                model=model_name,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            # response 对象包含：
            # - response.status_code  # HTTP 状态码
            # - response.output
            #         "text": "回答内容",
            #         "choices": [...],
            #         "finish_reason": "stop"
            # - response.usage        # 用量统计

            #新结构
            #output choices messages

            output = getattr(response, "output", None)

            #兼容旧字段
            text = getattr(output, "text", None) if output else None
            if text:
                return text

            #兼容新字段
            choices = getattr(output,"choices", None) if output else None
            if choices and len(choices) > 0:
                msg = choices[0].get("message") if isinstance(choices[0], dict) else getattr(choices, "message", None)
                if isinstance(msg, dict):
                    content = msg.get("content")
                else:
                    content = getattr(msg, "content", None)
                if content:
                    return content
                return "抱歉，我暂时无法回答这个问题。"
        except Exception as e:
            print(f"❌ DashScope API 调用失败: {e}")
            return "抱歉，服务暂时不可用，请稍后重试。"

    def generate_stream(self, prompt: str, model: str = None):
        """流式 返回"""
        model_name = model or settings.rag_model
        try:
            responses = dashscope.Generation.stream_call(
                model=model_name,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            for response in responses:
                if response.output and response.output.text:
                    yield response.output.text
        except Exception as e:
            print(f"❌ DashScope 流式调用失败: {e}")
            yield "抱歉，流式服务暂时不可用。"