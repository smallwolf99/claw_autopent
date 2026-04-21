#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码测试 - 验证 UTF-8 编码是否正确
"""

import sys
import io

# 设置 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("  UTF-8 编码测试")
print("=" * 70)

print("\n✅ 中文测试:")
print("  • 智能测试编排器")
print("  • 资产收集")
print("  • 漏洞检测")
print("  • 漏洞验证")
print("  • 报告生成")

print("\n🎯 Emoji 测试:")
print("  • 🎯 目标")
print("  • 📊 报告")
print("  • ✅ 成功")
print("  • ❌ 失败")
print("  • ⏱️  时间")

print("\n📋 混合测试:")
print("  • 🚀 开始智能安全测试")
print("  • 🎯 目标：http://example.com")
print("  • 📊 模式：full")
print("  • ⏱️  时间限制：120 分钟")

print("\n" + "=" * 70)
print("  测试完成！如果能看到正常中文和 Emoji，说明编码正确 ✅")
print("=" * 70)
