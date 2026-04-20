#!/usr/bin/env python3
"""
补丁asset_normalizer.py文件
"""

import re
import shutil
from pathlib import Path

def main():
    original_path = Path("asset_normalizer.py")
    backup_path = original_path.with_suffix(".py.backup")
    
    # 创建备份
    shutil.copy2(original_path, backup_path)
    print(f"📋 已创建备份: {backup_path}")
    
    # 读取原始内容
    content = original_path.read_text(encoding='utf-8')
    
    # 1. 在AssetNormalizer类中添加_strip_ansi_codes方法
    class_pos = content.find('class AssetNormalizer:')
    if class_pos != -1:
        # 找到第一个def
        first_def = content.find('def ', class_pos)
        # 在第一个def之前插入新方法
        insert_pos = content.rfind('\n', class_pos, first_def)
        
        strip_method = '''
    def _strip_ansi_codes(self, text: str) -> str:
        """去除ANSI颜色代码"""
        import re
        ansi_escape = re.compile(r'\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
'''
        content = content[:insert_pos] + strip_method + content[insert_pos:]
        print("✅ 添加了_strip_ansi_codes方法")
    
    # 2. 修改normalize_whatweb_text方法
    method_start = content.find('def normalize_whatweb_text')
    if method_start != -1:
        # 找到方法结束
        next_def = content.find('\n    def ', method_start + 10)
        class_end = content.find('\n\n', method_start + 10)
        method_end = next_def if next_def != -1 else class_end
        if method_end == -1:
            method_end = len(content)
        
        method = content[method_start:method_end]
        
        # 在方法开头添加clean_text
        if '"""解析WhatWeb文本输出为标准化资产"""' in method:
            method = method.replace(
                '"""解析WhatWeb文本输出为标准化资产"""', 
                '"""解析WhatWeb文本输出为标准化资产"""\n        # 去除ANSI颜色代码\n        clean_text = self._strip_ansi_codes(text_data)'
            )
            
            # 替换URL提取逻辑
            old_pattern = "url_match = re.search(r'WhatWeb report for .*?\\\\s+(http[^\\\\s]+)', text_data)"
            if old_pattern in method:
                new_url_logic = '''        # 改进的URL正则表达式，处理ANSI清理后的文本
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
                
                # 替换整个URL提取部分
                import re as re2
                method = re2.sub(
                    r"url_match = re.search\(r'WhatWeb report for \.*?\\s\+\(http\[\^\\s\]\+\)', text_data\)\s*url = url_match\.group\(1\) if url_match else \"unknown\"",
                    new_url_logic,
                    method
                )
            
            # 将所有text_data替换为clean_text（除了参数声明）
            lines = method.split('\n')
            for i in range(len(lines)):
                if 'text_data' in lines[i] and not ('def normalize_whatweb_text' in lines[i] or 'text_data: str' in lines[i]):
                    lines[i] = lines[i].replace('text_data', 'clean_text')
            method = '\n'.join(lines)
            
            # 替换原方法
            content = content[:method_start] + method + content[method_end:]
            print("✅ 修改了normalize_whatweb_text方法")
    
    # 保存修复版本
    fixed_path = original_path.with_suffix(".py.fixed")
    fixed_path.write_text(content, encoding='utf-8')
    print(f"💾 修复版本已保存: {fixed_path}")
    
    # 简单测试
    print("\n🧪 简单测试修复...")
    test_text = "WhatWeb report for \x1b[1m\x1b[34mhttp://zero.webappsecurity.com\x1b[0m"
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean = ansi_escape.sub('', test_text)
    print(f"原始: {repr(test_text)}")
    print(f"清理后: {repr(clean)}")
    
    url_match = re.search(r'WhatWeb report for\s+(https?://[^\s]+)', clean)
    if url_match:
        print(f"✅ URL提取成功: {url_match.group(1)}")
    else:
        print("❌ URL提取失败")
    
    print(f"\n📋 总结:")
    print(f"  备份: {backup_path}")
    print(f"  修复: {fixed_path}")
    print(f"  要应用修复: cp {fixed_path} {original_path}")

if __name__ == "__main__":
    main()
