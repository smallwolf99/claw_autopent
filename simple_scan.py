#!/usr/bin/env python3
"""简单快速扫描"""
import socket

target = "172.16.8.151"
ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 3306, 3389, 8080, 8443]

print(f"\n快速扫描目标：{target}\n")
print("端口扫描结果:")
print("-" * 50)

open_ports = []
for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        if sock.connect_ex((target, port)) == 0:
            open_ports.append(port)
            print(f"  ✓ {port}/tcp OPEN")
        sock.close()
    except:
        pass

print("-" * 50)
print(f"\n开放端口：{open_ports}")
print(f"共发现 {len(open_ports)} 个开放端口\n")

# HTTP 探测
if 80 in open_ports:
    import urllib.request
    try:
        req = urllib.request.Request(f"http://{target}", headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=3)
        print(f"\nHTTP 服务探测 (http://{target}):")
        print(f"  状态码：{resp.status}")
        print(f"  Server: {resp.headers.get('Server', 'Unknown')}")
        html = resp.read().decode('utf-8', errors='ignore')
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.I)
        if match:
            print(f"  网站标题：{match.group(1)}")
    except Exception as e:
        print(f"\nHTTP 探测失败：{e}")
