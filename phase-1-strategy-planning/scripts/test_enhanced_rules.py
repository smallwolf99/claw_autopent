#!/usr/bin/env python3
"""测试增强规则库加载"""

import sys
import yaml
from pathlib import Path
from rule_engine import RuleEngine, RuleDefinition

def test_rule_loading():
    """测试增强规则库加载"""
    print("🚀 测试智能测试规划引擎增强规则库")
    print("=" * 60)
    
    # 规则目录
    rules_dir = Path(__file__).parent.parent / "data" / "rules"
    print(f"规则目录: {rules_dir}")
    
    # 检查目录是否存在
    if not rules_dir.exists():
        print(f"❌ 规则目录不存在: {rules_dir}")
        return False
    
    # 列出所有规则文件
    yaml_files = list(rules_dir.glob("*.yml")) + list(rules_dir.glob("*.yaml"))
    print(f"发现 {len(yaml_files)} 个规则文件:")
    
    for file_path in sorted(yaml_files):
        file_size = file_path.stat().st_size
        print(f"  ✅ {file_path.name} ({file_size} 字节)")
    
    print()
    
    # 测试规则引擎加载
    print("🧪 测试RuleEngine加载...")
    try:
        engine = RuleEngine(rules_dir=rules_dir)
        rule_count = len(engine.rules)
        print(f"  ✅ RuleEngine成功加载 {rule_count} 条规则")
        
        # 显示一些规则示例
        print("  📋 规则示例 (前5条):")
        for i, (rule_id, rule) in enumerate(list(engine.rules.items())[:5]):
            print(f"    [{i+1}] {rule_id}: {rule.name}")
            print(f"        优先级: {rule.priority}, 启用: {rule.enabled}")
        
        # 特别检查增强规则
        enhanced_rules = [r for r in engine.rules.values() if "enhanced" in r.name.lower() or "增强" in r.name]
        print(f"  🔍 检测到 {len(enhanced_rules)} 条增强规则")
        
        return True
        
    except Exception as e:
        print(f"❌ RuleEngine加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def test_yaml_syntax():
    """测试YAML语法"""
    print()
    print("📖 测试YAML语法正确性...")
    
    rules_dir = Path(__file__).parent.parent / "data" / "rules"
    yaml_files = list(rules_dir.glob("*.yml")) + list(rules_dir.glob("*.yaml"))
    
    for file_path in sorted(yaml_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            # 检查基本结构
            if isinstance(content, dict) and 'rules' in content:
                rules = content['rules']
                if isinstance(rules, list):
                    print(f"  ✅ {file_path.name}: {len(rules)} 条规则 (结构正确)")
                else:
                    print(f"  ⚠️ {file_path.name}: rules字段不是列表")
            else:
                print(f"  ⚠️ {file_path.name}: 缺少'规则'字段或根对象不是字典")
                
        except yaml.YAMLError as e:
            print(f"❌ {file_path.name}: YAML语法错误 - {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path.name}: 其他错误 - {e}")
            return False
    
    print("  ✅ 所有YAML文件语法检查通过")
    return True

def test_enhanced_rule_content():
    """测试增强规则具体内容"""
    print()
    print("🔍 检查增强规则具体内容...")
    
    enhanced_files = [
        "authentication_enhanced_rules.yml",
        "banking_enhanced_rules.yml", 
        "jquery_enhanced_rules.yml",
        "tomcat_enhanced_rules.yml"
    ]
    
    rules_dir = Path(__file__).parent.parent / "data" / "rules"
    
    for file_name in enhanced_files:
        file_path = rules_dir / file_name
        if not file_path.exists():
            print(f"  ⚠️ {file_name}: 文件不存在")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            rules = content.get('rules', [])
            print(f"  📄 {file_name}: {len(rules)} 条规则")
            
            # 显示规则ID和描述
            for rule in rules[:3]:  # 只显示前3条
                rule_id = rule.get('id', '未知')
                rule_name = rule.get('name', '未知')
                rule_desc = rule.get('description', '无描述')
                print(f"    • {rule_id}: {rule_name}")
                if 'cve' in rule_desc.lower() or 'CVE' in rule.get('name', ''):
                    print(f"      🔴 CVE规则: {rule_desc[:100]}...")
                    
        except Exception as e:
            print(f"  ❌ {file_name}: 解析失败 - {e}")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 智能测试规划引擎增强规则库完整性测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行测试
    test_results.append(("YAML语法测试", test_yaml_syntax()))
    test_results.append(("规则引擎加载", test_rule_loading()))
    test_results.append(("增强规则内容", test_enhanced_rule_content()))
    
    print()
    print("=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有测试通过！增强规则库已成功集成。")
        print(f"📦 总计: {len(list(rules_dir.glob('*.yml')))} 个YAML规则文件")
        
        # 显示增强规则统计
        rules_dir = Path(__file__).parent.parent / "data" / "rules"
        enhanced_files = [f for f in rules_dir.glob("*enhanced*.yml")]
        print(f"🚀 增强规则: {len(enhanced_files)} 个专门规则集")
        return 0
    else:
        print("⚠️  部分测试失败，需要检查规则文件。")
        return 1

if __name__ == "__main__":
    sys.exit(main())