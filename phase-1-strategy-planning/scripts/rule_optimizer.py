#!/usr/bin/env python3
"""
规则优化器 - 基于历史数据自动优化规则权重和阈值

核心功能：分析规则的实际效果，基于模式学习结果和测试历史，
自动调整规则权重，优化决策阈值，解决规则冲突，提高系统整体性能。
"""

import json
import math
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Rule:
    """规则定义"""
    rule_id: str                    # 规则标识
    rule_type: str                  # 规则类型: feature_rule, strategy_rule, priority_rule
    condition: Dict[str, Any]       # 条件部分
    action: Dict[str, Any]          # 行动部分
    weight: float                   # 规则权重 (0-1)
    threshold: float                # 触发阈值
    description: str                # 规则描述
    
    # 统计信息
    execution_count: int = 0        # 执行次数
    success_count: int = 0          # 成功次数
    effectiveness: float = 0.0      # 效果指标 (0-1)
    confidence: float = 0.5         # 置信度
    last_updated: str = ""          # 最后更新时间


@dataclass
class RuleAdjustment:
    """规则调整建议"""
    rule_id: str                    # 目标规则ID
    adjustment_type: str            # 调整类型: weight_increase, weight_decrease, threshold_adjust, enable, disable
    current_value: float            # 当前值
    new_value: float                # 新建议值
    adjustment_amount: float        # 调整量
    reason: str                     # 调整原因
    confidence: float               # 调整置信度 (0-1)
    
    expected_improvement: float     # 预期改进 (0-1)
    suggested_test: str             # 建议的测试验证方法
    risk_level: str                 # 风险级别: low, medium, high


