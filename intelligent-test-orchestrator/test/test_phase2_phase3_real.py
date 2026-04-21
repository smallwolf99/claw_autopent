#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-2 和 Phase-3 真实工具调用测试脚本

用途：
- 测试 Phase-2 漏洞检测适配器（真实工具）
- 测试 Phase-3 漏洞验证器（真实工具）
- 验证完整漏洞检测和验证流程
"""

import asyncio
import sys
import time
from pathlib import Path

# 自动定位项目根目录
def get_project_root():
    current_file = Path(__file__).resolve()
    search_path = current_file
    
    for _ in range(5):
        if (search_path / 'adapters').exists():
            return search_path
        search_path = search_path.parent
    
    return None

project_root = get_project_root()
if project_root:
    sys.path.insert(0, str(project_root))
    print(f"✅ 项目根目录：{project_root}")
else:
    print("❌ 无法找到项目根目录")
    sys.exit(1)


async def test_phase2():
    """测试 Phase-2 漏洞检测"""
    print("\n" + "=" * 70)
    print("  Phase-2 漏洞检测 - 真实工具测试")
    print("=" * 70)
    print()
    
    from adapters.phase2_adapter_real import Phase2Adapter
    
    # 真实靶场 - Altoro Mutual 银行演示站点
    test_assets = [
        {
            "type": "web",
            "url": "http://demo.testfire.net",
            "host": "demo.testfire.net",
            "description": "Altoro Mutual - 漏洞测试靶场"
        }
    ]
    
    adapter = Phase2Adapter()
    
    start_time = time.time()
    
    print(f"🎯 测试目标：http://demo.testfire.net")
    print(f"📝 目标说明：Altoro Mutual 银行演示站点（漏洞测试靶场）")
    print("📡 开始漏洞检测...")
    print()
    
    try:
        vulnerabilities = await adapter.detect(test_assets)
        
        elapsed_time = time.time() - start_time
        
        print()
        print("📊 测试结果:")
        print(f"  • 发现漏洞数：{len(vulnerabilities)}")
        print(f"  • 耗时：{elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")
        print()
        
        if vulnerabilities:
            print("📋 漏洞详情:")
            for i, vuln in enumerate(vulnerabilities[:10], 1):  # 只显示前 10 个
                print(f"\n  [{i}] {vuln.get('name', 'Unknown')}")
                print(f"      严重程度：{vuln.get('severity', 'unknown').upper()}")
                print(f"      检测工具：{vuln.get('tool', 'unknown')}")
                print(f"      置信度：{vuln.get('confidence', 0) * 100:.0f}%")
                if vuln.get('description'):
                    print(f"      描述：{vuln.get('description')[:100]}...")
            
            print()
            
            # 验证是否真实调用
            print("✅ 验证结果:")
            
            # 检查是否有真实数据
            has_real_data = False
            
            tools_used = set()
            for vuln in vulnerabilities:
                tool = vuln.get('tool', '')
                if tool:
                    tools_used.add(tool)
                    has_real_data = True
            
            if tools_used:
                print(f"  ✅ 使用的工具：{', '.join(tools_used)}")
                print(f"  ✅ 检测到 {len(vulnerabilities)} 个漏洞")
            else:
                print("  ⚠️  警告：没有检测到漏洞")
            
            # 时间验证
            print()
            print("⏱️  时间分析:")
            
            if elapsed_time < 10:
                print(f"  ⚠️  警告：耗时过短 ({elapsed_time:.2f}秒)")
                print("     预期：漏洞扫描至少需要 1-5 分钟")
            elif elapsed_time < 300:
                print(f"  ✅ 时间合理：{elapsed_time:.2f}秒")
            else:
                print(f"  ✅ 时间正常：{elapsed_time:.2f}秒 ({elapsed_time/60:.2f}分钟)")
        
        else:
            print("  ℹ️  未检测到漏洞")
            print("     可能原因:")
            print("     - 目标系统很安全")
            print("     - 工具未安装")
            print("     - 网络问题")
        
        return vulnerabilities
    
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return []


async def test_phase3(vulnerabilities):
    """测试 Phase-3 漏洞验证"""
    print("\n" + "=" * 70)
    print("  Phase-3 漏洞验证 - 真实工具测试")
    print("=" * 70)
    print()
    
    from adapters.phase3_validator_real import Phase3Validator
    
    if not vulnerabilities:
        print("⚠️  没有漏洞需要验证，跳过 Phase-3 测试")
        return []
    
    # 真实靶场资产
    test_assets = [
        {
            "type": "web",
            "url": "http://demo.testfire.net",
            "host": "demo.testfire.net",
            "description": "Altoro Mutual - 漏洞测试靶场"
        }
    ]
    
    validator = Phase3Validator()
    
    start_time = time.time()
    
    print(f"🔍 开始验证 {len(vulnerabilities)} 个漏洞...")
    print()
    
    try:
        results = await validator.verify(vulnerabilities, test_assets)
        
        elapsed_time = time.time() - start_time
        
        print()
        print("📊 验证结果:")
        print(f"  • 验证漏洞数：{len(results)}")
        print(f"  • 已确认：{sum(1 for r in results if r.verified)}")
        print(f"  • 误报：{sum(1 for r in results if not r.verified)}")
        print(f"  • 耗时：{elapsed_time:.2f} 秒")
        print()
        
        if results:
            print("📋 验证详情:")
            for i, result in enumerate(results[:10], 1):  # 只显示前 10 个
                status = "✅" if result.verified else "❌"
                print(f"\n  [{i}] {status} {result.name}")
                print(f"      严重程度：{result.severity.upper()}")
                print(f"      置信度：{result.confidence * 100:.0f}%")
                if result.false_positive_reason:
                    print(f"      误报原因：{result.false_positive_reason}")
                if result.exploit_chain:
                    print(f"      利用链：{len(result.exploit_chain)} 步")
            
            print()
            
            # 统计
            verified_count = sum(1 for r in results if r.verified)
            total_count = len(results)
            
            print("✅ 验证总结:")
            print(f"  • 验证通过率：{verified_count}/{total_count} ({verified_count/total_count*100:.1f}%)")
            
            if verified_count > 0:
                print(f"  ✅ 成功验证 {verified_count} 个真实漏洞")
            
            if verified_count < total_count:
                print(f"  ⚠️  {total_count - verified_count} 个漏洞可能是误报")
        
        return results
    
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    """主测试函数"""
    print("=" * 70)
    print("  Phase-2 & Phase-3 真实工具调用测试")
    print("=" * 70)
    
    # 测试 Phase-2
    vulnerabilities = await test_phase2()
    
    # 测试 Phase-3
    if vulnerabilities:
        await asyncio.sleep(2)  # 短暂休息
        results = await test_phase3(vulnerabilities)
    else:
        print("\n⚠️  跳过 Phase-3 测试（没有漏洞需要验证）")
    
    # 总结
    print("\n" + "=" * 70)
    print("  测试总结")
    print("=" * 70)
    print()
    print("✅ 测试完成！")
    print()
    print("下一步:")
    print("  1. 检查上方输出，确认工具调用是否正常")
    print("  2. 如果正常，可以部署到服务器")
    print("  3. 如果有问题，检查工具是否安装")
    print()
    print("工具检查命令:")
    print("  which nuclei afrog nikto zap-cli sqlmap")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
