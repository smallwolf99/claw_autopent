#!/usr/bin/env python3
"""
修复正则表达式中的双反斜杠
"""

with open('asset_normalizer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复URL正则表达式
fixed = content.replace(r"r'WhatWeb report for\\s+(https?://[^\\s]+)'", r"r'WhatWeb report for\s+(https?://[^\s]+)'")
fixed = fixed.replace(r"r'report for\\s+(https?://[^\\s]+)'", r"r'report for\s+(https?://[^\s]+)'")
fixed = fixed.replace(r"r'WhatWeb report for .*?\\s+(http[^\\s]+)'", r"r'WhatWeb report for .*?\s+(http[^\s]+)'")

with open('asset_normalizer.py', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("✅ 修复了正则表达式")

