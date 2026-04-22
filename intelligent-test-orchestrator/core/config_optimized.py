"""
优化配置模块 - 使用 dataclass 和 Pydantic 进行类型安全和验证
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json
import yaml
from pathlib import Path


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


class RiskScoreMode(str, Enum):
    """风险评分模式"""
    THREAT = "threat"       # 威胁模式：分数越高风险越高
    SAFETY = "safety"       # 安全模式：分数越低越危险


@dataclass
class ToolConfig:
    """工具配置"""
    enabled: bool = True
    timeout: int = 300
    max_retries: int = 2
    concurrent_limit: int = 3
    custom_args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Phase0Config:
    """Phase-0 资产收集配置"""
    whatweb: ToolConfig = field(default_factory=ToolConfig)
    nmap: ToolConfig = field(default_factory=ToolConfig)
    httpx: ToolConfig = field(default_factory=ToolConfig)
    subfinder: ToolConfig = field(default_factory=ToolConfig)


@dataclass
class Phase2Config:
    """Phase-2 漏洞检测配置"""
    nuclei: ToolConfig = field(default_factory=lambda: ToolConfig(timeout=900))
    afrog: ToolConfig = field(default_factory=ToolConfig)
    nikto: ToolConfig = field(default_factory=lambda: ToolConfig(timeout=600))
    zap: ToolConfig = field(default_factory=lambda: ToolConfig(timeout=900, custom_args={'port': 8080}))
    sqlmap: ToolConfig = field(default_factory=lambda: ToolConfig(timeout=600, max_retries=1))


@dataclass
class Phase3Config:
    """Phase-3 漏洞验证配置"""
    enabled: bool = True
    timeout: int = 300
    max_concurrent: int = 3
    confidence_threshold: float = 0.7


@dataclass
class RiskProfilerConfig:
    """风险评分器配置"""
    score_mode: RiskScoreMode = RiskScoreMode.SAFETY
    max_score: float = 100.0
    severity_weights: Dict[str, float] = field(default_factory=lambda: {
        'critical': 10.0,
        'high': 7.0,
        'medium': 4.0,
        'low': 2.0,
        'info': 1.0,
    })


@dataclass
class OrchestratorConfig:
    """智能编排器主配置"""
    # 基本配置
    test_mode: TestMode = TestMode.FULL
    report_formats: List[ReportFormat] = field(default_factory=lambda: [ReportFormat.HTML, ReportFormat.MARKDOWN])
    
    # 资源限制
    time_limit: int = 120           # 分钟
    concurrent_tools: int = 3       # 并发工具数
    max_memory_mb: int = 2048       # 最大内存使用（MB）
    
    # 功能开关
    skip_verification: bool = False
    enable_caching: bool = True
    enable_progress_feedback: bool = True
    
    # 严重性过滤
    severity_filter: List[str] = field(default_factory=lambda: ['critical', 'high', 'medium', 'low', 'info'])
    
    # 各阶段配置
    phase0: Phase0Config = field(default_factory=Phase0Config)
    phase2: Phase2Config = field(default_factory=Phase2Config)
    phase3: Phase3Config = field(default_factory=Phase3Config)
    risk_profiler: RiskProfilerConfig = field(default_factory=RiskProfilerConfig)
    
    # 报告配置
    output_dir: str = "./reports"
    log_dir: str = "./logs"
    log_level: str = "INFO"
    
    # 高级配置
    enable_retry: bool = True
    max_retries: int = 2
    retry_delay: int = 5            # 秒
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        from dataclasses import asdict
        config_dict = asdict(self)
        # 转换枚举为字符串
        config_dict['test_mode'] = self.test_mode.value
        config_dict['report_formats'] = [fmt.value for fmt in self.report_formats]
        config_dict['risk_profiler']['score_mode'] = self.risk_profiler.score_mode.value
        return config_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestratorConfig':
        """从字典创建"""
        # 转换字符串为枚举
        if 'test_mode' in data:
            data['test_mode'] = TestMode(data['test_mode'])
        if 'report_formats' in data:
            data['report_formats'] = [ReportFormat(fmt) for fmt in data['report_formats']]
        if 'risk_profiler' in data and 'score_mode' in data['risk_profiler']:
            data['risk_profiler']['score_mode'] = RiskScoreMode(data['risk_profiler']['score_mode'])
        
        # 嵌套 dataclass 处理
        if 'phase0' in data:
            data['phase0'] = Phase0Config(**data['phase0'])
        if 'phase2' in data:
            data['phase2'] = Phase2Config(**data['phase2'])
        if 'phase3' in data:
            data['phase3'] = Phase3Config(**data['phase3'])
        if 'risk_profiler' in data:
            data['risk_profiler'] = RiskProfilerConfig(**data['risk_profiler'])
        
        return cls(**data)
    
    def to_json(self, indent: int = 2) -> str:
        """导出为 JSON"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """导出为 YAML"""
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'OrchestratorConfig':
        """从 JSON 加载"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'OrchestratorConfig':
        """从 YAML 加载"""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: str) -> None:
        """保存到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix in ['.json']:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
        elif path.suffix in ['.yml', '.yaml']:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.to_yaml())
        else:
            raise ValueError(f"不支持的文件格式：{path.suffix}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'OrchestratorConfig':
        """从文件加载"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在：{filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if path.suffix in ['.json']:
            return cls.from_json(content)
        elif path.suffix in ['.yml', '.yaml']:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"不支持的文件格式：{path.suffix}")


class ConfigManager:
    """配置管理器 - 单例模式"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[OrchestratorConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if self._config is None:
            self._config = OrchestratorConfig()
    
    @property
    def config(self) -> OrchestratorConfig:
        """获取当前配置"""
        return self._config
    
    @config.setter
    def config(self, new_config: OrchestratorConfig) -> None:
        """设置新配置"""
        self._config = new_config
    
    def load(self, filepath: str) -> OrchestratorConfig:
        """从文件加载配置"""
        self._config = OrchestratorConfig.load_from_file(filepath)
        return self._config
    
    def save(self, filepath: str) -> None:
        """保存配置到文件"""
        self._config.save_to_file(filepath)
    
    def reset(self) -> None:
        """重置为默认配置"""
        self._config = OrchestratorConfig()
    
    def update(self, **kwargs) -> None:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return getattr(self._config, key, default)
    
    def validate(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        # 验证时间限制
        if self._config.time_limit <= 0:
            errors.append("time_limit 必须大于 0")
        
        # 验证并发数
        if self._config.concurrent_tools < 1:
            errors.append("concurrent_tools 必须至少为 1")
        
        # 验证内存限制
        if self._config.max_memory_mb < 512:
            errors.append("max_memory_mb 必须至少为 512MB")
        
        # 验证严重性权重
        for severity, weight in self._config.risk_profiler.severity_weights.items():
            if weight < 0:
                errors.append(f"severity_weights.{severity} 不能为负数")
        
        return errors


# 全局配置管理器实例
config_manager = ConfigManager()


# 便捷函数
def get_config() -> OrchestratorConfig:
    """获取当前配置"""
    return config_manager.config


def load_config(filepath: str) -> OrchestratorConfig:
    """从文件加载配置"""
    return config_manager.load(filepath)


def save_config(filepath: str) -> None:
    """保存配置到文件"""
    config_manager.save(filepath)


def reset_config() -> None:
    """重置为默认配置"""
    config_manager.reset()


def update_config(**kwargs) -> None:
    """更新配置"""
    config_manager.update(**kwargs)
