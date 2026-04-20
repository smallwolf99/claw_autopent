#!/usr/bin/env python3
"""
资源优化分配模型 - Dynamic Planning Algorithm Phase 2

处理测试任务的各种资源约束，优化资源分配，确保在有限资源下最大化测试效果。
核心功能：资源约束检查、分配优化、冲突检测、调度可行性验证。
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

# 导入优先级引擎的数据结构
from priority_engine import TestTask, ResourceConstraint

# ============================================
# 数据结构定义
# ============================================

class ResourceType(Enum):
    """资源类型枚举"""
    TIME = "time"                    # 时间资源
    COMPUTATION = "computation"      # 计算资源 (CPU/RAM)
    NETWORK = "network"              # 网络资源 (带宽)
    SKILL = "skill"                  # 技能资源 (人员技能)
    LICENSE = "license"              # 许可证资源 (工具许可证)


@dataclass
class ResourceAllocation:
    """资源分配记录"""
    task_id: str
    resource_type: ResourceType
    amount: float                    # 分配的数量
    start_time: float                # 开始时间 (从0开始计时)
    duration: float                  # 持续时间


@dataclass
class ResourcePool:
    """资源池定义"""
    total_time: float                # 总可用时间 (分钟)
    computation_capacity: float      # 计算能力 (0-1, 1表示满负载)
    network_bandwidth: float         # 网络带宽 (MB/s)
    available_skills: List[str]      # 可用技能列表
    tool_licenses: Dict[str, int]    # 工具许可证数量
    
    # 当前已分配资源
    allocated_time: float = 0.0
    allocated_computation: float = 0.0
    allocated_bandwidth: float = 0.0
    allocated_tools: Dict[str, int] = field(default_factory=dict)
    
    def clone(self) -> 'ResourcePool':
        """克隆资源池的当前状态"""
        return ResourcePool(
            total_time=self.total_time,
            computation_capacity=self.computation_capacity,
            network_bandwidth=self.network_bandwidth,
            available_skills=self.available_skills.copy(),
            tool_licenses=self.tool_licenses.copy(),
            allocated_time=self.allocated_time,
            allocated_computation=self.allocated_computation,
            allocated_bandwidth=self.allocated_bandwidth,
            allocated_tools=self.allocated_tools.copy()
        )


@dataclass
class SchedulingResult:
    """调度结果"""
    task: TestTask
    feasible: bool                    # 是否可调度
    scheduling_time: Optional[float]  # 建议调度时间 (如果可调度)
    required_delay: float = 0.0       # 需要延迟的时间 (如果有冲突)
    conflicts: List[str] = field(default_factory=list)  # 冲突描述
    resource_usage: Dict[str, float] = field(default_factory=dict)  # 资源使用情况


# ============================================
# 资源需求映射
# ============================================

class TaskResourceMapper:
    """测试任务到资源需求的映射器"""
    
    # 测试类型到资源需求的默认映射
    TYPE_RESOURCE_MAP = {
        "port_scan": {
            "time_factor": 1.0,        # 基础时间因子
            "computation": 0.3,        # 计算需求
            "network": 2.0,            # 网络需求 (MB/s)
            "skills": ["network_scan"], # 所需技能
            "tools": ["nmap"],         # 所需工具
        },
        "web_scan": {
            "time_factor": 3.0,        # 基础时间因子
            "computation": 0.6,        # 计算需求
            "network": 1.5,            # 网络需求
            "skills": ["web_security"], # 所需技能
            "tools": ["zap", "nuclei"], # 所需工具
        },
        "cve_verification": {
            "time_factor": 2.0,        # 基础时间因子
            "computation": 0.4,        # 计算需求
            "network": 0.5,            # 网络需求
            "skills": ["cve_research"], # 所需技能
            "tools": ["nuclei"],       # 所需工具
        },
        "config_test": {
            "time_factor": 1.5,        # 基础时间因子
            "computation": 0.3,        # 计算需求
            "network": 0.3,            # 网络需求
            "skills": ["config_audit"], # 所需技能
            "tools": ["nikto"],        # 所需工具
        },
        "auth_test": {
            "time_factor": 2.5,        # 基础时间因子
            "computation": 0.5,        # 计算需求
            "network": 0.8,            # 网络需求
            "skills": ["auth_testing"], # 所需技能
            "tools": ["hydra"],        # 所需工具
        },
    }
    
    @classmethod
    def get_resource_requirements(cls, task: TestTask) -> Dict[str, Any]:
        """
        获取测试任务的资源需求
        
        Args:
            task: 测试任务
            
        Returns:
            Dict[str, Any]: 资源需求字典
        """
        # 获取基础映射
        task_type = task.test_type.value
        base_req = cls.TYPE_RESOURCE_MAP.get(task_type, cls.TYPE_RESOURCE_MAP["web_scan"])
        
        # 根据任务属性调整
        requirements = {
            "time_minutes": task.time_cost_minutes,
            "computation": base_req["computation"] * (1.0 + task.resource_intensity * 0.5),
            "network_mbps": base_req["network"] * (1.0 + task.resource_intensity * 0.3),
            "skills": base_req["skills"],
            "tools": base_req["tools"],
            "skill_level": task.skill_requirement,
        }
        
        return requirements


# ============================================
# 资源优化引擎
# ============================================

class ResourceOptimizer:
    """资源优化分配引擎"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化资源优化器
        
        Args:
            config: 配置参数
        """
        self.config = config or self.default_config()
        self.resource_mapper = TaskResourceMapper()
        
    @staticmethod
    def default_config() -> Dict[str, Any]:
        """默认配置参数"""
        return {
            # 资源约束参数
            "max_computation_load": 0.8,       # 最大计算负载 (80%)
            "max_network_load": 0.7,           # 最大网络负载 (70%)
            "tool_license_limit": 1,           # 每个工具的许可证限制
            
            # 调度参数
            "scheduling_granularity": 5.0,     # 调度粒度 (分钟)
            "max_scheduling_delay": 240.0,     # 最大调度延迟 (4小时)
            "parallelism_factor": 1.5,         # 并行度因子
            
            # 优化参数
            "time_preference": 0.7,            # 时间偏好 (越高越倾向于快速完成任务)
            "resource_efficiency": 0.5,        # 资源效率偏好
            "fairness_factor": 0.3,            # 公平性因子
        }
    
    def create_resource_pool(self, constraint: ResourceConstraint) -> ResourcePool:
        """
        从资源约束创建资源池
        
        Args:
            constraint: 资源约束
            
        Returns:
            ResourcePool: 资源池对象
        """
        return ResourcePool(
            total_time=constraint.total_time_minutes,
            computation_capacity=self.config["max_computation_load"],
            network_bandwidth=constraint.network_bandwidth_limit,
            available_skills=["network_scan", "web_security", "cve_research", "config_audit"],
            tool_licenses={
                "nmap": 2,
                "zap": 1,
                "nuclei": 1,
                "nikto": 1,
                "hydra": 1,
            }
        )
    
    def check_task_feasibility(self, task: TestTask, 
                               resource_pool: ResourcePool,
                               current_time: float = 0.0) -> SchedulingResult:
        """
        检查单个任务在给定时间的调度可行性
        
        Args:
            task: 测试任务
            resource_pool: 资源池 (当前状态)
            current_time: 当前时间
            
        Returns:
            SchedulingResult: 调度结果
        """
        # 获取任务资源需求
        requirements = self.resource_mapper.get_resource_requirements(task)
        task_duration = requirements["time_minutes"]
        
        # 检查各项资源约束
        conflicts = []
        
        # 1. 时间约束检查
        available_time = resource_pool.total_time - resource_pool.allocated_time
        if task_duration > available_time:
            conflicts.append(f"时间不足: 需要{task_duration:.1f}分钟, 剩余{available_time:.1f}分钟")
        
        # 2. 计算资源检查
        required_computation = requirements["computation"]
        available_computation = resource_pool.computation_capacity - resource_pool.allocated_computation
        if required_computation > available_computation:
            conflicts.append(f"计算资源不足: 需要{required_computation:.2f}, 剩余{available_computation:.2f}")
        
        # 3. 网络资源检查
        required_network = requirements["network_mbps"]
        available_network = resource_pool.network_bandwidth - resource_pool.allocated_bandwidth
        if required_network > available_network:
            conflicts.append(f"网络带宽不足: 需要{required_network:.1f}MB/s, 剩余{available_network:.1f}MB/s")
        
        # 4. 技能资源检查
        required_skills = requirements["skills"]
        skill_level = requirements["skill_level"]
        for skill in required_skills:
            if skill not in resource_pool.available_skills:
                conflicts.append(f"技能不足: 需要{skill}技能")
            elif skill_level > 0.7 and skill not in ["cve_research", "auth_testing"]:
                # 高技能要求任务需要特定高级技能
                conflicts.append(f"高级技能不足: {skill}需要高级水平")
        
        # 5. 工具许可证检查
        required_tools = requirements["tools"]
        for tool in required_tools:
            available_licenses = resource_pool.tool_licenses.get(tool, 0)
            allocated = resource_pool.allocated_tools.get(tool, 0)
            if allocated >= available_licenses:
                conflicts.append(f"工具许可证不足: {tool}已全部分配")
        
        # 判断是否可调度
        feasible = len(conflicts) == 0
        
        # 计算资源使用情况
        if feasible:
            resource_usage = {
                "time": task_duration,
                "computation": required_computation,
                "network": required_network,
                "skills": len(required_skills),
                "tools": required_tools,
            }
        else:
            resource_usage = {}
            
        return SchedulingResult(
            task=task,
            feasible=feasible,
            scheduling_time=current_time if feasible else None,
            required_delay=0.0,
            conflicts=conflicts,
            resource_usage=resource_usage
        )
    
    def allocate_resources(self, task: TestTask, 
                           resource_pool: ResourcePool,
                           start_time: float) -> Tuple[ResourcePool, Dict[str, float]]:
        """
        分配资源给指定任务
        
        Args:
            task: 测试任务
            resource_pool: 资源池
            start_time: 开始时间
            
        Returns:
            Tuple[ResourcePool, Dict[str, float]]: (更新后的资源池, 资源使用量)
        """
        # 先检查可行性
        result = self.check_task_feasibility(task, resource_pool, start_time)
        if not result.feasible:
            raise ValueError(f"任务{task.task_id}不可调度: {result.conflicts}")
        
        # 克隆资源池以避免修改原对象
        updated_pool = resource_pool.clone()
        requirements = self.resource_mapper.get_resource_requirements(task)
        
        # 分配时间资源
        task_duration = requirements["time_minutes"]
        updated_pool.allocated_time += task_duration
        
        # 分配计算资源
        required_computation = requirements["computation"]
        updated_pool.allocated_computation += required_computation
        
        # 分配网络资源
        required_network = requirements["network_mbps"]
        updated_pool.allocated_bandwidth += required_network
        
        # 分配工具许可证
        required_tools = requirements["tools"]
        for tool in required_tools:
            updated_pool.allocated_tools[tool] = updated_pool.allocated_tools.get(tool, 0) + 1
        
        # 记录资源使用量
        resource_usage = {
            "time_minutes": task_duration,
            "computation": required_computation,
            "network_mbps": required_network,
            "tools_count": len(required_tools),
        }
        
        return updated_pool, resource_usage
    
    def find_optimal_schedule(self, tasks: List[TestTask], 
                              resource_pool: ResourcePool,
                              prioritized_order: List[str] = None) -> List[Dict[str, Any]]:
        """
        寻找最优调度方案
        
        Args:
            tasks: 测试任务列表
            resource_pool: 资源池
            prioritized_order: 任务优先级顺序 (任务ID列表)
            
        Returns:
            List[Dict[str, Any]]: 调度方案列表
        """
        # 如果没有提供优先级顺序，按任务ID排序
        if prioritized_order is None:
            prioritized_order = [task.task_id for task in tasks]
        
        # 创建任务ID到任务的映射
        task_map = {task.task_id: task for task in tasks}
        
        # 当前资源池状态和调度结果
        current_pool = resource_pool.clone()
        current_time = 0.0
        schedule = []
        
        # 按优先级顺序尝试调度
        for task_id in prioritized_order:
            task = task_map.get(task_id)
            if not task:
                continue
            
            # 检查任务可行性
            result = self.check_task_feasibility(task, current_pool, current_time)
            
            if result.feasible:
                # 可以立即调度
                schedule_entry = {
                    "task_id": task.task_id,
                    "task_type": task.test_type.value,
                    "start_time": current_time,
                    "duration": task.time_cost_minutes,
                    "resource_usage": result.resource_usage,
                    "delayed": False,
                    "delay_reason": None,
                }
                
                # 分配资源
                current_pool, _ = self.allocate_resources(task, current_pool, current_time)
                current_time += task.time_cost_minutes
                
                schedule.append(schedule_entry)
            else:
                # 需要延迟调度
                # 简单策略：等待当前正在执行的任务完成
                delay_needed = 0.0
                delay_reason = result.conflicts[0] if result.conflicts else "资源冲突"
                
                # 实际实现中这里应该有更复杂的冲突解决策略
                # 这里简化为等待一定时间后重试
                delay_needed = 30.0  # 默认等待30分钟
                
                schedule_entry = {
                    "task_id": task.task_id,
                    "task_type": task.test_type.value,
                    "start_time": current_time + delay_needed,
                    "duration": task.time_cost_minutes,
                    "resource_usage": {},
                    "delayed": True,
                    "delay_reason": delay_reason,
                    "conflicts": result.conflicts,
                }
                
                # 在延迟后重新检查可行性
                # 这里简化处理，实际应该重新计算
                schedule.append(schedule_entry)
                current_time += delay_needed + task.time_cost_minutes
        
        return schedule
    
    def evaluate_schedule_quality(self, schedule: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        评估调度方案的质量
        
        Args:
            schedule: 调度方案
            
        Returns:
            Dict[str, float]: 质量评估指标
        """
        if not schedule:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_time": 0.0,
                "resource_utilization": 0.0,
                "delayed_tasks": 0,
                "quality_score": 0.0,
            }
        
        total_tasks = len(schedule)
        completed_tasks = sum(1 for s in schedule if not s.get("delayed", True))
        delayed_tasks = total_tasks - completed_tasks
        
        # 计算总耗时
        end_times = []
        for s in schedule:
            start = s.get("start_time", 0.0)
            duration = s.get("duration", 0.0)
            end_times.append(start + duration)
        
        total_time = max(end_times) if end_times else 0.0
        
        # 计算资源利用率 (简化版本)
        total_duration = sum(s.get("duration", 0.0) for s in schedule)
        if total_time > 0:
            time_utilization = total_duration / total_time
        else:
            time_utilization = 0.0
        
        # 计算质量分数 (越高越好)
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        time_efficiency = 1.0 / (1.0 + total_time / 100.0)  # 总时间越短分数越高
        
        quality_score = (
            completion_rate * 0.5 +
            time_efficiency * 0.3 +
            time_utilization * 0.2
        )
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "delayed_tasks": delayed_tasks,
            "total_time": total_time,
            "time_utilization": time_utilization,
            "completion_rate": completion_rate,
            "quality_score": min(quality_score * 100, 100.0),
        }


