from mcp.server.fastmcp import FastMCP

from tools.date_time_tool import get_current_date, get_current_datetime, get_current_time
from tools.internal_docs_tool import query_internal_docs
from tools.query_log_tool import get_available_log_topics, query_logs
from tools.query_metrics_tool import query_prometheus_alerts

mcp = FastMCP(
    "SuperBizAgent MCP Server",
    instructions="SuperBizAgent AI Service - provides oncall tools for datetime, internal docs, logs, and metrics",
    port=8001,
    host="0.0.0.0",
)


@mcp.tool()
async def get_datetime() -> str:
    """获取当前日期和时间，返回格式如 2026-04-23 14:30:00"""
    return get_current_datetime()


@mcp.tool()
async def get_date() -> str:
    """获取当前日期，返回格式如 2026-04-23"""
    return get_current_date()


@mcp.tool()
async def search_internal_docs(query: str, top_k: int = 3) -> dict:
    """查询内部文档知识库，使用向量相似性搜索与查询最相关的文档"""
    return query_internal_docs(query, top_k)


@mcp.tool()
async def search_logs(
    region: str = "ap-guangzhou",
    log_topic: str = "system-metrics",
    query: str = "",
    limit: int = 20,
) -> dict:
    """查询系统日志"""
    return query_logs(region, log_topic, query, limit)


@mcp.tool()
async def get_log_topics() -> dict:
    """获取可用的日志主题列表"""
    return get_available_log_topics()


@mcp.tool()
async def get_active_alerts() -> dict:
    """查询 Prometheus 当前活跃告警"""
    return query_prometheus_alerts()
