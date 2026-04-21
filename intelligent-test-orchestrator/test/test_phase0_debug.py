#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-0 真实工具调用测试脚本（调试版本）

用途：
- 显示详细的工具调用日志
- 显示工具原始输出
- 帮助诊断为什么返回模拟数据
"""

import asyncio
import sys
import time
import logging
from pathlib import Path

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# 自动定位项目根目录
def get_project_root():
    """自动查找项目根目录"""
    current_file = Path(__file__).resolve()
    search_path = current_file
    
    for _ in range(5):
        if (search_path / 'adapters').exists():
            return search_path
        search_path = search_path.parent
    
    if 'OPENCLAW_SKILLS_PATH' in locals():
        return Path(locals()['OPENCLAW_SKILLS_PATH'])
    
    cwd = Path.cwd()
    if (cwd / 'adapters').exists():
        return cwd
    
    return None

project_root = get_project_root()
if project_root:
    sys.path.insert(0, str(project_root))
    print(f"✅ 项目根目录：{project_root}")
else:
    print("❌ 无法找到项目根目录")
    sys.exit(1)

from adapters.phase0_adapter_real import Phase0Adapter


async def test_phase0_debug():
    """调试版本测试"""
    
    print("=" * 70)
    print("  Phase-0 真实工具调用 - 调试模式")
    print("=" * 70)
    print()
    
    # 测试目标
    test_target = "http://example.com"
    
    print(f"🎯 测试目标：{test_target}")
    print()
    
    adapter = Phase0Adapter()
    
    start_time = time.time()
    
    # 执行资产收集
    print("📡 开始资产收集...")
    print()
    
    try:
        # 逐个工具测试
        print("-" * 70)
        print("1. 测试 Nmap")
        print("-" * 70)
        nmap_result = await adapter._call_nmap(test_target)
        print(f"Nmap 结果：{len(nmap_result)} 个资产")
        if nmap_result:
            print(f"详细数据：{nmap_result[0]}")
        print()
        
        print("-" * 70)
        print("2. 测试 WhatWeb")
        print("-" * 70)
        whatweb_result = await adapter._call_whatweb(test_target)
        print(f"WhatWeb 结果：{len(whatweb_result)} 个资产")
        if whatweb_result:
            print(f"详细数据：{whatweb_result[0]}")
        print()
        
        print("-" * 70)
        print("3. 测试 Httpx")
        print("-" * 70)
        httpx_result = await adapter._call_httpx(test_target)
        print(f"Httpx 结果：{len(httpx_result)} 个资产")
        if httpx_result:
            print(f"详细数据：{httpx_result[0]}")
        print()
        
        print("-" * 70)
        print("4. 测试 Subfinder")
        print("-" * 70)
        subfinder_result = await adapter._call_subfinder(test_target)
        print(f"Subfinder 结果：{len(subfinder_result)} 个资产")
        if subfinder_result:
            print(f"详细数据：{subfinder_result[0]}")
        print()
        
        # 汇总
        elapsed_time = time.time() - start_time
        
        print("=" * 70)
        print("📊 测试结果汇总")
        print("=" * 70)
        print()
        print(f"总耗时：{elapsed_time:.2f} 秒")
        print()
        
        all_results = nmap_result + whatweb_result + httpx_result + subfinder_result
        print(f"总资产数：{len(all_results)}")
        print()
        
        # 分析
        print("🔍 数据分析:")
        print()
        
        # Nmap 分析
        if nmap_result:
            ports = nmap_result[0].get('ports', [])
            print(f"  Nmap:")
            print(f"    - 端口数：{len(ports)}")
            if ports:
                for port in ports[:5]:
                    print(f"      • {port.get('port')}/{port.get('protocol')} - {port.get('service', 'unknown')}")
            else:
                print(f"      ⚠️  端口数为 0，可能 Nmap 执行失败")
        else:
            print(f"  Nmap: ❌ 无结果")
        print()
        
        # WhatWeb 分析
        if whatweb_result:
            techs = whatweb_result[0].get('technologies', [])
            print(f"  WhatWeb:")
            print(f"    - 技术栈数量：{len(techs)}")
            if techs:
                for tech in techs[:5]:
                    print(f"      • {tech.get('name')} {tech.get('version', '')}")
            else:
                print(f"      ⚠️  技术栈为空，可能 WhatWeb 执行失败")
        else:
            print(f"  WhatWeb: ❌ 无结果")
        print()
        
        # Httpx 分析
        if httpx_result:
            print(f"  Httpx:")
            print(f"    - 状态码：{httpx_result[0].get('status_code', 'N/A')}")
            print(f"    - 标题：{httpx_result[0].get('title', 'N/A')}")
        else:
            print(f"  Httpx: ❌ 无结果")
        print()
        
        # 总结
        print("=" * 70)
        print("✅ 诊断结论")
        print("=" * 70)
        print()
        
        has_real_data = False
        
        if nmap_result and len(nmap_result[0].get('ports', [])) > 2:
            print("✅ Nmap: 检测到真实端口数据")
            has_real_data = True
        else:
            print("❌ Nmap: 数据异常（可能工具未执行或解析失败）")
        
        if whatweb_result and len(whatweb_result[0].get('technologies', [])) > 0:
            print("✅ WhatWeb: 检测到真实技术栈")
            has_real_data = True
        else:
            print("❌ WhatWeb: 数据异常（可能工具未执行或解析失败）")
        
        if httpx_result:
            print("✅ Httpx: 成功获取 HTTP 信息")
            has_real_data = True
        else:
            print("❌ Httpx: 数据异常")
        
        print()
        
        if has_real_data:
            print("🎉 工具调用正常，使用真实数据！")
        else:
            print("⚠️  警告：所有工具都未返回有效数据")
            print()
            print("可能原因:")
            print("  1. 工具未安装（nmap, whatweb, httpx, subfinder）")
            print("  2. 工具执行失败（权限、网络问题）")
            print("  3. 输出解析失败（格式不匹配）")
            print()
            print("解决建议:")
            print("  1. 检查工具是否安装：which nmap whatweb httpx subfinder")
            print("  2. 手动测试工具：nmap -sV http://example.com")
            print("  3. 查看详细日志（上方输出）")
        
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_phase0_debug())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
