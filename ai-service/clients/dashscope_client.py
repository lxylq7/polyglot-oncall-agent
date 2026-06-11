import dashscope

from config import settings


class DashScopeClient:
    """初始化 DashScope 客户端"""

    def __init__(self):
        dashscope.api_key = settings.dashscope_api_key
        print(f"DashScope 初始化成功")

    def generate(self, prompt: str, model: str = None) -> str:
        """调用大模型生成回答（非流式，纯文本）"""
        model_name = model or settings.rag_model

        try:
            response = dashscope.Generation.call(
                model=model_name,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7,
            )
            output = getattr(response, "output", None)
            text = getattr(output, "text", None) if output else None
            if text:
                return text

            choices = getattr(output, "choices", None) if output else None
            if choices and len(choices) > 0:
                msg = choices[0].get("message") if isinstance(choices[0], dict) else getattr(choices[0], "message", None)
                if isinstance(msg, dict):
                    return msg.get("content", "")
                return getattr(msg, "content", "")
            return "抱歉，我暂时无法回答这个问题。"
        except Exception as e:
            print(f"DashScope API 调用失败: {e}")
            return "抱歉，服务暂时不可用，请稍后重试。"

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        model: str = None,
    ) -> dict:
        """
        调用大模型，支持 function calling（工具调用）

        Args:
            messages: 对话消息列表 [{"role": "user/assistant/tool", "content": "..."}]
            tools: 工具定义列表，DashScope 格式
            model: 模型名称

        Returns:
            {
                "finish_reason": "stop" | "tool_calls",
                "content": "文本回答" | None,
                "tool_calls": [{"name": "...", "arguments": {...}}] | None,
            }
        """
        model_name = model or settings.rag_model

        try:
            response = dashscope.Generation.call(
                model=model_name,
                messages=messages,
                tools=tools,
                max_tokens=2000,
                temperature=0.7,
            )

            output = getattr(response, "output", None)
            if not output:
                return {"finish_reason": "stop", "content": "抱歉，我暂时无法回答。"}

            choices = getattr(output, "choices", None)
            if not choices or len(choices) == 0:
                return {"finish_reason": "stop", "content": "抱歉，我暂时无法回答。"}

            choice = choices[0]
            finish_reason = getattr(choice, "finish_reason", "stop")

            # 模型决定调用工具
            if finish_reason == "tool_calls":
                message = getattr(choice, "message", {})
                if isinstance(message, dict):
                    raw_tool_calls = message.get("tool_calls", [])
                else:
                    raw_tool_calls = getattr(message, "tool_calls", [])

                tool_calls = []
                for tc in raw_tool_calls:
                    if isinstance(tc, dict):
                        func = tc.get("function", {})
                        name = func.get("name", "")
                        arguments_str = func.get("arguments", "{}")
                    else:
                        func = getattr(tc, "function", None)
                        name = getattr(func, "name", "") if func else ""
                        arguments_str = getattr(func, "arguments", "{}") if func else "{}"

                    # arguments 可能是 JSON 字符串，需要解析
                    import json
                    try:
                        arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                    except json.JSONDecodeError:
                        arguments = {}

                    tool_calls.append({"name": name, "arguments": arguments})

                return {
                    "finish_reason": "tool_calls",
                    "content": None,
                    "tool_calls": tool_calls,
                }

            # 模型直接回答
            message = getattr(choice, "message", {})
            if isinstance(message, dict):
                content = message.get("content", "")
            else:
                content = getattr(message, "content", "")

            return {
                "finish_reason": "stop",
                "content": content or "抱歉，我暂时无法回答。",
                "tool_calls": None,
            }

        except Exception as e:
            print(f"DashScope function calling 失败: {e}")
            return {
                "finish_reason": "stop",
                "content": "抱歉，服务暂时不可用，请稍后重试。",
            }

    def generate_stream(self, prompt: str, model: str = None):
        """流式调用大模型"""
        model_name = model or settings.rag_model
        try:
            responses = dashscope.Generation.stream_call(
                model=model_name,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7,
            )
            for response in responses:
                if response.output and response.output.text:
                    yield response.output.text
        except Exception as e:
            print(f"DashScope 流式调用失败: {e}")
            yield "抱歉，流式服务暂时不可用。"
