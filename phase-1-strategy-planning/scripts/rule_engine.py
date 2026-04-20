#!/usr/bin/env python3
"""
规则引擎模块 - 基于可配置规则的条件-动作决策引擎

核心功能：
1. YAML规则解析和加载
2. 条件表达式求值
3. 动作执行和结果输出
4. 优先级排序和冲突解决

规则语法示例：
```yaml
rules:
  tomcat_cve_test:
    name: "Tomcat CVE验证规则"  
    description: "当检测到Apache Tomcat时，验证相关CVE"
    priority: 100
    enabled: true
    conditions:
      - "technology.name == 'Apache Tomcat'"
      - "technology.version.parsed.major <= 8"
    actions:
      - action: "add_test"
        category: "cve_validation"
        tests: ["tomcat_cve_scan"]
        tools: ["nuclei_tomcat", "afrog_tomcat"]
        priority: "high"
        estimated_time: "30m"
        commands:
          - "nuclei -u {url} -tags tomcat"
          - "afrog -S vuln -S tomcat -t {url}"
```
"""

import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import operator
from dataclasses import dataclass, field

class RuleActionType(str, Enum):
    """规则动作类型"""
    ADD_TEST = "add_test"
    SET_PRIORITY = "set_priority"
    SELECT_TOOL = "select_tool"
    GENERATE_COMMAND = "generate_command"
    SCHEDULE_TEST = "schedule_test"

