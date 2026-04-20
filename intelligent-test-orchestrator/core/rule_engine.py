#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则引擎模块 - 基于可配置规则的条件 - 动作决策引擎

核心功能：
1. YAML 规则解析和加载
2. 条件表达式求值
3. 动作执行和结果输出
4. 优先级排序
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RuleActionType(str, Enum):
    """规则动作类型"""
    ADD_TEST = "add_test"
    SET_PRIORITY = "set_priority"
    SELECT_TOOL = "select_tool"


class TestPriority(str, Enum):
    """测试优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RuleEngine:
    """规则引擎"""
    
    def __init__(self, rules_dir: Optional[str] = None):
        """初始化规则引擎
        
        Args:
            rules_dir: 规则文件目录路径
        """
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.rules_dir = Path(rules_dir) if rules_dir else None
        
        logger.info("规则引擎初始化完成")
        
        # 如果有规则目录，自动加载规则
        if self.rules_dir and self.rules_dir.exists():
            self.load_rules_from_dir()
    
    def load_rules_from_dir(self):
        """从目录加载所有 YAML 规则文件"""
        if not self.rules_dir:
            return
        
        yaml_files = list(self.rules_dir.glob("*.yml"))
        logger.info(f"发现 {len(yaml_files)} 个规则文件")
        
        for yaml_file in yaml_files:
            try:
                self.load_rules_from_file(yaml_file)
                logger.info(f"已加载规则：{yaml_file.name}")
            except Exception as e:
                logger.error(f"加载规则文件失败 {yaml_file}: {e}")
    
    def load_rules_from_file(self, rule_file: Union[str, Path]):
        """从 YAML 文件加载规则
        
        Args:
            rule_file: 规则文件路径
        """
        rule_path = Path(rule_file)
        if not rule_path.exists():
            raise FileNotFoundError(f"规则文件不存在：{rule_path}")
        
        with open(rule_path, 'r', encoding='utf-8') as f:
            rule_data = yaml.safe_load(f)
        
        rules = rule_data.get('rules', {})
        for rule_id, rule_def in rules.items():
            self.rules[rule_id] = rule_def
        
        logger.info(f"从 {rule_path.name} 加载了 {len(rules)} 条规则")
    
    def evaluate(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估资产，应用匹配的规则
        
        Args:
            asset: 资产对象
            
        Returns:
            匹配的规则动作列表
        """
        matched_actions = []
        
        for rule_id, rule_def in self.rules.items():
            if not rule_def.get('enabled', True):
                continue
            
            # 检查条件
            conditions = rule_def.get('conditions', [])
            if self._check_conditions(conditions, asset):
                # 条件匹配，执行动作
                actions = rule_def.get('actions', [])
                priority = rule_def.get('priority', 50)
                
                for action in actions:
                    matched_actions.append({
                        'rule_id': rule_id,
                        'priority': priority,
                        'action': action
                    })
        
        # 按优先级排序
        matched_actions.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"规则评估完成：匹配 {len(matched_actions)} 个动作")
        return matched_actions
    
    def _check_conditions(self, conditions: List[str], asset: Dict[str, Any]) -> bool:
        """检查条件是否满足
        
        Args:
            conditions: 条件表达式列表
            asset: 资产对象
            
        Returns:
            bool: 是否满足所有条件
        """
        if not conditions:
            return True
        
        for condition in conditions:
            if not self._evaluate_condition(condition, asset):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str, asset: Dict[str, Any]) -> bool:
        """评估单个条件
        
        Args:
            condition: 条件表达式
            asset: 资产对象
            
        Returns:
            bool: 条件是否满足
        """
        # 简单实现：支持基本的条件检查
        # 例如："technology.name == 'Apache Tomcat'"
        
        try:
            # 提取技术栈信息
            technologies = asset.get('technologies', [])
            tech_names = [t.get('name', '') for t in technologies]
            
            # 检查是否包含某个技术
            if '==' in condition:
                parts = condition.split('==')
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    if field == 'technology.name':
                        return any(value.lower() in name.lower() for name in tech_names)
            
            # 检查是否包含
            if 'in' in condition:
                parts = condition.split('in')
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    if field == 'technology.name':
                        return any(value.lower() in name.lower() for name in tech_names)
            
            return False
        except Exception as e:
            logger.error(f"评估条件失败 '{condition}': {e}")
            return False
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.get('enabled', True)),
            "disabled_rules": sum(1 for r in self.rules.values() if not r.get('enabled', True)),
            "rules_dir": str(self.rules_dir) if self.rules_dir else None
        }
