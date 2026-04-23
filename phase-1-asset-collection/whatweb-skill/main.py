#!/usr/bin/env python3
"""
whatweb Web 指纹识别技能 - 跨平台优化版
功能：Web 技术栈识别、指纹检测、批量扫描、结构化输出
"""
import subprocess
import sys
import os
import json
import tempfile
import shutil
import re
from pathlib import Path
from typing import Union, List, Dict, Any, Optional


def is_valid_url(url: str) -> bool:
    """验证是否为有效 URL"""
    try:
        if not url or not isinstance(url, str):
            return False
        url = url.strip()
        # 基本 URL 格式检查
        return url.startswith(('http://', 'https://')) and '.' in url.split('/')[2] if '//' in url else False
    except Exception:
        return False


def find_whatweb_executable() -> str:
    """
    跨平台查找 whatweb 可执行文件
    优先级：环境变量 > 系统 PATH > 常见安装路径
    """
    # 1. 环境变量优先
    if env_path := os.environ.get("WHATWEB_PATH"):
        if Path(env_path).exists():
            return env_path
    
    # 2. 系统 PATH 查找
    if whatweb_path := shutil.which("whatweb"):
        return whatweb_path
    
    # 3. 常见安装路径（跨平台）
    possible_paths = []
    
    # Windows 路径
    if sys.platform == 'win32':
        possible_paths.extend([
            Path(os.environ.get("USERPROFILE", "~")) / "bin" / "whatweb.exe",
            Path("C:/Program Files/whatweb/whatweb.exe"),
            Path("~/bin/whatweb.exe").expanduser(),
            Path("C:/Ruby/bin/whatweb.exe"),  # whatweb 通常是 Ruby 编写
        ])
    # Unix/Linux/macOS 路径
    else:
        possible_paths.extend([
            Path("/usr/bin/whatweb"),
            Path("/usr/local/bin/whatweb"),
            Path("~/bin/whatweb").expanduser(),
            Path("/usr/local/share/whatweb/whatweb"),
        ])
    
    # 4. 检查路径是否存在
    for path in possible_paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    
    # 5. 未找到，返回默认值并提示
    print("警告：未找到 whatweb 可执行文件", file=sys.stderr)
    print("请安装：gem install whatweb 或 apt-get install whatweb", file=sys.stderr)
    print("或设置环境变量：export WHATWEB_PATH=/path/to/whatweb", file=sys.stderr)
    return "whatweb"


