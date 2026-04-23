#!/usr/bin/env python3
"""
subfinder 子域名枚举技能 - 跨平台优化版
功能：被动子域名枚举、多数据源聚合、httpx 存活验证、结果解析
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


def is_valid_domain(domain: str) -> bool:
    """验证是否为有效域名"""
    try:
        # 简单验证：包含点且无空格
        if not domain or ' ' in domain:
            return False
        # 检查是否为有效域名格式
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        # 基本格式检查
        return all(part and not part.startswith('-') and not part.endswith('-') 
                  for part in parts)
    except Exception:
        return False


def find_subfinder_executable() -> str:
    """
    跨平台查找 subfinder 可执行文件
    优先级：环境变量 > 系统 PATH > 常见安装路径
    """
    # 1. 环境变量优先
    if env_path := os.environ.get("SUBFINDER_PATH"):
        if Path(env_path).exists():
            return env_path
    
    # 2. 系统 PATH 查找
    if subfinder_path := shutil.which("subfinder"):
        return subfinder_path
    
    # 3. 常见安装路径（跨平台）
    possible_paths = []
    
    # Windows 路径
    if sys.platform == 'win32':
        possible_paths.extend([
            Path(os.environ.get("USERPROFILE", "~")) / "bin" / "subfinder.exe",
            Path("C:/Program Files/subfinder/subfinder.exe"),
            Path("~/bin/subfinder.exe").expanduser(),
        ])
    # Unix/Linux/macOS 路径
    else:
        possible_paths.extend([
            Path("/usr/local/bin/subfinder"),
            Path("/usr/bin/subfinder"),
            Path("~/bin/subfinder").expanduser(),
            Path("/usr/local/go/bin/subfinder"),
        ])
    
    # 4. 检查路径是否存在
    for path in possible_paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    
    # 5. 未找到，返回默认值并提示
    print("警告：未找到 subfinder 可执行文件", file=sys.stderr)
    print("请安装：go install github.com/projectdiscovery/subfinder/cmd/subfinder@latest", 
          file=sys.stderr)
    print("或设置环境变量：export SUBFINDER_PATH=/path/to/subfinder", file=sys.stderr)
    return "subfinder"


def parse_targets(targets: Union[str, List[str]]) -> tuple:
    """
    智能解析目标，返回 (域名列表，临时文件路径)
    支持：单个域名、域名列表、文件路径、逗号分隔字符串
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
            domains = [line.strip() for line in f if line.strip()]
        return domains, None
    
    # 逗号分隔的多个域名
    if ',' in targets:
        domains = [t.strip() for t in targets.split(',') if t.strip()]
        if len(domains) > 1:
            return domains, None
    
    # 单个域名
    if is_valid_domain(targets):
        return [targets], None
    
    # 尝试作为文件路径（可能不存在）
    if Path(targets).suffix in ['.txt', '.lst']:
        return [], Path(targets)
    
    # 默认为单个域名
    return [targets], None


def run_subfinder(
    targets: Union[str, List[str]],
    output_format: str = "json",
    recursive: bool = False,
    sources: str = "",
    exclude_sources: str = "",
    threads: int = 10,
    rate_limit: int = 0,
    timeout: int = 30,
    max_time: int = 0,
    proxy: str = "",
    output_file: Optional[str] = None,
    silent: bool = True,
    version_check: bool = False,
) -> str:
    """
    执行 subfinder 枚举
    
    Args:
        targets: 目标域名（支持多种格式）
        output_format: 输出格式（json/txt）
        recursive: 递归枚举（默认 False）
        sources: 指定数据源（逗号分隔）
        exclude_sources: 排除数据源（逗号分隔）
        threads: 并发线程数（默认 10）
        rate_limit: 速率限制（每秒请求数，0 表示不限）
        timeout: 枚举超时（秒，默认 30）
        max_time: 最大执行时间（分钟，0 表示不限）
        proxy: 代理地址
        output_file: 输出文件路径
        silent: 静默模式（默认 True）
        version_check: 版本检查（默认 False）
    
    Returns:
        subfinder 输出结果
    """
    subfinder_cmd = find_subfinder_executable()
    base_cmd = [subfinder_cmd]
    
    # 解析目标
    domain_list, temp_file = parse_targets(targets)
    
    # 构建命令参数
    if domain_list:
        if len(domain_list) == 1:
            base_cmd.extend(["-d", domain_list[0]])
        else:
            # 多个域名使用临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.txt', 
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write('\n'.join(domain_list))
                temp_path = f.name
            
            base_cmd.extend(["-dL", temp_path])
            temp_file = Path(temp_path)
    elif temp_file:
        base_cmd.extend(["-dL", str(temp_file)])
    
    # 输出格式
    if output_format == "json":
        base_cmd.append("-oJ")
    else:
        base_cmd.append("-o")
        if output_file:
            base_cmd.extend([output_file])
        else:
            # 文本输出到 stdout
            base_cmd.append("/dev/stdout" if sys.platform != 'win32' else "CON")
    
    # 递归枚举
    if recursive:
        base_cmd.append("-recursive")
    
    # 数据源控制
    if sources:
        base_cmd.extend(["-s", sources])
    
    if exclude_sources:
        base_cmd.extend(["-es", exclude_sources])
    
    # 性能参数
    base_cmd.extend(["-t", str(threads)])
    
    if rate_limit > 0:
        base_cmd.extend(["-rl", str(rate_limit)])
    
    base_cmd.extend(["-timeout", str(timeout)])
    
    if max_time > 0:
        base_cmd.extend(["-max-time", str(max_time)])
    
    # 代理
    if proxy:
        base_cmd.extend(["-proxy", proxy])
    
    # 静默模式
    if silent:
        base_cmd.append("-silent")
    
    # 版本检查
    if not version_check:
        base_cmd.append("-nc")
    
    # 动态调整超时（基于域名数量）
    dynamic_timeout = max(timeout * len(domain_list), 60) if domain_list else timeout
    
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
                "reason": f"subfinder 执行失败 (退出码：{result.returncode})"
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


