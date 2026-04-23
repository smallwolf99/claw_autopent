#!/usr/bin/env python3
"""
nmap 网络扫描技能 - 跨平台优化版
功能：端口扫描、服务识别、操作系统检测、漏洞扫描、结构化输出
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
from datetime import datetime


def is_valid_target(target: str) -> bool:
    """验证是否为有效的扫描目标（IP、域名、网段）"""
    try:
        if not target or not isinstance(target, str):
            return False
        target = target.strip()
        
        # IP 地址
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(/d{1,2})?$'
        if re.match(ip_pattern, target):
            return True
        
        # 域名
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(domain_pattern, target):
            return True
        
        # 网段（CIDR）
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
        if re.match(cidr_pattern, target):
            return True
        
        return False
    except Exception:
        return False


def find_nmap_executable() -> str:
    """
    跨平台查找 nmap 可执行文件
    优先级：环境变量 > 系统 PATH > 常见安装路径
    """
    # 1. 环境变量优先
    if env_path := os.environ.get("NMAP_PATH"):
        if Path(env_path).exists():
            return env_path
    
    # 2. 系统 PATH 查找
    if nmap_path := shutil.which("nmap"):
        return nmap_path
    
    # 3. 常见安装路径（跨平台）
    possible_paths = []
    
    # Windows 路径
    if sys.platform == 'win32':
        possible_paths.extend([
            Path("C:/Program Files (x86)/Nmap/nmap.exe"),
            Path("C:/Program Files/Nmap/nmap.exe"),
            Path(os.environ.get("USERPROFILE", "~")) / "bin" / "nmap.exe",
            Path("~/bin/nmap.exe").expanduser(),
        ])
    # Unix/Linux/macOS 路径
    else:
        possible_paths.extend([
            Path("/usr/bin/nmap"),
            Path("/usr/local/bin/nmap"),
            Path("~/bin/nmap").expanduser(),
            Path("/usr/local/share/nmap/nmap"),
        ])
    
    # 4. 检查路径是否存在
    for path in possible_paths:
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    
    # 5. 未找到，返回默认值并提示
    print("警告：未找到 nmap 可执行文件", file=sys.stderr)
    print("请安装：apt-get install nmap 或 yum install nmap", file=sys.stderr)
    print("或设置环境变量：export NMAP_PATH=/path/to/nmap", file=sys.stderr)
    return "nmap"


def parse_targets(targets: Union[str, List[str]]) -> tuple:
    """
    智能解析目标，返回 (目标列表，临时文件路径)
    支持：单个 IP/域名、目标列表、文件路径、逗号分隔字符串
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
            target_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return target_list, None
    
    # 逗号/分号/换行分隔的多个目标
    if any(sep in targets for sep in [',', ';', '\n']):
        target_list = [t.strip() for t in re.split('[,;\n]+', targets) if t.strip()]
        if len(target_list) > 1:
            return target_list, None
    
    # 单个目标
    if is_valid_target(targets):
        return [targets], None
    
    # 尝试作为文件路径（可能不存在）
    if Path(targets).suffix in ['.txt', '.lst', '.targets']:
        return [], Path(targets)
    
    # 默认为单个目标（即使格式不完全正确）
    return [targets], None


