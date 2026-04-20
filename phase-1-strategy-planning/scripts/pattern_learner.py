#!/usr/bin/env python3
"""
模式学习器 - 从历史测试中学习成功模式

核心功能：分析历史测试记录，识别技术特征、测试策略与测试效果之间的关联关系。
基于关联规则挖掘概念，发现哪些技术特征组合适合哪些测试策略，
哪些策略在特定技术场景下更容易发现漏洞等。
"""

import json
import math
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LearningPattern:
    """学习到的模式"""
    pattern_id: str                     # 模式标识
    pattern_type: str                  # 模式类型: tech_to_strategy, strategy_effectiveness, tech_combo_success
    antecedent: List[Any]              # 前件（条件）
    consequent: List[Any]              # 后件（结果）
    support: float                     # 支持度 (在数据集中出现的频率)
    confidence: float                  # 置信度 (当条件满足时结果出现的频率)
    lift: float                        # 提升度 (规则实际效果/随机预期)
    coverage: float                    # 覆盖率 (规则覆盖的记录比例)
    quality_score: float               # 模式质量分数
    
    examples: List[str]                # 示例记录ID
    evidence_strength: float           # 证据强度 (基于示例数量和质量)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取模式摘要"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "support": self.support,
            "confidence": self.confidence,
            "lift": self.lift,
            "quality_score": self.quality_score
        }


