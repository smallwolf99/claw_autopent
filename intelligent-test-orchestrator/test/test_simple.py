#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 - 直接调用 main.py 测试完整流程
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from main import OpenClawHandler


async def test_full_flow():
    """测试完整流程"""
    print("\n" + "="*70)
    print("  智能测试编排器 - 完整流程测试")
    print("="*70 + "\n")
    
    handler = OpenClawHandler()
    
    # 执行完整测试
    result = await handler.execute_intelligent_test(
        target="http://demo-test.example.com",
        test_mode="full",
        time_limit=60,
        report_format="html"
    )
    
    # 显示结果
    print("\n" + "="*70)
    print("  测试结果")
    print("="*70)
    
    if result.get('success'):
        print("\n✅ 测试成功！")
        print(f"\n📊 摘要：{result.get('summary', 'N/A')}")
        print(f"\n📁 数据:")
        data = result.get('data', {})
        for key, value in data.items():
            print(f"  • {key}: {value}")
    else:
        print(f"\n❌ 测试失败：{result.get('message', 'Unknown error')}")
    
    return result.get('success', False)


if __name__ == "__main__":
    try:
        success = asyncio.run(test_full_flow())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