def run_nmap(
    targets: Union[str, List[str]],
    scan_type: str = "fast",
    ports: str = "",
    rate_limit: int = 0,
    timeout: int = 1800,
    os_detection: bool = False,
    version_detection: bool = True,
    script_scan: str = "",
    output_format: str = "json",
    verbose: bool = False,
    opts: str = "",
) -> str:
    """
    执行 nmap 扫描
    
    Args:
        targets: 扫描目标（支持多种格式）
        scan_type: 扫描类型（fast/full/web/service）
        ports: 指定端口
        rate_limit: 速率限制
        timeout: 超时时间（秒）
        os_detection: 操作系统检测
        version_detection: 版本检测
        script_scan: NSE 脚本扫描
        output_format: 输出格式（json/xml/text）
        verbose: 详细输出
        opts: 附加参数
    
    Returns:
        nmap 输出结果
    """
    nmap_cmd = find_nmap_executable()
    base_cmd = [nmap_cmd]
    
    # 解析目标
    target_list, temp_file = parse_targets(targets)
    
    # 构建命令参数
    if target_list:
        if len(target_list) == 1:
            base_cmd.append(target_list[0])
        else:
            # 多个目标使用临时文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write('\n'.join(target_list))
                temp_path = f.name
            
            base_cmd.extend(["-iL", temp_path])
            temp_file = Path(temp_path)
    elif temp_file:
        base_cmd.extend(["-iL", str(temp_file)])
    
    # 扫描类型
    if scan_type == "fast":
        base_cmd.extend(["-F", "-T4"])
    elif scan_type == "full":
        base_cmd.extend(["-p-", "-T4"])
    elif scan_type == "web":
        base_cmd.extend(["-p", "80,443,8080,8443", "-T4"])
    elif scan_type == "service":
        base_cmd.extend(["-sV", "--version-intensity", "5"])
    
    # 端口指定
    if ports:
        base_cmd.extend(["-p", ports])
    
    # 速率限制
    if rate_limit > 0:
        base_cmd.extend(["--max-rate", str(rate_limit)])
    
    # 操作系统检测
    if os_detection:
        base_cmd.append("-O")
    
    # 版本检测
    if version_detection:
        base_cmd.append("-sV")
    
    # NSE 脚本扫描
    if script_scan:
        base_cmd.extend(["--script", script_scan])
    
    # 输出格式
    output_file = None
    if output_format == "json":
        json_fd, json_path = tempfile.mkstemp(suffix='.json', prefix='nmap_')
        os.close(json_fd)
        base_cmd.extend(["-oX", json_path])  # nmap 输出 XML，稍后转 JSON
        output_file = json_path
    elif output_format == "xml":
        xml_fd, xml_path = tempfile.mkstemp(suffix='.xml', prefix='nmap_')
        os.close(xml_fd)
        base_cmd.extend(["-oX", xml_path])
        output_file = xml_path
    
    # 详细输出
    if verbose:
        base_cmd.append("-v")
    
    # 附加参数
    if opts:
        try:
            base_cmd.extend(shlex.split(opts))
        except Exception:
            base_cmd.append(opts)
    
    # 动态调整超时（基于目标数量）
    dynamic_timeout = max(timeout, 120 * len(target_list)) if target_list else timeout
    
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
                "reason": f"nmap 执行失败 (退出码：{result.returncode})"
            }
            return json.dumps(error_info, ensure_ascii=False, indent=2)
        
        # 读取输出文件（JSON/XML 模式）
        if output_file and Path(output_file).exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    output = f.read()
                Path(output_file).unlink()
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


def parse_nmap_xml(xml_content: str) -> Dict[str, Any]:
    """解析 nmap XML 输出为结构化数据"""
    try:
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(xml_content)
        
        result = {
            "status": "success",
            "scan_stats": {
                "start_time": root.findtext('runstats/finished/@time', ''),
                "end_time": datetime.now().isoformat(),
                "targets_count": 0,
                "hosts_up": 0,
                "hosts_down": 0,
            },
            "hosts": []
        }
        
        for host in root.findall('host'):
            host_info = {
                "ip": "",
                "hostname": "",
                "state": "",
                "ports": [],
                "os": [],
            }
            
            # IP 地址
            addr = host.find('address')
            if addr is not None:
                host_info["ip"] = addr.get('addr', '')
            
            # 主机名
            hostname = host.find('hostnames/hostname')
            if hostname is not None:
                host_info["hostname"] = hostname.get('name', '')
            
            # 状态
            status = host.find('status')
            if status is not None:
                host_info["state"] = status.get('state', '')
                if host_info["state"] == "up":
                    result["scan_stats"]["hosts_up"] += 1
                else:
                    result["scan_stats"]["hosts_down"] += 1
            
            # 端口
            for port in host.findall('ports/port'):
                port_info = {
                    "port": port.get('portid', ''),
                    "protocol": port.get('protocol', ''),
                    "state": "",
                    "service": "",
                    "version": "",
                }
                
                state = port.find('state')
                if state is not None:
                    port_info["state"] = state.get('state', '')
                
                service = port.find('service')
                if service is not None:
                    port_info["service"] = service.get('name', '')
                    port_info["version"] = service.get('version', '')
                
                host_info["ports"].append(port_info)
            
            # 操作系统
            osmatch = host.find('os/osmatch')
            if osmatch is not None:
                for os_item in host.findall('os/osmatch'):
                    host_info["os"].append({
                        "name": os_item.get('name', ''),
                        "accuracy": os_item.get('accuracy', ''),
                    })
            
            result["hosts"].append(host_info)
            result["scan_stats"]["targets_count"] += 1
        
        return result
    
    except Exception as e:
        return {
            "status": "parse_error",
            "reason": str(e),
            "content": xml_content[:200] if xml_content else ""
        }