class PatternLearner:
    """模式学习器"""
    
    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.6):
        """
        初始化模式学习器
        
        Args:
            min_support: 最小支持度阈值 (0-1)
            min_confidence: 最小置信度阈值 (0-1)
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.patterns: List[LearningPattern] = []
        
    def learn_from_records(self, records: List[Dict[str, Any]]) -> List[LearningPattern]:
        """
        从测试记录中学习模式
        
        Args:
            records: 历史测试记录列表
            
        Returns:
            List[LearningPattern]: 学习到的模式列表
        """
        print(f"🔍 开始从 {len(records)} 条记录中学习模式...")
        
        # 清空现有模式
        self.patterns = []
        
        # 1. 提取技术特征项集
        print("  步骤1: 提取技术特征项集...")
        tech_item_sets = self._extract_tech_item_sets(records)
        
        # 2. 提取测试策略项集
        print("  步骤2: 提取测试策略项集...")
        strategy_item_sets = self._extract_strategy_item_sets(records)
        
        # 3. 提取测试结果项集
        print("  步骤3: 提取测试结果项集...")
        result_item_sets = self._extract_result_item_sets(records)
        
        # 4. 学习技术到策略的关联模式
        print("  步骤4: 学习技术到策略的关联模式...")
        tech_to_strategy_patterns = self._learn_tech_to_strategy_patterns(
            tech_item_sets, strategy_item_sets, records
        )
        self.patterns.extend(tech_to_strategy_patterns)
        
        # 5. 学习策略有效性模式
        print("  步骤5: 学习策略有效性模式...")
        strategy_effectiveness_patterns = self._learn_strategy_effectiveness_patterns(
            strategy_item_sets, result_item_sets, records
        )
        self.patterns.extend(strategy_effectiveness_patterns)
        
        # 6. 学习技术组合成功模式
        print("  步骤6: 学习技术组合成功模式...")
        tech_combo_patterns = self._learn_tech_combo_success_patterns(
            tech_item_sets, result_item_sets, records
        )
        self.patterns.extend(tech_combo_patterns)
        
        # 7. 按质量分数排序
        self.patterns.sort(key=lambda p: p.quality_score, reverse=True)
        
        print(f"✅ 模式学习完成，发现 {len(self.patterns)} 个有效模式")
        return self.patterns
    
    def _extract_tech_item_sets(self, records: List[Dict[str, Any]]) -> List[Set[str]]:
        """提取技术特征项集"""
        item_sets = []
        
        for record in records:
            tech_items = set()
            
            # 技术特征
            tech_features = record.get("technology_features", {})
            if tech_features:
                for key, value in tech_features.items():
                    if isinstance(value, list):
                        for item in value:
                            tech_items.add(f"{key}={item}")
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            tech_items.add(f"{key}.{k}={v}")
                    else:
                        tech_items.add(f"{key}={value}")
            
            item_sets.append(tech_items)
        
        return item_sets
    
    def _extract_strategy_item_sets(self, records: List[Dict[str, Any]]) -> List[Set[str]]:
        """提取测试策略项集"""
        item_sets = []
        
        for record in records:
            strategy_items = set()
            
            # 测试策略
            planned_strategy = record.get("planned_strategy", {})
            if planned_strategy:
                # 策略类型
                strategy_type = planned_strategy.get("strategy_type")
                if strategy_type:
                    strategy_items.add(f"strategy_type={strategy_type}")
                
                # 测试强度
                test_intensity = planned_strategy.get("test_intensity")
                if test_intensity:
                    strategy_items.add(f"test_intensity={test_intensity}")
                
                # 时间分配模式
                time_budget = planned_strategy.get("time_allocation", {}).get("total_minutes")
                if time_budget:
                    budget_range = self._categorize_time_budget(time_budget)
                    strategy_items.add(f"time_budget={budget_range}")
            
            # 计划任务类型
            planned_tasks = record.get("planned_tasks", [])
            if planned_tasks:
                task_types = Counter(task.get("type") for task in planned_tasks)
                for task_type, count in task_types.items():
                    if task_type:
                        if count >= 3:
                            strategy_items.add(f"task_type_heavy={task_type}")
                        else:
                            strategy_items.add(f"task_type={task_type}")
            
            item_sets.append(strategy_items)
        
        return item_sets
    
    def _extract_result_item_sets(self, records: List[Dict[str, Any]]) -> List[Set[str]]:
        """提取测试结果项集"""
        item_sets = []
        
        for record in records:
            result_items = set()
            
            # 测试结果分类
            quality_score = record.get("quality_score", 0)
            if quality_score >= 75:
                result_items.add("result=high_quality")
            elif quality_score >= 50:
                result_items.add("result=medium_quality")
            else:
                result_items.add("result=low_quality")
            
            # 漏洞发现情况
            vuln_count = len(record.get("discovered_vulnerabilities", []))
            if vuln_count >= 3:
                result_items.add("vuln_discovery=high")
            elif vuln_count >= 1:
                result_items.add("vuln_discovery=medium")
            else:
                result_items.add("vuln_discovery=low")
            
            # 时间效率
            time_efficiency = record.get("effectiveness_metrics", {}).get("time_efficiency", 1.0)
            if time_efficiency >= 1.2:
                result_items.add("time_efficiency=very_efficient")
            elif time_efficiency >= 0.9:
                result_items.add("time_efficiency=efficient")
            else:
                result_items.add("time_efficiency=inefficient")
            
            item_sets.append(result_items)
        
        return item_sets
    
    def _categorize_time_budget(self, minutes: float) -> str:
        """将时间预算分类"""
        if minutes < 60:
            return "short"
        elif minutes < 180:
            return "medium"
        else:
            return "long"
    
    def _learn_tech_to_strategy_patterns(self,
                                        tech_item_sets: List[Set[str]],
                                        strategy_item_sets: List[Set[str]],
                                        records: List[Dict[str, Any]]) -> List[LearningPattern]:
        """学习技术特征到测试策略的关联模式"""
        patterns = []
        total_records = len(records)
        
        # 收集所有技术项和策略项
        all_tech_items = set()
        all_strategy_items = set()
        for tech_items, strategy_items in zip(tech_item_sets, strategy_item_sets):
            all_tech_items.update(tech_items)
            all_strategy_items.update(strategy_items)
        
        # 计算关联规则
        for tech_item in all_tech_items:
            for strategy_item in all_strategy_items:
                # 计算支持度、置信度等指标
                support_tech = self._calculate_support(tech_item, tech_item_sets)
                support_strategy = self._calculate_support(strategy_item, strategy_item_sets)
                support_both = self._calculate_support_both(tech_item, strategy_item, 
                                                          tech_item_sets, strategy_item_sets)
                
                # 检查是否达到最小阈值
                if support_both >= self.min_support and support_tech > 0:
                    confidence = support_both / support_tech
                    if confidence >= self.min_confidence:
                        # 计算提升度
                        expected_support = support_tech * support_strategy
                        lift = support_both / expected_support if expected_support > 0 else 0
                        
                        # 找到示例记录
                        example_records = self._find_example_records(tech_item, strategy_item, 
                                                                    tech_item_sets, strategy_item_sets, 
                                                                    records)
                        
                        # 计算质量分数
                        quality_score = self._calculate_pattern_quality(
                            support=support_both,
                            confidence=confidence,
                            lift=lift,
                            example_count=len(example_records)
                        )
                        
                        pattern = LearningPattern(
                            pattern_id=f"tech2strat_{tech_item}_{strategy_item}",
                            pattern_type="tech_to_strategy",
                            antecedent=[tech_item],
                            consequent=[strategy_item],
                            support=support_both,
                            confidence=confidence,
                            lift=lift,
                            coverage=support_tech,
                            quality_score=quality_score,
                            examples=example_records[:5],  # 取前5个示例
                            evidence_strength=min(len(example_records) / 10.0, 1.0)
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _learn_strategy_effectiveness_patterns(self,
                                             strategy_item_sets: List[Set[str]],
                                             result_item_sets: List[Set[str]],
                                             records: List[Dict[str, Any]]) -> List[LearningPattern]:
        """学习策略有效性模式"""
        patterns = []
        total_records = len(records)
        
        # 收集所有策略项和结果项
        all_strategy_items = set()
        all_result_items = set()
        for strategy_items, result_items in zip(strategy_item_sets, result_item_sets):
            all_strategy_items.update(strategy_items)
            all_result_items.update(result_items)
        
        # 关注高质量结果
        target_results = ["result=high_quality", "vuln_discovery=high", "time_efficiency=very_efficient"]
        
        for strategy_item in all_strategy_items:
            for result_item in target_results:
                if result_item in all_result_items:
                    # 计算指标
                    support_strategy = self._calculate_support(strategy_item, strategy_item_sets)
                    support_result = self._calculate_support(result_item, result_item_sets)
                    support_both = self._calculate_support_both(strategy_item, result_item, 
                                                              strategy_item_sets, result_item_sets)
                    
                    if support_both >= self.min_support * 0.5 and support_strategy > 0:
                        confidence = support_both / support_strategy
                        # 策略有效性需要较高置信度
                        if confidence >= max(self.min_confidence, 0.7):
                            expected_support = support_strategy * support_result
                            lift = support_both / expected_support if expected_support > 0 else 0
                            
                            # 只有提升度>1.2才有意义
                            if lift > 1.2:
                                example_records = self._find_example_records(strategy_item, result_item,
                                                                            strategy_item_sets, result_item_sets,
                                                                            records)
                                
                                quality_score = self._calculate_pattern_quality(
                                    support=support_both,
                                    confidence=confidence,
                                    lift=lift,
                                    example_count=len(example_records),
                                    importance_factor=1.5  # 策略有效性更重要
                                )
                                
                                pattern = LearningPattern(
                                    pattern_id=f"strat_eff_{strategy_item}_{result_item}",
                                    pattern_type="strategy_effectiveness",
                                    antecedent=[strategy_item],
                                    consequent=[result_item],
                                    support=support_both,
                                    confidence=confidence,
                                    lift=lift,
                                    coverage=support_strategy,
                                    quality_score=quality_score,
                                    examples=example_records[:5],
                                    evidence_strength=min(len(example_records) / 5.0, 1.0)
                                )
                                patterns.append(pattern)
        
        return patterns
    
    def _learn_tech_combo_success_patterns(self,
                                         tech_item_sets: List[Set[str]],
                                         result_item_sets: List[Set[str]],
                                         records: List[Dict[str, Any]]) -> List[LearningPattern]:
        """学习技术组合成功模式"""
        patterns = []
        total_records = len(records)
        
        # 目标结果：成功测试
        target_result = "result=high_quality"
        
        # 寻找常见技术组合
        freq_items = self._find_frequent_itemsets(tech_item_sets, min_freq=self.min_support)
        
        for itemset in freq_items:
            if len(itemset) >= 2:  # 至少2项的组合
                # 计算该技术组合的情况下高质量结果的比例
                count_itemset = 0
                count_itemset_with_success = 0
                
                for i, tech_items in enumerate(tech_item_sets):
                    if itemset.issubset(tech_items):
                        count_itemset += 1
                        result_items = result_item_sets[i]
                        if target_result in result_items:
                            count_itemset_with_success += 1
                
                if count_itemset > 0:
                    support_itemset = count_itemset / total_records
                    confidence = count_itemset_with_success / count_itemset
                    
                    # 结果出现的基础概率
                    base_success_rate = self._calculate_support(target_result, result_item_sets)
                    
                    if confidence >= max(self.min_confidence, base_success_rate * 1.5):
                        lift = confidence / base_success_rate if base_success_rate > 0 else 0
                        
                        # 找到示例记录
                        example_records = []
                        for i, tech_items in enumerate(tech_item_sets):
                            if itemset.issubset(tech_items) and target_result in result_item_sets[i]:
                                example_records.append(records[i].get("test_id", f"record_{i}"))
                        
                        quality_score = self._calculate_pattern_quality(
                            support=support_itemset,
                            confidence=confidence,
                            lift=lift,
                            example_count=len(example_records),
                            complexity_factor=len(itemset)  # 考虑组合复杂度
                        )
                        
                        pattern = LearningPattern(
                            pattern_id=f"tech_combo_{hash(frozenset(itemset))}",
                            pattern_type="tech_combo_success",
                            antecedent=list(itemset),
                            consequent=[target_result],
                            support=support_itemset,
                            confidence=confidence,
                            lift=lift,
                            coverage=support_itemset,
                            quality_score=quality_score,
                            examples=example_records[:5],
                            evidence_strength=min(len(example_records) / 3.0, 1.0)
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _calculate_support(self, item: str, item_sets: List[Set[str]]) -> float:
        """计算单项支持度"""
        count = sum(1 for item_set in item_sets if item in item_set)
        return count / len(item_sets) if item_sets else 0.0
    
    def _calculate_support_both(self, item1: str, item2: str, 
                               item_sets1: List[Set[str]], item_sets2: List[Set[str]]) -> float:
        """计算两项同时出现的支持度"""
        count = 0
        for i in range(len(item_sets1)):
            if item1 in item_sets1[i] and item2 in item_sets2[i]:
                count += 1
        return count / len(item_sets1) if item_sets1 else 0.0
    
    def _find_example_records(self, item1: str, item2: str,
                             item_sets1: List[Set[str]], item_sets2: List[Set[str]],
                             records: List[Dict[str, Any]]) -> List[str]:
        """找到满足模式的示例记录ID"""
        examples = []
        for i in range(len(item_sets1)):
            if item1 in item_sets1[i] and item2 in item_sets2[i]:
                record_id = records[i].get("test_id", f"record_{i}")
                examples.append(record_id)
        return examples
    
    def _find_frequent_itemsets(self, item_sets: List[Set[str]], min_freq: float = 0.1):
        """查找频繁项集（简化版本）"""
        total = len(item_sets)
        min_count = int(min_freq * total)
        
        if min_count < 1:
            min_count = 1
        
        # 统计单项频率
        item_counts = Counter()
        for item_set in item_sets:
            for item in item_set:
                item_counts[item] += 1
        
        # 取出现频率较高的项
        freq_items = []
        for item, count in item_counts.items():
            if count >= min_count:
                freq_items.append(item)
        
        # 生成候选2项集
        candidate_pairs = set()
        for i in range(len(freq_items)):
            for j in range(i+1, len(freq_items)):
                item1 = freq_items[i]
                item2 = freq_items[j]
                pair = frozenset([item1, item2])
                candidate_pairs.add(pair)
        
        # 检查候选对频率
        freq_pairs = []
        for pair in candidate_pairs:
            count = 0
            for item_set in item_sets:
                if pair.issubset(item_set):
                    count += 1
            
            if count >= min_count:
                freq_pairs.append(pair)
        
        return freq_pairs[:20]  # 取前20个，避免组合爆炸
    
    def _calculate_pattern_quality(self, support: float, confidence: float, 
                                 lift: float, example_count: int,
                                 importance_factor: float = 1.0,
                                 complexity_factor: float = 1.0) -> float:
        """计算模式质量分数"""
        # 基础质量 = 支持度×0.2 + 置信度×0.4 + 提升度因子×0.4
        lift_factor = min(lift / 2.0, 2.0)  # 标准化提升度
        
        base_quality = (
            support * 0.2 +
            confidence * 0.4 +
            (lift_factor * 0.4)
        )
        
        # 基于示例数量的调整
        example_factor = min(example_count / 5.0, 1.5)
        
        # 综合质量
        quality = base_quality * example_factor * importance_factor / complexity_factor
        
        return min(max(quality, 0.0), 1.0)
    
    def get_patterns_summary(self) -> Dict[str, Any]:
        """获取模式摘要报告"""
        if not self.patterns:
            return {"total_patterns": 0}
        
        # 按类型统计
        type_counts = Counter(p.pattern_type for p in self.patterns)
        
        # 按质量分级
        high_quality = [p for p in self.patterns if p.quality_score >= 0.8]
        medium_quality = [p for p in self.patterns if 0.6 <= p.quality_score < 0.8]
        low_quality = [p for p in self.patterns if p.quality_score < 0.6]
        
        return {
            "total_patterns": len(self.patterns),
            "pattern_types": dict(type_counts),
            "quality_distribution": {
                "high": len(high_quality),
                "medium": len(medium_quality),
                "low": len(low_quality)
            },
            "average_quality": sum(p.quality_score for p in self.patterns) / len(self.patterns),
            "top_patterns": [p.get_summary() for p in self.patterns[:5]]
        }


def demo_pattern_learner():
    """演示模式学习器"""
    print("=" * 70)
    print("模式学习器演示")
    print("=" * 70)
    
    # 加载历史数据
    data_path = "history_database.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get("test_records", [])
        print(f"📁 加载 {len(records)} 条历史测试记录")
        
    except FileNotFoundError:
        print(f"⚠️ 历史数据文件不存在: {data_path}")
        print("🎲 生成模拟数据...")
        
        # 生成简单的模拟数据
        records = []
        for i in range(20):
            record = {
                "test_id": f"test_{i:04d}",
                "quality_score": 70.0 + i,
                "technology_features": {
                    "technology_type": ["web_server", "database", "cms"][i % 3],
                    "protocols": ["HTTP/1.1", "AJP"][:i%2+1]
                },
                "planned_strategy": {
                    "strategy_type": ["comprehensive", "fast_scan", "focused"][i % 3],
                    "test_intensity": ["low", "medium", "high"][i % 3],
                    "time_allocation": {"total_minutes": [60, 120, 180][i % 3]}
                },
                "planned_tasks": [
                    {"type": "port_scan"},
                    {"type": "web_scan"},
                    {"type": "auth_test"}
                ],
                "discovered_vulnerabilities": [{"id": f"vuln_{i}"}] if i % 2 == 0 else [],
                "effectiveness_metrics": {
                    "time_efficiency": 0.9 + i * 0.02
                }
            }
            records.append(record)
    
    # 创建模式学习器
    learner = PatternLearner(min_support=0.1, min_confidence=0.7)
    
    # 学习模式
    patterns = learner.learn_from_records(records)
    
    # 生成摘要报告
    summary = learner.get_patterns_summary()
    
    print(f"\n📊 模式学习结果摘要:")
    print(f"  总模式数: {summary['total_patterns']}")
    for pattern_type, count in summary.get("pattern_types", {}).items():
        print(f"  {pattern_type}: {count}个")
    
    print(f"  质量分布: 高={summary['quality_distribution']['high']}, "
          f"中={summary['quality_distribution']['medium']}, "
          f"低={summary['quality_distribution']['low']}")
    
    print(f"  平均质量分数: {summary['average_quality']:.3f}")
    
    # 显示前3个最佳模式
    print(f"\n🏆 最佳模式 (前3个):")
    for i, pattern in enumerate(patterns[:3], 1):
        print(f"\n  {i}. {pattern.pattern_type}")
        print(f"     前件: {pattern.antecedent}")
        print(f"     后件: {pattern.consequent}")
        print(f"     支持度: {pattern.support:.3f}, 置信度: {pattern.confidence:.3f}")
        print(f"     提升度: {pattern.lift:.3f}, 质量分数: {pattern.quality_score:.3f}")
    
    print("\n" + "=" * 70)
    print("模式学习演示完成 ✅")
    print("=" * 70)


if __name__ == "__main__":
    demo_pattern_learner()