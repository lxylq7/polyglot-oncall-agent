#提供Prometheus告警查询功能 当用户问有什么告警时使用
#导入requests库 用于发送HTTP请求
import requests
from config import settings

def query_prometheus_alerts() -> dict:
    """
        查询 Prometheus 活动告警
        根据配置决定使用真实 API 还是模拟数据：
        - prometheus_mock_enabled=True: 返回模拟数据（开发测试用）
        - prometheus_mock_enabled=False: 调用真实 Prometheus API

        Returns:
            告警数据字典，格式：
            {
                "success": True,
                "alerts": [
                    {"alert_name": "...", "description": "...", "state": "...", "duration": "..."}
                ]
            }
    """
    #检查是否需要使用模拟数据
    if settings.prometheus_mock_enabled:
        return _build_mock_alerts()

    #真实模式 调用prometheus api
    #构建api地址
    try:
        api_url = f"{settings.prometheus_url}/api/v1/alerts"
        response = requests.get(api_url,timeout=10)
        #检查http状态码
        response.raise_for_status()
        #返回json数据
        return response.json()
    except Exception as e:
        #出错时返回错误信息
        return {"success": False,"error":str(e)}


def _build_mock_alerts() -> dict:
    """
    构建模拟告警数据（私有函数，以 _ 开头）

    用于开发和测试，不需要真实的 Prometheus 服务

    Returns:
        模拟的告警数据
    """
    return {
        "success": True,
        "alerts": [
            {
                "alert_name": "HighCPUUsage",
                "description": "服务 payment-service 的 CPU 使用率持续超过 80%，当前值为 92%",
                "state": "firing",
                "duration": "25m"
            },
            {
                "alert_name": "HighMemoryUsage",
                "description": "服务 order-service 的内存使用率持续超过 85%，当前值为 91%",
                "state": "firing",
                "duration": "15m"
            },
            {
                "alert_name": "SlowResponse",
                "description": "服务 user-service 的 P99 响应时间持续超过 3 秒，当前值为 4.2 秒",
                "state": "firing",
                "duration": "10m"
            }
        ]
    }