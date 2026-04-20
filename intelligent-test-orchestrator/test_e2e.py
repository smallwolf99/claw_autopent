#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试 - 完整智能测试编排流程

测试场景：
1. 用户提供测试目标
2. Phase-0: 资产收集（模拟）
3. Phase-1: 风险画像（真实）
4. Phase-2: 测试策略生成（真实）
5. Phase-3: 漏洞验证（模拟）
6. Phase-4: 报告生成（模拟）
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config import TestMode, ReportFormat
from core.risk_profiler import RiskProfiler
from core.test_strategist import TestStrategist
from core.rule_engine import RuleEngine


def print_section(title: str, emoji: str = "📋"):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {emoji} {title}")
    print(f"{'='*70}\n")


def print_step(step: int, title: str):
    """打印步骤标题"""
    print(f"\n{'─'*70}")
    print(f"  步骤 {step}: {title}")
    print(f"{'─'*70}\n")


async def test_end_to_end():
    """执行端到端测试"""
    
    # =========================================
    # 初始化
    # =========================================
    print_section("智能测试编排器 - 端到端测试", "🚀")
    
    test_target = "http://example-test.com"
    test_mode = TestMode.FULL
    
    print(f"🎯 测试目标：{test_target}")
    print(f"📊 测试模式：{test_mode.value}")
    print(f"⏰ 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # =========================================
    # Phase 0: 资产收集
    # =========================================
    print_step(1, "Phase-0: 资产收集")
    
    print("📡 正在收集资产信息...")
    await asyncio.sleep(0.5)  # 模拟收集时间
    
    # 模拟资产数据
    assets = [
        {
            "url": test_target,
            "technologies": [
                {"name": "Apache Tomcat", "version": "7.0.70", "confidence": 0.9},
                {"name": "Spring Framework", "version": "4.3.0", "confidence": 0.8},
                {"name": "MySQL", "version": "5.7.20", "confidence": 0.7}
            ],
            "endpoints": [
                {"path": "/admin", "methods": ["GET", "POST"], "auth_required": False},
                {"path": "/api/v1/users", "methods": ["GET", "POST", "PUT", "DELETE"], "auth_required": True},
                {"path": "/api/v1/data", "methods": ["GET"], "auth_required": True}
            ],
            "business_hints": {
                "type": "enterprise",
                "industry": "technology"
            },
            "metadata": {
                "ip": "192.168.1.100",
                "port": 8080,
                "protocol": "https"
            }
        }
    ]
    
    print(f"✅ 资产收集完成")
    print(f"  • 发现资产数：{len(assets)}")
    print(f"  • 技术栈：{', '.join([t['name'] for t in assets[0]['technologies']])}")
    print(f"  • 端点数：{len(assets[0]['endpoints'])}")
    
    # =========================================
    # Phase 1: 风险画像
    # =========================================
    print_step(2, "Phase-1: 风险画像评估")
    
    print("🧠 正在分析资产风险...")
    
    profiler = RiskProfiler()
    risk_report = profiler.assess(assets)
    
    print(f"✅ 风险评估完成")
    print(f"  • 总体风险分：{risk_report['overall_score']}/100")
    print(f"  • 风险等级：{risk_report['risk_level']}")
    print(f"  • 评估资产数：{risk_report['assets_assessed']}")
    print(f"  • 高风险资产：{len(risk_report['high_risk_assets'])}")
    print(f"  • 中风险资产：{len(risk_report['medium_risk_assets'])}")
    print(f"  • 低风险资产：{len(risk_report['low_risk_assets'])}")
    
    # =========================================
    # Phase 2: 测试策略生成
    # =========================================
    print_step(3, "Phase-2: 测试策略生成")
    
    print("📋 正在生成测试策略...")
    
    strategist = TestStrategist()
    strategy = strategist.generate_strategy(assets, risk_report)
    
    print(f"✅ 测试策略生成完成")
    print(f"  • 目标：{strategy.target}")
    print(f"  • 测试动作总数：{strategy.total_actions}")
    print(f"  • 预计执行时间：{strategy.get_total_time()}分钟")
    
    # 按优先级统计
    priorities = {}
    for action in strategy.actions:
        p = action.priority.value
        priorities[p] = priorities.get(p, 0) + 1
    
    print(f"\n📊 优先级分布:")
    for priority, count in sorted(priorities.items(), key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0]) if x[0] in ['critical', 'high', 'medium', 'low'] else 99):
        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
        print(f"  {emoji} {priority.upper()}: {count}个测试")
    
    # 显示详细测试动作
    print(f"\n📝 测试动作列表:")
    for i, action in enumerate(strategy.actions, 1):
        print(f"  {i:2d}. [{action.priority.value.upper():8s}] {action.name}")
        print(f"       {action.description}")
        if hasattr(action, 'command') and action.command:
            print(f"       命令：{action.command[:60]}...")
        print()
    
    # =========================================
    # Phase 3: 漏洞验证（模拟）
    # =========================================
    print_step(4, "Phase-3: 漏洞验证")
    
    print("🔬 正在验证漏洞...")
    await asyncio.sleep(0.3)
    
    # 模拟验证结果
    verified_vulns = [
        {
            "id": "VULN-001",
            "name": "Apache Tomcat CVE-2017-12617 RCE",
            "severity": "critical",
            "verified": True,
            "confidence": 0.95
        },
        {
            "id": "VULN-002",
            "name": "Spring Framework CVE-2018-1270 RCE",
            "severity": "high",
            "verified": True,
            "confidence": 0.85
        }
    ]
    
    print(f"✅ 漏洞验证完成")
    print(f"  • 验证漏洞数：{len(verified_vulns)}")
    for vuln in verified_vulns:
        emoji = '🔴' if vuln['severity'] == 'critical' else '🟠'
        print(f"  {emoji} {vuln['name']} (置信度：{vuln['confidence']*100:.0f}%)")
    
    # =========================================
    # Phase 4: 报告生成（模拟）
    # =========================================
    print_step(5, "Phase-4: 报告生成")
    
    print("📄 正在生成测试报告...")
    await asyncio.sleep(0.2)
    
    report = {
        "target": test_target,
        "test_mode": test_mode.value,
        "start_time": datetime.now().isoformat(),
        "assets_count": len(assets),
        "risk_score": risk_report['overall_score'],
        "risk_level": risk_report['risk_level'],
        "tests_planned": strategy.total_actions,
        "vulns_verified": len(verified_vulns),
        "summary": {
            "critical": 1,
            "high": 1,
            "medium": 0,
            "low": 0
        }
    }
    
    print(f"✅ 报告生成完成")
    print(f"  • 测试目标：{report['target']}")
    print(f"  • 风险评分：{report['risk_score']}/100 ({report['risk_level']})")
    print(f"  • 计划测试：{report['tests_planned']}个")
    print(f"  • 已验证漏洞：{report['vulns_verified']}个")
    
    # =========================================
    # 测试总结
    # =========================================
    print_section("测试完成总结", "🎉")
    
    print("✅ 端到端测试成功完成！\n")
    print("📊 测试统计:")
    print(f"  • 资产收集：{len(assets)}个资产")
    print(f"  • 风险评估：{risk_report['overall_score']}/100 ({risk_report['risk_level']})")
    print(f"  • 测试规划：{strategy.total_actions}个测试动作")
    print(f"  • 漏洞验证：{len(verified_vulns)}个已验证")
    print(f"  • 报告生成：完成")
    
    print("\n🎯 核心功能验证:")
    print("  ✅ Phase-0: 资产收集（模拟）")
    print("  ✅ Phase-1: 风险画像（真实）")
    print("  ✅ Phase-2: 策略生成（真实）")
    print("  ✅ Phase-3: 漏洞验证（模拟）")
    print("  ✅ Phase-4: 报告生成（模拟）")
    
    print("\n🚀 智能测试编排器已就绪！")
    print("\n💡 提示:")
    print("  • Phase-1 和 Phase-2 使用真实的核心模块")
    print("  • Phase-0、Phase-3、Phase-4 目前为模拟实现")
    print("  • 后续将集成真实的工具技能")
    
    return True


async def main():
    """主函数"""
    try:
        success = await test_end_to_end()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
