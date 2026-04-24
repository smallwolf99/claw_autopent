#!/usr/bin/env python3
"""
快速扫描脚本 - 用于快速探测目标信息
"""
import subprocess
import sys
import socket
from datetime import datetime

def print_banner(text):
    """打印横幅"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_port(ip, port, timeout=1):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def quick_scan(target):
    """快速扫描目标"""
    print_banner(f"快速扫描目标：{target}")
    
    start_time = datetime.now()
    
    # 常见端口列表
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 
        443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443
    ]
    
    print(f"[*] 开始扫描时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] 扫描常见端口：{common_ports}\n")
    
    open_ports = []
    
    # 扫描端口
    print("[+] 端口扫描结果:")
    print("-" * 60)
    
    for port in common_ports:
        if check_port(target, port):
            open_ports.append(port)
            service = get_service_name(port)
            print(f"  ✓ {port}/tcp    OPEN    ({service})")
    
    if not open_ports:
        print("  未发现开放端口")
    
    print("-" * 60)
    print(f"\n[+] 共发现 {len(open_ports)} 个开放端口\n")
    
    # HTTP/HTTPS 探测
    if 80 in open_ports or 8080 in open_ports:
        print("[+] HTTP 服务探测:")
        print("-" * 60)
        probe_http(target, open_ports)
        print("-" * 60)
    
    if 443 in open_ports or 8443 in open_ports:
        print("\n[+] HTTPS 服务探测:")
        print("-" * 60)
        probe_https(target, open_ports)
        print("-" * 60)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n[*] 扫描完成时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] 扫描耗时：{duration:.2f} 秒")
    
    return open_ports

def get_service_name(port):
    """获取端口对应的服务名称"""
    services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        111: "RPC",
        135: "MSRPC",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        993: "IMAPS",
        995: "POP3S",
        1723: "PPTP",
        3306: "MySQL",
        3389: "RDP",
        5900: "VNC",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt"
    }
    return services.get(port, "Unknown")

def probe_http(target, open_ports):
    """探测 HTTP 服务"""
    ports = [80, 8080]
    
    for port in [p for p in ports if p in open_ports]:
        url = f"http://{target}:{port}" if port != 80 else f"http://{target}"
        print(f"\n  探测 {url}")
        
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            
            print(f"    状态码：{response.status}")
            print(f"    Server: {response.headers.get('Server', 'Unknown')}")
            title = extract_title(response.read())
            if title:
                print(f"    网站标题：{title}")
                
        except Exception as e:
            print(f"    探测失败：{str(e)}")

def probe_https(target, open_ports):
    """探测 HTTPS 服务"""
    ports = [443, 8443]
    
    for port in [p for p in ports if p in open_ports]:
        url = f"https://{target}:{port}" if port != 443 else f"https://{target}"
        print(f"\n  探测 {url}")
        
        try:
            import urllib.request
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5, context=ctx)
            
            print(f"    状态码：{response.status}")
            print(f"    Server: {response.headers.get('Server', 'Unknown')}")
            title = extract_title(response.read())
            if title:
                print(f"    网站标题：{title}")
                
        except Exception as e:
            print(f"    探测失败：{str(e)}")

def extract_title(html):
    """提取 HTML 标题"""
    try:
        import re
        match = re.search(r'<title>(.*?)</title>', html.decode('utf-8', errors='ignore'), re.I)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python quick_scan.py <目标 IP>")
        print("示例：python quick_scan.py 172.16.8.151")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_scan(target)
