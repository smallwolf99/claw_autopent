#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试策略生成器 - 基于资产信息和风险画像生成针对性测试策略

核心功能：
1. 根据风险评分生成测试动作
2. 按优先级排序测试计划
3. 生成可执行的测试命令列表
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestPriority(str, Enum):
    """测试优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestCategory(str, Enum):
    """测试分类"""
    CVE_VALIDATION = "cve_validation"
    CONFIGURATION_TEST = "configuration_test"
    AUTHENTICATION_TEST = "authentication_test"
    BUSINESS_LOGIC_TEST = "business_logic_test"
    INFORMATION_DISCLOSURE = "information_disclosure"


class TestAction:
    """测试动作"""
    
    def __init__(self, id: str, category: str, name: str, description: str,
                 priority: TestPriority = TestPriority.MEDIUM,
                 estimated_time: int = 30,
                 tools: Optional[List[str]] = None,
                 commands: Optional[List[str]] = None):
        self.id = id
        self.category = category
        self.name = name
        self.description = description
        self.priority = priority
        self.estimated_time_minutes = estimated_time
        self.tools = tools or []
        self.commands = commands or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "estimated_time_minutes": self.estimated_time_minutes,
            "tools": self.tools,
            "commands": self.commands
        }


class TestStrategy:
    """测试策略"""
    
    def __init__(self, target: str, risk_score: float):
        self.target = target
        self.risk_score = risk_score
        self.created_at = datetime.now()
        self.actions: List[TestAction] = []
    
    def add_action(self, action: TestAction):
        """添加测试动作"""
        self.actions.append(action)
    
    def get_actions_by_priority(self, priority: TestPriority) -> List[TestAction]:
        """按优先级获取动作"""
        return [a for a in self.actions if a.priority == priority]
    
    @property
    def total_actions(self) -> int:
        """获取总动作数"""
        return len(self.actions)
    
    def get_total_time(self) -> int:
        """获取总估计时间"""
        return sum(a.estimated_time_minutes for a in self.actions)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat(),
            "total_actions": len(self.actions),
            "total_time_minutes": self.get_total_time(),
            "actions": [a.to_dict() for a in self.actions]
        }


class TestStrategist:
    """测试策略生成器"""
    
    def __init__(self):
        """初始化策略生成器"""
        self.action_templates = self._load_action_templates()
        logger.info("测试策略生成器初始化完成")
    
    def generate_strategy(self, assets: List[Dict[str, Any]], 
                         risk_report: Dict[str, Any]) -> TestStrategy:
        """生成测试策略
        
        Args:
            assets: 资产列表
            risk_report: 风险评估报告
            
        Returns:
            TestStrategy: 测试策略
        """
        logger.info("开始生成测试策略")
        
        target = assets[0].get('url', 'unknown') if assets else 'unknown'
        risk_score = risk_report.get('overall_score', 50.0)
        
        strategy = TestStrategy(target=target, risk_score=risk_score)
        
        # 根据风险评分生成不同优先级的测试
        if risk_score >= 80:
            # 危急风险 - 生成大量关键测试
            self._add_critical_tests(strategy, assets)
            self._add_high_priority_tests(strategy, assets)
        elif risk_score >= 60:
            # 高风险 - 生成高优先级测试
            self._add_high_priority_tests(strategy, assets)
            self._add_medium_priority_tests(strategy, assets)
        elif risk_score >= 40:
            # 中风险 - 生成中等优先级测试
            self._add_medium_priority_tests(strategy, assets)
            self._add_low_priority_tests(strategy, assets)
        else:
            # 低风险 - 生成基础测试
            self._add_low_priority_tests(strategy, assets)
        
        logger.info(f"测试策略生成完成：共{len(strategy.actions)}个测试动作")
        return strategy
    
    def _add_critical_tests(self, strategy: TestStrategy, assets: List[Dict]):
        """添加关键优先级测试"""
        # CVE 验证测试
        strategy.add_action(TestAction(
            id="cve_critical_001",
            category=TestCategory.CVE_VALIDATION.value,
            name="关键 CVE 验证",
            description="验证已知关键 CVE 漏洞",
            priority=TestPriority.CRITICAL,
            estimated_time=60,
            tools=["nuclei", "afrog"],
            commands=["nuclei -u {url} -tags cve,critical", "afrog -S critical -t {url}"]
        ))
    
    def _add_high_priority_tests(self, strategy: TestStrategy, assets: List[Dict]):
        """添加高优先级测试"""
        # 配置测试
        strategy.add_action(TestAction(
            id="config_high_001",
            category=TestCategory.CONFIGURATION_TEST.value,
            name="安全配置检查",
            description="检查安全配置问题",
            priority=TestPriority.HIGH,
            estimated_time=30,
            tools=["nuclei"],
            commands=["nuclei -u {url} -tags config,misconfig"]
        ))
        
        # 认证测试
        strategy.add_action(TestAction(
            id="auth_high_001",
            category=TestCategory.AUTHENTICATION_TEST.value,
            name="认证机制测试",
            description="测试认证机制安全性",
            priority=TestPriority.HIGH,
            estimated_time=45,
            tools=["nuclei", "hydra"],
            commands=["nuclei -u {url} -tags auth", "hydra -L users.txt -P passwords.txt {url}"]
        ))
    
    def _add_medium_priority_tests(self, strategy: TestStrategy, assets: List[Dict]):
        """添加中等优先级测试"""
        # 信息泄露测试
        strategy.add_action(TestAction(
            id="info_medium_001",
            category=TestCategory.INFORMATION_DISCLOSURE.value,
            name="信息泄露检测",
            description="检测敏感信息泄露",
            priority=TestPriority.MEDIUM,
            estimated_time=20,
            tools=["nuclei"],
            commands=["nuclei -u {url} -tags exposure"]
        ))
    
    def _add_low_priority_tests(self, strategy: TestStrategy, assets: List[Dict]):
        """添加低优先级测试"""
        # 基础扫描
        strategy.add_action(TestAction(
            id="basic_low_001",
            category=TestCategory.CONFIGURATION_TEST.value,
            name="基础安全扫描",
            description="执行基础安全检查",
            priority=TestPriority.LOW,
            estimated_time=15,
            tools=["nuclei"],
            commands=["nuclei -u {url}"]
        ))
    
    def _load_action_templates(self) -> Dict[str, Any]:
        """加载测试动作模板"""
        return {
            "cve_validation": {
                "critical": ["nuclei -tags cve,critical", "afrog -S critical"],
                "high": ["nuclei -tags cve,high"]
            },
            "configuration": {
                "high": ["nuclei -tags misconfig"],
                "medium": ["nuclei -tags config"]
            }
        }
