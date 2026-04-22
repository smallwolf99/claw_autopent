"""
Pydantic 验证配置模块 - 提供运行时数据验证
"""

from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
import json
import yaml


class TestMode(str, Enum):
    """测试模式枚举"""
    FULL = "full"
    LIGHT = "light"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """报告格式枚举"""
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    JSON = "json"


class RiskScoreMode(str, Enum):
    """风险评分模式"""
    THREAT = "threat"
    SAFETY = "safety"


class ToolConfig(BaseModel):
    """工具配置（Pydantic 验证）"""
    enabled: bool = True
    timeout: int = Field(default=300, ge=10, le=3600)
    max_retries: int = Field(default=2, ge=0, le=10)
    concurrent_limit: int = Field(default=3, ge=1, le=10)
    custom_args: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v % 10 != 0:
            raise ValueError('timeout 必须是 10 的倍数')
        return v


class Phase0Config(BaseModel):
    """Phase-0 配置"""
    whatweb: ToolConfig = Field(default_factory=ToolConfig)
    nmap: ToolConfig = Field(default_factory=ToolConfig)
    httpx: ToolConfig = Field(default_factory=ToolConfig)
    subfinder: ToolConfig = Field(default_factory=ToolConfig)


class Phase2Config(BaseModel):
    """Phase-2 配置"""
    nuclei: ToolConfig = Field(default_factory=lambda: ToolConfig(timeout=900))
    afrog: ToolConfig = Field(default_factory=ToolConfig)
    nikto: ToolConfig = Field(default_factory=lambda: ToolConfig(timeout=600))
    zap: ToolConfig = Field(default_factory=lambda: ToolConfig(timeout=900))
    sqlmap: ToolConfig = Field(default_factory=lambda: ToolConfig(timeout=600, max_retries=1))


class Phase3Config(BaseModel):
    """Phase-3 配置"""
    enabled: bool = True
    timeout: int = Field(default=300, ge=60, le=600)
    max_concurrent: int = Field(default=3, ge=1, le=10)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class RiskProfilerConfig(BaseModel):
    """风险评分器配置"""
    score_mode: RiskScoreMode = RiskScoreMode.SAFETY
    max_score: float = Field(default=100.0, gt=0)
    severity_weights: Dict[str, float] = Field(default_factory=lambda: {
        'critical': 10.0,
        'high': 7.0,
        'medium': 4.0,
        'low': 2.0,
        'info': 1.0,
    })
    
    @validator('severity_weights')
    def validate_severity_weights(cls, v):
        required_severities = ['critical', 'high', 'medium', 'low', 'info']
        for severity in required_severities:
            if severity not in v:
                raise ValueError(f'缺少严重性级别：{severity}')
            if v[severity] < 0:
                raise ValueError(f'严重性权重不能为负数：{severity}')
        return v


class OrchestratorConfig(BaseModel):
    """智能编排器主配置（Pydantic 验证）"""
    
    # 基本配置
    test_mode: TestMode = TestMode.FULL
    report_formats: List[ReportFormat] = Field(
        default_factory=lambda: [ReportFormat.HTML, ReportFormat.MARKDOWN]
    )
    
    # 资源限制
    time_limit: int = Field(default=120, ge=5, le=1440)  # 5 分钟到 24 小时
    concurrent_tools: int = Field(default=3, ge=1, le=10)
    max_memory_mb: int = Field(default=2048, ge=512, le=8192)
    
    # 功能开关
    skip_verification: bool = False
    enable_caching: bool = True
    enable_progress_feedback: bool = True
    
    # 严重性过滤
    severity_filter: List[str] = Field(
        default_factory=lambda: ['critical', 'high', 'medium', 'low', 'info']
    )
    
    # 各阶段配置
    phase0: Phase0Config = Field(default_factory=Phase0Config)
    phase2: Phase2Config = Field(default_factory=Phase2Config)
    phase3: Phase3Config = Field(default_factory=Phase3Config)
    risk_profiler: RiskProfilerConfig = Field(default_factory=RiskProfilerConfig)
    
    # 报告配置
    output_dir: str = "./reports"
    log_dir: str = "./logs"
    log_level: str = "INFO"
    
    # 高级配置
    enable_retry: bool = True
    max_retries: int = Field(default=2, ge=0, le=5)
    retry_delay: int = Field(default=5, ge=0, le=60)
    
    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        validate_assignment = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestratorConfig':
        """从字典创建"""
        return cls(**data)
    
    def to_json(self, indent: int = 2) -> str:
        """导出为 JSON"""
        return self.json(indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'OrchestratorConfig':
        """从 JSON 加载"""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_yaml(self) -> str:
        """导出为 YAML"""
        return yaml.dump(self.dict(), default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'OrchestratorConfig':
        """从 YAML 加载"""
        data = yaml.safe_load(yaml_str)
        return cls(**data)
    
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
    
    def validate_all(self) -> List[str]:
        """执行额外验证（Pydantic 已处理基本验证）"""
        errors = []
        
        # 自定义验证逻辑
        if self.test_mode == TestMode.LIGHT and 'info' in self.severity_filter:
            errors.append("LIGHT 模式下不应包含 info 级别")
        
        if self.skip_verification and self.phase3.enabled:
            errors.append("跳过验证时不应启用 Phase-3")
        
        return errors


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate(config: OrchestratorConfig) -> Dict[str, Any]:
        """验证配置并返回结果"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config': config
        }
        
        # Pydantic 自动验证（在创建时已执行）
        
        # 执行额外验证
        extra_errors = config.validate_all()
        if extra_errors:
            result['valid'] = False
            result['errors'].extend(extra_errors)
        
        # 添加警告
        if config.time_limit > 600:
            result['warnings'].append("时间限制超过 10 小时，可能导致资源浪费")
        
        if config.max_memory_mb > 4096:
            result['warnings'].append("内存限制超过 4GB，请确保系统有足够内存")
        
        return result
    
    @staticmethod
    def validate_file(filepath: str) -> Dict[str, Any]:
        """验证配置文件"""
        try:
            config = OrchestratorConfig.load_from_file(filepath)
            return ConfigValidator.validate(config)
        except ValidationError as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'warnings': [],
                'config': None
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"加载失败：{e}"],
                'warnings': [],
                'config': None
            }


# 便捷函数
def create_default_config() -> OrchestratorConfig:
    """创建默认配置"""
    return OrchestratorConfig()


def create_light_config() -> OrchestratorConfig:
    """创建轻量级配置（快速扫描）"""
    return OrchestratorConfig(
        test_mode=TestMode.LIGHT,
        time_limit=30,
        concurrent_tools=2,
        severity_filter=['critical', 'high'],
        skip_verification=True,
        phase2=Phase2Config(
            nuclei=ToolConfig(timeout=300),
            afrog=ToolConfig(enabled=False),
            nikto=ToolConfig(enabled=False),
        )
    )


def create_full_config() -> OrchestratorConfig:
    """创建完整配置"""
    return OrchestratorConfig(
        test_mode=TestMode.FULL,
        time_limit=180,
        concurrent_tools=3,
        enable_caching=True,
        enable_progress_feedback=True,
    )