class RuleOptimizer:
    """规则优化器"""
    
    def __init__(self, learning_rate: float = 0.1, min_effectiveness: float = 0.6):
        """
        初始化规则优化器
        
        Args:
            learning_rate: 学习率，控制权重调整幅度
            min_effectiveness: 最小效果阈值，低于此值的规则可能需要禁用
        """
        self.learning_rate = learning_rate
        self.min_effectiveness = min_effectiveness
        self.rules: Dict[str, Rule] = {}
        self.adjustments: List[RuleAdjustment] = []
        
    def load_rules_from_file(self, rules_file: str) -> bool:
        """从文件加载规则"""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            for rule_data in rules_data.get("rules", []):
                rule = Rule(**rule_data)
                self.rules[rule.rule_id] = rule
            
            print(f"✅ 加载 {len(self.rules)} 条规则")
            return True
            
        except FileNotFoundError:
            print(f"⚠️ 规则文件不存在: {rules_file}")
            return False
        except Exception as e:
            print(f"⚠️ 加载规则失败: {e}")
            return False
    
    def initialize_default_rules(self):
        """初始化默认规则集"""
        print("🎯 初始化默认规则集...")
        
        default_rules = [
            # 技术特征规则
            Rule(
                rule_id="tech_web_server_port_scan",
                rule_type="feature_rule",
                condition={"technology_type": "web_server"},
                action={"tasks": ["port_scan"], "priority": "high"},
                weight=0.8,
                threshold=0.5,
                description="web服务器技术需要端口扫描",
                execution_count=10,
                success_count=8,
                effectiveness=0.8,
                confidence=0.7
            ),
            Rule(
                rule_id="tech_database_auth_test",
                rule_type="feature_rule",
                condition={"technology_type": "database"},
                action={"tasks": ["auth_test", "sql_injection_test"], "priority": "critical"},
                weight=0.9,
                threshold=0.6,
                description="数据库技术需要鉴权和SQL注入测试",
                execution_count=15,
                success_count=12,
                effectiveness=0.8,
                confidence=0.8
            ),
            # 漏洞风险规则
            Rule(
                rule_id="vuln_high_priority",
                rule_type="priority_rule",
                condition={"vulnerability_risk": "high"},
                action={"time_allocation": "increase_50%", "priority": "critical"},
                weight=0.95,
                threshold=0.7,
                description="高风险漏洞需要增加时间分配",
                execution_count=20,
                success_count=16,
                effectiveness=0.8,
                confidence=0.75
            ),
            # 测试策略规则
            Rule(
                rule_id="strategy_time_constrained",
                rule_type="strategy_rule",
                condition={"time_budget": "short"},
                action={"strategy_type": "focused", "task_selection": "risk_based"},
                weight=0.85,
                threshold=0.65,
                description="时间紧张时采用聚焦策略",
                execution_count=12,
                success_count=10,
                effectiveness=0.833,
                confidence=0.7
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
        
        print(f"✅ 初始化 {len(self.rules)} 条默认规则")
    
    def optimize_based_on_patterns(self, patterns: List[Dict[str, Any]], 
                                 test_records: List[Dict[str, Any]]) -> List[RuleAdjustment]:
        """
        基于学习到的模式优化规则
        
        Args:
            patterns: 学习到的模式列表
            test_records: 测试记录数据
            
        Returns:
            List[RuleAdjustment]: 规则调整建议列表
        """
        print("🔧 基于学习到的模式优化规则...")
        self.adjustments = []
        
        # 1. 分析规则当前效果
        print("  步骤1: 分析规则当前效果...")
        rule_effectiveness = self._analyze_rule_effectiveness(test_records)
        
        # 2. 基于模式调整规则
        print("  步骤2: 基于模式调整规则权重...")
        self._adjust_rules_based_on_patterns(patterns, rule_effectiveness)
        
        # 3. 优化规则阈值
        print("  步骤3: 优化规则阈值...")
        self._optimize_rule_thresholds(rule_effectiveness)
        
        # 4. 识别和修复规则冲突
        print("  步骤4: 识别和修复规则冲突...")
        self._resolve_rule_conflicts()
        
        # 5. 提出高风险规则调整建议
        print("  步骤5: 提出高风险规则调整建议...")
        self._suggest_high_risk_adjustments(rule_effectiveness)
        
        print(f"✅ 生成 {len(self.adjustments)} 条规则调整建议")
        return self.adjustments
    
    def _analyze_rule_effectiveness(self, test_records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """分析规则效果（简化版本）"""
        rule_effectiveness = {}
        
        for rule_id, rule in self.rules.items():
            # 简化模拟分析
            if rule.execution_count > 0:
                effectiveness = rule.effectiveness
            else:
                # 无历史数据，基于规则类型估计
                if rule.rule_type == "feature_rule":
                    effectiveness = 0.7
                elif rule.rule_type == "priority_rule":
                    effectiveness = 0.75
                else:
                    effectiveness = 0.65
            
            rule_effectiveness[rule_id] = {
                "effectiveness": effectiveness,
                "confidence": rule.confidence,
                "execution_count": rule.execution_count,
                "success_rate": rule.success_count / max(rule.execution_count, 1)
            }
        
        return rule_effectiveness
    
    def _adjust_rules_based_on_patterns(self, patterns: List[Dict[str, Any]], 
                                       rule_effectiveness: Dict[str, Dict[str, float]]):
        """基于模式调整规则权重"""
        for pattern in patterns:
            pattern_type = pattern.get("pattern_type", "")
            
            if pattern_type == "tech_to_strategy":
                # 技术到策略的模式：调整相关特征规则的权重
                antecedent = pattern.get("antecedent", [])
                consequent = pattern.get("consequent", [])
                confidence = pattern.get("confidence", 0.0)
                lift = pattern.get("lift", 1.0)
                
                if confidence >= 0.8 and lift >= 1.2:
                    # 寻找相关规则
                    related_rules = self._find_rules_matching_pattern(antecedent, consequent)
                    
                    for rule in related_rules:
                        # 计算调整量
                        current_weight = self.rules[rule].weight
                        adjustment_amount = confidence * self.learning_rate * min(lift, 2.0)
                        new_weight = min(current_weight + adjustment_amount, 0.95)
                        
                        if new_weight > current_weight + 0.01:
                            adjustment = RuleAdjustment(
                                rule_id=rule,
                                adjustment_type="weight_increase",
                                current_value=current_weight,
                                new_value=new_weight,
                                adjustment_amount=adjustment_amount,
                                reason=f"基于成功模式: {antecedent} → {consequent} (置信度: {confidence:.2f}, 提升度: {lift:.2f})",
                                confidence=min(confidence, 0.9),
                                expected_improvement=min(adjustment_amount * 2, 0.15),
                                suggested_test="A/B测试验证权重调整效果",
                                risk_level="low"
                            )
                            self.adjustments.append(adjustment)
            
            elif pattern_type == "strategy_effectiveness":
                # 策略有效性模式：调整策略规则的阈值
                antecedent = pattern.get("antecedent", [])
                consequent = pattern.get("consequent", [])
                confidence = pattern.get("confidence", 0.0)
                
                if "result=high_quality" in consequent and confidence >= 0.7:
                    # 策略有效，可以考虑降低阈值使其更容易触发
                    related_rules = self._find_strategy_rules(antecedent)
                    
                    for rule in related_rules:
                        current_threshold = self.rules[rule].threshold
                        # 有效策略降低阈值（更敏感）
                        adjustment_amount = -0.1 * confidence  # 最多降低0.1
                        new_threshold = max(current_threshold + adjustment_amount, 0.3)
                        
                        if new_threshold < current_threshold - 0.02:
                            adjustment = RuleAdjustment(
                                rule_id=rule,
                                adjustment_type="threshold_adjust",
                                current_value=current_threshold,
                                new_value=new_threshold,
                                adjustment_amount=adjustment_amount,
                                reason=f"策略有效性模式: {antecedent} 关联高质量结果 (置信度: {confidence:.2f})",
                                confidence=confidence * 0.8,
                                expected_improvement=0.05,
                                suggested_test="阈值梯度测试验证敏感度变化",
                                risk_level="medium"
                            )
                            self.adjustments.append(adjustment)
    
    def _optimize_rule_thresholds(self, rule_effectiveness: Dict[str, Dict[str, float]]):
        """基于规则效果优化阈值"""
        for rule_id, effectiveness_info in rule_effectiveness.items():
            effectiveness = effectiveness_info["effectiveness"]
            confidence = effectiveness_info["confidence"]
            execution_count = effectiveness_info["execution_count"]
            
            rule = self.rules[rule_id]
            current_threshold = rule.threshold
            
            if execution_count >= 10:  # 有足够数据
                if effectiveness >= 0.8 and confidence >= 0.7:
                    # 规则效果很好，可以降低阈值使其更敏感
                    adjustment_amount = -0.05
                    new_threshold = max(current_threshold + adjustment_amount, 0.3)
                    
                    if new_threshold < current_threshold:
                        adjustment = RuleAdjustment(
                            rule_id=rule_id,
                            adjustment_type="threshold_adjust",
                            current_value=current_threshold,
                            new_value=new_threshold,
                            adjustment_amount=adjustment_amount,
                            reason=f"规则效果优秀 (效果: {effectiveness:.2f}, 置信度: {confidence:.2f}, 执行次数: {execution_count})",
                            confidence=min(effectiveness * confidence, 0.8),
                            expected_improvement=0.02,
                            suggested_test="敏感度测试验证",
                            risk_level="low"
                        )
                        self.adjustments.append(adjustment)
                
                elif effectiveness < 0.4 and confidence >= 0.6:
                    # 规则效果较差，提高阈值减少误触
                    adjustment_amount = 0.1
                    new_threshold = min(current_threshold + adjustment_amount, 0.9)
                    
                    if new_threshold > current_threshold:
                        adjustment = RuleAdjustment(
                            rule_id=rule_id,
                            adjustment_type="threshold_adjust",
                            current_value=current_threshold,
                            new_value=new_threshold,
                            adjustment_amount=adjustment_amount,
                            reason=f"规则效果不佳 (效果: {effectiveness:.2f}, 置信度: {confidence:.2f})，提高阈值减少误判",
                            confidence=0.7,
                            expected_improvement=0.08,
                            suggested_test="误报率测试",
                            risk_level="medium"
                        )
                        self.adjustments.append(adjustment)
    
    def _resolve_rule_conflicts(self):
        """识别和解决规则冲突"""
        # 识别潜在冲突的规则对
        rule_ids = list(self.rules.keys())
        potential_conflicts = []
        
        for i in range(len(rule_ids)):
            for j in range(i+1, len(rule_ids)):
                rule1 = self.rules[rule_ids[i]]
                rule2 = self.rules[rule_ids[j]]
                
                # 检查条件相似但行动冲突
                if self._conditions_similar(rule1.condition, rule2.condition):
                    if self._actions_conflict(rule1.action, rule2.action):
                        potential_conflicts.append((rule_ids[i], rule_ids[j]))
        
        # 为冲突规则提供调整建议
        for rule_id1, rule_id2 in potential_conflicts:
            rule1 = self.rules[rule_id1]
            rule2 = self.rules[rule_id2]
            
            # 根据置信度和效果决定优先级
            if rule1.confidence * rule1.effectiveness > rule2.confidence * rule2.effectiveness:
                # 规则1优先级更高
                adjustment = RuleAdjustment(
                    rule_id=rule_id2,
                    adjustment_type="weight_decrease",
                    current_value=rule2.weight,
                    new_value=rule2.weight * 0.8,
                    adjustment_amount=-rule2.weight * 0.2,
                    reason=f"与高优先级规则 {rule_id1} 冲突，降低权重避免冲突",
                    confidence=0.7,
                    expected_improvement=0.05,
                    suggested_test="冲突场景测试验证",
                    risk_level="high"
                )
                self.adjustments.append(adjustment)
    
    def _suggest_high_risk_adjustments(self, rule_effectiveness: Dict[str, Dict[str, float]]):
        """提出高风险规则调整建议"""
        for rule_id, effectiveness_info in rule_effectiveness.items():
            effectiveness = effectiveness_info["effectiveness"]
            execution_count = effectiveness_info["execution_count"]
            
            if execution_count > 0 and effectiveness < self.min_effectiveness:
                rule = self.rules[rule_id]
                
                if effectiveness < 0.3:
                    # 效果极差的规则建议禁用
                    adjustment = RuleAdjustment(
                        rule_id=rule_id,
                        adjustment_type="disable",
                        current_value=1.0,
                        new_value=0.0,
                        adjustment_amount=-1.0,
                        reason=f"规则效果极差 (效果: {effectiveness:.2f}, 执行次数: {execution_count})，建议禁用",
                        confidence=0.8,
                        expected_improvement=0.1,
                        suggested_test="禁用后对比测试",
                        risk_level="medium"
                    )
                elif effectiveness < 0.5:
                    # 效果较差的规则建议显著降低权重
                    adjustment = RuleAdjustment(
                        rule_id=rule_id,
                        adjustment_type="weight_decrease",
                        current_value=rule.weight,
                        new_value=rule.weight * 0.6,
                        adjustment_amount=-rule.weight * 0.4,
                        reason=f"规则效果较差 (效果: {effectiveness:.2f}, 执行次数: {execution_count})，降低权重",
                        confidence=0.7,
                        expected_improvement=0.07,
                        suggested_test="权重梯度测试",
                        risk_level="low"
                    )
                    self.adjustments.append(adjustment)
    
    def _find_rules_matching_pattern(self, antecedent: List[Any], consequent: List[Any]) -> List[str]:
        """寻找与模式匹配的规则"""
        matching_rules = []
        
        for rule_id, rule in self.rules.items():
            # 检查条件是否匹配模式的antecedent
            condition_matches = False
            for item in antecedent:
                if isinstance(item, str) and "technology_type" in item:
                    tech_type = item.split("=")[1]
                    if rule.condition.get("technology_type") == tech_type:
                        condition_matches = True
                        break
            
            # 检查行动是否匹配模式的consequent
            action_matches = False
            for item in consequent:
                if isinstance(item, str) and "task_type" in item:
                    task_type = item.split("=")[1]
                    if rule.action.get("tasks") and task_type in rule.action.get("tasks", []):
                        action_matches = True
                        break
            
            if condition_matches and action_matches:
                matching_rules.append(rule_id)
        
        return matching_rules
    
    def _find_strategy_rules(self, strategy_items: List[Any]) -> List[str]:
        """寻找策略相关的规则"""
        strategy_rules = []
        
        for item in strategy_items:
            if isinstance(item, str):
                if "strategy_type=" in item:
                    strategy_type = item.split("=")[1]
                    # 寻找策略类型相关的规则
                    for rule_id, rule in self.rules.items():
                        if rule.rule_type == "strategy_rule":
                            if rule.condition.get("strategy_type") == strategy_type:
                                strategy_rules.append(rule_id)
        
        return list(set(strategy_rules))
    
    def _conditions_similar(self, condition1: Dict[str, Any], condition2: Dict[str, Any]) -> bool:
        """检查两个条件是否相似"""
        if not condition1 or not condition2:
            return False
        
        # 简单的相似度检查
        common_keys = set(condition1.keys()) & set(condition2.keys())
        if len(common_keys) >= 2:
            # 至少有2个相同的关键字
            return True
        
        return False
    
    def _actions_conflict(self, action1: Dict[str, Any], action2: Dict[str, Any]) -> bool:
        """检查两个行动是否冲突"""
        if not action1 or not action2:
            return False
        
        # 检查优先级冲突
        if "priority" in action1 and "priority" in action2:
            if action1["priority"] == "critical" and action2["priority"] == "low":
                return True
        
        # 检查时间分配冲突
        if "time_allocation" in action1 and "time_allocation" in action2:
            if "increase" in action1["time_allocation"] and "decrease" in action2["time_allocation"]:
                return True
        
        return False
    
    def get_adjustments_summary(self) -> Dict[str, Any]:
        """获取调整建议摘要"""
        if not self.adjustments:
            return {"total_adjustments": 0}
        
        # 按类型统计
        type_counts = defaultdict(int)
        risk_counts = defaultdict(int)
        
        for adj in self.adjustments:
            type_counts[adj.adjustment_type] += 1
            risk_counts[adj.risk_level] += 1
        
        # 计算预期改进总和
        total_expected_improvement = sum(adj.expected_improvement for adj in self.adjustments)
        avg_confidence = sum(adj.confidence for adj in self.adjustments) / len(self.adjustments)
        
        return {
            "total_adjustments": len(self.adjustments),
            "adjustment_types": dict(type_counts),
            "risk_distribution": dict(risk_counts),
            "total_expected_improvement": total_expected_improvement,
            "average_confidence": avg_confidence,
            "top_adjustments": [
                {
                    "rule_id": adj.rule_id,
                    "adjustment_type": adj.adjustment_type,
                    "reason": adj.reason[:50] + "..." if len(adj.reason) > 50 else adj.reason,
                    "expected_improvement": adj.expected_improvement,
                    "risk_level": adj.risk_level
                }
                for adj in self.adjustments[:5]
            ]
        }
    
    def apply_adjustments(self) -> Dict[str, Any]:
        """应用调整建议"""
        if not self.adjustments:
            return {"applied": 0, "errors": []}
        
        applied = 0
        errors = []
        
        for adjustment in self.adjustments:
            try:
                if adjustment.rule_id in self.rules:
                    rule = self.rules[adjustment.rule_id]
                    
                    if adjustment.adjustment_type == "weight_increase":
                        rule.weight = adjustment.new_value
                        applied += 1
                    elif adjustment.adjustment_type == "weight_decrease":
                        rule.weight = adjustment.new_value
                        applied += 1
                    elif adjustment.adjustment_type == "threshold_adjust":
                        rule.threshold = adjustment.new_value
                        applied += 1
                    elif adjustment.adjustment_type == "disable":
                        rule.weight = 0.0  # 权重设为0等效于禁用
                        applied += 1
                    
                    rule.last_updated = "2026-04-16T15:45:00"  # 简化的更新时间
                else:
                    errors.append(f"规则不存在: {adjustment.rule_id}")
            except Exception as e:
                errors.append(f"应用调整失败 {adjustment.rule_id}: {e}")
        
        return {
            "total_adjustments": len(self.adjustments),
            "applied": applied,
            "errors": errors,
            "success_rate": applied / len(self.adjustments) if self.adjustments else 0.0
        }


def demo_rule_optimizer():
    """演示规则优化器"""
    print("=" * 70)
    print("规则优化器演示")
    print("=" * 70)
    
    # 创建规则优化器
    optimizer = RuleOptimizer(learning_rate=0.15, min_effectiveness=0.55)
    
    # 初始化默认规则
    optimizer.initialize_default_rules()
    
    print(f"\n📊 初始规则状态:")
    print(f"  总规则数: {len(optimizer.rules)}")
    for rule_id, rule in optimizer.rules.items():
        print(f"  • {rule_id}: 权重={rule.weight:.2f}, 阈值={rule.threshold:.2f}, "
              f"效果={rule.effectiveness:.2f}, 置信度={rule.confidence:.2f}")
    
    # 加载或生成学习到的模式
    print(f"\n🎯 加载学习到的模式...")
    # 创建示例模式数据
    example_patterns = [
        {
            "pattern_type": "tech_to_strategy",
            "antecedent": ["technology_type=web_server"],
            "consequent": ["task_type=port_scan"],
            "confidence": 0.85,
            "lift": 1.3
        },
        {
            "pattern_type": "tech_to_strategy",
            "antecedent": ["technology_type=database"],
            "consequent": ["task_type=auth_test"],
            "confidence": 0.9,
            "lift": 1.5
        },
        {
            "pattern_type": "strategy_effectiveness",
            "antecedent": ["strategy_type=comprehensive"],
            "consequent": ["result=high_quality"],
            "confidence": 0.75,
            "lift": 1.4
        }
    ]
    
    print(f"  使用 {len(example_patterns)} 个示例模式")
    
    # 优化规则
    adjustments = optimizer.optimize_based_on_patterns(example_patterns, [])
    
    # 显示优化结果
    summary = optimizer.get_adjustments_summary()
    print(f"\n🔧 规则优化结果:")
    print(f"  生成调整建议: {summary['total_adjustments']} 条")
    
    if summary['total_adjustments'] > 0:
        print(f"  调整类型分布: {summary['adjustment_types']}")
        print(f"  风险分布: {summary['risk_distribution']}")
        print(f"  总预期改进: {summary['total_expected_improvement']:.3f}")
        print(f"  平均置信度: {summary['average_confidence']:.3f}")
        
        print(f"\n🏆 前3条调整建议:")
        for i, adj in enumerate(summary['top_adjustments'][:3], 1):
            print(f"  {i}. {adj['rule_id']} - {adj['adjustment_type']}")
            print(f"     原因: {adj['reason']}")
            print(f"     预期改进: {adj['expected_improvement']:.3f}, 风险: {adj['risk_level']}")
    
    # 应用调整
    print(f"\n⚙️ 应用调整建议...")
    apply_result = optimizer.apply_adjustments()
    
    print(f"  总调整建议: {apply_result['total_adjustments']}")
    print(f"  成功应用: {apply_result['applied']}")
    print(f"  成功率: {apply_result['success_rate']:.1%}")
    
    if apply_result['errors']:
        print(f"  错误: {len(apply_result['errors'])} 个")
        for error in apply_result['errors'][:3]:
            print(f"    • {error}")
    
    # 更新后的规则状态
    print(f"\n📈 更新后规则状态:")
    for rule_id, rule in optimizer.rules.items():
        original_weight = [0.8, 0.9, 0.95, 0.85][list(optimizer.rules.keys()).index(rule_id) % 4]
        weight_change = rule.weight - original_weight
        if abs(weight_change) > 0.01:
            print(f"  • {rule_id}: 权重 {original_weight:.2f} → {rule.weight:.2f} "
                  f"(变化: {weight_change:+.2f})")
    
    print("\n" + "=" * 70)
    print("规则优化器演示完成 ✅")
    print("=" * 70)


if __name__ == "__main__":
    demo_rule_optimizer()