def parse_targets(targets: Union[str, List[str]]) -> tuple:
    """
    智能解析目标，返回 (URL 列表，临时文件路径)
    支持：单个 URL、URL 列表、文件路径、逗号/分号分隔字符串
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
    
    # 逗号/分号/换行分隔的多个 URL
    if any(sep in targets for sep in [',', ';', '\n']):
        url_list = [t.strip() for t in re.split('[,;\n]+', targets) if t.strip()]
        if len(url_list) > 1:
            return url_list, None
    
    # 单个 URL
    if is_valid_url(targets):
        return [targets], None
    
    # 尝试作为文件路径（可能不存在）
    if Path(targets).suffix in ['.txt', '.lst', '.url']:
        return [], Path(targets)
    
    # 默认为单个 URL（即使格式不完全正确）
    return [targets], None


def run_whatweb(
    targets: Union[str, List[str]],
    opts: str = "",
    output_format: str = "text",
    aggression: int = 1,
    plugins: str = "",
    timeout: int = 300,
    verbose: bool = False,
    color: bool = False,
) -> str:
    """
    执行 whatweb 指纹识别
    
    Args:
        targets: 目标 URL（支持多种格式）
        opts: 附加参数（可选）
        output_format: 输出格式（text/json）
        aggression: 攻击性级别（1-5，默认 1）
        plugins: 指定插件（逗号分隔）
        timeout: 超时时间（秒，默认 300）
        verbose: 详细输出
        color: 彩色输出
    
    Returns:
        whatweb 输出结果
    """
    whatweb_cmd = find_whatweb_executable()
    base_cmd = [whatweb_cmd]
    
    # 解析目标
    url_list, temp_file = parse_targets(targets)
    
    # 构建命令参数
    if url_list:
        if len(url_list) == 1:
            base_cmd.append(url_list[0])
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
            
            base_cmd.extend(["-i", temp_path])
            temp_file = Path(temp_path)
    elif temp_file:
        base_cmd.extend(["-i", str(temp_file)])
    
    # 输出格式
    if output_format == "json":
        # 使用临时文件存储 JSON 输出
        json_fd, json_path = tempfile.mkstemp(suffix='.json', prefix='whatweb_')
        os.close(json_fd)
        base_cmd.extend(["--log-json", json_path])
    
    # 攻击性级别
    if aggression > 1:
        base_cmd.extend(["-a", str(aggression)])
    
    # 指定插件
    if plugins:
        base_cmd.extend(["--plugins", plugins])
    
    # 详细输出
    if verbose:
        base_cmd.append("-v")
    
    # 彩色输出（仅文本模式）
    if color and output_format == "text":
        base_cmd.append("--color")
    
    # 附加参数
    if opts:
        try:
            base_cmd.extend(shlex.split(opts))
        except Exception:
            # 如果 shlex 解析失败，直接添加
            base_cmd.append(opts)
    
    # 动态调整超时（基于 URL 数量）
    dynamic_timeout = max(timeout, 60 * len(url_list)) if url_list else timeout
    
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
                "reason": f"whatweb 执行失败 (退出码：{result.returncode})"
            }
            return json.dumps(error_info, ensure_ascii=False, indent=2)
        
        # JSON 模式读取临时文件
        if output_format == "json" and 'json_path' in locals():
            try:
                if Path(json_path).exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        output = f.read()
                    Path(json_path).unlink()
            except Exception:
                pass
        
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


def parse_whatweb_json(content: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """解析 whatweb JSON 输出"""
    try:
        # whatweb JSON 输出可能是多行 JSON 或单个 JSON 数组
        content = content.strip()
        if not content:
            return []
        
        # 尝试解析为 JSON 数组
        if content.startswith('['):
            return json.loads(content)
        
        # 尝试解析为多行 JSON（每行一个对象）
        results = []
        for line in content.splitlines():
            line = line.strip()
            if line and line.startswith('{'):
                results.append(json.loads(line))
        
        return results if results else {"status": "empty", "reason": "无有效 JSON 数据"}
    
    except json.JSONDecodeError as e:
        return {"status": "parse_error", "reason": str(e), "content": content[:200]}


def scan(
    targets: Union[str, List[str]],
    opts: str = "",
    output_format: str = "json",
    aggression: int = 1,
    plugins: str = "",
    timeout: int = 300,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    标准扫描接口（符合 skill.json 定义）
    
    Args:
        targets: 目标 URL 列表或文件路径
        opts: 附加参数
        output_format: 输出格式
        aggression: 攻击性级别
        plugins: 指定插件
        timeout: 超时时间
        verbose: 详细输出
    
    Returns:
        结构化结果
    """
    output = run_whatweb(
        targets=targets,
        opts=opts,
        output_format=output_format,
        aggression=aggression,
        plugins=plugins,
        timeout=timeout,
        verbose=verbose,
    )
    
    # 尝试解析 JSON
    if output_format == "json":
        try:
            parsed = parse_whatweb_json(output)
            if isinstance(parsed, list):
                # 提取关键信息
                technologies = []
                for result in parsed:
                    if isinstance(result, dict):
                        target = result.get('target', '')
                        plugins_data = result.get('plugins', [])
                        for plugin in plugins_data:
                            if isinstance(plugin, dict):
                                tech_name = plugin.get('name', '')
                                if tech_name:
                                    technologies.append({
                                        "target": target,
                                        "technology": tech_name,
                                        "version": plugin.get('version', ''),
                                        "module": plugin.get('module', ''),
                                    })
                
                result = {
                    "status": "success",
                    "count": len(parsed),
                    "results": parsed,
                    "technologies": technologies,
                    "unique_targets": len(set(r.get('target', '') for r in parsed)),
                }
                return result
        except Exception:
            pass
    
    return {"status": "success", "output": output}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="whatweb Web 指纹识别技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单 URL 基础识别
  python main.py -u https://example.com
  
  # JSON 输出（结构化）
  python main.py -u https://example.com --format json
  
  # 高攻击性模式（更准确但更慢）
  python main.py -u https://example.com --aggression 3
  
  # 指定插件
  python main.py -u https://example.com --plugins "CMS,WebServer"
  
  # 批量扫描（文件输入）
  python main.py -l urls.txt --timeout 600
  
  # 详细输出
  python main.py -u https://example.com --verbose
  
  # 自定义参数
  python main.py -u https://example.com --opts "--no-errors"
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--url", type=str, help="单个目标 URL")
    group.add_argument("-l", "--list", type=str, help="目标文件路径")
    group.add_argument("--targets", type=str, help="目标（兼容旧版）")
    
    parser.add_argument("--format", type=str, default="json",
                       choices=["json", "text"], help="输出格式")
    parser.add_argument("--opts", type=str, default="",
                       help="附加参数（可选）")
    parser.add_argument("--aggression", "-a", type=int, default=1,
                       choices=range(1, 6), metavar='1-5',
                       help="攻击性级别 (1-5，默认：1)")
    parser.add_argument("--plugins", "-p", type=str, default="",
                       help="指定插件（逗号分隔）")
    parser.add_argument("--timeout", type=int, default=300,
                       help="超时时间 (秒，默认：300)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")
    parser.add_argument("--color", action="store_true",
                       help="彩色输出（仅文本模式）")
    parser.add_argument("--parse", action="store_true",
                       help="二次结构化 JSON 输出")
    
    args = parser.parse_args()
    
    # 确定目标
    targets = args.url or args.list or args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)
    
    # 执行扫描
    output = run_whatweb(
        targets=targets,
        opts=args.opts,
        output_format=args.format,
        aggression=args.aggression,
        plugins=args.plugins,
        timeout=args.timeout,
        verbose=args.verbose,
        color=args.color,
    )
    
    # 输出结果
    if args.parse and args.format == "json":
        print(json.dumps(parse_whatweb_json(output), indent=2, ensure_ascii=False))
    else:
        print(output)
