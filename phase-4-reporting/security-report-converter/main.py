#!/usr/bin/env python3
"""
security-report-converter 安全报告转换技能 - 跨平台优化版
功能：Markdown 安全扫描报告转 HTML/PDF 专业格式报告
"""
import subprocess
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple
from datetime import datetime
import re


def check_dependencies() -> Dict[str, bool]:
    """
    检查依赖库是否已安装
    返回：{库名：是否已安装}
    """
    deps = {
        "markdown": False,
        "jinja2": False,
        "weasyprint": False,
        "yaml": False,
    }
    
    try:
        import markdown
        deps["markdown"] = True
    except ImportError:
        pass
    
    try:
        import jinja2
        deps["jinja2"] = True
    except ImportError:
        pass
    
    try:
        import weasyprint
        deps["weasyprint"] = True
    except ImportError:
        pass
    
    try:
        import yaml
        deps["yaml"] = True
    except ImportError:
        pass
    
    return deps


def install_dependencies():
    """自动安装缺失的依赖"""
    deps = check_dependencies()
    missing = [name for name, installed in deps.items() if not installed]
    
    if not missing:
        return True
    
    print(f"[INFO] 检测到缺失的依赖：{', '.join(missing)}")
    print("[INFO] 正在自动安装...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q",
            "markdown", "jinja2", "weasyprint", "pyyaml"
        ])
        print("[INFO] 依赖安装完成")
        return True
    except Exception as e:
        print(f"[ERROR] 依赖安装失败：{e}")
        print("[HINT] 请手动运行：pip install markdown jinja2 weasyprint pyyaml")
        return False


def find_templates_dir() -> Optional[Path]:
    """
    跨平台查找模板目录
    优先级：当前目录 templates > 脚本同级 templates > 常见路径
    """
    possible_paths = [
        Path.cwd() / "templates",
        Path(__file__).parent / "templates",
        Path(__file__).parent.parent / "templates",
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    return None


def load_config(config_file: str = "") -> Dict[str, Any]:
    """
    加载配置文件
    支持：YAML/JSON/默认配置
    """
    if not config_file:
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config.yaml"
        )
    
    config_path = Path(config_file)
    
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    
    # 默认配置
    return {
        "templates": {
            "professional": "template_professional.html",
            "simple": "template_simple.html",
            "executive": "template_executive.html"
        },
        "styles": {
            "professional": "style_professional.css",
            "simple": "style_simple.css",
            "executive": "style_executive.css"
        },
        "output": {
            "html_extension": ".html",
            "pdf_extension": ".pdf"
        },
        "fonts": {
            "chinese": ["Noto Sans CJK SC", "SimSun", "Microsoft YaHei"],
            "fallback": "sans-serif"
        }
    }


def read_markdown_file(input_file: str) -> Tuple[str, str]:
    """
    读取 Markdown 文件内容
    返回：(文件内容，编码格式)
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise IOError(f"无法读取文件 {input_file}: {e}")
    
    raise IOError(f"无法解码文件 {input_file}，尝试的编码：{encodings}")


def extract_title_from_markdown(content: str, default: str = "安全扫描报告") -> str:
    """
    从 Markdown 内容中提取标题
    优先级：H1 标题 > 文件名 > 默认值
    """
    lines = content.split('\n')
    
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            if title:
                return title
    
    return default


def convert_markdown_to_html(
    markdown_content: str,
    template_name: str = "professional",
    title: str = "",
    author: str = "安全团队",
    report_date: str = "",
    extra_vars: Dict[str, Any] = None,
) -> str:
    """
    将 Markdown 转换为 HTML
    
    Args:
        markdown_content: Markdown 内容
        template_name: 模板名称
        title: 报告标题
        author: 报告作者
        report_date: 报告日期
        extra_vars: 额外模板变量
    
    Returns:
        HTML 内容
    """
    try:
        import markdown
        from jinja2 import Environment, FileSystemLoader
    except ImportError as e:
        raise ImportError(f"缺少必要的依赖库：{e}")
    
    # 转换 Markdown 为 HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br'
        ]
    )
    
    # 查找模板目录
    templates_dir = find_templates_dir()
    
    if not templates_dir:
        # 使用内置简单模板
        return create_simple_html_report(
            html_content=html_content,
            title=title,
            author=author,
            report_date=report_date or datetime.now().strftime('%Y-%m-%d')
        )
    
    # 加载模板
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=True
    )
    
    template_file = f"template_{template_name}.html"
    
    if not (templates_dir / template_file).exists():
        template_file = "template_professional.html"
        if not (templates_dir / template_file).exists():
            # 回退到简单模板
            return create_simple_html_report(
                html_content=html_content,
                title=title,
                author=author,
                report_date=report_date or datetime.now().strftime('%Y-%m-%d')
            )
    
    template = env.get_template(template_file)
    
    # 准备模板变量
    template_vars = {
        "content": html_content,
        "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "template_name": template_name,
        "title": title,
        "author": author,
        "report_date": report_date or datetime.now().strftime('%Y-%m-%d'),
    }
    
    if extra_vars:
        template_vars.update(extra_vars)
    
    # 渲染模板
    final_html = template.render(**template_vars)
    return final_html


def create_simple_html_report(
    html_content: str,
    title: str,
    author: str,
    report_date: str,
) -> str:
    """
    创建简单的 HTML 报告（无模板时使用）
    """
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #2c3e50;
        }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", Courier, monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        <p>作者：{author} | 生成日期：{report_date}</p>
    </div>
    {html_content}
</body>
</html>"""


