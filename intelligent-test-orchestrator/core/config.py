"""
配置模块 - 定义测试模式和报告格式枚举
"""

from enum import Enum


class TestMode(str, Enum):
    """测试模式枚举"""
    FULL = "full"           # 完整测试流程
    LIGHT = "light"         # 快速扫描（仅高危）
    CUSTOM = "custom"       # 自定义配置


class ReportFormat(str, Enum):
    """报告格式枚举"""
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    JSON = "json"


# 默认配置
DEFAULT_CONFIG = {
    'time_limit': 120,              # 默认时间限制（分钟）
    'concurrent_tools': 3,          # 并发工具数
    'skip_verification': False,     # 是否跳过验证
    'severity_filter': ['critical', 'high', 'medium', 'low', 'info'],
}
