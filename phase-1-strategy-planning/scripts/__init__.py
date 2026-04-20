#!/usr/bin/env python3
"""
智能测试规划引擎 - Phase 0
将专家经验固化为可复用的系统能力，从"工具驱动"盲目扫描转向"情报驱动"针对性测试。

核心流程: 资产收集 → 资产地图测绘 → 风险画像生成 → 针对性测试策略

四大核心模块:
1. Asset Normalizer - 资产标准化器
2. Risk Profiler - 风险画像器
3. Rule Engine - 规则引擎  
4. Test Strategist - 测试策略器

版本: v0.1.0 (MVP)
创建日期: 2026-04-16
"""

__version__ = "0.1.0"
__author__ = "高级安全渗透测试专家团队"

import sys
import json
from pathlib import Path

# 确保父目录在Python路径中
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 导出主要模块
__all__ = [
    "asset_normalizer",
    "rule_engine", 
    "strategist",
]

print(f"🧠 智能测试规划引擎 v{__version__} 已加载")
print("🎯 目标: 将专家经验固化为可复用的系统能力")
print("🔄 流程: 资产收集 → 地图测绘 → 风险画像 → 针对性测试策略")