def save_html(html_content: str, output_path: str) -> bool:
    """
    保存 HTML 文件
    自动创建目录，确保 UTF-8 编码
    """
    try:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return True
    except Exception as e:
        print(f"[ERROR] 无法保存 HTML 文件 {output_path}: {e}")
        return False


def save_pdf(html_content: str, output_path: str, fonts: List[str] = None) -> bool:
    """
    将 HTML 转换为 PDF 并保存
    支持中文字体配置
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontManager
    except ImportError as e:
        print(f"[ERROR] 缺少 WeasyPrint 库：{e}")
        print("[HINT] 请运行：pip install weasyprint")
        return False
    
    try:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置中文字体
        font_config = ""
        if fonts:
            font_list = ", ".join([f'"{f}"' for f in fonts])
            font_config = f"""
            @font-face {{
                font-family: 'ChineseFallback';
                src: local('Noto Sans CJK SC'), local('SimSun'), local('Microsoft YaHei');
            }}
            body {{ font-family: {font_list}, sans-serif; }}
            """
        
        # 添加字体配置到 HTML
        if font_config:
            html_with_fonts = html_content.replace(
                '</head>',
                f'<style>{font_config}</style></head>'
            )
        else:
            html_with_fonts = html_content
        
        # 生成 PDF
        HTML(string=html_with_fonts).write_pdf(output_path)
        
        return True
    except Exception as e:
        print(f"[ERROR] 无法生成 PDF 文件 {output_path}: {e}")
        print("[HINT] 可能需要安装中文字体：sudo apt-get install fonts-noto-cjk")
        return False


def convert_report(
    input_file: str,
    output_prefix: str,
    output_format: str = "all",
    template_name: str = "professional",
    title: str = "",
    author: str = "安全团队",
    report_date: str = "",
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    转换报告为主函数
    
    Args:
        input_file: 输入 Markdown 文件路径
        output_prefix: 输出文件前缀（不含扩展名）
        output_format: 输出格式（html/pdf/all）
        template_name: 模板名称
        title: 报告标题
        author: 报告作者
        report_date: 报告日期
        config: 配置字典
    
    Returns:
        转换结果信息
    """
    result = {
        "status": "success",
        "input_file": input_file,
        "output_files": [],
        "errors": []
    }
    
    # 检查输入文件
    if not Path(input_file).exists():
        result["status"] = "error"
        result["errors"].append(f"输入文件不存在：{input_file}")
        return result
    
    # 读取 Markdown 文件
    try:
        markdown_content, encoding = read_markdown_file(input_file)
        result["encoding"] = encoding
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        return result
    
    # 提取标题
    if not title:
        title = extract_title_from_markdown(markdown_content)
    
    # 转换 Markdown 为 HTML
    try:
        html_content = convert_markdown_to_html(
            markdown_content=markdown_content,
            template_name=template_name,
            title=title,
            author=author,
            report_date=report_date,
        )
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"HTML 转换失败：{e}")
        return result
    
    # 保存文件
    if output_format in ("html", "all"):
        html_path = f"{output_prefix}.html"
        if save_html(html_content, html_path):
            result["output_files"].append(html_path)
        else:
            result["errors"].append(f"HTML 保存失败：{html_path}")
    
    if output_format in ("pdf", "all"):
        pdf_path = f"{output_prefix}.pdf"
        fonts = config.get("fonts", {}).get("chinese", []) if config else []
        if save_pdf(html_content, pdf_path, fonts):
            result["output_files"].append(pdf_path)
        else:
            result["errors"].append(f"PDF 生成失败：{pdf_path}")
    
    # 汇总结果
    if result["errors"]:
        result["status"] = "partial_success"
    
    result["title"] = title
    result["template"] = template_name
    result["generation_time"] = datetime.now().isoformat()
    
    return result


