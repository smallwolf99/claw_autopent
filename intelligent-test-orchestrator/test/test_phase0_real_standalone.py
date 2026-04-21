#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-0 真实工具调用测试脚本（独立版本）

用途：验证 Phase-0 适配器是否正确调用真实工具

特点：
- 完全独立，不依赖 Python 路径设置
- 可以在任何位置运行
- 自动定位项目根目录和模块
"""

import asyncio
import sys
import time
import os
from pathlib import Path

# 自动定位项目根目录
def get_project_root():
    """自动查找项目根目录"""
    # 方法 1: 从当前文件向上查找
    current_file = Path(__file__).resolve()
    search_path = current_file
    
    # 向上最多查找 5 级目录
    for _ in range(5):
        # 检查是否存在 adapters 目录
        if (search_path / 'adapters').exists():
            return search_path
        search_path = search_path.parent
    
    # 方法 2: 使用环境变量
    if 'OPENCLAW_SKILLS_PATH' in os.environ:
        return Path(os.environ['OPENCLAW_SKILLS_PATH'])
    
    # 方法 3: 使用当前工作目录
    cwd = Path.cwd()
    if (cwd / 'adapters').exists():
        return cwd
    
    # 默认返回 None
    return None


# 获取项目根目录并添加到 Python 路径
project_root = get_project_root()
if project_root:
    sys.path.insert(0, str(project_root))
    print(f"✅ 项目根目录：{project_root}")
else:
    print("❌ 无法找到项目根目录，尝试使用当前目录")
    sys.path.insert(0, str(Path.cwd()))


# 现在导入适配器
try:
    from adapters.phase0_adapter_real import Phase0Adapter
    print("✅ 成功导入 Phase0Adapter")
except ImportError as e:
    print(f"❌ 导入失败：{e}")
    print("\n请尝试以下方法:")
    print("  1. 确保在项目根目录运行：cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator")
    print("  2. 检查 adapters 目录是否存在")
    print("  3. 运行：python3 -c \"import sys; print('\\n'.join(sys.path))\"")
    sys.exit(1)


async def test_phase0_real():
    """测试 Phase-0 真实工具调用"""
    
    print("=" * 70)
    print("  Phase-0 资产收集 - 真实工具调用测试")
    print("=" * 70)
    print()
    
    # 测试目标（使用安全的公共测试目标）
    test_targets = [
        "http://example.com",  # 简单 HTTP
        "https://example.com",  # HTTPS
    ]
    
    for target in test_targets:
        print(f"🎯 测试目标：{target}")
        print("-" * 70)
        
        adapter = Phase0Adapter()
        
        start_time = time.time()
        
        # 执行资产收集
        print("📡 开始资产收集...")
        print()
        
        try:
            assets = await adapter.collect(target)
            
            elapsed_time = time.time() - start_time
            
            print()
            print("📊 测试结果:")
            print(f"  • 发现资产数：{len(assets)}")
            print(f"  • 耗时：{elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")
            print()
            
            # 显示详细信息
            if assets:
                print("📋 资产详情:")
                for i, asset in enumerate(assets, 1):
                    asset_type = asset.get('type', 'unknown')
                    print(f"\n  [{i}] {asset_type.upper()}")
                    
                    if asset_type == 'web':
                        print(f"      URL: {asset.get('url', 'N/A')}")
                        print(f"      状态码：{asset.get('metadata', {}).get('status_code', 'N/A')}")
                        print(f"      标题：{asset.get('metadata', {}).get('title', 'N/A')}")
                        techs = asset.get('technologies', [])
                        if techs:
                            print(f"      技术栈:")
                            for tech in techs[:5]:  # 只显示前 5 个
                                print(f"        - {tech.get('name', 'N/A')} {tech.get('version', '')}")
                    
                    elif asset_type == 'port':
                        print(f"      主机：{asset.get('host', 'N/A')}")
                        ports = asset.get('ports', [])
                        if ports:
                            print(f"      开放端口 ({len(ports)} 个):")
                            for port in ports[:10]:  # 只显示前 10 个
                                print(f"        - {port.get('port')}/{port.get('protocol')} "
                                      f"{port.get('service', '')} {port.get('version', '')}")
                    
                    elif asset_type == 'subdomain':
                        print(f"      域名：{asset.get('domain', 'N/A')}")
                        subdomains = asset.get('subdomains', [])
                        if subdomains:
                            print(f"      子域名 ({len(subdomains)} 个):")
                            for sub in subdomains[:10]:  # 只显示前 10 个
                                print(f"        - {sub}")
                
                print()
                
                # 验证是否真实调用
                print("✅ 验证结果:")
                
                # 检查是否有真实数据
                has_real_data = False
                
                for asset in assets:
                    if asset.get('type') == 'web':
                        techs = asset.get('technologies', [])
                        if techs and len(techs) > 0:
                            has_real_data = True
                            print("  ✅ WhatWeb: 检测到真实技术栈")
                            break
                
                for asset in assets:
                    if asset.get('type') == 'port':
                        ports = asset.get('ports', [])
                        if ports and len(ports) > 2:  # 模拟数据通常只有 2 个端口
                            has_real_data = True
                            print("  ✅ Nmap: 检测到真实端口")
                            break
                
                if not has_real_data:
                    print("  ⚠️  警告：数据看起来像模拟数据")
                    print("     - 端口数 <= 2")
                    print("     - 技术栈为空或过于简单")
                
                # 时间验证
                print()
                print("⏱️  时间分析:")
                
                if elapsed_time < 1:
                    print(f"  ⚠️  警告：耗时过短 ({elapsed_time:.2f}秒)，可能是模拟数据")
                    print("     预期：Nmap 扫描至少需要 1-3 分钟")
                elif elapsed_time < 60:
                    print(f"  ✅ 时间合理：{elapsed_time:.2f}秒")
                    print("     符合快速扫描的特征")
                else:
                    print(f"  ✅ 时间正常：{elapsed_time:.2f}秒 ({elapsed_time/60:.2f}分钟)")
                    print("     符合真实工具扫描的特征")
            
            else:
                print("  ⚠️  未发现任何资产")
                print("     可能原因:")
                print("     - 目标不可达")
                print("     - 工具未安装")
                print("     - 网络问题")
        
        except Exception as e:
            print(f"\n❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("=" * 70)
        print()
    
    # 总结
    print("📊 测试总结")
    print("=" * 70)
    print()
    print("✅ 测试完成！")
    print()
    print("下一步:")
    print("  1. 检查上方输出，确认是否调用真实工具")
    print("  2. 如果正常，继续测试 Phase-2 和 Phase-3")
    print("  3. 如果有问题，检查工具是否安装")
    print()
    print("工具检查命令:")
    print("  which nmap whatweb httpx subfinder")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(test_phase0_real())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
