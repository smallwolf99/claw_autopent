#!/usr/bin/env python3
"""
动态规划算法 - 智能测试规划核心引擎

核心功能：基于风险画像和资源约束，动态生成最优测试策略

算法设计目标：
1. 在给定资源约束下最大化期望漏洞发现价值
2. 考虑测试成本、成功率、依赖关系
3. 支持动态调整和在线学习
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
from enum import Enum
import copy

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"      # 未开始
    RUNNING = "running"     # 执行中
    SUCCESS = "success"     # 成功完成
    FAILED = "failed"       # 执行失败
    SKIPPED = "skipped"     # 跳过(依赖失败)


@dataclass
class TestTask:
    """测试任务定义"""
    id: str                  # 任务唯一标识
    name: str               # 任务名称
    description: str        # 任务描述
    
    # 测试价值 (期望收益)
    expected_value: float   # 期望发现漏洞价值 (0-100)
    success_probability: float  # 成功概率 (0-1)
    
    # 资源成本
    time_cost: float        # 预计执行时间 (分钟)
    cpu_cost: float         # CPU消耗相对值 (0-10)
    memory_cost: float      # 内存消耗相对值 (0-10)
    network_cost: float     # 网络消耗相对值 (0-10)
    
    # 依赖关系
    prerequisites: List[str]  # 前置任务ID列表
    conflicts: List[str]      # 冲突任务ID列表
    
    # 工具和类型
    tool: str               # 使用工具 (nuclei, afrog, sqlmap等)
    test_type: str          # 测试类型 (cve_validation, auth_bypass等)
    category: str           # 测试类别 (tech_stack, exposure, business等)
    
    # 执行状态
    status: TestStatus = TestStatus.PENDING
    actual_cost: float = 0.0  # 实际执行成本
    actual_value: float = 0.0  # 实际获得价值
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "expected_value": self.expected_value,
            "success_probability": self.success_probability,
            "time_cost": self.time_cost,
            "cpu_cost": self.cpu_cost,
            "memory_cost": self.memory_cost,
            "network_cost": self.network_cost,
            "prerequisites": self.prerequisites,
            "conflicts": self.conflicts,
            "tool": self.tool,
            "test_type": self.test_type,
            "category": self.category,
            "status": self.status.value,
            "value_cost_ratio": self.value_cost_ratio()
        }
    
    def total_cost(self, weights: Dict[str, float] = None) -> float:
        """计算总成本（加权）"""
        weights = weights or {
            'time': 0.5,
            'cpu': 0.2,
            'memory': 0.2,
            'network': 0.1
        }
        
        return (
            self.time_cost * weights['time'] +
            self.cpu_cost * weights['cpu'] +
            self.memory_cost * weights['memory'] +
            self.network_cost * weights['network']
        )
    
    def expected_benefit(self) -> float:
        """计算期望收益"""
        return self.expected_value * self.success_probability
    
    def value_cost_ratio(self) -> float:
        """计算价值成本比（用于贪心算法）"""
        cost = self.total_cost()
        if cost <= 0:
            return float('inf')  # 零成本任务优先执行
        return self.expected_benefit() / cost
    
    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """检查任务是否就绪（依赖是否满足）"""
        return all(prereq in completed_tasks for prereq in self.prerequisites)


@dataclass
class ResourceBudget:
    """资源预算约束"""
    max_time: float         # 最大总时间 (分钟)
    max_cpu: float          # 最大CPU总消耗
    max_memory: float       # 最大内存总消耗
    max_network: float      # 最大网络总消耗
    max_concurrency: int     # 最大并发任务数
    
    # 当前使用量
    time_used: float = 0.0
    cpu_used: float = 0.0
    memory_used: float = 0.0
    network_used: float = 0.0
    tasks_running: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "max_time": self.max_time,
            "max_cpu": self.max_cpu,
            "max_memory": self.max_memory,
            "max_network": self.max_network,
            "max_concurrency": self.max_concurrency,
            "time_used": self.time_used,
            "cpu_used": self.cpu_used,
            "memory_used": self.memory_used,
            "network_used": self.network_used,
            "tasks_running": self.tasks_running,
            "time_utilization": self.time_used / self.max_time if self.max_time > 0 else 0,
            "overall_utilization": self.overall_utilization()
        }
    
    def can_accept(self, task: TestTask) -> Tuple[bool, str]:
        """检查是否能够接受新任务"""
        if self.time_used + task.time_cost > self.max_time:
            return False, f"时间不足: 已用{self.time_used}/{self.max_time}, 还需{task.time_cost}"
        
        if self.cpu_used + task.cpu_cost > self.max_cpu:
            return False, f"CPU不足: 已用{self.cpu_used}/{self.max_cpu}, 还需{task.cpu_cost}"
        
        if self.memory_used + task.memory_cost > self.max_memory:
            return False, f"内存不足: 已用{self.memory_used}/{self.max_memory}, 还需{task.memory_cost}"
        
        if self.network_used + task.network_cost > self.max_network:
            return False, f"网络不足: 已用{self.network_used}/{self.max_network}, 还需{task.network_cost}"
        
        if self.tasks_running >= self.max_concurrency:
            return False, f"并发数限制: {self.tasks_running}/{self.max_concurrency}"
        
        return True, "资源充足"
    
    def accept(self, task: TestTask):
        """接受任务，更新资源使用情况"""
        self.time_used += task.time_cost
        self.cpu_used += task.cpu_cost
        self.memory_used += task.memory_cost
        self.network_used += task.network_cost
        self.tasks_running += 1
    
    def release(self, task: TestTask):
        """释放任务占用的资源"""
        self.tasks_running = max(0, self.tasks_running - 1)
        # 注意：一旦任务开始执行，资源实际上已被占用
        # 释放只是减少并发计数，不减少实际资源消耗
    
    def overall_utilization(self) -> float:
        """计算总体资源利用率"""
        if (self.max_time + self.max_cpu + self.max_memory + self.max_network) == 0:
            return 0.0
        
        return (
            (self.time_used / self.max_time if self.max_time > 0 else 0) * 0.5 +
            (self.cpu_used / self.max_cpu if self.max_cpu > 0 else 0) * 0.2 +
            (self.memory_used / self.max_memory if self.max_memory > 0 else 0) * 0.2 +
            (self.network_used / self.max_network if self.max_network > 0 else 0) * 0.1
        )


@dataclass
class PlanningResult:
    """规划结果"""
    selected_tasks: List[TestTask]          # 选择的测试任务
    schedule: List[Tuple[TestTask, float]]  # 调度序列 (任务, 开始时间)
    total_expected_value: float             # 总期望价值
    total_cost: float                       # 总成本
    resource_utilization: float             # 资源利用率
    algorithm_used: str                     # 使用的算法
    planning_time: float                    # 规划耗时 (秒)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_expected_value": self.total_expected_value,
            "total_cost": self.total_cost,
            "value_cost_ratio": self.total_expected_value / self.total_cost if self.total_cost > 0 else float('inf'),
            "resource_utilization": self.resource_utilization,
            "algorithm_used": self.algorithm_used,
            "planning_time": self.planning_time,
            "selected_task_count": len(self.selected_tasks),
            "schedule_summary": self._schedule_summary(),
            "task_breakdown": self._task_breakdown()
        }
    
    def _schedule_summary(self) -> List[Dict[str, Any]]:
        """生成调度摘要"""
        summary = []
        for task, start_time in self.schedule[:10]:  # 只显示前10个
            summary.append({
                "task_id": task.id,
                "task_name": task.name,
                "start_time": start_time,
                "duration": task.time_cost,
                "expected_value": task.expected_benefit(),
                "value_cost_ratio": task.value_cost_ratio()
            })
        return summary
    
    def _task_breakdown(self) -> Dict[str, Any]:
        """生成任务分类统计"""
        breakdown = {
            "by_category": {},
            "by_tool": {},
            "by_type": {}
        }
        
        for task in self.selected_tasks:
            # 按类别统计
            cat = task.category
            breakdown["by_category"][cat] = breakdown["by_category"].get(cat, 0) + 1
            
            # 按工具统计
            tool = task.tool
            breakdown["by_tool"][tool] = breakdown["by_tool"].get(tool, 0) + 1
            
            # 按测试类型统计
            test_type = task.test_type
            breakdown["by_type"][test_type] = breakdown["by_type"].get(test_type, 0) + 1
        
        return breakdown


class DynamicPlanner:
    """动态规划器核心类"""
    
    def __init__(self, risk_profile: Optional[Dict[str, Any]] = None):
        """初始化动态规划器
        
        Args:
            risk_profile: 风险画像数据（第一阶段结果）
        """
        self.risk_profile = risk_profile or {}
        self.task_catalog = {}  # 任务ID -> TestTask映射
        self._load_default_task_catalog()
        
        logger.info(f"动态规划器初始化完成，任务目录大小: {len(self.task_catalog)}")
    
    def _load_default_task_catalog(self):
        """加载默认任务目录（基于风险的测试任务映射）"""
        # 技术栈相关测试任务
        self.task_catalog.update({
            "tech_tomcat_cve": TestTask(
                id="tech_tomcat_cve",
                name="Tomcat CVE验证",
                description="验证Tomcat相关的已知高危CVE",
                expected_value=80.0,
                success_probability=0.3,
                time_cost=15.0,
                cpu_cost=5.0,
                memory_cost=3.0,
                network_cost=2.0,
                prerequisites=[],
                conflicts=[],
                tool="nuclei",
                test_type="cve_validation",
                category="tech_stack"
            ),
            "tech_jquery_xss": TestTask(
                id="tech_jquery_xss",
                name="JQuery XSS安全测试",
                description="测试JQuery相关的XSS和DOM漏洞",
                expected_value=45.0,
                success_probability=0.4,
                time_cost=10.0,
                cpu_cost=3.0,
                memory_cost=2.0,
                network_cost=3.0,
                prerequisites=[],
                conflicts=[],
                tool="custom_scripts",
                test_type="xss_testing",
                category="tech_stack"
            )
        })
        
        # 暴露面相关测试任务
        self.task_catalog.update({
            "exposure_login_test": TestTask(
                id="exposure_login_test",
                name="登录页面安全测试",
                description="测试登录页面的认证安全机制",
                expected_value=60.0,
                success_probability=0.5,
                time_cost=20.0,
                cpu_cost=4.0,
                memory_cost=3.0,
                network_cost=6.0,
                prerequisites=[],
                conflicts=[],
                tool="hydra",
                test_type="auth_bypass",
                category="exposure"
            ),
            "exposure_session_test": TestTask(
                id="exposure_session_test",
                name="会话管理测试",
                description="测试会话管理机制的安全性",
                expected_value=40.0,
                success_probability=0.6,
                time_cost=10.0,
                cpu_cost=3.0,
                memory_cost=4.0,
                network_cost=3.0,
                prerequisites=["exposure_login_test"],
                conflicts=[],
                tool="burpsuite",
                test_type="session_security",
                category="exposure"
            )
        })
        
        # 业务逻辑相关测试任务
        self.task_catalog.update({
            "business_transfer_test": TestTask(
                id="business_transfer_test",
                name="银行转账逻辑测试",
                description="测试银行系统转账功能的安全逻辑",
                expected_value=90.0,
                success_probability=0.2,
                time_cost=30.0,
                cpu_cost=2.0,
                memory_cost=2.0,
                network_cost=2.0,
                prerequisites=["exposure_login_test"],
                conflicts=["exposure_session_test"],
                tool="custom_scripts",
                test_type="business_logic",
                category="business"
            ),
            "business_account_test": TestTask(
                id="business_account_test",
                name="账户权限隔离测试",
                description="测试不同账户间的数据隔离安全",
                expected_value=70.0,
                success_probability=0.3,
                time_cost=25.0,
                cpu_cost=2.0,
                memory_cost=3.0,
                network_cost=4.0,
                prerequisites=["exposure_login_test"],
                conflicts=[],
                tool="sqlmap",
                test_type="data_isolation",
                category="business"
            )
        })
        
        # 配置安全相关测试任务
        self.task_catalog.update({
            "config_headers_test": TestTask(
                id="config_headers_test",
                name="安全头配置测试",
                description="检查HTTP安全头的正确配置",
                expected_value=30.0,
                success_probability=0.8,
                time_cost=5.0,
                cpu_cost=1.0,
                memory_cost=1.0,
                network_cost=1.0,
                prerequisites=[],
                conflicts=[],
                tool="custom_scripts",
                test_type="config_check",
                category="config"
            )
        })
    
    def plan(self, risk_profile: Dict[str, Any], budget: ResourceBudget, 
             algorithm: str = "greedy") -> PlanningResult:
        """执行动态规划
        
        Args:
            risk_profile: 风险画像数据
            budget: 资源预算约束
            algorithm: 规划算法 ("greedy", "dp", "mcts")
            
        Returns:
            PlanningResult: 规划结果
        """
        logger.info(f"开始动态规划，算法: {algorithm}, 预算: {budget}")
        start_time = datetime.now()
        
        # 根据风险画像调整任务价值
        adjusted_tasks = self._adjust_task_values(risk_profile)
        
        # 选择规划算法
        if algorithm == "greedy":
            result = self._greedy_plan(adjusted_tasks, budget)
        elif algorithm == "dp":
            result = self._dp_plan(adjusted_tasks, budget)
        elif algorithm == "mcts":
            result = self._mcts_plan(adjusted_tasks, budget)
        else:
            raise ValueError(f"未知算法: {algorithm}")
        
        # 计算规划时间
        planning_time = (datetime.now() - start_time).total_seconds()
        result.planning_time = planning_time
        result.algorithm_used = algorithm
        
        logger.info(f"动态规划完成: 选择{len(result.selected_tasks)}个任务, "
                   f"总期望价值={result.total_expected_value:.1f}, "
                   f"规划耗时={planning_time:.2f}秒")
        
        return result
    
    def _adjust_task_values(self, risk_profile: Dict[str, Any]) -> List[TestTask]:
        """根据风险画像调整任务价值"""
        adjusted_tasks = []
        
        # 提取风险评分
        tech_risk = risk_profile.get("tech_risk", 50.0)
        exposure_risk = risk_profile.get("exposure_risk", 50.0)
        business_risk = risk_profile.get("business_risk", 50.0)
        config_risk = risk_profile.get("config_risk", 50.0)
        
        # 提取业务类型
        business_type = risk_profile.get("business_type", "unknown")
        business_confidence = risk_profile.get("business_confidence", 0.5)
        
        for task in self.task_catalog.values():
            # 创建任务副本避免修改原始对象
            task_copy = copy.deepcopy(task)
            
            # 根据风险类别调整价值
            if task.category == "tech_stack":
                # 技术栈任务价值与tech_risk成正比
                adjustment_factor = min(2.0, tech_risk / 50.0)
                task_copy.expected_value *= adjustment_factor
            
            elif task.category == "exposure":
                # 暴露面任务价值与exposure_risk成正比
                adjustment_factor = min(2.0, exposure_risk / 50.0)
                task_copy.expected_value *= adjustment_factor
            
            elif task.category == "business":
                # 业务任务价值与business_risk成正比，业务类型敏感度加成
                business_factor = self._business_type_factor(business_type, business_confidence)
                adjustment_factor = min(2.5, business_risk / 50.0 * business_factor)
                task_copy.expected_value *= adjustment_factor
            
            elif task.category == "config":
                # 配置任务价值与config_risk成正比
                adjustment_factor = min(1.5, config_risk / 50.0)
                task_copy.expected_value *= adjustment_factor
            
            # 额外优化：根据风险画像的具体特征微调
            if tech_risk > 70.0 and "tomcat" in task.name.lower():
                task_copy.expected_value *= 1.5  # Tomcat高风险时相关测试价值增加
            
            if business_type == "banking" and "business" in task.category:
                task_copy.expected_value *= 1.8  # 银行系统的业务测试特别重要
            
            adjusted_tasks.append(task_copy)
        
        return adjusted_tasks
    
    def _business_type_factor(self, business_type: str, confidence: float) -> float:
        """计算业务类型的风险调整因子"""
        business_factors = {
            'banking': 1.8,
            'financial': 1.7,
            'healthcare': 1.6,
            'government': 1.5,
            'ecommerce': 1.4,
            'social': 1.3,
            'education': 1.2,
            'enterprise': 1.1,
            'unknown': 1.0
        }
        
        base_factor = business_factors.get(business_type, 1.0)
        # 置信度调整：置信度越低，不确定性越高，需要更谨慎的测试
        confidence_adj = 1.0 + (1.0 - confidence) * 0.5
        
        return base_factor * confidence_adj
    
    def _greedy_plan(self, tasks: List[TestTask], budget: ResourceBudget) -> PlanningResult:
        """贪心算法规划：按价值/成本比排序"""
        # 过滤不可用的任务（价值<=0或成本<=0）
        valid_tasks = [t for t in tasks if t.expected_benefit() > 0 and t.time_cost > 0]
        
        # 按价值成本比降序排序
        valid_tasks.sort(key=lambda t: t.value_cost_ratio(), reverse=True)
        
        selected = []
        schedule = []
        total_value = 0.0
        total_cost = 0.0
        
        current_time = 0.0
        
        for task in valid_tasks:
            # 检查资源约束
            can_accept, reason = budget.can_accept(task)
            if not can_accept:
                logger.debug(f"跳过任务 {task.id}: {reason}")
                continue
            
            # 检查依赖是否满足
            completed_ids = {t.id for t in selected}
            if not task.is_ready(completed_ids):
                logger.debug(f"跳过任务 {task.id}: 依赖未满足")
                continue
            
            # 检查冲突
            conflicting = any(task.id in t.conflicts for t in selected)
            if conflicting:
                logger.debug(f"跳过任务 {task.id}: 存在冲突")
                continue
            
            # 接受任务
            budget.accept(task)
            selected.append(task)
            schedule.append((task, current_time))
            
            total_value += task.expected_benefit()
            total_cost += task.time_cost
            current_time += task.time_cost
            
            logger.debug(f"选择任务 {task.id}: 价值={task.expected_benefit():.1f}, "
                        f"价值成本比={task.value_cost_ratio():.2f}")
            
            # 检查是否达到预算限制
            if budget.time_used >= budget.max_time * 0.95:
                logger.info(f"达到时间预算限制: {budget.time_used}/{budget.max_time}")
                break
        
        # 计算资源利用率
        resource_utilization = budget.overall_utilization()
        
        return PlanningResult(
            selected_tasks=selected,
            schedule=schedule,
            total_expected_value=total_value,
            total_cost=total_cost,
            resource_utilization=resource_utilization,
            algorithm_used="greedy",
            planning_time=0.0
        )
    
    def _dp_plan(self, tasks: List[TestTask], budget: ResourceBudget) -> PlanningResult:
        """动态规划算法（0-1背包问题变种）"""
        # 简化版：将所有资源转换为等价"成本单位"
        logger.warning("完整动态规划算法较复杂，暂时使用贪心算法近似")
        # TODO: 实现完整的多维背包问题动态规划
        return self._greedy_plan(tasks, budget)
    
    def _mcts_plan(self, tasks: List[TestTask], budget: ResourceBudget) -> PlanningResult:
        """蒙特卡洛树搜索算法（复杂环境优化）"""
        logger.warning("MCTS算法较复杂，暂时使用贪心算法近似")
        # TODO: 实现蒙特卡洛树搜索算法
        return self._greedy_plan(tasks, budget)


def main():
    """主函数：示例运行动态规划器"""
    print("🧠 动态规划算法 - 示例运行")
    
    # 创建示例风险画像 (模拟第一阶段输出)
    example_risk_profile = {
        "overall_score": 33.5,
        "tech_risk": 43.3,
        "exposure_risk": 7.5,
        "business_risk": 58.3,
        "config_risk": 23.0,
        "business_type": "banking",
        "business_confidence": 0.8
    }
    
    # 创建资源预算 (4小时总时间，中等资源限制)
    budget = ResourceBudget(
        max_time=240.0,     # 4小时
        max_cpu=40.0,
        max_memory=50.0,
        max_network=30.0,
        max_concurrency=3
    )
    
    # 创建动态规划器
    planner = DynamicPlanner()
    
    # 使用贪心算法规划
    result = planner.plan(example_risk_profile, budget, algorithm="greedy")
    
    # 输出规划结果摘要
    print(f"\n📋 动态规划结果摘要:")
    print(f"   算法: {result.algorithm_used}")
    print(f"   选择任务: {len(result.selected_tasks)}/{len(planner.task_catalog)}")
    print(f"   总期望价值: {result.total_expected_value:.1f}")
    print(f"   总成本: {result.total_cost:.1f}分钟")
    print(f"   价值成本比: {result.total_expected_value/result.total_cost:.2f}")
    print(f"   资源利用率: {result.resource_utilization*100:.1f}%")
    print(f"   规划耗时: {result.planning_time:.2f}秒")
    
    # 显示前5个任务的调度
    print(f"\n⏱️ 调度序列 (前5个):")
    for i, (task, start_time) in enumerate(result.schedule[:5], 1):
        print(f"   {i}. [{start_time:.0f}分开始] {task.name} (价值={task.expected_benefit():.1f}, 耗时={task.time_cost}分)")
    
    # 按类别统计
    breakdown = result._task_breakdown()
    print(f"\n📊 任务分类统计:")
    for category, count in breakdown["by_category"].items():
        print(f"   {category}: {count}个")
    
    # 保存完整结果
    output_path = Path(__file__).parent.parent / "deliverables" / "planning_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 完整规划结果已保存到: {output_path}")


if __name__ == "__main__":
    main()