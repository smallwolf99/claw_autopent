"""
Markdown 封面报告转换工具
将 Markdown 格式的封面报告转换为 HTML 和 PDF
"""

from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime


def read_template(template_path):
    """读取模板文件"""
    return Path(template_path).read_text(encoding='utf-8')


def replace_variables(content, context):
    """替换模板变量"""
    for key, value in context.items():
        # 替换 {{ key }} 格式的变量
        pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        content = re.sub(pattern, str(value), content, flags=re.IGNORECASE)
    return content


def markdown_to_html(markdown_content, css_path=None):
    """
    将 Markdown 内容转换为 HTML
    简单实现，支持基本 Markdown 语法
    """
    html = markdown_content
    
    # 处理代码块
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # 处理行内代码
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 处理标题
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # 处理粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # 处理列表
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # 处理引用
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # 处理分隔线
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    
    # 处理表格（简化版）
    # 这里可以添加更复杂的表格解析逻辑
    
    # 处理段落
    paragraphs = html.split('\n\n')
    processed_paragraphs = []
    for p in paragraphs:
        if p.strip() and not p.strip().startswith('<'):
            processed_paragraphs.append(f'<p>{p.strip()}</p>')
        else:
            processed_paragraphs.append(p)
    
    html = '\n'.join(processed_paragraphs)
    
    return html


def create_html_report(markdown_path, output_path, context, css_path=None):
    """创建 HTML 报告"""
    # 读取 Markdown 模板
    markdown_content = read_template(markdown_path)
    
    # 替换变量
    content = replace_variables(markdown_content, context)
    
    # 转换为 HTML
    html_content = markdown_to_html(content)
    
    # 添加 HTML 包装
    html_wrapper = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>安全渗透测试报告</title>
    {"<link rel='stylesheet' href='" + css_path + "'>" if css_path else ""}
</head>
<body>
    {html_content}
</body>
</html>"""
    
    # 保存 HTML
    Path(output_path).write_text(html_wrapper, encoding='utf-8')
    print(f"✓ HTML 报告已生成：{output_path}")
    
    return output_path


def convert_to_pdf(input_path, output_path, css_path=None):
    """
    转换为 PDF（需要 Pandoc 和 wkhtmltopdf）
    """
    try:
        # 检查 Pandoc 是否安装
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            print("✗ Pandoc 未安装，请先安装 Pandoc")
            print("  Windows: choco install pandoc")
            print("  macOS: brew install pandoc")
            print("  Linux: sudo apt-get install pandoc")
            return None
        
        # 构建 Pandoc 命令
        cmd = [
            'pandoc',
            str(input_path),
            '-o', str(output_path),
            '--pdf-engine=wkhtmltopdf',
            '--variable', 'paper-size=a4',
            '--variable', 'margin-top=0mm',
            '--variable', 'margin-bottom=0mm',
            '--variable', 'margin-left=0mm',
            '--variable', 'margin-right=0mm'
        ]
        
        if css_path:
            cmd.extend(['--css', str(css_path)])
        
        # 执行转换
        print(f"正在转换 PDF...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✓ PDF 报告已生成：{output_path}")
            return output_path
        else:
            print(f"✗ PDF 转换失败：{result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("✗ PDF 转换超时")
        return None
    except FileNotFoundError as e:
        print(f"✗ 找不到命令：{e}")
        print("  请确保已安装 Pandoc 和 wkhtmltopdf")
        return None


def main():
    """主函数"""
    # 示例上下文数据
    context = {
        'report.target_name': 'DVWA 系统',
        'report.target_url': 'http://dvwa.example.com',
        'report.target_ip': '192.168.1.100',
        'report.target_port': '80',
        'report.test_time': '2026-04-23 10:00:00',
        'report.report_date': '2026-04-23',
        'report.overall_risk': '极度危险',
        'report.risk_level': '危急',
        'report.total_vulnerabilities': '18',
        'report.high_count': '12',
        'report.medium_count': '2',
        'report.low_count': '3',
        'report.info_count': '4'
    }
    
    # 文件路径
    base_dir = Path(__file__).parent
    markdown_template = base_dir / 'markdown-cover-template.md'
    css_file = base_dir / 'markdown-cover-styles.css'
    output_dir = base_dir / 'output'
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 生成 HTML
    html_output = output_dir / 'test-report.html'
    create_html_report(markdown_template, html_output, context, css_file)
    
    # 生成 PDF
    pdf_output = output_dir / 'test-report.pdf'
    convert_to_pdf(markdown_template, pdf_output, css_file)
    
    print("\n完成！")
    print(f"HTML: {html_output}")
    print(f"PDF:  {pdf_output if pdf_output else '转换失败，请检查是否安装了 Pandoc 和 wkhtmltopdf'}")


if __name__ == '__main__':
    main()
