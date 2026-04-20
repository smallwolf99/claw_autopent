#!/usr/bin/env python3
"""
修复asset_normalizer.py中的URL提取
"""

import re

with open('asset_normalizer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到normalize_whatweb_text方法
method_start = content.find('def normalize_whatweb_text')
if method_start != -1:
    # 找到方法结束
    next_def = content.find('\n    def ', method_start + 10)
    class_end = content.find('\n\n', method_start + 10)
    method_end = next_def if next_def != -1 else class_end
    if method_end == -1:
        method_end = len(content)
    
    method = content[method_start:method_end]
    
    # 替换URL提取部分
    old_url_section = '''        # 简单的文本解析器
        url_match = re.search(r'WhatWeb report for .*?\\s+(http[^\\s]+)', clean_text)
        url = url_match.group(1) if url_match else "unknown"'''
    
    new_url_section = '''        # 改进的URL正则表达式，处理ANSI清理后的文本
        url_patterns = [
            r'WhatWeb report for\\\\s+(https?://[^\\\\s]+)',
            r'report for\\\\s+(https?://[^\\\\s]+)',
            r'WhatWeb report for .*?\\\\s+(http[^\\\\s]+)',
        ]
        
        url = "unknown"
        for pattern in url_patterns:
            match = re.search(pattern, clean_text)
            if match:
                url = match.group(1)
                break'''
    
    if old_url_section in method:
        method = method.replace(old_url_section, new_url_section)
        print("✅ 替换了URL提取部分")
    else:
        print("⚠️  未找到旧的URL提取部分，可能已经修改")
    
    # 更新整个方法
    content = content[:method_start] + method + content[method_end:]
    
    # 写入文件
    with open('asset_normalizer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("💾 文件已更新")

