"""MCP Streamable-HTTP 客户端，连接本地 MCP Server"""
import httpx
import json


class MCPClient:
    """轻量级 MCP 客户端，通过 streamable-http 与 MCP Server 通信"""

    def __init__(self, url: str = "http://localhost:8001/mcp"):
        self.url = url
        self._request_id = 0

    def _rpc(self, method: str, params: dict = None) -> dict:
        """发送 JSON-RPC 2.0 请求"""
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {},
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(self.url, json=payload)
                resp.raise_for_status()
                result = resp.json()
                if "error" in result:
                    raise Exception(f"MCP error: {result['error']}")
                return result.get("result", {})
        except httpx.ConnectError:
            raise Exception(f"无法连接 MCP Server ({self.url})，请确认 MCP Server 已启动")

    def list_tools(self) -> list[dict]:
        """获取 MCP Server 暴露的所有工具定义"""
        result = self._rpc("tools/list")
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        """调用 MCP Server 上的指定工具"""
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        # MCP tool result 格式: { "content": [{"type": "text", "text": "..."}] }
        content = result.get("content", [])
        if content and isinstance(content, list):
            return content[0] if len(content) == 1 else content
        return result
