#!/usr/bin/env python3
"""
学习优化机制核心引擎 - 智能测试规划引擎阶段四

核心功能：从历史测试中学习并持续优化测试策略。
基于历史测试数据，识别成功模式，优化规则权重，改进测试策略，
实现从经验中学习和持续改进的智能系统。
"""

import json
import datetime
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime as dt
from enum import Enum


# ============================================
# 数据结构定义
# ============================================

class TestResult(Enum):
    """测试结果枚举"""
    SUCCESS = "success"      # 发现有效漏洞
    PARTIAL = "partial"      # 发现部分漏洞
    FAILURE = "failure"      # 未发现漏洞
    ERROR = "error"         # 执行错误


class VulnerabilitySeverity(Enum):
    """漏洞严重程度枚举"""
    CRITICAL = 4.0     # 严重 (9.0-10.0 CVSS)
    HIGH = 3.0         # 高危 (7.0-8.9 CVSS)  
    MEDIUM = 2.0       # 中危 (4.0-6.9 CVSS)
    LOW = 1.0          # 低危 (0.1-3.9 CVSS)
    INFO = 0.5         # 信息 (0.0 CVSS)


@dataclass
class TestRecord:
    """历史测试记录"""
    test_id: str                    # 测试唯一标识
    plan_id: str                    # 对应计划ID
    target: str                     # 测试目标
    execution_time: str             # 执行时间 (ISO格式)
    
    # 计划数据
    planned_strategy: Dict[str, Any]  # 原始计划
    planned_tasks: List[Dict[str, Any]]  # 计划任务列表
    
    # 执行结果
    actual_execution: Dict[str, Any]    # 实际执行数据
    discovered_vulnerabilities: List[Dict[str, Any]]  # 发现的漏洞
    false_positives: List[Dict[str, Any]]           # 误报
    time_consumed: float               # 实际耗时（分钟）
    resource_consumed: float           # 资源消耗（归一化0-1）
    
    # 技术特征（如果有）
    technology_features: Optional[Dict[str, Any]] = None
    
    # 效果指标（计算后填充）
    effectiveness_metrics: Optional[Dict[str, float]] = None
    quality_score: Optional[float] = None
    
    def calculate_quality_score(self) -> float:
        """计算测试质量分数（0-100）"""
        if not self.effectiveness_metrics:
            self._calculate_effectiveness_metrics()
        
        metrics = self.effectiveness_metrics
        
        # 加权综合评分
        score = (
            metrics["vulnerability_discovery_rate"] * 40 +
            (1.0 - metrics["false_positive_rate"]) * 30 +
            metrics["time_efficiency"] * 15 +
            metrics["resource_efficiency"] * 15
        )
        
        # 考虑漏洞严重程度
        vuln_severity_factor = self._calculate_vulnerability_severity_factor()
        score *= vuln_severity_factor
        
        self.quality_score = min(max(score, 0.0), 100.0)
        return self.quality_score
    
    def _calculate_effectiveness_metrics(self) -> None:
        """计算效果指标"""
        metrics = {}
        
        # 漏洞发现率
        planned_vulns = self.planned_strategy.get("expected_vulnerabilities", 1.0)
        actual_vulns = len(self.discovered_vulnerabilities)
        metrics["vulnerability_discovery_rate"] = min(actual_vulns / max(planned_vulns, 0.1), 2.0)
        
        # 误报率
        total_reports = actual_vulns + len(self.false_positives)
        metrics["false_positive_rate"] = len(self.false_positives) / max(total_reports, 1.0)
        
        # 时间效率
        planned_time = self.planned_strategy.get("total_duration", self.time_consumed)
        metrics["time_efficiency"] = planned_time / max(self.time_consumed, 0.1)
        
        # 资源效率
        planned_resource = self.planned_strategy.get("resource_intensity", 0.5)
        metrics["resource_efficiency"] = planned_resource / max(self.resource_consumed, 0.1)
        
        # 覆盖率（简化）
        planned_tasks = len(self.planned_tasks)
        executed_tasks = len(self.actual_execution.get("executed_tasks", []))
        metrics["coverage_score"] = executed_tasks / max(planned_tasks, 1.0)
        
        # 风险降低评分
        vuln_severity = self._calculate_average_vulnerability_severity()
        metrics["risk_reduction_score"] = vuln_severity / 4.0  # 标准化到0-1
        
        self.effectiveness_metrics = metrics
    
    def _calculate_vulnerability_severity_factor(self) -> float:
        """计算漏洞严重程度因子"""
        if not self.discovered_vulnerabilities:
            return 0.7  # 无漏洞发现，降低评分
        
        total_severity = sum(v.get("severity_score", 2.0) for v in self.discovered_vulnerabilities)
        avg_severity = total_severity / len(self.discovered_vulnerabilities)
        
        # 严重漏洞提升评分
        if avg_severity >= 3.0:
            return 1.3  # 高危以上漏洞，提升30%
        elif avg_severity >= 2.0:
            return 1.1  # 中危漏洞，提升10%
        else:
            return 1.0  # 低危漏洞，不变
    
    def _calculate_average_vulnerability_severity(self) -> float:
        """计算平均漏洞严重程度"""
        if not self.discovered_vulnerabilities:
            return 0.0
        
        total_severity = sum(v.get("severity_score", 2.0) for v in self.discovered_vulnerabilities)
        return total_severity / len(self.discovered_vulnerabilities)