def scan(
    input_file: str,
    output_prefix: str,
    output_format: str = "all",
    template_name: str = "professional",
    title: str = "",
    author: str = "安全团队",
    report_date: str = "",
    config_file: str = "",
) -> Dict[str, Any]:
    """
    标准扫描接口（符合 skill.json 定义）
    
    Args:
        input_file: 输入 Markdown 文件路径
        output_prefix: 输出文件前缀
        output_format: 输出格式（html/pdf/all）
        template_name: 模板名称
        title: 报告标题
        author: 报告作者
        report_date: 报告日期
        config_file: 配置文件路径
    
    Returns:
        结构化结果
    """
    config = load_config(config_file)
    
    result = convert_report(
        input_file=input_file,
        output_prefix=output_prefix,
        output_format=output_format,
        template_name=template_name,
        title=title,
        author=author,
        report_date=report_date,
        config=config,
    )
    
    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="security-report-converter 安全报告转换技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个 Markdown 文件（生成 HTML+PDF）
  python main.py -i report.md -o report
  
  # 仅生成 HTML
  python main.py -i report.md -o report --format html
  
  # 仅生成 PDF
  python main.py -i report.md -o report --format pdf
  
  # 指定模板
  python main.py -i report.md -o report --template professional
  
  # 自定义标题和作者
  python main.py -i report.md -o report --title "渗透测试报告" --author "安全团队"
  
  # 指定输出目录
  python main.py -i report.md -o /path/to/output/report
  
  # 自动安装依赖
  python main.py --install-deps
        """
    )
    
    parser.add_argument("-i", "--input", type=str, required=True,
                       help="输入 Markdown 文件路径")
    parser.add_argument("-o", "--output", type=str, required=True,
                       help="输出文件前缀（不含扩展名）")
    parser.add_argument("-f", "--format", type=str, default="all",
                       choices=["html", "pdf", "all"],
                       help="输出格式：html, pdf, all (默认：all)")
    parser.add_argument("-t", "--template", type=str, default="professional",
                       choices=["professional", "simple", "executive"],
                       help="模板类型 (默认：professional)")
    parser.add_argument("--title", type=str, default="",
                       help="报告标题（默认从文件提取）")
    parser.add_argument("--author", type=str, default="安全团队",
                       help="报告作者 (默认：安全团队)")
    parser.add_argument("--date", type=str, default="",
                       help="报告日期（默认当前日期）")
    parser.add_argument("--config", type=str, default="",
                       help="配置文件路径")
    parser.add_argument("--install-deps", action="store_true",
                       help="自动安装依赖")
    parser.add_argument("--debug", action="store_true",
                       help="启用调试模式")
    
    args = parser.parse_args()
    
    # 安装依赖
    if args.install_deps:
        success = install_dependencies()
        sys.exit(0 if success else 1)
    
    # 检查依赖
    deps = check_dependencies()
    missing = [name for name, installed in deps.items() if not installed]
    
    if missing:
        print(f"[WARNING] 检测到缺失的依赖：{', '.join(missing)}")
        print("[HINT] 运行 --install-deps 自动安装，或手动运行：")
        print("       pip install " + " ".join(missing))
        print()
    
    # 加载配置
    config = load_config(args.config)
    
    # 执行转换
    result = convert_report(
        input_file=args.input,
        output_prefix=args.output,
        output_format=args.format,
        template_name=args.template,
        title=args.title,
        author=args.author,
        report_date=args.date,
        config=config,
    )
    
    # 输出结果
    if args.debug:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["status"] in ("success", "partial_success"):
            print(f"[OK] 报告转换完成")
            print(f"  标题：{result.get('title', 'N/A')}")
            print(f"  模板：{result.get('template', 'N/A')}")
            print(f"  生成文件:")
            for file_path in result.get("output_files", []):
                print(f"    - {file_path}")
            
            if result.get("errors"):
                print(f"  警告:")
                for error in result["errors"]:
                    print(f"    - {error}")
        else:
            print(f"[ERROR] 报告转换失败")
            for error in result.get("errors", []):
                print(f"  - {error}")
    
    sys.exit(0 if result["status"] in ("success", "partial_success") else 1)
