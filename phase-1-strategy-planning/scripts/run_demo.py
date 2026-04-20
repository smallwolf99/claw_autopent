#!/usr/bin/env python3
"""
智能测试规划引擎 - MVP演示

这个脚本演示如何使用新创建的智能测试规划引擎为zero.webappsecurity.com生成测试策略。
"""

import sys
from pathlib import Path
import json

# 添加当前目录到路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from asset_normalizer import AssetNormalizer, StandardizedAsset
from rule_engine import RuleEngine
from test_strategist import TestStrategist

def demonstrate_asset_normalization():
    """演示资产标准化功能"""
    print("=" * 60)
    print("📊 演示: 资产标准化模块")
    print("=" * 60)
    
    # 创建标准化器
    normalizer = AssetNormalizer()
    
    # 使用模拟数据演示
    print("📄 使用模拟whatweb数据")
    mock_whatweb = {
        "target": {"url": "http://zero.webappsecurity.com"},
        "title": "Zero - Personal Banking - Loans - Credit Cards",
        "plugins": {
            "HTTPServer": {"string": "Apache-Coyote/1.1"},
            "JQuery": {"version": "1.8.2"},
            "Bootstrap": {},
            "HTML5": {},
            "Apache": {}
        }
    }
    
    assets = [normalizer.normalize_whatweb_json(mock_whatweb)]
    
    # 也添加模拟nmap数据
    mock_nmap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun>
