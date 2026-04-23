#!/usr/bin/env python3
"""
httpx Web 资产探测技能 - 跨平台优化版
功能：批量存活探测与 Web 信息采集
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


def find_httpx_executable() -> str:
    """
    跨平台查找 httpx 可执行文件
    优先级：环境变量 > 系统 PATH > 常见安装路径
    """
    # 1. 环境变量优先
    if env_path := os.environ.get("HTTPX_PATH"):
        if Path(env_path).exists():
            return env_path
    
    # 2. 系统 PATH 查找
    if httpx_path := shutil.which("httpx"):
        return httpx_path
    
    # 3. 常见安装路径（跨平台）
    possible_paths = []
    
    # Windows 路径
    if sys.platform == 'win32':
        possible_paths.extend([
            Path(os.environ.get("GOPATH", "~/go")).expanduser() / "bin" / "httpx.exe",
            Path("C:/Go/bin/httpx.exe"),
            Path("~/go/bin/httpx.exe").expanduser(),
        ])
    # Unix/Linux/macOS 路径
    else:
        possible_paths.extend([
            Path("/usr/local/bin/httpx"),
            Path("/usr/bin/httpx"),
            Path("~/go/bin/httpx").expanduser(),
            Path("/usr/local/go/bin/httpx"),
        ])
    
    # 4. 检查路径是否存在
    for path in possible_paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    
    # 5. 未找到，返回默认值并提示
    print("警告：未找到 httpx 可执行文件", file=sys.stderr)
    print("请安装：go install github.com/projectdiscovery/httpx/cmd/httpx@latest", 
          file=sys.stderr)
    print("或设置环境变量：export HTTPX_PATH=/path/to/httpx", file=sys.stderr)
    return "httpx"


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


def run_httpx(
    targets: Union[str, List[str]],
    opts: str = "",
    output_format: str = "text",
    timeout: int = 300,
    concurrency: Optional[int] = None,
    rate_limit: Optional[int] = None
) -> str:
    """
    执行 httpx 扫描
    
    Args:
        targets: 目标 URL（支持多种格式）
        opts: 额外命令行参数
        output_format: 输出格式 (text/json)
        timeout: 超时时间（秒）
        concurrency: 并发数
        rate_limit: 速率限制
    
    Returns:
        httpx 输出结果
    """
    httpx_cmd = find_httpx_executable()
    base_cmd = [httpx_cmd]
    
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
            
            base_cmd.extend(["-l", temp_path])
            temp_file = Path(temp_path)
    elif temp_file:
        base_cmd.extend(["-l", str(temp_file)])
    
    # 添加并发控制
    if concurrency:
        base_cmd.extend(["-concurrency", str(concurrency)])
    if rate_limit:
        base_cmd.extend(["-rate-limit", str(rate_limit)])
    
    # 添加额外参数
    if opts:
        base_cmd.extend(opts.split())
    
    # 设置输出格式
    if output_format == "json":
        base_cmd.append("-json")
    
    # 动态调整超时（基于目标数量）
    dynamic_timeout = max(timeout, len(url_list) * 10) if url_list else timeout
    
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
                "reason": f"httpx 执行失败 (退出码：{result.returncode})"
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


def parse_httpx_json(content: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """解析 httpx JSON 输出（多行 JSON Lines 格式）"""
    try:
        results = []
        for line in content.strip().splitlines():
            line = line.strip()
            if line and line.startswith('{'):
                results.append(json.loads(line))
        return results
    except json.JSONDecodeError as e:
        return {"status": "parse_error", "reason": str(e), "content": content[:200]}


def scan(
    targets: Union[str, List[str]],
    opts: str = "-status-code -title -web-server",
    output_format: str = "json",
    concurrency: int = 25,
    rate_limit: int = 100,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    标准扫描接口（符合 skill.json 定义）
    
    Args:
        targets: 目标 URL 列表或文件路径
        opts: httpx 额外参数
        output_format: 输出格式
        concurrency: 并发数
        rate_limit: 速率限制
        timeout: 超时时间
    
    Returns:
        结构化结果
    """
    output = run_httpx(
        targets=targets,
        opts=opts,
        output_format=output_format,
        concurrency=concurrency,
        rate_limit=rate_limit,
        timeout=timeout
    )
    
    # 尝试解析 JSON
    if output_format == "json":
        try:
            parsed = parse_httpx_json(output)
            if isinstance(parsed, list):
                return {
                    "status": "success",
                    "count": len(parsed),
                    "results": parsed
                }
        except Exception:
            pass
    
    return {"status": "success", "output": output}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="httpx Web 资产探测技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单目标探测
  python main.py -u http://example.com
  
  # 批量扫描（文件输入）
  python main.py -l urls.txt --opts "-title -tech-detect"
  
  # 高并发模式
  python main.py -l urls.txt --concurrency 50 --rate-limit 200
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--url", type=str, help="单个目标 URL")
    group.add_argument("-l", "--list", type=str, help="目标文件路径")
    group.add_argument("--targets", type=str, help="目标（兼容旧版）")
    
    parser.add_argument("--opts", type=str, default="", 
                       help="httpx 额外参数")
    parser.add_argument("--format", type=str, default="json",
                       choices=["text", "json"], help="输出格式")
    parser.add_argument("--parse", action="store_true",
                       help="二次结构化 JSON 输出")
    parser.add_argument("--concurrency", type=int, default=25,
                       help="并发数 (默认：25)")
    parser.add_argument("--rate-limit", type=int, default=100,
                       help="速率限制 (默认：100)")
    parser.add_argument("--timeout", type=int, default=300,
                       help="超时时间 (秒，默认：300)")
    
    args = parser.parse_args()
    
    # 确定目标
    targets = args.url or args.list or args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)
    
    # 执行扫描
    output = run_httpx(
        targets=targets,
        opts=args.opts or "-status-code -title -web-server",
        output_format=args.format,
        concurrency=args.concurrency,
        rate_limit=args.rate_limit,
        timeout=args.timeout
    )
    
    # 输出结果
    if args.parse and args.format == "json":
        print(json.dumps(parse_httpx_json(output), indent=2, ensure_ascii=False))
    else:
        print(output)
