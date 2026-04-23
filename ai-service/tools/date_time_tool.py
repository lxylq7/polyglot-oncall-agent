from datetime import datetime

def get_current_datetime() -> str:
    """
    获取当前日期和时间
        Returns:
            格式化的时间字符串，如 "2026-04-23 14:30:00"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
    """
    获取当前日期
        Returns:
            格式化的时间字符串，如 "2026-04-23"
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

def get_current_time() -> str:
    """
    获取当前时间
        Returns:
            格式化的时间字符串，如 "14:30:00"
    """
    now = datetime.now()
    return now.strftime("%H:%M:%S")