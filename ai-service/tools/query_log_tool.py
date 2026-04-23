from datetime import datetime, timedelta


def get_available_log_topics() -> dict:
    """获取可用的日志主题列表"""
    return {
        "success": True,
        "topics": [
            {
                "topic_name": "system-metrics",
                "description": "系统指标日志（CPU、内存、磁盘）",
                "related_alerts": ["HighCPUUsage", "HighMemoryUsage"]
            },
            {
                "topic_name": "application-logs",
                "description": "应用日志（错误、慢请求、依赖调用）",
                "related_alerts": ["ServiceUnavailable", "SlowResponse"]
            }
        ],
        "default_region": "ap-guangzhou"
    }

def query_logs(region: str = "ap-guangzhou", log_topic: str = "system-metrics",
               query: str = "", limit: int = 20) -> dict:
    """查询日志（目前只支持 Mock 模式）"""
    now = datetime.now()
    #先返回少量Mock数据够 测试
    mock_logs = [
        {
            "timestamp": (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "level": "ERROR",
            "service": "order-service",
            "message": "数据库连接池耗尽: active: 50/50, waiting: 23",
            "metrics": {"pool_active": "50", "pool_max": "50"}
        },
        {
            "timestamp": (now - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "level": "WARN",
            "service": "payment-service",
            "message": "CPU使用率过高: 92.0%",
            "metrics": {"cpu_usage": "92.0"}
        }
    ]
    return {
        "success": True,
        "region": region,
        "log_topic": log_topic,
        "logs": mock_logs[:limit],
        "total": len(mock_logs),
        "message": f"成功查询到 {len(mock_logs)} 条日志（Mock 数据）"
    }