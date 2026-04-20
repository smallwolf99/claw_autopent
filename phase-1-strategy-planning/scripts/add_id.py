#!/usr/bin/env python3
"""
在normalize_whatweb_text方法中添加id字段
"""

import re
import hashlib

with open('asset_normalizer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到normalize_whatweb_text方法中的StandardizedAsset创建部分
# 查找"asset = StandardizedAsset("
asset_creation = re.search(r'asset = StandardizedAsset\(([^)]+)\)', content, re.DOTALL)
if asset_creation:
    print("找到StandardizedAsset创建")
    # 在url参数后添加id参数
    # 但更简单的方法是在方法开头生成id
    pass

# 更好的方法：在方法开头生成id，然后添加到StandardizedAsset调用中
# 查找"url = "unknown" 或 url = match.group(1)"之后
url_assignment = re.search(r'(url = "[^"]+"|url = match\.group\(1\))', content)
if url_assignment:
    print(f"找到URL赋值: {url_assignment.group(0)}")

# 在URL赋值后插入id生成代码
url_pos = url_assignment.end()
# 查找下一个空行或注释
next_line = content.find('\n', url_pos)
if content.find('\n        ', next_line) == next_line:
    # 在URL赋值后插入id生成
    id_code = '''
        # 生成ID
        import hashlib
        if url and url != "unknown":
            id_str = f"{url}:{AssetCategory.WEB_APPLICATION}"
            asset_id = hashlib.md5(id_str.encode()).hexdigest()[:12]
        else:
            import datetime
            asset_id = "unknown_" + str(datetime.datetime.now().timestamp()).replace('.', '')[-8:]'''
    
    # 插入位置
    insert_pos = content.find('\n', url_pos) + 1
    content = content[:insert_pos] + id_code + content[insert_pos:]
    
    # 现在需要修改StandardizedAsset调用，添加id=asset_id
    # 查找"asset = StandardizedAsset("
    asset_call = re.search(r'asset = StandardizedAsset\(', content)
    if asset_call:
        # 找到括号内的参数
        start = asset_call.end()
        # 找到匹配的括号
        paren_count = 1
        pos = start
        while paren_count > 0 and pos < len(content):
            if content[pos] == '(':
                paren_count += 1
            elif content[pos] == ')':
                paren_count -= 1
            pos += 1
        end = pos
        
        asset_args = content[start:end-1]  # 去掉最后一个括号
        # 在参数开头添加id=asset_id,
        new_args = 'id=asset_id, ' + asset_args
        content = content[:start] + new_args + content[end-1:]
        
    print("✅ 添加了ID生成")

with open('asset_normalizer.py', 'w', encoding='utf-8') as f:
    f.write(content)

