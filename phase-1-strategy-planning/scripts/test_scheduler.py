#!/usr/bin/env python3
"""
测试任务调度器 - Dynamic Planning Algorithm Phase 2

整合优先级排序引擎和资源优化器，生成完整的测试计划。
核心功能：任务规划、调度生成、计划优化、输出格式化。
"""

import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 导入依赖模块
from priority_engine import (
    TestTask, ResourceConstraint, PriorityEngine, 
    TestType, PriorityResult
)
from resource_optimizer import (
    ResourceOptimizer, ResourcePool, SchedulingResult,
    ResourceConstraint as RC  # 别名避免冲突
)


# ============================================
# 数据结构定义
# ============================================

@dataclass
class ScheduledTask:
    """已调度的测试任务"""
    task: TestTask
    start_time: float          # 开始时间 (从0开始的分钟数)
    end_time: float            # 结束时间
    resource_usage: Dict[str, float]  # 资源使用情况
    dependencies_satisfied: bool  # 依赖是否满足
    delayed_reason: Optional[str] = None  # 延迟原因（如果有）


@dataclass
class TestPlan:
    """完整的测试计划"""
    plan_id: str
    generated_at: str
    target: str
    total_duration: float      # 总耗时 (分钟)
    total_tasks: int           # 总任务数
    scheduled_tasks: List[ScheduledTask]  # 已调度任务
    resource_constraints: ResourceConstraint  # 资源约束
    quality_metrics: Dict[str, float]  # 质量指标
    execution_order: List[str]  # 执行顺序 (任务ID列表)


@dataclass 
class SchedulingOptions:
    """调度选项"""
    planning_horizon: float = 240.0  # 计划时间范围 (分钟)
    allow_task_splitting: bool = False  # 是否允许任务拆分
    max_retry_attempts: int = 3      # 最大重试次数
    reserve_buffer_time: float = 30.0  # 预留缓冲时间 (分钟)
    optimize_for_time: bool = True   # 优化目标：时间 vs 覆盖率


# ============================================
# 测试任务调度器
# ============================================

