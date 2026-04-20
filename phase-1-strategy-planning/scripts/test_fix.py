#!/usr/bin/env python3
"""
测试修复后的asset_normalizer.py
"""

import sys
sys.path.insert(0, '.')

# 测试原始修复版本
print("🧪 测试修复后的asset_normalizer.py")

# 导入修复版本
from asset_normalizer import AssetNormalizer

# 读取whatweb数据
whatweb_file = "/home/ubuntu/.openclaw/workspace-coder/tasks/2026-04-16__001__智能测试规划引擎/assets/whatweb_detailed.txt"
with open(whatweb_file, 'r', encoding='utf-8', errors='ignore') as f:
    whatweb_text = f.read()

print(f"📄 读取文件: {whatweb_file}")
print(f"📏 文件大小: {len(whatweb_text)} 字符")

# 创建标准化器
normalizer = AssetNormalizer()

try:
    asset = normalizer.normalize_whatweb_text(whatweb_text)
    print(f"\n✅ 解析成功!")
    print(f"   URL: {asset.url}")
    print(f"   ID: {asset.id}")
    print(f"   技术栈:")
    for t in asset.technologies:
        print(f"     - {t.name} {t.version or ''} (置信度: {t.confidence})")
    
    print(f"   业务类型: {asset.business_hints.type} (置信度: {asset.business_hints.confidence})")
    
    # 验证
    assert asset.url == "http://zero.webappsecurity.com", f"URL不匹配: {asset.url}"
    assert len(asset.technologies) >= 3, f"技术栈数量不足: {len(asset.technologies)}"
    assert asset.business_hints.type == "banking", f"业务类型不是banking: {asset.business_hints.type}"
    
    print("\n✅ 所有验证通过!")
    
    # 测试load_from_file方法
    print("\n📁 测试load_from_file方法...")
    assets = normalizer.load_from_file(whatweb_file, "whatweb_text")
    print(f"✅ 成功加载 {len(assets)} 个资产")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