def scan(
    targets: Union[str, List[str]],
    scan_type: str = "fast",
    ports: str = "",
    rate_limit: int = 0,
    timeout: int = 1800,
    os_detection: bool = False,
    version_detection: bool = True,
    script_scan: str = "",
    output_format: str = "json",
    verbose: bool = False,
    opts: str = "",
) -> Dict[str, Any]:
    """
    标准扫描接口（符合 skill.json 定义）
    
    Args:
        targets: 扫描目标列表或文件路径
        scan_type: 扫描类型
        ports: 指定端口
        rate_limit: 速率限制
        timeout: 超时时间
        os_detection: 操作系统检测
        version_detection: 版本检测
        script_scan: NSE 脚本扫描
        output_format: 输出格式
        verbose: 详细输出
        opts: 附加参数
    
    Returns:
        结构化结果
    """
    output = run_nmap(
        targets=targets,
        scan_type=scan_type,
        ports=ports,
        rate_limit=rate_limit,
        timeout=timeout,
        os_detection=os_detection,
        version_detection=version_detection,
        script_scan=script_scan,
        output_format=output_format,
        verbose=verbose,
        opts=opts,
    )
    
    # 尝试解析 XML/JSON
    if output_format in ["json", "xml"]:
        try:
            parsed = parse_nmap_xml(output)
            if isinstance(parsed, dict) and parsed.get("status") == "success":
                return parsed
        except Exception:
            pass
    
    return {"status": "success", "output": output}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="nmap 网络扫描技能 - 跨平台优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速扫描
  python main.py -t scanme.nmap.org
  
  # 完整端口扫描
  python main.py -t scanme.nmap.org --scan-type full
  
  # Web 服务扫描
  python main.py -t example.com --scan-type web
  
  # 指定端口
  python main.py -t example.com --ports "80,443,8080"
  
  # 操作系统检测
  python main.py -t scanme.nmap.org --os-detection
  
  # NSE 脚本扫描
  python main.py -t example.com --script "vuln"
  
  # 批量扫描（文件输入）
  python main.py -l targets.txt --timeout 3600
  
  # 限速扫描
  python main.py -t example.com --rate-limit 100
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--target", type=str, help="单个扫描目标")
    group.add_argument("-l", "--list", type=str, help="目标文件路径")
    group.add_argument("--targets", type=str, help="目标（兼容旧版）")
    
    parser.add_argument("--scan-type", type=str, default="fast",
                       choices=["fast", "full", "web", "service"],
                       help="扫描类型（默认：fast）")
    parser.add_argument("--ports", "-p", type=str, default="",
                       help="指定端口（如：80,443,8080 或 1-1000）")
    parser.add_argument("--rate-limit", type=int, default=0,
                       help="速率限制（每秒包数，0 表示不限）")
    parser.add_argument("--timeout", type=int, default=1800,
                       help="超时时间（秒，默认：1800）")
    parser.add_argument("--os-detection", action="store_true",
                       help="操作系统检测")
    parser.add_argument("--version-detection", action="store_true", default=True,
                       help="版本检测（默认开启）")
    parser.add_argument("--script", type=str, default="",
                       help="NSE 脚本扫描（如：vuln,auth,default）")
    parser.add_argument("--format", type=str, default="json",
                       choices=["json", "xml", "text"], help="输出格式")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")
    parser.add_argument("--opts", type=str, default="",
                       help="附加参数（可选）")
    parser.add_argument("--parse", action="store_true",
                       help="二次结构化输出")
    
    args = parser.parse_args()
    
    # 确定目标
    targets = args.target or args.list or args.targets
    if not targets:
        parser.print_help()
        sys.exit(1)
    
    # 执行扫描
    output = run_nmap(
        targets=targets,
        scan_type=args.scan_type,
        ports=args.ports,
        rate_limit=args.rate_limit,
        timeout=args.timeout,
        os_detection=args.os_detection,
        version_detection=args.version_detection,
        script_scan=args.script,
        output_format=args.format,
        verbose=args.verbose,
        opts=args.opts,
    )
    
    # 输出结果
    if args.parse and args.format in ["json", "xml"]:
        print(json.dumps(parse_nmap_xml(output), indent=2, ensure_ascii=False))
    else:
        print(output)
