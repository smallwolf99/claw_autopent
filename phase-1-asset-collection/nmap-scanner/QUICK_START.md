# Nmap技能包快速使用指南

## 🚀 快速开始

### 1. 基础扫描
```bash
# 快速扫描单个目标
./basic_network_scan.sh target.com

# 完整端口扫描
./full_port_scan.sh 192.168.1.1
```

### 2. 批量扫描
```bash
# 批量快速扫描
./batch_target_scan.sh targets.txt fast

# 批量Web服务扫描
./batch_target_scan.sh websites.txt web
```

### 3. 数据提取
```bash
# 提取开放端口
./extract_open_ports.sh scan.json list

# 生成CSV报告
./extract_open_ports.sh scan.json csv > report.csv
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `basic_network_scan.sh` | 基础网络扫描脚本 |
| `full_port_scan.sh` | 完整端口扫描脚本 |
| `batch_target_scan.sh` | 批量目标扫描脚本 |
| `extract_open_ports.sh` | 数据提取工具 |
| `nmap_config.conf` | 配置文件 |
| `example_targets.txt` | 示例目标文件 |
| `SKILL.md` | 完整技能文档 |

## ⚙️ 常用命令

### 扫描命令
```bash
# 快速扫描最常用的1000个端口
nmap -T4 -F -oJ result.json target.com

# 完整端口扫描
nmap -p- -T4 -sS -sV -oJ full_scan.json target.com

# Web服务扫描
nmap -p 80,443,8080,8443 -sV -oJ web_scan.json target.com
```

### 数据提取命令
```bash
# 使用jq提取开放端口
jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | "\(.protocol)/\(.portid)"' scan.json

# 统计开放端口数量
jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | .portid' scan.json | wc -l
```

## 🔧 故障排除

### 常见问题
1. **权限不足**: 使用 `sudo` 运行脚本
2. **nmap未安装**: 运行 `./install.sh` 安装依赖
3. **扫描超时**: 调整配置文件中的超时时间
4. **内存不足**: 减少并行扫描数量

### 错误代码
- `1`: 一般错误
- `2`: 无效参数
- `3`: 网络错误
- `4`: 权限不足
- `124`: 超时

## 📞 支持

如有问题，请参考:
1. 完整文档: `SKILL.md`
2. 配置文件: `nmap_config.conf`
3. 示例文件: `example_targets.txt`

## 📝 更新日志

- v1.0 (2026-03-26): 初始版本发布
- 包含基础扫描、批量处理、数据提取功能

