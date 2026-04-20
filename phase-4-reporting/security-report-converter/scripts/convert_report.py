#!/usr/bin/env python3
"""
安全报告转换器 - 将Markdown安全扫描报告转换为HTML和PDF格式
"""

import os
import sys
import argparse
import datetime
import markdown
import yaml
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("错误: 缺少Jinja2库，请运行: pip3 install jinja2")
    sys.exit(1)

try:
    from weasyprint import HTML
except ImportError:
    print("错误: 缺少WeasyPrint库，请运行: pip3 install weasyprint")
    sys.exit(1)

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"警告: 无法读取配置文件: {e}")
    
    # 返回默认配置
    return {
        'templates': {
            'professional': 'template_professional.html',
            'simple': 'template_simple.html',
            'executive': 'template_executive.html'
        },
        'styles': {
            'professional': 'style_professional.css',
            'simple': 'style_simple.css',
            'executive': 'style_executive.css'
        },
        'output': {
            'html_extension': '.html',
            'pdf_extension': '.pdf'
        }
    }

def read_markdown_file(input_file):
    """读取Markdown文件内容"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except UnicodeDecodeError:
        # 尝试其他编码
        with open(input_file, 'r', encoding='gbk') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"错误: 无法读取文件 {input_file}: {e}")
        sys.exit(1)

def extract_title_from_markdown(content):
    """从Markdown内容中提取标题"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    # 如果没有找到标题，使用文件名
    return "安全扫描报告"

def convert_markdown_to_html(markdown_content, template_name='professional'):
    """将Markdown转换为HTML"""
    # 转换Markdown为HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    # 加载模板
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    template_file = f"template_{template_name}.html"
    if not (templates_dir / template_file).exists():
        print(f"警告: 模板 {template_file} 不存在，使用默认模板")
        template_file = "template_professional.html"
    
    try:
        template = env.get_template(template_file)
    except Exception as e:
        print(f"错误: 无法加载模板 {template_file}: {e}")
        sys.exit(1)
    
    # 准备模板变量
    template_vars = {
        'content': html_content,
        'generation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'template_name': template_name
    }
    
    # 渲染模板
    final_html = template.render(**template_vars)
    return final_html

def save_html(html_content, output_path):
    """保存HTML文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML报告已生成: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 无法保存HTML文件 {output_path}: {e}")
        return False

def save_pdf(html_content, output_path):
    """将HTML转换为PDF并保存"""
    try:
        # 使用WeasyPrint生成PDF
        HTML(string=html_content).write_pdf(output_path)
        print(f"✅ PDF报告已生成: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 无法生成PDF文件 {output_path}: {e}")
        print("提示: 可能需要安装系统字体: sudo apt-get install fonts-noto-cjk")
        return False

def main():
    parser = argparse.ArgumentParser(description='安全报告转换器 - Markdown转HTML/PDF')
    parser.add_argument('-i', '--input', required=True, help='输入Markdown文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件前缀（不含扩展名）')
    parser.add_argument('-f', '--format', choices=['html', 'pdf', 'all'], default='all', 
                       help='输出格式：html, pdf, all (默认: all)')
    parser.add_argument('-t', '--template', choices=['professional', 'simple', 'executive'], 
                       default='professional', help='模板类型 (默认: professional)')
    parser.add_argument('--title', help='报告标题（默认从文件提取）')
    parser.add_argument('--author', default='安全团队', help='报告作者 (默认: 安全团队)')
    parser.add_argument('--date', help='报告日期（默认当前日期）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    # 验证输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 读取Markdown内容
    if args.debug:
        print(f"📄 读取Markdown文件: {input_path}")
    
    markdown_content = read_markdown_file(input_path)
    
    # 提取标题（如果未指定）
    title = args.title
    if not title:
        title = extract_title_from_markdown(markdown_content)
    
    # 确定输出路径
    output_prefix = Path(args.output)
    html_path = output_prefix.with_suffix('.html')
    pdf_path = output_prefix.with_suffix('.pdf')
    
    # 创建输出目录（如果需要）
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    
    # 转换Markdown为HTML
    if args.debug:
        print(f"🔄 转换Markdown到HTML，使用模板: {args.template}")
    
    html_content = convert_markdown_to_html(markdown_content, args.template)
    
    # 生成HTML报告
    if args.format in ['html', 'all']:
        if not save_html(html_content, html_path):
            if args.format == 'html':  # 如果只生成HTML且失败，退出
                sys.exit(1)
    
    # 生成PDF报告
    if args.format in ['pdf', 'all']:
        if not save_pdf(html_content, pdf_path):
            if args.format == 'pdf':  # 如果只生成PDF且失败，退出
                sys.exit(1)
    
    print("🎉 报告生成完成！")
    if args.format in ['html', 'all'] and html_path.exists():
        print(f"   📄 HTML: {html_path}")
    if args.format in ['pdf', 'all'] and pdf_path.exists():
        print(f"   📊 PDF: {pdf_path}")

if __name__ == '__main__':
    main()