class TestScheduler:
    """测试任务调度器核心类"""
    
    def __init__(self, options: Optional[SchedulingOptions] = None):
        """
        初始化调度器
        
        Args:
            options: 调度选项
        """
        self.options = options or SchedulingOptions()
        self.priority_engine = PriorityEngine()
        self.resource_optimizer = ResourceOptimizer()
        
    def create_test_plan(self, 
                         tasks: List[TestTask],
                         constraint: ResourceConstraint,
                         target: str = "unknown") -> TestPlan:
        """
        创建完整的测试计划
        
        Args:
            tasks: 测试任务列表
            constraint: 资源约束
            target: 测试目标
            
        Returns:
            TestPlan: 完整的测试计划
        """
        plan_id = f"plan_{int(time.time())}_{hash(target) % 1000:04d}"
        
        print(f"📋 开始创建测试计划 {plan_id}...")
        print(f"  目标: {target}")
        print(f"  任务数: {len(tasks)}")
        print(f"  资源约束: {constraint.total_time_minutes}分钟总时间, {constraint.max_concurrent_tests}并发")
        
        # 1. 优先级排序
        print("\n🔢 步骤1: 优先级排序...")
        priority_results = self.priority_engine.prioritize_tasks(tasks)
        prioritized_order = [result.task.task_id for result in priority_results]
        
        print(f"  优先级排序完成，前3个任务:")
        for i, result in enumerate(priority_results[:3], 1):
            print(f"    {i}. {result.task.task_id} - 分数: {result.priority_score:.2f} - {result.justification}")
        
        # 2. 资源调度
        print("\n🔄 步骤2: 资源调度...")
        resource_pool = self.resource_optimizer.create_resource_pool(constraint)
        schedule = self.resource_optimizer.find_optimal_schedule(
            tasks, resource_pool, prioritized_order
        )
        
        # 3. 创建已调度任务列表
        print("\n📅 步骤3: 创建调度表...")
        scheduled_tasks = []
        task_map = {task.task_id: task for task in tasks}
        execution_order = []
        
        for schedule_entry in schedule:
            task_id = schedule_entry["task_id"]
            task = task_map.get(task_id)
            
            if not task:
                continue
                
            scheduled_task = ScheduledTask(
                task=task,
                start_time=schedule_entry.get("start_time", 0.0),
                end_time=schedule_entry.get("start_time", 0.0) + schedule_entry.get("duration", 0.0),
                resource_usage=schedule_entry.get("resource_usage", {}),
                dependencies_satisfied=self._check_dependencies(
                    task, [st.task.task_id for st in scheduled_tasks]
                ),
                delayed_reason=schedule_entry.get("delay_reason") if schedule_entry.get("delayed") else None,
            )
            
            scheduled_tasks.append(scheduled_task)
            execution_order.append(task_id)
        
        # 4. 计算总耗时和质量指标
        print("\n📊 步骤4: 计算质量指标...")
        total_duration = 0.0
        if scheduled_tasks:
            total_duration = max(task.end_time for task in scheduled_tasks)
        
        quality_metrics = self.resource_optimizer.evaluate_schedule_quality([
            {
                "task_id": t.task.task_id,
                "start_time": t.start_time,
                "duration": t.end_time - t.start_time,
                "delayed": t.delayed_reason is not None,
            }
            for t in scheduled_tasks
        ])
        
        # 5. 创建测试计划
        test_plan = TestPlan(
            plan_id=plan_id,
            generated_at=datetime.now().isoformat(),
            target=target,
            total_duration=total_duration,
            total_tasks=len(tasks),
            scheduled_tasks=scheduled_tasks,
            resource_constraints=constraint,
            quality_metrics=quality_metrics,
            execution_order=execution_order,
        )
        
        print(f"\n✅ 测试计划创建完成!")
        print(f"  计划ID: {plan_id}")
        print(f"  总耗时: {total_duration:.1f}分钟")
        print(f"  质量分数: {quality_metrics.get('quality_score', 0):.1f}/100")
        print(f"  任务完成率: {quality_metrics.get('completion_rate', 0)*100:.1f}%")
        
        return test_plan
    
    def _check_dependencies(self, task: TestTask, completed_tasks: List[str]) -> bool:
        """检查任务依赖是否满足"""
        if not task.dependencies:
            return True
        
        return all(dep in completed_tasks for dep in task.dependencies)
    
    def export_plan_to_markdown(self, plan: TestPlan, output_path: str) -> str:
        """
        将测试计划导出为Markdown格式
        
        Args:
            plan: 测试计划
            output_path: 输出文件路径
            
        Returns:
            str: 生成的Markdown内容
        """
        md_content = []
        
        # 头部信息
        md_content.append(f"# 🧪 智能渗透测试计划")
        md_content.append(f"")
        md_content.append(f"**计划ID**: `{plan.plan_id}`  ")
        md_content.append(f"**生成时间**: {plan.generated_at}  ")
        md_content.append(f"**测试目标**: `{plan.target}`  ")
        md_content.append(f"")
        
        # 执行摘要
        md_content.append(f"## 📋 执行摘要")
        md_content.append(f"")
        md_content.append(f"- **总任务数**: {plan.total_tasks}个测试任务")
        md_content.append(f"- **预计总耗时**: {plan.total_duration:.1f}分钟 ({plan.total_duration/60:.1f}小时)")
        md_content.append(f"- **计划质量**: {plan.quality_metrics.get('quality_score', 0):.1f}/100分")
        md_content.append(f"- **任务完成率**: {plan.quality_metrics.get('completion_rate', 0)*100:.1f}%")
        md_content.append(f"- **资源利用率**: {plan.quality_metrics.get('time_utilization', 0)*100:.1f}%")
        md_content.append(f"")
        
        # 资源约束
        md_content.append(f"## 🔧 资源约束条件")
        md_content.append(f"")
        md_content.append(f"| 资源类型 | 约束值 |")
        md_content.append(f"|---------|--------|")
        md_content.append(f"| 总时间 | {plan.resource_constraints.total_time_minutes:.0f}分钟 |")
        md_content.append(f"| 最大并发测试数 | {plan.resource_constraints.max_concurrent_tests}个 |")
        md_content.append(f"| 网络带宽限制 | {plan.resource_constraints.network_bandwidth_limit:.1f} MB/s |")
        md_content.append(f"")
        
        # 调度时间表 (甘特图风格)
        md_content.append(f"## 🕒 调度时间表")
        md_content.append(f"")
        md_content.append(f"| 任务ID | 任务类型 | 开始时间 | 结束时间 | 持续时间 | 依赖状态 | 备注 |")
        md_content.append(f"|--------|----------|----------|----------|----------|----------|------|")
        
        for scheduled_task in plan.scheduled_tasks:
            task = scheduled_task.task
            
            # 时间格式化
            start_str = f"{scheduled_task.start_time:.0f}分钟"
            end_str = f"{scheduled_task.end_time:.0f}分钟"
            duration_str = f"{scheduled_task.end_time - scheduled_task.start_time:.0f}分钟"
            
            # 依赖状态
            if task.dependencies:
                if scheduled_task.dependencies_satisfied:
                    deps_str = f"✅ 依赖已满足 ({len(task.dependencies)}个)"
                else:
                    deps_str = f"⚠️ 等待依赖 ({len(task.dependencies)}个)"
            else:
                deps_str = "无依赖"
            
            # 备注
            notes = []
            if scheduled_task.delayed_reason:
                notes.append(f"延迟: {scheduled_task.delayed_reason}")
            
            if task.risk_score > 70:
                notes.append(f"高风险({task.risk_score:.0f})")
            elif task.risk_score > 40:
                notes.append(f"中风险({task.risk_score:.0f})")
            
            notes_str = " | ".join(notes) if notes else "-"
            
            md_content.append(f"| `{task.task_id}` | {task.test_type.value} | {start_str} | {end_str} | {duration_str} | {deps_str} | {notes_str} |")
        
        md_content.append(f"")
        
        # 详细任务信息
        md_content.append(f"## 📝 详细任务信息")
        md_content.append(f"")
        
        for i, scheduled_task in enumerate(plan.scheduled_tasks, 1):
            task = scheduled_task.task
            
            md_content.append(f"### {i}. {task.task_id} - {task.test_type.value}")
            md_content.append(f"")
            md_content.append(f"- **目标**: `{task.target}`")
            md_content.append(f"- **调度时间**: {scheduled_task.start_time:.0f} - {scheduled_task.end_time:.0f}分钟")
            md_content.append(f"- **风险分数**: {task.risk_score:.1f}/100")
            md_content.append(f"- **预计漏洞数**: {task.expected_vulnerabilities:.1f}个")
            md_content.append(f"- **漏洞严重程度**: {task.severity_weight:.2f}")
            md_content.append(f"- **任务成本**: {task.time_cost_minutes:.0f}分钟")
            md_content.append(f"- **资源强度**: {task.resource_intensity:.2f}")
            md_content.append(f"- **技能要求**: {task.skill_requirement:.2f}")
            
            if task.dependencies:
                md_content.append(f"- **依赖任务**: {', '.join([f'`{dep}`' for dep in task.dependencies])}")
            
            if scheduled_task.delayed_reason:
                md_content.append(f"- **⏰ 延迟原因**: {scheduled_task.delayed_reason}")
            
            if scheduled_task.resource_usage:
                # 处理资源使用信息，支持不同类型（数字、列表等）
                resource_items = []
                for k, v in scheduled_task.resource_usage.items():
                    if isinstance(v, list):
                        resource_items.append(f"{k}: {len(v)}个")
                    elif isinstance(v, (int, float)):
                        resource_items.append(f"{k}: {v:.1f}")
                    else:
                        resource_items.append(f"{k}: {v}")
                md_content.append(f"- **资源使用**: {', '.join(resource_items)}")
            
            md_content.append(f"")
        
        # 风险评估与建议
        md_content.append(f"## ⚠️ 风险评估与建议")
        md_content.append(f"")
        
        # 按风险排序
        high_risk_tasks = [st for st in plan.scheduled_tasks if st.task.risk_score > 70]
        medium_risk_tasks = [st for st in plan.scheduled_tasks if st.task.risk_score > 40 and st.task.risk_score <= 70]
        
        if high_risk_tasks:
            md_content.append(f"### 🔴 高风险任务 ({len(high_risk_tasks)}个)")
            md_content.append(f"")
            for task in high_risk_tasks[:3]:  # 最多显示3个
                md_content.append(f"- **{task.task.task_id}** (风险: {task.task.risk_score:.1f}): {task.task.test_type.value}")
                md_content.append(f"  - 建议优先执行，预计发现{task.task.expected_vulnerabilities:.1f}个漏洞")
                md_content.append(f"  - 调度时间: {task.start_time:.0f}分钟开始")
                if task.task.time_cost_minutes > 60:
                    md_content.append(f"  - ⏱️ 注意：此任务耗时较长 ({task.task.time_cost_minutes:.0f}分钟)")
            md_content.append(f"")
        
        if medium_risk_tasks:
            md_content.append(f"### 🟡 中风险任务 ({len(medium_risk_tasks)}个)")
            md_content.append(f"")
            for task in medium_risk_tasks[:3]:
                md_content.append(f"- **{task.task.task_id}** (风险: {task.task.risk_score:.1f}): {task.task.test_type.value}")
                md_content.append(f"  - 建议按计划执行")
            md_content.append(f"")
        
        # 执行建议
        md_content.append(f"## 🎯 执行建议")
        md_content.append(f"")
        md_content.append(f"1. **建议执行顺序**: 按调度时间表顺序执行，注意任务依赖关系")
        md_content.append(f"2. **风险应对**: 高风险任务需重点关注，建议安排经验丰富的测试人员")
        md_content.append(f"3. **资源监控**: 注意网络带宽和工具许可证使用情况，避免资源冲突")
        md_content.append(f"4. **时间管理**: 总计划时间{plan.total_duration:.0f}分钟，建议预留{plan.resource_constraints.total_time_minutes - plan.total_duration:.0f}分钟缓冲时间")
        md_content.append(f"5. **质量保证**: 关注计划质量指标，如完成率低于80%可考虑调整资源约束")
        md_content.append(f"")
        
        # 脚注
        md_content.append(f"---")
        md_content.append(f"")
        md_content.append(f"*本计划由智能测试规划引擎生成，基于风险评估和资源优化算法。*  ")
        md_content.append(f"*生成时间: {plan.generated_at}*  ")
        md_content.append(f"*引擎版本: Dynamic Planning Algorithm v1.0*")
        
        # 合并所有内容
        full_md = "\n".join(md_content)
        
        # 写入文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_md)
            print(f"📄 测试计划已导出到: {output_path}")
        except Exception as e:
            print(f"⚠️ 导出测试计划失败: {e}")
        
        return full_md
    
    def generate_sample_plan(self, risk_report_path: str, 
                             constraint: ResourceConstraint) -> TestPlan:
        """
        基于风险报告生成示例测试计划
        
        Args:
            risk_report_path: 风险报告路径
            constraint: 资源约束
            
        Returns:
            TestPlan: 生成的测试计划
        """
        print(f"\n🎯 基于风险报告生成示例测试计划...")
        print(f"  风险报告: {risk_report_path}")
        
        # 从风险报告创建任务
        tasks = self.priority_engine.create_tasks_from_risk_report(risk_report_path)
        
        if not tasks:
            # 如果无法从风险报告创建任务，使用默认示例任务
            print(f"  ⚠️ 无法从风险报告创建任务，使用示例任务")
            tasks = self._create_sample_tasks()
        
        # 设置测试目标
        target = "unknown"
        try:
            with open(risk_report_path, 'r') as f:
                risk_data = json.load(f)
                target = risk_data.get("report_metadata", {}).get("asset_url", "unknown")
        except:
            pass
        
        # 创建测试计划
        return self.create_test_plan(tasks, constraint, target)
    
    def _create_sample_tasks(self) -> List[TestTask]:
        """创建示例测试任务"""
        from priority_engine import TestType
        
        return [
            TestTask(
                task_id="port_scan_001",
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
                task_id="web_scan_002",
                test_type=TestType.WEB_SCAN,
                target="http://example.com",
                time_cost_minutes=45.0,
                resource_intensity=0.6,
                skill_requirement=0.4,
                risk_score=65.0,
                expected_vulnerabilities=2.5,
                severity_weight=0.8,
                dependencies=["port_scan_001"],
            ),
            TestTask(
                task_id="cve_verify_003",
                test_type=TestType.CVE_VERIFICATION,
                target="http://example.com",
                time_cost_minutes=30.0,
                resource_intensity=0.4,
                skill_requirement=0.7,
                risk_score=80.0,
                expected_vulnerabilities=1.2,
                severity_weight=0.9,
                dependencies=["port_scan_001", "web_scan_002"],
            ),
            TestTask(
                task_id="config_test_004",
                test_type=TestType.CONFIG_TEST,
                target="http://example.com",
                time_cost_minutes=25.0,
                resource_intensity=0.3,
                skill_requirement=0.5,
                risk_score=55.0,
                expected_vulnerabilities=1.0,
                severity_weight=0.7,
                dependencies=["port_scan_001"],
            ),
        ]