<host starttime="1776260448" endtime="1776260491">
<address addr="54.82.22.214" addrtype="ipv4"/>
<ports><port protocol="tcp" portid="80">
<service name="http" product="Apache Tomcat/Coyote JSP engine" version="7.0.70" method="probed" conf="10">
<cpe>cpe:/a:apache:tomcat:7.0.70</cpe></service></port>
<port protocol="tcp" portid="443"><service name="https"/></port>
<port protocol="tcp" portid="8080"><service name="http" product="Apache Tomcat"/></port>
</ports>
</host>
</nmaprun>'''
    
    # 保存临时文件
    temp_xml = Path("/tmp/mock_nmap.xml")
    temp_xml.write_text(mock_nmap_xml)
    nmap_assets = normalizer.normalize_nmap_xml(temp_xml)
    assets.extend(nmap_assets)
    
    print(f"✅ 使用模拟数据创建了 {len(assets)} 个资产")
    
    print(f"✅ 成功标准化 {len(assets)} 个资产")
    
    for i, asset in enumerate(assets, 1):
        print(f"\n  {i}. {asset.category.value.upper()}: {asset.url or 'N/A'}")
        
        if asset.technologies:
            tech_names = [f"{t.name} {t.version or ''}".strip() for t in asset.technologies]
            print(f"     技术栈: {', '.join(tech_names)}")
        
        if asset.business_hints.type != "unknown":
            print(f"     业务类型: {asset.business_hints.type} (置信度: {asset.business_hints.confidence:.1f})")
    
    return assets

def demonstrate_rule_engine(assets):
    """演示规则引擎功能"""
    print("\n" + "=" * 60)
    print("⚡ 演示: 规则引擎模块")
    print("=" * 60)
    
    # 创建规则引擎
    engine = RuleEngine()
    
    # 添加一些示例规则
    sample_rules = [
        {
            "id": "tomcat_cve_test",
            "name": "Tomcat CVE验证规则",
            "description": "当检测到Apache Tomcat时，验证相关CVE",
            "priority": 100,
            "enabled": True,
            "conditions": [
                "technology.name == 'Apache Tomcat'",
                "technology.version.parsed.major <= 8"
            ],
            "actions": [
                {
                    "action": "add_test",
                    "params": {
                        "category": "cve_validation",
                        "tests": ["tomcat_cve_scan"],
                        "tools": ["nuclei_tomcat", "afrog_tomcat"],
                        "priority": "high",
                        "estimated_time_minutes": 30,
                        "commands": [
                            "nuclei -u {url} -tags tomcat",
                            "afrog -S vuln -S tomcat -t {url}"
                        ]
                    }
                }
            ]
        },
        {
            "id": "jquery_xss_test",
            "name": "JQuery XSS测试规则",
            "description": "当检测到旧版本JQuery时，测试XSS漏洞",
            "priority": 80,
            "enabled": True,
            "conditions": [
                "technology.name == 'JQuery'",
                "technology.version.parsed.major <= 3"
            ],
            "actions": [
                {
                    "action": "add_test",
                    "params": {
                        "category": "cve_validation",
                        "tests": ["jquery_xss_scan"],
                        "tools": ["nuclei_jquery", "custom_scripts"],
                        "priority": "medium",
                        "estimated_time_minutes": 20,
                        "commands": [
                            "nuclei -u {url} -tags jquery",
                            "python3 jquery_xss_scanner.py -u {url}"
                        ]
                    }
                }
            ]
        },
        {
            "id": "banking_login_test",
            "name": "银行登录安全测试规则",
            "description": "当检测到银行系统时，测试登录安全",
            "priority": 90,
            "enabled": True,
            "conditions": [
                "business.type == 'banking'",
                "business.confidence >= 0.5"
            ],
            "actions": [
                {
                    "action": "add_test",
                    "params": {
                        "category": "authentication_test",
                        "tests": ["login_security_test"],
                        "tools": ["hydra", "burp_suite"],
                        "priority": "high",
                        "estimated_time_minutes": 45,
                        "commands": [
                            "hydra -L users.txt -P passwords.txt {url} http-post-form",
                            "# 使用Burp Suite进行手动登录测试"
                        ]
                    }
                }
            ]
        }
    ]
    
    # 加载规则
    print("📋 加载示例规则...")
    for rule_data in sample_rules:
        engine.load_rule(rule_data)
    
    print(f"✅ 加载了 {len(engine.rules)} 条规则")
    
    # 评估资产
    print("\n🔍 评估资产匹配规则...")
    for asset in assets:
        asset_dict = asset.dict() if hasattr(asset, 'dict') else asset
        results = engine.evaluate_asset(asset_dict)
        
        if results:
            print(f"\n  🎯 资产匹配 {len(results)} 条规则:")
            for result in results:
                print(f"    - {result['rule_name']} → {result['action_type']}")
        else:
            print(f"\n  ℹ️  资产未匹配任何规则")
    
    return engine

def demonstrate_test_strategist(assets, rule_engine):
    """演示测试策略生成器"""
    print("\n" + "=" * 60)
    print("🧠 演示: 测试策略生成器")
    print("=" * 60)
    
    # 创建测试策略生成器
    strategist = TestStrategist()
    
    # 添加资产数据（在实际使用中会从文件加载）
    for asset in assets:
        strategist.asset_normalizer.add_asset(asset)
    
    # 设置规则引擎
    strategist.rule_engine = rule_engine
    
    # 生成策略
    print("🚀 生成测试策略...")
    try:
        strategy = strategist.generate_strategy("zero.webappsecurity.com")
        
        print(f"\n✅ 策略生成成功!")
        print(f"📊 总计: {strategy.total_actions} 个测试项")
        print(f"⏱️  预计总时间: {strategy.total_estimated_time_minutes} 分钟")
        
        print(f"\n📋 执行计划:")
        for phase in strategy.execution_plan:
            print(f"\n  阶段 {phase['phase']}: {phase['name']}")
            print(f"    - 描述: {phase['description']}")
            print(f"    - 时间: {phase['estimated_time_minutes']} 分钟")
            print(f"    - 测试项: {len(phase['actions'])} 个")
        
        print(f"\n🎯 按优先级分组:")
        print(f"   🔴 紧急: {len(strategy.critical_actions)} 个")
        print(f"   🟠 高优先级: {len(strategy.high_priority_actions)} 个")
        print(f"   🟡 中优先级: {len(strategy.medium_priority_actions)} 个")
        print(f"   🟢 低优先级: {len(strategy.low_priority_actions)} 个")
        
        print(f"\n📁 按类别分组:")
        for category, actions in strategy.actions_by_category.items():
            print(f"   - {category}: {len(actions)} 个")
        
        return strategy
        
    except Exception as e:
        print(f"❌ 策略生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def export_strategy(strategy):
    """导出策略到文件"""
    if not strategy:
        return
    
    print("\n" + "=" * 60)
    print("💾 演示: 策略导出")
    print("=" * 60)
    
    output_dir = Path("/tmp/smart_testing_strategy")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 导出Markdown报告
    md_path = output_dir / "zero_webappsecurity_test_strategy.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(strategy.to_markdown())
    
    print(f"📄 Markdown报告已保存到: {md_path}")
    
    # 导出命令列表
    sh_path = output_dir / "zero_webappsecurity_test_commands.sh"
    with open(sh_path, 'w') as f:
        f.write(strategy.to_commands_list())
    sh_path.chmod(0o755)
    
    print(f"⚡ 命令列表已保存到: {sh_path}")
    print(f"🔍 文件内容前几行示例:")
    
    # 显示部分内容
    with open(md_path, 'r') as f:
        lines = f.readlines()[:15]
        print("\n" + "".join(lines))
        print("...")
    
    with open(sh_path, 'r') as f:
        lines = f.readlines()[:10]
        print("\n" + "".join(lines))
        print("...")

def main():
    """主演示函数"""
    print("🧠 智能测试规划引擎 - MVP演示")
    print("目标: zero.webappsecurity.com")
    print("=" * 60)
    
    try:
        # 1. 演示资产标准化
        assets = demonstrate_asset_normalization()
        
        # 2. 演示规则引擎
        rule_engine = demonstrate_rule_engine(assets)
        
        # 3. 演示测试策略生成器
        strategy = demonstrate_test_strategist(assets, rule_engine)
        
        # 4. 演示策略导出
        if strategy:
            export_strategy(strategy)
        
        print("\n" + "=" * 60)
        print("🎉 演示完成!")
        print("=" * 60)
        print("\n📋 MVP功能总结:")
        print("✅ 资产标准化: 统一WhatWeb/Nmap等工具输出格式")
        print("✅ 规则引擎: 基于条件的智能决策")
        print("✅ 测试策略生成: 针对性测试规划和优先级排序")
        print("✅ 策略导出: Markdown报告 + 可执行命令列表")
        print("\n🚀 下一步: 将此框架集成到日常安全测试工作流中")
        
    except Exception as e:
        print(f"\n❌ 演示过程发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()