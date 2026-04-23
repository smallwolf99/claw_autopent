#!/usr/bin/env python3
"""
katana Web 爬虫技能 - 跨平台优化版
功能：Web 页面爬取、目录枚举、端点发现、JS 解析、表单提取
"""
import subprocess
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """验证是否为有效 URL"""
    try:
        result = urlparse(url)
        return result.scheme in ('http', 'https') and bool(result.netloc)
    except Exception:
        return False


def find_katana_executable() -> str:
    """
    跨平台查找 katana 可执行文件
    优先级：环境变量 > 系统 PATH > 常见安装路径
    """
    # 1. 环境变量优先
    if env_path := os.environ.get("KATANA_PATH"):
        if Path(env_path).exists():
            return env_path
    
    # 2. 系统 PATH 查找
    if katana_path := shutil.which("katana"):
        return katana_path
    
    # 3. 常见安装路径（跨平台）
    possible_paths = []
    
    # Windows 路径
    if sys.platform == 'win32':
        possible_paths.extend([
            Path(os.environ.get("USERPROFILE", "~")) / "bin" / "katana.exe",
            Path("C:/Program Files/katana/katana.exe"),
            Path("~/bin/katana.exe").expanduser(),
        ])
    # Unix/Linux/macOS 路径
    else:
        possible_paths.extend([
            Path("/usr/local/bin/katana"),
            Path("/usr/bin/katana"),
            Path("~/bin/katana").expanduser(),
            Path("/usr/local/go/bin/katana"),
        ])
    
    # 4. 检查路径是否存在
    for path in possible_paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    
    # 5. 未找到，返回默认值并提示
    print("警告：未找到 katana 可执行文件", file=sys.stderr)
    print("请安装：go install github.com/projectdiscovery/katana/cmd/katana@latest", 
          file=sys.stderr)
    print("或设置环境变量：export KATANA_PATH=/path/to/katana", file=sys.stderr)
    return "katana"