# ============================================
# 演示代码
# ============================================

def demo_test_scheduler():
    """演示测试调度器的使用"""
    print("=" * 60)
    print("测试任务调度器演示")
    print("=" * 60)
    
    # 1. 初始化调度器
    scheduler = TestScheduler()
    print("✅ 测试调度器初始化成功")
    
    # 2. 创建资源约束
    constraint = ResourceConstraint(
        total_time_minutes=180.0,    # 3小时总时间
        max_concurrent_tests=2,      # 最多同时运行2个测试
        network_bandwidth_limit=5.0, # 5 MB/s网络带宽
    )
    
    # 3. 生成示例测试计划
    print("\n🎯 生成示例测试计划...")
    risk_report_path = "../assets/risk_report.json"
    
    try:
        plan = scheduler.generate_sample_plan(risk_report_path, constraint)
        
        # 4. 导出测试计划
        print("\n📄 导出测试计划...")
        output_path = "../deliverables/sample_test_plan.md"
        md_content = scheduler.export_plan_to_markdown(plan, output_path)
        
        # 5. 显示计划摘要
        print("\n📋 计划摘要:")
        print(f"  计划ID: {plan.plan_id}")
        print(f"  目标: {plan.target}")
        print(f"  总任务数: {plan.total_tasks}")
        print(f"  预计总耗时: {plan.total_duration:.1f}分钟")
        print(f"  质量分数: {plan.quality_metrics.get('quality_score', 0):.1f}/100")
        
        # 6. 显示调度时间表
        print("\n🕒 调度时间表 (前3个任务):")
        for i, scheduled_task in enumerate(plan.scheduled_tasks[:3], 1):
            task = scheduled_task.task
            delayed = " ⏰延迟" if scheduled_task.delayed_reason else ""
            print(f"  {i}. {task.task_id}: {task.test_type.value} - {scheduled_task.start_time:.0f}分钟开始{delayed}")
            if scheduled_task.delayed_reason:
                print(f"     延迟原因: {scheduled_task.delayed_reason}")
        
        print(f"\n📁 完整计划已保存到: {output_path}")
        
    except Exception as e:
        print(f"\n⚠️ 生成测试计划失败: {e}")
        print("正在使用纯示例任务生成计划...")
        
        # 使用纯示例任务
        from priority_engine import TestType
        tasks = [
            TestTask(
                task_id="port_scan_001",
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
                task_id="web_scan_002",
                test_type=TestType.WEB_SCAN,
                target="http://example.com",
                time_cost_minutes=45.0,
                resource_intensity=0.6,
                skill_requirement=0.4,
                risk_score=65.0,
                expected_vulnerabilities=2.5,
                severity_weight=0.8,
                dependencies=["port_scan_001"],
            ),
        ]
        
        plan = scheduler.create_test_plan(tasks, constraint, "http://example.com")
        output_path = "../deliverables/sample_test_plan.md"
        scheduler.export_plan_to_markdown(plan, output_path)
        print(f"📁 示例计划已保存到: {output_path}")
    
    print("\n" + "=" * 60)
    print("演示完成 ✅")
    print("=" * 60)


if __name__ == "__main__":
    # 运行演示代码
    demo_test_scheduler()