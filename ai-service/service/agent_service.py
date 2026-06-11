import json

from clients.mcp_client import MCPClient
from clients.dashscope_client import DashScopeClient


class AgentService:
    """AI Agent 服务 —— 由大模型通过 function calling 自主决定调用哪些 MCP 工具"""

    def __init__(self, rag_service, dashscope_client: DashScopeClient, mcp_client: MCPClient):
        self.rag_service = rag_service
        self.dashscope = dashscope_client
        self.mcp = mcp_client
        self._tools_cache = None  # 缓存 MCP 工具列表

    # ── 工具定义 ──────────────────────────────────────────

    def _load_tools(self) -> list[dict]:
        """从 MCP Server 获取工具列表并转为 DashScope function calling 格式"""
        if self._tools_cache is not None:
            return self._tools_cache

        try:
            mcp_tools = self.mcp.list_tools()
        except Exception as e:
            print(f"获取 MCP 工具列表失败: {e}")
            mcp_tools = []

        tools = []
        for t in mcp_tools:
            schema = t.get("inputSchema", {})
            tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": {
                        "type": schema.get("type", "object"),
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    },
                },
            })

        self._tools_cache = tools
        return tools

    # ── 对话流程 ──────────────────────────────────────────

    def chat(self, question: str, history: list = None) -> dict:
        """
        由大模型自主决定调哪些工具、如何回答。

        流程:
        1. 从 MCP Server 拉取工具定义
        2. 把工具定义 + 用户问题 + 历史发给大模型
        3. 大模型决定: 直接回答 / 调用某个 MCP 工具
        4. 如需调工具 → 通过 MCP Client 执行 → 结果回传大模型 → 生成最终回答
        """
        tools = self._load_tools()

        # 构建消息
        messages = self._build_messages(question, history)

        # 第一轮：大模型决策（回答 or 调工具）
        result = self.dashscope.chat_with_tools(messages, tools)

        if result["finish_reason"] == "tool_calls" and result["tool_calls"]:
            # 大模型要求调工具
            tool_calls = result["tool_calls"]

            # 把模型的 tool_calls 加入消息
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"], ensure_ascii=False),
                        },
                    }
                    for i, tc in enumerate(tool_calls)
                ],
            })

            # 依次执行每个工具调用
            tool_results = []
            for i, tc in enumerate(tool_calls):
                try:
                    raw = self.mcp.call_tool(tc["name"], tc["arguments"])
                    tool_output = self._extract_text(raw)
                except Exception as e:
                    tool_output = f"工具调用失败: {str(e)}"

                tool_results.append({
                    "name": tc["name"],
                    "result": tool_output,
                })

                # 把工具结果加入消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": f"call_{i}",
                    "content": tool_output,
                })

            # 第二轮：大模型根据工具结果生成最终回答
            final = self.dashscope.chat_with_tools(messages, tools)

            return {
                "answer": final.get("content", "抱歉，无法生成回答。"),
                "tool_used": [tr["name"] for tr in tool_results],
                "tool_results": tool_results,
            }

        # 大模型直接回答（不需要调工具）
        return {
            "answer": result.get("content", "抱歉，我暂时无法回答。"),
            "tool_used": [],
        }

    # ── 辅助方法 ──────────────────────────────────────────

    def _build_messages(self, question: str, history: list = None) -> list[dict]:
        """构建包含历史记录的 messages 列表"""
        system_prompt = (
            "你是一个运维 AI 助手 SuperBizAgent。"
            "你可以使用提供的工具来帮助用户查询时间、搜索内部文档、查询日志和告警。"
            "当用户的问题可以通过工具回答时，请调用相应的工具。"
            "调用工具后，请根据工具返回的结果生成清晰的中文回答。"
        )
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for item in history:
                role = item.get("role", "user")
                content = item.get("content", "")
                if role in ("user", "assistant"):
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": question})
        return messages

    def _extract_text(self, raw: dict | list | str) -> str:
        """从 MCP 工具返回值中提取纯文本"""
        if isinstance(raw, str):
            return raw
        if isinstance(raw, dict):
            # MCP content 格式: {"type": "text", "text": "..."}
            if raw.get("type") == "text":
                return raw.get("text", "")
            return json.dumps(raw, ensure_ascii=False, default=str)
        if isinstance(raw, list):
            parts = []
            for item in raw:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(raw)
