# nmap Skill 快速指南

## 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install nmap

# CentOS/RHEL
sudo yum install nmap

# macOS
brew install nmap

# Windows
# 下载安装包：https://nmap.org/download.html
```

## 基本使用

### 快速扫描
```bash
python main.py -t scanme.nmap.org
```

### 完整端口扫描
```bash
python main.py -t scanme.nmap.org --scan-type full
```

### Web 服务扫描
```bash
python main.py -t example.com --scan-type web
```

### 指定端口
```bash
python main.py -t example.com --ports "80,443,8080"
```

### 操作系统检测
```bash
python main.py -t scanme.nmap.org --os-detection
```

### NSE 脚本扫描
```bash
python main.py -t example.com --script "vuln"
```

### 批量扫描
```bash
python main.py -l targets.txt --timeout 3600
```

### 限速扫描
```bash
python main.py -t example.com --rate-limit 100
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-t, --target` | 单个扫描目标 | - |
| `-l, --list` | 目标文件路径 | - |
| `--scan-type` | 扫描类型（fast/full/web/service） | fast |
| `--ports, -p` | 指定端口 | - |
| `--rate-limit` | 速率限制（每秒包数） | 0 |
| `--timeout` | 超时时间（秒） | 1800 |
| `--os-detection` | 操作系统检测 | False |
| `--version-detection` | 版本检测 | True |
| `--script` | NSE 脚本扫描 | - |
| `--format` | 输出格式（json/xml/text） | json |
| `--verbose, -v` | 详细输出 | False |
| `--opts` | 附加参数 | - |

## 程序化调用

```python
from main import scan

result = scan(
    targets=["192.168.1.0/24", "scanme.nmap.org"],
    scan_type="fast",
    ports="",
    rate_limit=0,
    timeout=1800,
    os_detection=False,
    version_detection=True,
    script_scan="",
    output_format="json",
    verbose=False
)

print(f"扫描 {result['scan_stats']['targets_count']} 个目标")
print(f"存活主机：{result['scan_stats']['hosts_up']}")
for host in result.get('hosts', []):
    print(f"  - {host.get('ip')} ({host.get('hostname')})")
    print(f"    开放端口：{len(host.get('ports', []))}")
```

## 运行测试

```bash
python tests/test_nmap_skill.py
```

## 扫描类型说明

- **fast**：快速扫描（-F -T4），扫描 1000 个常用端口
- **full**：完整扫描（-p- -T4），扫描所有 65535 个端口
- **web**：Web 服务扫描（80,443,8080,8443）
- **service**：服务识别（-sV --version-intensity 5）

## 注意事项

1. **权限要求**：某些扫描功能（如 OS 检测）需要管理员权限
2. **速率限制**：生产环境建议使用 `--rate-limit` 避免触发防火墙
3. **超时设置**：批量扫描建议增加 `--timeout`
4. **合法使用**：仅扫描授权的目标