class TestPriority(str, Enum):
    """测试优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class RuleCondition:
    """规则条件"""
    expression: str
    negated: bool = False
    
    def __str__(self):
        prefix = "NOT " if self.negated else ""
        return f"{prefix}{self.expression}"

@dataclass
class RuleAction:
    """规则动作"""
    action_type: RuleActionType
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "action_type": self.action_type.value,
            "params": self.params
        }

@dataclass
class RuleDefinition:
    """规则定义"""
    rule_id: str
    name: str
    description: str
    priority: int = 50
    enabled: bool = True
    conditions: List[RuleCondition] = field(default_factory=list)
    actions: List[RuleAction] = field(default_factory=list)
    
    def __str__(self):
        return f"Rule[{self.rule_id}]: {self.name} (prio: {self.priority})"
    
    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "enabled": self.enabled,
            "conditions": [str(c) for c in self.conditions],
            "actions": [a.to_dict() for a in self.actions]
        }

class ConditionEvaluator:
    """条件表达式求值器"""
    
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.operators = {
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge,
            'contains': lambda a, b: str(b) in str(a) if a else False,
            'matches': lambda a, b: bool(re.search(str(b), str(a))) if a else False,
            'in': lambda a, b: str(a) in b if isinstance(b, list) else False,
        }
    
    def evaluate(self, condition: str) -> bool:
        """评估单个条件表达式"""
        try:
            # 预处理：处理特殊关键字
            if condition.strip().startswith("technology."):
                return self._evaluate_technology_condition(condition)
            elif condition.strip().startswith("endpoint."):
                return self._evaluate_endpoint_condition(condition)
            elif condition.strip().startswith("business."):
                return self._evaluate_business_condition(condition)
            else:
                # 简单表达式求值
                return self._evaluate_simple_expression(condition)
        except Exception as e:
            print(f"⚠️ 条件求值失败: {condition} - {e}")
            return False
    
    def _evaluate_technology_condition(self, condition: str) -> bool:
        """评估技术栈条件"""
        # 格式: technology.name == 'Apache Tomcat'
        # 格式: technology.version contains '7.0'
        
        # 从上下文中获取资产的技术栈
        technologies = self.context.get('technologies', [])
        
        match = re.match(r'technology\.(\w+)\s*(==|!=|contains|matches|in)\s*["\']?([^"\']+)["\']?', condition)
        if not match:
            return False
        
        field_name, op, expected_value = match.groups()
        
        for tech in technologies:
            tech_value = tech.get(field_name)
            if tech_value is None:
                continue
            
            # 执行操作符
            if op in self.operators:
                if self.operators[op](str(tech_value).lower(), str(expected_value).lower()):
                    return True
        
        return False
    
    def _evaluate_endpoint_condition(self, condition: str) -> bool:
        """评估端点条件"""
        # 格式: endpoint.path contains 'login'
        # 格式: endpoint.methods in ['POST', 'GET']
        
        endpoints = self.context.get('endpoints', [])
        
        match = re.match(r'endpoint\.(\w+)\s*(==|!=|contains|matches|in)\s*["\']?([^"\']+)["\']?', condition)
        if not match:
            return False
        
        field_name, op, expected_value = match.groups()
        
        for endpoint in endpoints:
            endpoint_value = endpoint.get(field_name)
            if endpoint_value is None:
                continue
            
            # 特殊处理列表类型
            if isinstance(endpoint_value, list):
                if op == 'contains':
                    if expected_value in endpoint_value:
                        return True
                elif op == 'in':
                    if any(item in expected_value.split(',') for item in endpoint_value):
                        return True
            else:
                if op in self.operators:
                    if self.operators[op](str(endpoint_value).lower(), str(expected_value).lower()):
                        return True
        
        return False
    
    def _evaluate_business_condition(self, condition: str) -> bool:
        """评估业务类型条件"""
        # 格式: business.type == 'banking'
        # 格式: business.confidence >= 0.7
        
        business_hints = self.context.get('business_hints', {})
        
        match = re.match(r'business\.(\w+)\s*(==|!=|>=|<=|>|<)\s*["\']?([^"\']+)["\']?', condition)
        if not match:
            return False
        
        field_name, op, expected_value = match.groups()
        
        business_value = business_hints.get(field_name)
        if business_value is None:
            return False
        
        # 转换类型
        try:
            if field_name in ['confidence']:
                business_value = float(business_value)
                expected_value = float(expected_value)
            elif field_name == 'type':
                business_value = str(business_value)
                expected_value = str(expected_value)
        except ValueError:
            pass
        
        if op in self.operators:
            return self.operators[op](business_value, expected_value)
        
        return False
    
    def _evaluate_simple_expression(self, expression: str) -> bool:
        """评估简单表达式"""
        # 这里实现一个简单的表达式求值
        # MVP版本简化：直接使用Python的eval（注意安全）
        try:
            # 安全过滤：只允许安全的字符
            safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.,:;!?=<>()[]{} \'"')
            if not all(c in safe_chars for c in expression):
                return False
            
            # 替换上下文变量
            eval_expr = expression
            for key, value in self.context.items():
                if isinstance(value, (str, int, float, bool)):
                    eval_expr = eval_expr.replace(key, repr(value))
                elif isinstance(value, list):
                    eval_expr = eval_expr.replace(key, str(value))
            
            # 简单求值
            return bool(eval(eval_expr, {"__builtins__": {}}, {}))
        except Exception as e:
            print(f"⚠️ 表达式求值失败: {expression} - {e}")
            return False
    
    def evaluate_all(self, conditions: List[RuleCondition]) -> bool:
        """评估所有条件（AND逻辑）"""
        for condition in conditions:
            result = self.evaluate(condition.expression)
            if condition.negated:
                result = not result
            if not result:
                return False
        return True

class RuleEngine:
    """规则引擎主类"""
    
    def __init__(self, rules_dir: Optional[Path] = None):
        self.rules: Dict[str, RuleDefinition] = {}
        self.evaluator_cache = {}
        
        if rules_dir:
            self.load_rules_from_directory(rules_dir)
    
    def load_rule(self, rule_data: Dict[str, Any]) -> Optional[RuleDefinition]:
        """加载单个规则"""
        try:
            rule_id = rule_data.get('id') or rule_data.get('rule_id')
            if not rule_id:
                raise ValueError("规则缺少ID")
            
            # 解析条件
            conditions = []
            raw_conditions = rule_data.get('conditions', [])
            if isinstance(raw_conditions, list):
                for cond in raw_conditions:
                    if isinstance(cond, str):
                        # 处理NOT表达式
                        negated = cond.strip().upper().startswith('NOT ')
                        expr = cond.strip()[4:] if negated else cond.strip()
                        conditions.append(RuleCondition(expression=expr, negated=negated))
                    elif isinstance(cond, dict):
                        expr = cond.get('expression', '')
                        negated = cond.get('negated', False)
                        conditions.append(RuleCondition(expression=expr, negated=negated))
            
            # 解析动作
            actions = []
            raw_actions = rule_data.get('actions', [])
            if isinstance(raw_actions, list):
                for action_data in raw_actions:
                    if isinstance(action_data, dict):
                        action_type_str = action_data.get('action')
                        if not action_type_str:
                            continue
                        
                        try:
                            action_type = RuleActionType(action_type_str)
                            actions.append(RuleAction(
                                action_type=action_type,
                                params=action_data.get('params', {})
                            ))
                        except ValueError:
                            print(f"⚠️ 未知动作类型: {action_type_str}")
            
            # 创建规则定义
            rule = RuleDefinition(
                rule_id=rule_id,
                name=rule_data.get('name', '未命名规则'),
                description=rule_data.get('description', ''),
                priority=rule_data.get('priority', 50),
                enabled=rule_data.get('enabled', True),
                conditions=conditions,
                actions=actions
            )
            
            self.rules[rule_id] = rule
            return rule
            
        except Exception as e:
            print(f"❌ 规则加载失败: {rule_data.get('name', '未知')} - {e}")
            return None
    
    def load_rules_from_file(self, file_path: Path) -> List[RuleDefinition]:
        """从文件加载规则"""
        loaded_rules = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    print(f"❌ 不支持的文件格式: {file_path.suffix}")
                    return []
            
            # 支持多种格式
            if isinstance(data, dict) and 'rules' in data:
                # 规则集合格式
                rules_data = data['rules']
                if isinstance(rules_data, dict):
                    # 嵌套字典格式: {rule_id: rule_data, ...}
                    for rule_data in rules_data.values():
                        rule = self.load_rule(rule_data)
                        if rule:
                            loaded_rules.append(rule)
                elif isinstance(rules_data, list):
                    # 列表格式: [{rule_data}, ...]
                    for rule_data in rules_data:
                        rule = self.load_rule(rule_data)
                        if rule:
                            loaded_rules.append(rule)
                else:
                    print(f"⚠️ 未知的rules格式: {type(rules_data)}")
            elif isinstance(data, list):
                # 规则列表格式
                for rule_data in data:
                    rule = self.load_rule(rule_data)
                    if rule:
                        loaded_rules.append(rule)
            elif isinstance(data, dict):
                # 单个规则格式
                rule = self.load_rule(data)
                if rule:
                    loaded_rules.append(rule)
            
            print(f"📋 从 {file_path} 加载了 {len(loaded_rules)} 条规则")
            
        except Exception as e:
            print(f"❌ 文件加载失败 {file_path}: {e}")
        
        return loaded_rules
    
    def load_rules_from_directory(self, dir_path: Path) -> List[RuleDefinition]:
        """从目录加载所有规则文件"""
        dir_path = Path(dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ 目录不存在: {dir_path}")
            return []
        
        loaded_rules = []
        rule_files = list(dir_path.glob('*.yaml')) + list(dir_path.glob('*.yml')) + list(dir_path.glob('*.json'))
        
        for file_path in rule_files:
            loaded_rules.extend(self.load_rules_from_file(file_path))
        
        print(f"🎯 总计加载 {len(self.rules)} 条规则")
        return loaded_rules
    
    def evaluate_asset(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估资产并返回匹配的规则动作"""
        matched_actions = []
        
        # 创建求值器
        evaluator = ConditionEvaluator(asset)
        
        # 按优先级降序排序规则
        sorted_rules = sorted(self.rules.values(), key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # 评估条件
            try:
                if evaluator.evaluate_all(rule.conditions):
                    print(f"✅ 规则匹配: {rule.name}")
                    
                    # 收集动作
                    for action in rule.actions:
                        action_result = {
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "action_type": action.action_type.value,
                            "params": action.params.copy(),
                            "asset_context": {
                                "url": asset.get('url'),
                                "technologies": [t['name'] for t in asset.get('technologies', [])],
                                "business_type": asset.get('business_hints', {}).get('type', 'unknown')
                            }
                        }
                        
                        # 替换参数中的模板变量
                        self._replace_template_variables(action_result, asset)
                        
                        matched_actions.append(action_result)
                else:
                    pass  # 条件不匹配，正常情况
                    
            except Exception as e:
                print(f"⚠️ 规则评估失败 {rule.rule_id}: {e}")
                continue
        
        return matched_actions
    
    def _replace_template_variables(self, action_result: Dict[str, Any], asset: Dict[str, Any]):
        """替换参数中的模板变量"""
        for key, value in action_result['params'].items():
            if isinstance(value, str):
                # 替换 {url}, {ip}, {port} 等变量
                if '{url}' in value and 'url' in asset:
                    action_result['params'][key] = value.replace('{url}', asset['url'])
                if '{ip}' in value and 'ip' in asset:
                    action_result['params'][key] = value.replace('{ip}', asset.get('ip', ''))
                if '{port}' in value and 'port' in asset:
                    action_result['params'][key] = value.replace('{port}', str(asset.get('port', '')))
        
        # 特殊处理commands列表
        if 'commands' in action_result['params'] and isinstance(action_result['params']['commands'], list):
            updated_commands = []
            for cmd in action_result['params']['commands']:
                if isinstance(cmd, str):
                    if '{url}' in cmd and 'url' in asset:
                        cmd = cmd.replace('{url}', asset['url'])
                    if '{ip}' in cmd and 'ip' in asset:
                        cmd = cmd.replace('{ip}', asset.get('ip', ''))
                    updated_commands.append(cmd)
                else:
                    updated_commands.append(cmd)
            action_result['params']['commands'] = updated_commands
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """获取规则摘要"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "rules_by_priority": sorted([r.to_dict() for r in self.rules.values()], key=lambda x: x['priority'], reverse=True)
        }

def main():
    """命令行测试入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description="规则引擎 - 测试模式")
    parser.add_argument("--rules", type=str, default="rules/", help="规则目录路径")
    parser.add_argument("--test-asset", type=str, help="测试资产JSON文件路径")
    parser.add_argument("--list", action="store_true", help="列出所有规则")
    
    args = parser.parse_args()
    
    # 初始化规则引擎
    engine = RuleEngine(Path(args.rules))
    
    if args.list:
        print("📋 加载的规则列表:")
        summary = engine.get_rules_summary()
        print(f"总计规则: {summary['total_rules']} (启用: {summary['enabled_rules']})")
        
        for rule in summary['rules_by_priority']:
            status = "✅" if rule['enabled'] else "❌"
            print(f"{status} [{rule['priority']}] {rule['name']}")
            if rule['conditions']:
                print(f"    条件: {' AND '.join(rule['conditions'])}")
            print()
    
    elif args.test_asset:
        try:
            with open(args.test_asset, 'r') as f:
                asset = json.load(f)
            
            print(f"🧪 测试资产: {asset.get('url', 'unknown')}")
            results = engine.evaluate_asset(asset)
            
            print(f"🎯 匹配 {len(results)} 个动作:")
            for result in results:
                print(f"\n  ✅ {result['rule_name']} -> {result['action_type']}")
                if result['params']:
                    print(f"     参数: {result['params']}")
        
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()