def parse_subfinder_json(content: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """解析 subfinder JSON Lines 输出"""
    try:
        results = []
        for line in content.strip().splitlines():
            line = line.strip()
            if line and line.startswith('{'):
                results.append(json.loads(line))
        return results
    except json.JSONDecodeError as e:
        return {"status": "parse_error", "reason": str(e), "content": content[:200]}


def enumerate(
    targets: Union[str, List[str]],
    output_format: str = "json",
    recursive: bool = False,
    sources: str = "",
    threads: int = 10,
    rate_limit: int = 0,
    timeout: int = 30,
    httpx_verify: bool = False,
) -> Dict[str, Any]:
    """
    标准枚举接口（符合 skill.json 定义）
    
    Args:
        targets: 目标域名列表或文件路径
        output_format: 输出格式
        recursive: 递归枚举
        sources: 指定数据源
        threads: 并发线程数
        rate_limit: 速率限制
        timeout: 枚举超时
        httpx_verify: 是否进行 httpx 存活验证
    
    Returns:
        结构化结果
    """
    output = run_subfinder(
        targets=targets,
        output_format=output_format,
        recursive=recursive,
        sources=sources,
        threads=threads,
        rate_limit=rate_limit,
        timeout=timeout,
    )
    
    # 尝试解析 JSON
    if output_format == "json":
        try:
            parsed = parse_subfinder_json(output)
            if isinstance(parsed, list):
                result = {
                    "status": "success",
                    "count": len(parsed),
                    "results": parsed,
                    "unique_domains": len(set(r.get('host', '') for r in parsed)),
                    "sources": list(set(r.get('source', '') for r in parsed if r.get('source'))),
                }
                
                # 可选：httpx 存活验证
                if httpx_verify and parsed:
                    # 这里可以集成 httpx 验证逻辑
                    # 为简化，暂时返回原始结果
                    result["httpx_verified"] = False
                    result["note"] = "httpx 验证功能待集成"
                
                return result
        except Exception:
            pass
    
    return {"status": "success", "output": output}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="subfinder 子域名枚举技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单域名基础枚举
  python main.py -d example.com
  
  # JSON 输出（含数据源信息）
  python main.py -d example.com --format json
  
  # 递归枚举
  python main.py -d example.com --recursive
  
  # 指定数据源
  python main.py -d example.com --sources "virustotal,shodan,censys"
  
  # 高并发模式
  python main.py -d example.com --threads 50
  
  # 批量枚举（文件输入）
  python main.py -l domains.txt --timeout 60
  
  # 限速枚举
  python main.py -d example.com --rate-limit 100
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--domain", type=str, help="单个目标域名")
    group.add_argument("-l", "--list", type=str, help="目标文件路径")
    group.add_argument("--targets", type=str, help="目标（兼容旧版）")
    
    parser.add_argument("--format", type=str, default="json",
                       choices=["json", "txt"], help="输出格式")
    parser.add_argument("--recursive", action="store_true",
                       help="递归枚举")
    parser.add_argument("--sources", type=str, default="",
                       help="指定数据源（逗号分隔）")
    parser.add_argument("--exclude-sources", type=str, default="",
                       help="排除数据源（逗号分隔）")
    parser.add_argument("--threads", "-t", type=int, default=10,
                       help="并发线程数 (默认：10)")
    parser.add_argument("--rate-limit", "-rl", type=int, default=0,
                       help="速率限制 (每秒请求数，0 表示不限)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="枚举超时 (秒，默认：30)")
    parser.add_argument("--max-time", type=int, default=0,
                       help="最大执行时间 (分钟，0 表示不限)")
    parser.add_argument("--proxy", type=str, default="",
                       help="代理地址")
    parser.add_argument("--output", "-o", type=str, default="",
                       help="输出文件路径")
    parser.add_argument("--httpx-verify", action="store_true",
                       help="httpx 存活验证")
    parser.add_argument("--parse", action="store_true",
                       help="二次结构化 JSON 输出")
    
    args = parser.parse_args()
    
    # 确定目标
    targets = args.domain or args.list or args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)
    
    # 执行枚举
    output = run_subfinder(
        targets=targets,
        output_format=args.format,
        recursive=args.recursive,
        sources=args.sources,
        exclude_sources=args.exclude_sources,
        threads=args.threads,
        rate_limit=args.rate_limit,
        timeout=args.timeout,
        max_time=args.max_time,
        proxy=args.proxy,
        output_file=args.output if args.output else None,
    )
    
    # 输出结果
    if args.parse and args.format == "json":
        print(json.dumps(parse_subfinder_json(output), indent=2, ensure_ascii=False))
    else:
        print(output)
