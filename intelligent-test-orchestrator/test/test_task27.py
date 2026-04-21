#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Task 27 迁移后的核心功能
"""

import sys
import json
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from core.risk_profiler import RiskProfiler
from core.test_strategist import TestStrategist
from core.rule_engine import RuleEngine

def test_risk_profiler():
    """测试风险画像模块"""
    print("\n" + "="*70)
    print("  测试 1: 风险画像模块 (RiskProfiler)")
    print("="*70)
    
    # 模拟资产数据
    assets = [
        {
            "url": "http://test.example.com",
            "technologies": [
                {"name": "Apache Tomcat", "version": "7.0.70", "confidence": 0.9},
                {"name": "Spring Framework", "version": "4.3.0", "confidence": 0.8}
            ],
            "endpoints": [
                {"path": "/admin", "methods": ["GET", "POST"], "auth_required": False},
                {"path": "/api/v1/users", "methods": ["GET", "POST", "PUT", "DELETE"], "auth_required": True}
            ],
            "business_hints": {"type": "enterprise"},
            "metadata": {}
        }
    ]
    
    # 创建风险画像引擎
    profiler = RiskProfiler()
    risk_report = profiler.assess(assets)
    
    print(f"\n✅ 风险评估完成:")
    print(f"  • 总体风险分：{risk_report['overall_score']}/100")
    print(f"  • 风险等级：{risk_report['risk_level']}")
    print(f"  • 评估资产数：{risk_report['assets_assessed']}")
    
    return risk_report

def test_test_strategist(risk_report):
    """测试测试策略生成器"""
    print("\n" + "="*70)
    print("  测试 2: 测试策略生成器 (TestStrategist)")
    print("="*70)
    
    # 模拟资产数据
    assets = [
        {
            "url": "http://test.example.com",
            "technologies": [
                {"name": "Apache Tomcat", "version": "7.0.70"}
            ]
        }
    ]
    
    # 创建策略生成器
    strategist = TestStrategist()
    strategy = strategist.generate_strategy(assets, risk_report)
    
    print(f"\n✅ 测试策略生成完成:")
    print(f"  • 目标：{strategy.target}")
    print(f"  • 风险评分：{strategy.risk_score}")
    print(f"  • 测试动作数：{strategy.total_actions}")
    print(f"  • 估计时间：{strategy.get_total_time()}分钟")
    
    # 显示前 3 个动作
    print(f"\n📋 前 3 个测试动作:")
    for i, action in enumerate(strategy.actions[:3], 1):
        print(f"  {i}. [{action.priority.value}] {action.name} - {action.description}")
    
    return strategy

def test_rule_engine():
    """测试规则引擎"""
    print("\n" + "="*70)
    print("  测试 3: 规则引擎 (RuleEngine)")
    print("="*70)
    
    # 创建规则引擎（没有规则文件）
    engine = RuleEngine()
    
    # 模拟资产
    asset = {
        "url": "http://test.example.com",
        "technologies": [
            {"name": "Apache Tomcat", "version": "7.0.70"}
        ]
    }
    
    # 评估
    actions = engine.evaluate(asset)
    
    print(f"\n✅ 规则评估完成:")
    print(f"  • 加载规则数：{len(engine.rules)}")
    print(f"  • 匹配动作数：{len(actions)}")
    
    return actions

def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("  Task 27 迁移功能测试")
    print("="*70)
    
    try:
        # 测试 1: 风险画像
        risk_report = test_risk_profiler()
        
        # 测试 2: 策略生成
        strategy = test_test_strategist(risk_report)
        
        # 测试 3: 规则引擎
        test_rule_engine()
        
        print("\n" + "="*70)
        print("  ✅ 所有测试通过！")
        print("="*70)
        print("\n🎉 Task 27 迁移成功！")
        print("\n已迁移的核心模块:")
        print("  • risk_profiler.py - 风险画像引擎")
        print("  • test_strategist.py - 测试策略生成器")
        print("  • rule_engine.py - 规则引擎")
        print("  • config.py - 配置模块")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
