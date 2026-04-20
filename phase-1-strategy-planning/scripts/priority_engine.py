#!/usr/bin/env python3
"""
优先级排序引擎 - Dynamic Planning Algorithm Phase 2

基于风险分数和测试成本，对测试任务进行优先级排序。
核心功能：计算每个测试任务的优先级分数，为动态规划提供决策基础。
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

# ============================================
# 数据结构定义
# ============================================

class TestType(Enum):
    """测试任务类型枚举"""
    PORT_SCAN = "port_scan"          # 端口扫描
    WEB_SCAN = "web_scan"            # Web应用扫描
    API_TEST = "api_test"            # API安全测试
    AUTH_TEST = "auth_test"          # 认证安全测试
    CONFIG_TEST = "config_test"      # 配置安全测试
    BUSINESS_LOGIC = "business_logic" # 业务逻辑测试
    CVE_VERIFICATION = "cve_verification" # CVE验证测试


@dataclass
class TestTask:
    """测试任务定义"""
    task_id: str                     # 任务唯一标识
    test_type: TestType              # 测试类型
    target: str                      # 测试目标 (URL/IP)
    
    # 成本相关属性
    time_cost_minutes: float         # 预计耗时 (分钟)
    resource_intensity: float        # 资源强度 (0-1, 1表示高资源需求)
    skill_requirement: float         # 技能要求 (0-1, 1表示需要高级技能)
    
    # 风险相关属性
    risk_score: float                # 关联的风险分数 (0-100)
    expected_vulnerabilities: float  # 预计漏洞发现数量 (期望值)
    severity_weight: float           # 漏洞严重程度权重 (基于CVSS)
    
    # 依赖关系
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID列表
    priority_score: float = 0.0      # 计算得到的优先级分数


@dataclass
class ResourceConstraint:
    """资源约束定义"""
    total_time_minutes: float        # 总测试时间限制 (分钟)
    max_concurrent_tests: int        # 最大并发测试数
    network_bandwidth_limit: float   # 网络带宽限制 (MB/s)
    skill_constraint: Optional[str] = None  # 技能约束 (可选)


@dataclass
class PriorityResult:
    """优先级排序结果"""
    task: TestTask
    priority_score: float
    justification: str               # 评分理由


# ============================================
# 优先级计算引擎
# ============================================

class PriorityEngine:
    """优先级排序引擎核心类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化优先级引擎
        
        Args:
            config: 配置参数，包含各项权重和参数
        """
        self.config = config or self.default_config()
        
    @staticmethod
    def default_config() -> Dict[str, Any]:
        """默认配置参数"""
        return {
            # 权重参数
            "risk_weight": 0.4,      # 风险分数权重
            "cost_weight": 0.3,      # 测试成本权重 (负向)
            "dependency_weight": 0.2, # 依赖关系权重
            "severity_weight": 0.1,   # 漏洞严重程度权重
            
            # 成本惩罚系数
            "time_penalty_factor": 0.01,  # 时间成本惩罚系数
            "resource_penalty_factor": 0.5, # 资源强度惩罚系数
            "skill_penalty_factor": 0.3,   # 技能要求惩罚系数
            
            # 其他参数
            "dependency_boost": 1.2,  # 依赖任务完成后的增益
            "min_priority_score": 0.01, # 最小优先级分数
        }
    
    def calculate_priority_score(self, task: TestTask, 
                                 completed_tasks: List[str] = None) -> float:
        """
        计算单个测试任务的优先级分数
        
        Args:
            task: 测试任务对象
            completed_tasks: 已完成的测试任务ID列表
            
        Returns:
            float: 优先级分数 (越高表示优先级越高)
        """
        # 确保已完成任务列表不为None
        completed_tasks = completed_tasks or []
        
        # 1. 风险得分 (正向影响)
        risk_component = task.risk_score * self.config["risk_weight"]
        
        # 2. 漏洞期望得分 (正向影响)
        vulnerability_component = (
            task.expected_vulnerabilities * 
            task.severity_weight * 
            self.config["severity_weight"]
        )
        
        # 3. 成本惩罚 (负向影响)
        time_penalty = task.time_cost_minutes * self.config["time_penalty_factor"]
        resource_penalty = task.resource_intensity * self.config["resource_penalty_factor"]
        skill_penalty = task.skill_requirement * self.config["skill_penalty_factor"]
        cost_penalty = (time_penalty + resource_penalty + skill_penalty) * self.config["cost_weight"]
        
        # 4. 依赖关系处理
        dependency_factor = 1.0
        if task.dependencies:
            # 检查是否所有依赖任务都已完成
            deps_completed = all(dep in completed_tasks for dep in task.dependencies)
            if deps_completed:
                # 所有依赖已完成，给予一定的增益
                dependency_factor = self.config["dependency_boost"]
            else:
                # 依赖未完成，大幅降低优先级
                dependency_factor = 0.1
        
        dependency_component = dependency_factor * self.config["dependency_weight"]
        
        # 5. 计算总分
        base_score = risk_component + vulnerability_component - cost_penalty
        total_score = base_score * dependency_component
        
        # 确保分数不为负
        return max(total_score, self.config["min_priority_score"])
    
    def prioritize_tasks(self, tasks: List[TestTask], 
                         completed_tasks: List[str] = None) -> List[PriorityResult]:
        """
        对测试任务列表进行优先级排序
        
        Args:
            tasks: 测试任务列表
            completed_tasks: 已完成的测试任务ID列表
            
        Returns:
            List[PriorityResult]: 按优先级排序的结果列表
        """
        completed_tasks = completed_tasks or []
        
        # 计算每个任务的优先级分数
        results = []
        for task in tasks:
            score = self.calculate_priority_score(task, completed_tasks)
            
            # 生成评分理由
            justification = self._generate_justification(task, score, completed_tasks)
            
            results.append(PriorityResult(
                task=task,
                priority_score=score,
                justification=justification
            ))
        
        # 按优先级分数降序排序
        results.sort(key=lambda x: x.priority_score, reverse=True)
        
        return results
    
    def _generate_justification(self, task: TestTask, score: float, 
                                completed_tasks: List[str]) -> str:
        """生成优先级评分理由"""
        justifications = []
        
        # 风险相关理由
        if task.risk_score > 50:
            justifications.append(f"高风险({task.risk_score:.1f}分)")
        elif task.risk_score > 30:
            justifications.append(f"中风险({task.risk_score:.1f}分)")
        
        # 漏洞期望相关理由
        if task.expected_vulnerabilities > 2:
            justifications.append(f"预计发现{task.expected_vulnerabilities:.1f}个漏洞")
        elif task.expected_vulnerabilities > 0.5:
            justifications.append(f"可能发现漏洞")
        
        # 成本相关理由
        if task.time_cost_minutes > 60:
            justifications.append(f"耗时较长({task.time_cost_minutes:.0f}分钟)")
        elif task.time_cost_minutes < 10:
            justifications.append(f"快速测试({task.time_cost_minutes:.0f}分钟)")
        
        # 依赖关系理由
        if task.dependencies:
            deps_completed = all(dep in completed_tasks for dep in task.dependencies)
            if deps_completed:
                justifications.append("依赖任务已完成")
            else:
                justifications.append(f"等待{len(task.dependencies)}个依赖任务")
        
        # 测试类型理由
        type_str = task.test_type.value.replace("_", " ").title()
        justifications.append(type_str)
        
        # 组合所有理由
        if justifications:
            return " | ".join(justifications)
        else:
            return "常规测试任务"
    
    def create_tasks_from_risk_report(self, risk_report_path: str) -> List[TestTask]:
        """
        从风险报告生成测试任务列表
        
        Args:
            risk_report_path: 风险报告JSON文件路径
            
        Returns:
            List[TestTask]: 生成的测试任务列表
        """
        try:
            with open(risk_report_path, 'r') as f:
                risk_data = json.load(f)
        except Exception as e:
            print(f"读取风险报告失败: {e}")
            return []
        
        # 简化版本：基于风险分数生成示例测试任务
        tasks = []
        
        # 读取总体风险分数
        overall_score = risk_data.get("risk_summary", {}).get("overall_score", 30.0)
        
        # 基于技术栈风险生成CVE验证任务
        tech_risk = risk_data.get("risk_summary", {}).get("tech_risk", 0.0)
        if tech_risk > 20:
            tasks.append(self._create_cve_verification_task(
                target=risk_data.get("report_metadata", {}).get("asset_url", "unknown"),
                risk_score=tech_risk,
                tech_count=len(risk_data.get("asset_overview", {}).get("technologies", []))
            ))
        
        # 基于暴露面风险生成端口扫描任务
        exposure_risk = risk_data.get("risk_summary", {}).get("exposure_risk", 0.0)
        if exposure_risk > 10:
            tasks.append(self._create_port_scan_task(
                target=risk_data.get("report_metadata", {}).get("asset_url", "unknown"),
                risk_score=exposure_risk
            ))
        
        # 基于配置风险生成配置检查任务
        config_risk = risk_data.get("risk_summary", {}).get("config_risk", 0.0)
        if config_risk > 15:
            tasks.append(self._create_config_test_task(
                target=risk_data.get("report_metadata", {}).get("asset_url", "unknown"),
                risk_score=config_risk
            ))
        
        # 始终生成Web扫描任务（基础任务）
        tasks.append(self._create_web_scan_task(
            target=risk_data.get("report_metadata", {}).get("asset_url", "unknown"),
            risk_score=overall_score
        ))
        
        return tasks
    
    def _create_port_scan_task(self, target: str, risk_score: float) -> TestTask:
        """创建端口扫描任务"""
        return TestTask(
            task_id=f"port_scan_{hash(target) % 1000:04d}",
            test_type=TestType.PORT_SCAN,
            target=target,
            time_cost_minutes=15.0,
            resource_intensity=0.3,
            skill_requirement=0.2,
            risk_score=risk_score,
            expected_vulnerabilities=risk_score / 50.0,  # 根据风险分数估算
            severity_weight=0.6,
            dependencies=[],  # 端口扫描无依赖
        )
    
    def _create_web_scan_task(self, target: str, risk_score: float) -> TestTask:
        """创建Web扫描任务"""
        return TestTask(
            task_id=f"web_scan_{hash(target) % 1000:04d}",
            test_type=TestType.WEB_SCAN,
            target=target,
            time_cost_minutes=45.0,
            resource_intensity=0.6,
            skill_requirement=0.4,
            risk_score=risk_score,
            expected_vulnerabilities=risk_score / 30.0,  # 根据风险分数估算
            severity_weight=0.8,
            dependencies=["port_scan"],  # 依赖端口扫描结果
        )
    
    def _create_cve_verification_task(self, target: str, risk_score: float, tech_count: int) -> TestTask:
        """创建CVE验证任务"""
        return TestTask(
            task_id=f"cve_verify_{hash(target) % 1000:04d}",
            test_type=TestType.CVE_VERIFICATION,
            target=target,
            time_cost_minutes=30.0 * tech_count,  # 每个技术栈约30分钟
            resource_intensity=0.4,
            skill_requirement=0.7,
            risk_score=risk_score,
            expected_vulnerabilities=tech_count * 0.5,  # 每个技术栈预计0.5个漏洞
            severity_weight=0.9,
            dependencies=["port_scan", "web_scan"],  # 依赖基础扫描
        )
    
    def _create_config_test_task(self, target: str, risk_score: float) -> TestTask:
        """创建配置检查任务"""
        return TestTask(
            task_id=f"config_test_{hash(target) % 1000:04d}",
            test_type=TestType.CONFIG_TEST,
            target=target,
            time_cost_minutes=25.0,
            resource_intensity=0.3,
            skill_requirement=0.5,
            risk_score=risk_score,
            expected_vulnerabilities=risk_score / 40.0,
            severity_weight=0.7,
            dependencies=["port_scan"],  # 依赖端口扫描
        )


# ============================================
# 工具函数和演示代码
# ============================================

def demo_priority_engine():
    """演示优先级引擎的使用"""
    print("=" * 60)
    print("优先级排序引擎演示")
    print("=" * 60)
    
    # 1. 初始化引擎
    engine = PriorityEngine()
    print("✅ 优先级引擎初始化成功")
    
    # 2. 创建示例测试任务
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
            dependencies=["task_001"],  # 依赖端口扫描
        ),
        TestTask(
            task_id="task_003",
            test_type=TestType.CVE_VERIFICATION,
            target="http://example.com",
            time_cost_minutes=30.0,
            resource_intensity=0.4,
            skill_requirement=0.7,
            risk_score=80.0,
            expected_vulnerabilities=1.2,
            severity_weight=0.9,
            dependencies=["task_001", "task_002"],  # 依赖前两个任务
        ),
    ]
    
    for task in tasks:
        print(f"  - {task.task_id}: {task.test_type.value} (风险: {task.risk_score:.1f})")
    
    # 3. 初始优先级排序 (无已完成任务)
    print("\n🎯 初始优先级排序 (无已完成任务):")
    results = engine.prioritize_tasks(tasks, completed_tasks=[])
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result.task.task_id:10s} | 分数: {result.priority_score:6.2f} | 理由: {result.justification}")
    
    # 4. 模拟任务完成后的重新排序
    print("\n🔄 模拟task_001完成后的重新排序:")
    results = engine.prioritize_tasks(tasks, completed_tasks=["task_001"])
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result.task.task_id:10s} | 分数: {result.priority_score:6.2f} | 理由: {result.justification}")
    
    # 5. 从风险报告创建任务
    print("\n📊 从风险报告创建测试任务:")
    try:
        # 尝试从assets目录加载风险报告
        risk_report_path = "../assets/risk_report.json"
        risk_tasks = engine.create_tasks_from_risk_report(risk_report_path)
        print(f"  从{risk_report_path}创建了{len(risk_tasks)}个任务")
        
        if risk_tasks:
            results = engine.prioritize_tasks(risk_tasks)
            print("  优先级排序结果:")
            for i, result in enumerate(results[:3], 1):
                print(f"    {i}. {result.task.task_id:20s} | 分数: {result.priority_score:6.2f}")
    except Exception as e:
        print(f"  ⚠️ 风险报告任务创建失败: {e}")
    
    print("\n" + "=" * 60)
    print("演示完成 ✅")
    print("=" * 60)


if __name__ == "__main__":
    # 运行演示代码
    demo_priority_engine()