@dataclass
class EffectivenessMetrics:
    """效果评估指标集合"""
    vulnerability_discovery_rate: float       # 漏洞发现率
    false_positive_rate: float                # 误报率
    time_efficiency: float                    # 时间效率
    resource_efficiency: float                # 资源效率
    coverage_score: float                     # 覆盖率评分
    risk_reduction_score: float               # 风险降低评分
    
    # 对比指标
    vs_random_baseline: float = 1.0          # 对比随机基线
    vs_expert_baseline: float = 1.0          # 对比专家基线
    improvement_trend: float = 0.0            # 改进趋势
    
    def overall_score(self) -> float:
        """计算总体效果分数"""
        weights = {
            "vulnerability_discovery_rate": 0.4,
            "false_positive_rate": 0.3,
            "time_efficiency": 0.15,
            "resource_efficiency": 0.15
        }
        
        # 误报率为负向指标，需要取反
        score = (
            self.vulnerability_discovery_rate * weights["vulnerability_discovery_rate"] +
            (1.0 - self.false_positive_rate) * weights["false_positive_rate"] +
            self.time_efficiency * weights["time_efficiency"] +
            self.resource_efficiency * weights["resource_efficiency"]
        )
        
        # 考虑对比基准
        baseline_factor = (self.vs_random_baseline + self.vs_expert_baseline) / 2.0
        score *= baseline_factor
        
        # 考虑改进趋势
        if self.improvement_trend > 0:
            score *= (1.0 + self.improvement_trend)
        
        return min(max(score, 0.0), 1.0)


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    optimization_id: str                     # 优化建议ID
    based_on_records: int                    # 基于多少条历史记录
    confidence: float                        # 建议置信度 (0-1)
    
    # 具体优化建议
    rule_adjustments: List[Dict[str, Any]]   # 规则调整
    parameter_changes: Dict[str, float]      # 参数变化
    knowledge_updates: List[Dict[str, Any]]  # 知识更新
    strategy_improvements: List[str]         # 策略改进
    
    # 预期效果
    expected_improvement: Dict[str, float]   # 预期改进
    verification_method: str                 # 验证方法
    
    # 元数据
    generated_at: str                        # 生成时间
    applicable_conditions: List[str]         # 适用条件
    
    def get_summary(self) -> Dict[str, Any]:
        """获取优化建议摘要"""
        total_expected_improvement = sum(self.expected_improvement.values()) / len(self.expected_improvement)
        
        return {
            "optimization_id": self.optimization_id,
            "based_on_n_records": self.based_on_records,
            "confidence": self.confidence,
            "expected_improvement": total_expected_improvement,
            "verification_method": self.verification_method,
            "rule_adjustments_count": len(self.rule_adjustments),
            "parameter_changes_count": len(self.parameter_changes),
            "strategy_improvements": len(self.strategy_improvements)
        }


# ============================================
# 历史数据管理器
# ============================================

