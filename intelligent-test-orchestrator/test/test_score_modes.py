#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险评分模式对比测试

展示威胁模式 vs 安全模式 的区别
"""

import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.risk_profiler import RiskProfiler, RiskScore

def test_score_modes():
    """测试两种评分模式"""
    
    print("=" * 70)
    print("  风险评分模式对比测试")
    print("=" * 70)
    print()
    
    # 模拟测试分数
    test_scores = [
        (12.5, "非常安全的目标"),
        (35.8, "低风险目标"),
        (55.3, "中等风险目标"),
        (72.6, "高风险目标"),
        (88.9, "危急目标"),
    ]
    
    # 威胁模式测试
    print("⚠️  威胁模式（分数越高越危险，推荐）")
    print("-" * 70)
    profiler_threat = RiskProfiler(score_mode='threat')
    
    print(f"{'分数':<10} {'等级':<15} {'描述':<30}")
    print("-" * 70)
    
    for score, description in test_scores:
        risk_score = RiskScore(
            overall_score=score,
            tech_risk=score * 0.9,
            exposure_risk=score * 0.8,
            business_risk=score * 0.7,
            config_risk=score * 0.6,
            score_mode='threat'
        )
        print(f"{score:<10.1f} {risk_score.get_risk_level():<15} {description:<30}")
    
    print()
    print()
    
    # 安全模式测试
    print("🔒 安全模式（分数越低越安全，旧版兼容）")
    print("-" * 70)
    profiler_safety = RiskProfiler(score_mode='safety')
    
    print(f"{'分数':<10} {'等级':<15} {'描述':<30}")
    print("-" * 70)
    
    for score, description in test_scores:
        risk_score = RiskScore(
            overall_score=score,
            tech_risk=score * 0.9,
            exposure_risk=score * 0.8,
            business_risk=score * 0.7,
            config_risk=score * 0.6,
            score_mode='safety'
        )
        print(f"{score:<10.1f} {risk_score.get_risk_level():<15} {description:<30}")
    
    print()
    print()
    
    # 对比总结
    print("=" * 70)
    print("  对比总结")
    print("=" * 70)
    print()
    
    print("示例：某系统风险评分 78.5 分")
    print()
    
    threat_score = RiskScore(
        overall_score=78.5,
        tech_risk=85.2,
        exposure_risk=72.5,
        business_risk=80.0,
        config_risk=65.3,
        score_mode='threat'
    )
    
    safety_score = RiskScore(
        overall_score=78.5,
        tech_risk=85.2,
        exposure_risk=72.5,
        business_risk=80.0,
        config_risk=65.3,
        score_mode='safety'
    )
    
    print(f"⚠️  威胁模式：{threat_score.get_risk_level()}")
    print(f"   → 直观理解：分数高 = 危险，需要立即处理")
    print()
    print(f"🔒 安全模式：{safety_score.get_risk_level()}")
    print(f"   → 反向理解：分数高 = 安全，系统很健康")
    print()
    
    print("=" * 70)
    print("  推荐配置")
    print("=" * 70)
    print()
    print("✅ 当前默认：安全模式（score_mode='safety'）")
    print()
    print("理由：")
    print("  1. 符合直觉（高分=安全，低分=危险）")
    print("  2. 便于向非安全背景的管理层汇报")
    print("  3. 类似健康评分，容易理解")
    print('  4. 减少沟通成本（"安全评分 90 分"比"风险评分 10 分"更积极）')
    print()
    print("配置方法：")
    print('  默认配置，无需额外设置')
    print('  如需使用威胁模式："score_mode": "threat"')
    print()
    
    # 实际资产测试
    print()
    print("=" * 70)
    print("  实际资产测试")
    print("=" * 70)
    print()
    
    # 模拟资产
    test_assets = [
        {
            'url': 'http://demo.test.com',
            'technologies': [
                {'name': 'WordPress', 'version': '5.8', 'cve_count': 3},
                {'name': 'PHP', 'version': '7.4', 'cve_count': 2}
            ],
            'endpoints': [
                {'url': 'http://demo.test.com/login', 'method': 'POST'},
                {'url': 'http://demo.test.com/api/users', 'method': 'GET'}
            ],
            'business_hints': {'type': 'cms'},
            'metadata': {}
        }
    ]
    
    print("测试目标：http://demo.test.com")
    print("技术栈：WordPress 5.8 + PHP 7.4")
    print()
    
    # 威胁模式评估
    print("⚠️  威胁模式评估:")
    profiler_threat = RiskProfiler(score_mode='threat')
    threat_report = profiler_threat.assess(test_assets)
    
    print(f"  风险评分：{threat_report['overall_score']}/100")
    print(f"  风险等级：{threat_report['risk_level']}")
    print()
    
    # 安全模式评估
    print("🔒 安全模式评估:")
    profiler_safety = RiskProfiler(score_mode='safety')
    safety_report = profiler_safety.assess(test_assets)
    
    print(f"  安全评分：{safety_report['overall_score']}/100")
    print(f"  安全等级：{safety_report['risk_level']}")
    print()
    
    print("=" * 70)
    print("  测试完成")
    print("=" * 70)

if __name__ == '__main__':
    test_score_modes()