# ============================================
# 演示代码
# ============================================

def demo_resource_optimizer():
    """演示资源优化器的使用"""
    print("=" * 60)
    print("资源优化分配模型演示")
    print("=" * 60)
    
    from priority_engine import TestTask, TestType, ResourceConstraint
    
    # 1. 初始化优化器
    optimizer = ResourceOptimizer()
    print("✅ 资源优化器初始化成功")
    
    # 2. 创建示例任务
    print("\n📋 创建示例测试任务:")
    tasks = [
        TestTask(
            task_id="task_001",
            test_type=TestType.PORT_SCAN,
            target="http://example.com",
            time_cost_minutes=15.0,
            resource_intensity=0.3,
            skill_requirement=0.2,
            risk_score=75.0,
            expected_vulnerabilities=1.5,
            severity_weight=0.6,
            dependencies=[],
        ),
        TestTask(
            task_id="task_002",
            test_type=TestType.WEB_SCAN,
            target="http://example.com",
            time_cost_minutes=45.0,
            resource_intensity=0.6,
            skill_requirement=0.4,
            risk_score=65.0,
            expected_vulnerabilities=2.5,
            severity_weight=0.8,
            dependencies=["task_001"],
        ),
        TestTask(
            task_id="task_003",
            test_type=TestType.CVE_VERIFICATION,
            target="http://example.com",
            time_cost_minutes=60.0,  # 需要更多时间
            resource_intensity=0.7,
            skill_requirement=0.8,
            risk_score=85.0,
            expected_vulnerabilities=2.0,
            severity_weight=0.9,
            dependencies=["task_001", "task_002"],
        ),
    ]
    
    for task in tasks:
        print(f"  - {task.task_id}: {task.test_type.value} (耗时: {task.time_cost_minutes:.0f}分钟)")
    
    # 3. 创建资源约束
    constraint = ResourceConstraint(
        total_time_minutes=120.0,    # 2小时总时间
        max_concurrent_tests=2,      # 最多同时运行2个测试
        network_bandwidth_limit=10.0, # 10 MB/s网络带宽
    )
    
    # 4. 创建资源池
    resource_pool = optimizer.create_resource_pool(constraint)
    print(f"\n🔄 创建资源池: 总时间{resource_pool.total_time}分钟, 网络带宽{resource_pool.network_bandwidth}MB/s")
    
    # 5. 检查任务可行性
    print("\n🔍 检查任务可行性:")
    for task in tasks:
        result = optimizer.check_task_feasibility(task, resource_pool)
        status = "✅ 可调度" if result.feasible else "❌ 不可调度"
        print(f"  {task.task_id}: {status}", end="")
        if not result.feasible and result.conflicts:
            print(f" (原因: {result.conflicts[0]})")
        else:
            print()
    
    # 6. 寻找最优调度方案
    print("\n📅 寻找最优调度方案:")
    schedule = optimizer.find_optimal_schedule(tasks, resource_pool, ["task_001", "task_002", "task_003"])
    
    for i, entry in enumerate(schedule, 1):
        delayed_str = "延迟" if entry.get("delayed") else ""
        print(f"  {i}. {entry['task_id']}: 开始于{entry['start_time']:.1f}分钟, 持续{entry['duration']:.1f}分钟 {delayed_str}")
        if entry.get("delay_reason"):
            print(f"    延迟原因: {entry['delay_reason']}")
    
    # 7. 评估调度质量
    print("\n📊 调度质量评估:")
    quality = optimizer.evaluate_schedule_quality(schedule)
    for key, value in quality.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # 8. 演示资源分配
    print("\n💾 资源分配演示:")
    try:
        allocated_pool, usage = optimizer.allocate_resources(tasks[0], resource_pool, 0.0)
        print(f"  成功分配任务 {tasks[0].task_id} 的资源:")
        for resource, amount in usage.items():
            print(f"    {resource}: {amount:.2f}")
        print(f"  资源池状态更新: 已分配时间{allocated_pool.allocated_time:.1f}分钟")
    except ValueError as e:
        print(f"  ⚠️ 资源分配失败: {e}")
    
    print("\n" + "=" * 60)
    print("演示完成 ✅")
    print("=" * 60)


if __name__ == "__main__":
    # 运行演示代码
    demo_resource_optimizer()