class HistoryManager:
    """历史数据管理器"""
    
    def __init__(self, storage_path: str = "history_database.json"):
        """
        初始化历史数据管理器
        
        Args:
            storage_path: 数据存储文件路径
        """
        self.storage_path = storage_path
        self.records: List[TestRecord] = []
        self.load_history()
    
    def load_history(self) -> bool:
        """加载历史数据"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为TestRecord对象
            self.records = []
            for record_data in data.get("test_records", []):
                record = TestRecord(**record_data)
                self.records.append(record)
            
            print(f"✅ 加载 {len(self.records)} 条历史测试记录")
            return True
            
        except FileNotFoundError:
            print(f"⚠️ 历史数据文件不存在: {self.storage_path}")
            self.records = []
            return False
        except Exception as e:
            print(f"⚠️ 加载历史数据失败: {e}")
            self.records = []
            return False
    
    def save_history(self) -> bool:
        """保存历史数据"""
        try:
            # 转换为可序列化格式
            records_data = []
            for record in self.records:
                record_dict = {
                    "test_id": record.test_id,
                    "plan_id": record.plan_id,
                    "target": record.target,
                    "execution_time": record.execution_time,
                    "planned_strategy": record.planned_strategy,
                    "planned_tasks": record.planned_tasks,
                    "actual_execution": record.actual_execution,
                    "discovered_vulnerabilities": record.discovered_vulnerabilities,
                    "false_positives": record.false_positives,
                    "time_consumed": record.time_consumed,
                    "resource_consumed": record.resource_consumed,
                    "technology_features": record.technology_features,
                    "effectiveness_metrics": record.effectiveness_metrics,
                    "quality_score": record.quality_score
                }
                records_data.append(record_dict)
            
            data = {
                "version": "1.0",
                "last_updated": dt.now().isoformat(),
                "total_records": len(self.records),
                "test_records": records_data
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 保存 {len(self.records)} 条历史测试记录")
            return True
            
        except Exception as e:
            print(f"⚠️ 保存历史数据失败: {e}")
            return False
    
    def add_record(self, record: TestRecord) -> str:
        """
        添加新的测试记录
        
        Args:
            record: 测试记录
            
        Returns:
            str: 分配的test_id
        """
        # 生成唯一ID
        if not record.test_id:
            timestamp = int(dt.now().timestamp())
            record.test_id = f"test_{timestamp}_{len(self.records):04d}"
        
        # 计算效果指标
        if not record.effectiveness_metrics:
            record._calculate_effectiveness_metrics()
        
        # 计算质量分数
        if not record.quality_score:
            record.calculate_quality_score()
        
        self.records.append(record)
        print(f"📝 添加新测试记录: {record.test_id} (质量分数: {record.quality_score:.1f})")
        
        return record.test_id
    
    def get_records_by_target(self, target: str) -> List[TestRecord]:
        """获取指定目标的测试记录"""
        return [r for r in self.records if r.target == target]
    
    def get_records_by_tech_feature(self, feature_name: str, feature_value: Any) -> List[TestRecord]:
        """获取具有特定技术特征的测试记录"""
        result = []
        for record in self.records:
            if record.technology_features and feature_name in record.technology_features:
                if record.technology_features[feature_name] == feature_value:
                    result.append(record)
        
        return result
    
    def get_recent_records(self, n: int = 10) -> List[TestRecord]:
        """获取最近n条测试记录"""
        # 按执行时间排序
        sorted_records = sorted(
            self.records,
            key=lambda x: x.execution_time,
            reverse=True
        )
        return sorted_records[:n]
    
    def get_high_quality_records(self, threshold: float = 70.0) -> List[TestRecord]:
        """获取高质量测试记录（质量分数≥阈值）"""
        high_quality = []
        for record in self.records:
            if record.quality_score and record.quality_score >= threshold:
                high_quality.append(record)
        
        return high_quality
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取历史数据统计信息"""
        if not self.records:
            return {"total_records": 0}
        
        # 计算平均质量分数
        quality_scores = [r.quality_score for r in self.records if r.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # 目标统计
        targets = {}
        for record in self.records:
            targets[record.target] = targets.get(record.target, 0) + 1
        
        # 时间范围
        execution_times = [r.execution_time for r in self.records if r.execution_time]
        earliest = min(execution_times) if execution_times else None
        latest = max(execution_times) if execution_times else None
        
        return {
            "total_records": len(self.records),
            "total_targets": len(targets),
            "average_quality_score": avg_quality,
            "high_quality_records": len(self.get_high_quality_records(70.0)),
            "earliest_record": earliest,
            "latest_record": latest,
            "top_targets": sorted(targets.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def generate_simulated_data(self, n: int = 20) -> None:
        """生成模拟历史数据用于测试和演示"""
        print(f"🎲 生成 {n} 条模拟历史测试数据...")
        
        for i in range(n):
            # 创建模拟测试记录
            record = TestRecord(
                test_id=f"sim_test_{i:04d}",
                plan_id=f"plan_{i:04d}",
                target=f"target_{i%5}.example.com",
                execution_time=(dt.now() - datetime.timedelta(days=i)).isoformat(),
                
                planned_strategy={
                    "expected_vulnerabilities": 2.0 + i * 0.1,
                    "total_duration": 120.0,
                    "resource_intensity": 0.5
                },
                
                planned_tasks=[
                    {"task_id": f"task_{i}_1", "type": "port_scan"},
                    {"task_id": f"task_{i}_2", "type": "web_scan"}
                ],
                
                actual_execution={
                    "executed_tasks": ["port_scan", "web_scan"],
                    "status": "completed"
                },
                
                # 模拟发现的漏洞
                discovered_vulnerabilities=[
                    {
                        "id": f"vuln_{i}",
                        "type": ["xss", "sqli", "rce"][i % 3],
                        "severity_score": [2.0, 3.0, 4.0][i % 3],
                        "confidence": 0.8
                    }
                ] if i % 3 != 0 else [],  # 1/3的记录无漏洞发现
                
                false_positives=[] if i % 4 != 0 else [{"id": f"fp_{i}", "reason": "误报"}],
                
                time_consumed=100.0 + i * 2.0,
                resource_consumed=0.4 + i * 0.02,
                
                technology_features={
                    "technology_type": ["web_server", "database", "cms"][i % 3],
                    "protocols": ["HTTP/1.1", "AJP"][:i%2+1]
                }
            )
            
            # 计算效果指标和质量分数
            record._calculate_effectiveness_metrics()
            record.calculate_quality_score()
            self.records.append(record)
        
        print(f"✅ 生成 {n} 条模拟历史测试数据完成")
        self.save_history()


# ============================================
# 效果评估器
# ============================================

class EffectivenessEvaluator:
    """效果评估器"""
    
    def __init__(self, history_manager: HistoryManager):
        """
        初始化效果评估器
        
        Args:
            history_manager: 历史数据管理器
        """
        self.history = history_manager
        
    def evaluate_single_test(self, record: TestRecord) -> EffectivenessMetrics:
        """
        评估单个测试效果
        
        Args:
            record: 测试记录
            
        Returns:
            EffectivenessMetrics: 效果指标
        """
        if not record.effectiveness_metrics:
            record._calculate_effectiveness_metrics()
        
        metrics = record.effectiveness_metrics
        
        # 对比基准
        baseline_comparison = self._calculate_baseline_comparison(record)
        
        # 改进趋势
        improvement_trend = self._calculate_improvement_trend(record.target)
        
        return EffectivenessMetrics(
            vulnerability_discovery_rate=metrics["vulnerability_discovery_rate"],
            false_positive_rate=metrics["false_positive_rate"],
            time_efficiency=metrics["time_efficiency"],
            resource_efficiency=metrics["resource_efficiency"],
            coverage_score=metrics["coverage_score"],
            risk_reduction_score=metrics["risk_reduction_score"],
            vs_random_baseline=baseline_comparison.get("random", 1.0),
            vs_expert_baseline=baseline_comparison.get("expert", 1.0),
            improvement_trend=improvement_trend
        )
    
    def _calculate_baseline_comparison(self, record: TestRecord) -> Dict[str, float]:
        """计算与基线的对比"""
        # 这里实现简化版本，实际中可能需要更多数据
        return {
            "random": 1.2,  # 假设比随机测试好20%
            "expert": 0.9   # 假设比专家测试差10%
        }
    
    def _calculate_improvement_trend(self, target: str) -> float:
        """计算改进趋势"""
        # 获取该目标的历史记录
        target_records = self.history.get_records_by_target(target)
        if len(target_records) < 3:
            return 0.0
        
        # 按时间排序
        sorted_records = sorted(target_records, key=lambda x: x.execution_time)
        
        # 计算早期和近期记录的平均质量分数
        early_records = sorted_records[:len(sorted_records)//3]
        recent_records = sorted_records[-len(sorted_records)//3:]
        
        early_avg = sum(r.quality_score for r in early_records if r.quality_score) / len(early_records)
        recent_avg = sum(r.quality_score for r in recent_records if r.quality_score) / len(recent_records)
        
        improvement = (recent_avg - early_avg) / max(early_avg, 1.0)
        return min(max(improvement, -0.5), 0.5)  # 限制在-50%到+50%
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        stats = self.history.get_statistics()
        
        # 计算总体效果指标
        all_metrics = []
        for record in self.history.records:
            metrics = self.evaluate_single_test(record)
            all_metrics.append(metrics)
        
        if not all_metrics:
            return {"error": "无历史数据可用"}
        
        # 计算平均指标
        avg_metrics = {
            "vulnerability_discovery_rate": sum(m.vulnerability_discovery_rate for m in all_metrics) / len(all_metrics),
            "false_positive_rate": sum(m.false_positive_rate for m in all_metrics) / len(all_metrics),
            "time_efficiency": sum(m.time_efficiency for m in all_metrics) / len(all_metrics),
            "resource_efficiency": sum(m.resource_efficiency for m in all_metrics) / len(all_metrics),
            "overall_score": sum(m.overall_score() for m in all_metrics) / len(all_metrics)
        }
        
        return {
            "statistics": stats,
            "performance_metrics": avg_metrics,
            "evaluation_time": dt.now().isoformat()
        }


# ============================================
# 主协调器
# ============================================

class LearningOptimizer:
    """学习优化主协调器"""
    
    def __init__(self, storage_path: str = "history_database.json"):
        """
        初始化学习优化器
        
        Args:
            storage_path: 历史数据存储路径
        """
        self.storage_path = storage_path
        self.history_manager = HistoryManager(storage_path)
        self.effectiveness_evaluator = EffectivenessEvaluator(self.history_manager)
        
    def add_test_record(self, record_data: Dict[str, Any]) -> str:
        """
        添加新的测试记录
        
        Args:
            record_data: 测试记录数据
            
        Returns:
            str: 分配的test_id
        """
        # 转换为TestRecord对象
        record = TestRecord(**record_data)
        test_id = self.history_manager.add_record(record)
        
        # 自动保存
        self.history_manager.save_history()
        
        return test_id
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return self.effectiveness_evaluator.generate_performance_report()
    
    def analyze_and_optimize(self, target: Optional[str] = None) -> OptimizationSuggestion:
        """
        分析历史数据并生成优化建议
        
        Args:
            target: 可选，指定分析目标
            
        Returns:
            OptimizationSuggestion: 优化建议
        """
        print("🔍 开始分析历史数据并生成优化建议...")
        
        # 获取相关记录
        if target:
            records = self.history_manager.get_records_by_target(target)
            analysis_scope = f"目标: {target}"
        else:
            records = self.history_manager.records
            analysis_scope = "全部历史记录"
        
        if not records:
            return self._create_no_data_suggestion()
        
        # 分析高质量记录模式
        high_quality_records = self.history_manager.get_high_quality_records(75.0)
        low_quality_records = [r for r in records if r.quality_score and r.quality_score < 50.0]
        
        # 生成优化建议
        suggestion = self._generate_optimization_suggestion(
            records, high_quality_records, low_quality_records
        )
        
        print(f"✅ 分析完成，基于 {len(records)} 条记录生成优化建议")
        print(f"   置信度: {suggestion.confidence:.1%}")
        print(f"   预期改进: {sum(suggestion.expected_improvement.values())/len(suggestion.expected_improvement):.1%}")
        
        return suggestion
    
    def _create_no_data_suggestion(self) -> OptimizationSuggestion:
        """创建无数据时的默认建议"""
        return OptimizationSuggestion(
            optimization_id="no_data_default",
            based_on_records=0,
            confidence=0.1,
            rule_adjustments=[],
            parameter_changes={},
            knowledge_updates=[],
            strategy_improvements=["收集更多测试数据以支持学习优化"],
            expected_improvement={"overall": 0.0},
            verification_method="数据收集验证",
            generated_at=dt.now().isoformat(),
            applicable_conditions=["数据不足场景"]
        )
    
    def _generate_optimization_suggestion(self,
                                        all_records: List[TestRecord],
                                        high_quality: List[TestRecord],
                                        low_quality: List[TestRecord]) -> OptimizationSuggestion:
        """生成具体优化建议"""
        
        # 分析成功模式
        successful_patterns = self._analyze_successful_patterns(high_quality)
        
        # 分析失败模式
        failure_patterns = self._analyze_failure_patterns(low_quality)
        
        # 基于模式生成优化建议
        rule_adjustments = []
        parameter_changes = {}
        strategy_improvements = []
        knowledge_updates = []
        
        # 规则调整建议
        if successful_patterns:
            for pattern in successful_patterns:
                rule_adjustments.append({
                    "rule_type": pattern.get("type", "unknown"),
                    "adjustment": "increase_weight",
                    "reason": f"在高质量测试中有效: {pattern.get('description', '')}",
                    "confidence": pattern.get("confidence", 0.7)
                })
        
        # 参数优化建议
        avg_quality = sum(r.quality_score for r in all_records if r.quality_score) / len(all_records)
        if avg_quality < 60.0:
            parameter_changes = {
                "risk_threshold": 0.7,  # 提高风险阈值，更保守
                "time_allocation_factor": 1.2,  # 增加时间分配
                "confidence_threshold": 0.6  # 提高置信度阈值
            }
        
        # 策略改进建议
        if failure_patterns:
            for pattern in failure_patterns:
                if "time" in pattern.get("issue", ""):
                    strategy_improvements.append("增加高风险技术的测试时间分配")
                elif "coverage" in pattern.get("issue", ""):
                    strategy_improvements.append("扩展测试覆盖范围")
                elif "tool" in pattern.get("issue", ""):
                    strategy_improvements.append("优化工具选择和组合策略")
        
        # 计算预期改进
        expected_improvement = self._estimate_expected_improvement(
            len(high_quality), len(low_quality), len(all_records)
        )
        
        # 计算置信度
        confidence = min(len(all_records) / 50.0, 0.9)  # 基于数据量计算置信度
        
        return OptimizationSuggestion(
            optimization_id=f"opt_{int(dt.now().timestamp())}",
            based_on_records=len(all_records),
            confidence=confidence,
            rule_adjustments=rule_adjustments,
            parameter_changes=parameter_changes,
            knowledge_updates=knowledge_updates,
            strategy_improvements=strategy_improvements,
            expected_improvement=expected_improvement,
            verification_method="A/B测试验证",
            generated_at=dt.now().isoformat(),
            applicable_conditions=["类似技术特征场景"]
        )
    
    def _analyze_successful_patterns(self, high_quality_records: List[TestRecord]) -> List[Dict[str, Any]]:
        """分析成功模式"""
        patterns = []
        
        if not high_quality_records:
            return patterns
        
        # 分析技术特征
        tech_features = {}
        for record in high_quality_records:
            if record.technology_features:
                for key, value in record.technology_features.items():
                    # 处理不可哈希的值（如列表）
                    if isinstance(value, (list, dict)):
                        # 将列表/字典转换为字符串表示用于比较
                        value_str = str(value)
                        tech_features.setdefault(key, []).append(value_str)
                    else:
                        tech_features.setdefault(key, []).append(value)
        
        # 生成模式
        for feature_name, values in tech_features.items():
            # 计算值分布
            from collections import Counter
            value_counts = Counter(values)
            
            # 检查是否有明显的主要值
            if len(value_counts) <= 3:  # 值种类比较少
                common_value, count = value_counts.most_common(1)[0]
                confidence = count / len(values)
                
                # 还原原始值类型（如果是字符串化的列表/字典）
                if isinstance(common_value, str) and common_value.startswith(('{', '[')):
                    try:
                        import ast
                        original_value = ast.literal_eval(common_value)
                    except:
                        original_value = common_value
                else:
                    original_value = common_value
                
                if confidence > 0.3:  # 至少30%的集中度
                    patterns.append({
                        "type": "technology_feature",
                        "feature": feature_name,
                        "value": original_value,
                        "description": f"高质量测试中常见特征: {feature_name}={original_value}",
                        "confidence": confidence
                    })
        
        return patterns
    
    def _analyze_failure_patterns(self, low_quality_records: List[TestRecord]) -> List[Dict[str, Any]]:
        """分析失败模式"""
        patterns = []
        
        if not low_quality_records:
            return patterns
        
        # 分析常见问题
        issues = []
        for record in low_quality_records:
            if record.effectiveness_metrics:
                metrics = record.effectiveness_metrics
                
                if metrics.get("vulnerability_discovery_rate", 0) < 0.3:
                    issues.append("低漏洞发现率")
                elif metrics.get("false_positive_rate", 0) > 0.5:
                    issues.append("高误报率")
                elif metrics.get("time_efficiency", 0) < 0.7:
                    issues.append("时间效率低下")
                elif metrics.get("coverage_score", 0) < 0.5:
                    issues.append("覆盖率不足")
        
        # 统计问题频率
        from collections import Counter
        issue_counts = Counter(issues)
        
        for issue, count in issue_counts.items():
            if count >= len(low_quality_records) * 0.3:  # 30%以上存在此问题
                patterns.append({
                    "type": "common_issue",
                    "issue": issue,
                    "frequency": count / len(low_quality_records),
                    "description": f"低质量测试中常见问题: {issue}"
                })
        
        return patterns
    
    def _estimate_expected_improvement(self,
                                     n_high: int,
                                     n_low: int,
                                     n_total: int) -> Dict[str, float]:
        """估计预期改进效果"""
        if n_total == 0:
            return {"overall": 0.0}
        
        # 基于高质量比例估计改进潜力
        quality_ratio = n_high / n_total if n_total > 0 else 0.0
        
        # 预期改进比例
        expected_overall = 0.1 + quality_ratio * 0.3  # 10%基础+基于质量比例
        
        return {
            "overall": min(expected_overall, 0.5),  # 最多50%改进
            "vulnerability_discovery": 0.15,
            "false_positive_reduction": 0.10,
            "time_efficiency": 0.08,
            "resource_efficiency": 0.05
        }


# ============================================
# 演示代码
# ============================================

def demo_learning_optimizer():
    """演示学习优化器的基本功能"""
    print("=" * 70)
    print("学习优化机制演示 - 阶段四")
    print("=" * 70)
    
    # 创建学习优化器
    optimizer = LearningOptimizer()
    
    # 生成模拟数据（如果无历史数据）
    if not optimizer.history_manager.records:
        print("\n🎲 无历史数据，生成模拟数据...")
        optimizer.history_manager.generate_simulated_data(15)
    
    print(f"\n📊 历史数据统计:")
    stats = optimizer.history_manager.get_statistics()
    for key, value in stats.items():
        if key != "top_targets":
            print(f"  {key}: {value}")
    
    # 分析并生成优化建议
    print("\n🔍 分析历史数据并生成优化建议...")
    suggestion = optimizer.analyze_and_optimize()
    
    print(f"\n🎯 优化建议摘要:")
    summary = suggestion.get_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n📋 具体优化建议:")
    if suggestion.rule_adjustments:
        print(f"  规则调整 ({len(suggestion.rule_adjustments)}条):")
        for i, adj in enumerate(suggestion.rule_adjustments[:3], 1):
            print(f"    {i}. {adj.get('rule_type')}: {adj.get('reason', '')}")
    
    if suggestion.parameter_changes:
        print(f"  参数变化 ({len(suggestion.parameter_changes)}个):")
        for key, value in suggestion.parameter_changes.items():
            print(f"    • {key}: {value:.2f}")
    
    if suggestion.strategy_improvements:
        print(f"  策略改进 ({len(suggestion.strategy_improvements)}条):")
        for i, improvement in enumerate(suggestion.strategy_improvements[:3], 1):
            print(f"    {i}. {improvement}")
    
    # 性能报告
    print("\n📈 性能报告:")
    report = optimizer.get_performance_report()
    if "performance_metrics" in report:
        metrics = report["performance_metrics"]
        print(f"  平均漏洞发现率: {metrics.get('vulnerability_discovery_rate', 0):.3f}")
        print(f"  平均误报率: {metrics.get('false_positive_rate', 0):.3f}")
        print(f"  平均时间效率: {metrics.get('time_efficiency', 0):.3f}")
        print(f"  总体效果分数: {metrics.get('overall_score', 0):.3f}")
    
    print("\n" + "=" * 70)
    print("演示完成 ✅")
    print("=" * 70)


if __name__ == "__main__":
    demo_learning_optimizer()