def parse_targets(targets: Union[str, List[str]]) -> tuple:
    """
    智能解析目标，返回 (URL 列表，临时文件路径)
    支持：单个 URL、URL 列表、文件路径、逗号分隔字符串
    """
    temp_file = None
    
    # 列表类型直接返回
    if isinstance(targets, list):
        return targets, None
    
    # 字符串类型需要解析
    targets = targets.strip()
    
    # 检查是否为文件
    if Path(targets).exists() and Path(targets).is_file():
        with open(targets, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls, None
    
    # 逗号分隔的多个 URL
    if ',' in targets:
        urls = [t.strip() for t in targets.split(',') if t.strip()]
        if len(urls) > 1:
            return urls, None
    
    # 单个 URL
    if is_valid_url(targets):
        return [targets], None
    
    # 尝试作为文件路径（可能不存在）
    if Path(targets).suffix in ['.txt', '.lst']:
        return [], Path(targets)
    
    # 默认为单个 URL
    return [targets], None


def run_katana(
    targets: Union[str, List[str]],
    depth: int = 3,
    headless: bool = False,
    js_crawl: bool = False,
    form_extraction: bool = False,
    xhr_crawl: bool = False,
    scope_filter: str = "",
    exclude_scope: str = "",
    extensions_match: str = "",
    filter_status: str = "",
    rate_limit: int = 0,
    delay: float = 0.0,
    proxy: str = "",
    output_format: str = "jsonl",
    output_file: Optional[str] = None,
    fields: str = "url",
    silent: bool = True,
    timeout: int = 300,
    concurrency: Optional[int] = None,
) -> str:
    """
    执行 katana 爬取
    
    Args:
        targets: 目标 URL（支持多种格式）
        depth: 爬取深度（默认 3）
        headless: 无头模式（默认 False）
        js_crawl: JS 端点解析（默认 False）
        form_extraction: 表单提取（默认 False）
        xhr_crawl: XHR 爬取（默认 False）
        scope_filter: 范围过滤正则
        exclude_scope: 排除范围正则
        extensions_match: 扩展名匹配（逗号分隔）
        filter_status: 状态码过滤
        rate_limit: 速率限制（请求/秒，0 表示不限）
        delay: 请求延迟（秒）
        proxy: 代理地址
        output_format: 输出格式（jsonl/txt/csv）
        output_file: 输出文件路径
        fields: 输出字段（逗号分隔）
        silent: 静默模式（默认 True）
        timeout: 超时时间（秒）
        concurrency: 并发数
    
    Returns:
        katana 输出结果
    """
    katana_cmd = find_katana_executable()
    base_cmd = [katana_cmd]
    
    # 解析目标
    url_list, temp_file = parse_targets(targets)
    
    # 构建命令参数
    if url_list:
        if len(url_list) == 1:
            base_cmd.extend(["-u", url_list[0]])
        else:
            # 多个 URL 使用临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.txt', 
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write('\n'.join(url_list))
                temp_path = f.name
            
            base_cmd.extend(["-list", temp_path])
            temp_file = Path(temp_path)
    elif temp_file:
        base_cmd.extend(["-list", str(temp_file)])
    
    # 核心功能参数
    base_cmd.extend(["-d", str(depth)])
    
    if headless:
        base_cmd.append("-hl")
    
    if js_crawl:
        base_cmd.append("-jc")
    
    if form_extraction:
        base_cmd.append("-fx")
    
    if xhr_crawl:
        base_cmd.append("-xhr")
    
    # 范围控制
    if scope_filter:
        base_cmd.extend(["-cs", scope_filter])
    
    if exclude_scope:
        base_cmd.extend(["-cos", exclude_scope])
    
    # 过滤参数
    if extensions_match:
        base_cmd.extend(["-em", extensions_match])
    
    if filter_status:
        base_cmd.extend(["-fdc", filter_status])
    
    # 速率控制
    if rate_limit > 0:
        base_cmd.extend(["-rl", str(rate_limit)])
    
    if delay > 0:
        base_cmd.extend(["-rd", str(delay)])
    
    # 代理
    if proxy:
        base_cmd.extend(["-proxy", proxy])
    
    # 输出控制
    if output_format == "jsonl":
        base_cmd.append("-j")
    elif output_format == "json":
        base_cmd.append("-oJ")
    
    if output_file:
        base_cmd.extend(["-o", output_file])
    
    # 输出字段
    if fields != "url":
        base_cmd.extend(["-f", fields])
    
    # 静默模式
    if silent:
        base_cmd.append("-silent")
    
    # 并发控制
    if concurrency:
        base_cmd.extend(["-c", str(concurrency)])
    
    # 动态调整超时（基于深度和目标数量）
    dynamic_timeout = max(timeout, depth * 30 + len(url_list) * 10) if url_list else timeout
    
    try:
        result = subprocess.run(
            base_cmd,
            capture_output=True,
            text=True,
            timeout=dynamic_timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout
        
        # 错误处理
        if result.returncode != 0:
            error_info = {
                "status": "error",
                "command": " ".join(base_cmd),
                "exit_code": result.returncode,
                "stderr": result.stderr,
                "reason": f"katana 执行失败 (退出码：{result.returncode})"
            }
            return json.dumps(error_info, ensure_ascii=False, indent=2)
        
        return output
    
    except subprocess.TimeoutExpired:
        error_info = {
            "status": "error",
            "command": " ".join(base_cmd),
            "reason": f"执行超时 ({dynamic_timeout}秒)"
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_info = {
            "status": "error",
            "command": " ".join(base_cmd),
            "reason": str(e)
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)
    
    finally:
        # 清理临时文件
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass


def parse_katana_jsonl(content: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """解析 katana JSON Lines 输出"""
    try:
        results = []
        for line in content.strip().splitlines():
            line = line.strip()
            if line and line.startswith('{'):
                results.append(json.loads(line))
        return results
    except json.JSONDecodeError as e:
        return {"status": "parse_error", "reason": str(e), "content": content[:200]}


def crawl(
    targets: Union[str, List[str]],
    depth: int = 3,
    headless: bool = False,
    js_crawl: bool = False,
    form_extraction: bool = False,
    output_format: str = "jsonl",
    rate_limit: int = 50,
    delay: float = 0.2,
    timeout: int = 300,
    concurrency: int = 10,
) -> Dict[str, Any]:
    """
    标准爬取接口（符合 skill.json 定义）
    
    Args:
        targets: 目标 URL 列表或文件路径
        depth: 爬取深度
        headless: 无头模式
        js_crawl: JS 端点解析
        form_extraction: 表单提取
        output_format: 输出格式
        rate_limit: 速率限制
        delay: 请求延迟
        timeout: 超时时间
        concurrency: 并发数
    
    Returns:
        结构化结果
    """
    output = run_katana(
        targets=targets,
        depth=depth,
        headless=headless,
        js_crawl=js_crawl,
        form_extraction=form_extraction,
        output_format=output_format,
        rate_limit=rate_limit,
        delay=delay,
        timeout=timeout,
        concurrency=concurrency,
    )
    
    # 尝试解析 JSON
    if output_format in ["jsonl", "json"]:
        try:
            parsed = parse_katana_jsonl(output)
            if isinstance(parsed, list):
                return {
                    "status": "success",
                    "count": len(parsed),
                    "results": parsed,
                    "unique_urls": len(set(r.get('url', '') for r in parsed)),
                }
        except Exception:
            pass
    
    return {"status": "success", "output": output}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="katana Web 爬虫技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速爬取（默认深度 3）
  python main.py -u https://example.com
  
  # JS 端点解析 + 深度 5
  python main.py -u https://example.com --js-crawl --depth 5
  
  # 无头模式（适用于 SPA/React/Angular）
  python main.py -u https://example.com --headless
  
  # 表单提取
  python main.py -u https://example.com --form-extraction
  
  # 批量爬取（文件输入）
  python main.py -l urls.txt --depth 3
  
  # 限速爬取
  python main.py -u https://example.com --rate-limit 30 --delay 0.5
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--url", type=str, help="单个目标 URL")
    group.add_argument("-l", "--list", type=str, help="目标文件路径")
    group.add_argument("--targets", type=str, help="目标（兼容旧版）")
    
    parser.add_argument("--depth", "-d", type=int, default=3,
                       help="爬取深度 (默认：3, 范围：1-10)")
    parser.add_argument("--headless", "-hl", action="store_true",
                       help="无头模式（渲染 JS，适用于 SPA）")
    parser.add_argument("--js-crawl", "-jc", action="store_true",
                       help="JS 端点解析")
    parser.add_argument("--form-extraction", "-fx", action="store_true",
                       help="提取表单和输入字段")
    parser.add_argument("--xhr-crawl", action="store_true",
                       help="XHR 请求爬取")
    parser.add_argument("--scope", type=str, default="",
                       help="范围过滤正则（仅爬取匹配域名）")
    parser.add_argument("--exclude-scope", type=str, default="",
                       help="排除范围正则")
    parser.add_argument("--extensions", type=str, default="",
                       help="扩展名匹配（逗号分隔，如 php,html,js）")
    parser.add_argument("--filter-status", type=str, default="",
                       help="状态码过滤（如 'status_code >= 200 && status_code < 400'）")
    parser.add_argument("--rate-limit", type=int, default=50,
                       help="速率限制 (请求/秒，默认：50)")
    parser.add_argument("--delay", type=float, default=0.2,
                       help="请求延迟 (秒，默认：0.2)")
    parser.add_argument("--proxy", type=str, default="",
                       help="代理地址（如 http://127.0.0.1:7890）")
    parser.add_argument("--format", type=str, default="jsonl",
                       choices=["jsonl", "json", "txt"], help="输出格式")
    parser.add_argument("--output", "-o", type=str, default="",
                       help="输出文件路径")
    parser.add_argument("--fields", type=str, default="url",
                       help="输出字段（逗号分隔）")
    parser.add_argument("--concurrency", "-c", type=int, default=10,
                       help="并发数 (默认：10)")
    parser.add_argument("--timeout", type=int, default=300,
                       help="超时时间 (秒，默认：300)")
    parser.add_argument("--parse", action="store_true",
                       help="二次结构化 JSON 输出")
    
    args = parser.parse_args()
    
    # 验证深度范围
    if args.depth < 1 or args.depth > 10:
        print("错误：爬取深度必须在 1-10 之间", file=sys.stderr)
        sys.exit(1)
    
    # 确定目标
    targets = args.url or args.list or args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)
    
    # 执行爬取
    output = run_katana(
        targets=targets,
        depth=args.depth,
        headless=args.headless,
        js_crawl=args.js_crawl,
        form_extraction=args.form_extraction,
        xhr_crawl=args.xhr_crawl,
        scope_filter=args.scope,
        exclude_scope=args.exclude_scope,
        extensions_match=args.extensions,
        filter_status=args.filter_status,
        rate_limit=args.rate_limit,
        delay=args.delay,
        proxy=args.proxy,
        output_format=args.format,
        output_file=args.output if args.output else None,
        fields=args.fields,
        concurrency=args.concurrency,
        timeout=args.timeout,
    )
    
    # 输出结果
    if args.parse and args.format in ["jsonl", "json"]:
        print(json.dumps(parse_katana_jsonl(output), indent=2, ensure_ascii=False))
    else:
        print(output)
