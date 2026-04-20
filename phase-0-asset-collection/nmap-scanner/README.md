# 🎯 Nmap JSON扫描技能包

## 📋 概述
一个专业的网络资产发现和端口扫描技能包，支持多种扫描类型并将结果保存为JSON格式。

**所属阶段**: Phase 1 - Asset Collection (资产收集阶段)  
**核心功能**: 网络侦察、端口扫描、服务识别  
**输出格式**: JSON (兼容自动化处理)  
**依赖工具**: nmap, jq (推荐)

---

## 🚀 快速开始

### 1. 安装依赖
```bash
# 运行安装脚本
./install.sh

# 或手动安装
sudo apt-get install nmap jq curl  # Ubuntu/Debian
sudo yum install nmap jq curl      # CentOS/RHEL
brew install nmap jq curl          # macOS
```

### 2. 基本使用
```bash
# 快速扫描单个目标
./basic_network_scan.sh target.com

# 完整端口扫描
./full_port_scan.sh 192.168.1.1

# 批量扫描
./batch_target_scan.sh targets.txt fast

# 数据提取
./extract_open_ports.sh scan.json list
```

### 3. 示例命令
```bash
# 测试扫描
./basic_network_scan.sh scanme.nmap.org

# 使用示例目标文件
./batch_target_scan.sh example_targets.txt web

# 生成详细报告
./extract_open_ports.sh scan.json detail
```

---

## 📁 文件说明

| 文件 | 描述 | 用途 |
|------|------|------|
| `SKILL.md` | 完整技能文档 | 详细使用说明 |
| `basic_network_scan.sh` | 基础扫描 | 快速网络侦察 |
| `full_port_scan.sh` | 完整扫描 | 深度端口扫描 |
| `batch_target_scan.sh` | 批量扫描 | 多目标处理 |
| `extract_open_ports.sh` | 数据提取 | 结果分析 |
| `install.sh` | 安装脚本 | 环境配置 |
| `nmap_config.conf` | 配置文件 | 参数调整 |
| `example_targets.txt` | 示例目标 | 测试使用 |
| `QUICK_START.md` | 快速指南 | 入门参考 |

---

## 🎯 核心功能

### 扫描类型
1. **快速扫描** (`-F`): 最常用的1000个端口
2. **完整扫描** (`-p-`): 所有65535个端口  
3. **Web扫描**: 常见Web服务端口
4. **服务识别** (`-sV`): 版本探测

### 输出格式
- **JSON** (`-oJ`): 结构化数据，便于自动化处理
- **HTML**: 可视化报告
- **CSV**: 表格数据
- **文本**: 人类可读摘要

### 批量处理
- 支持多目标并行扫描
- 自动生成汇总报告
- 失败重试机制

---

## 🔧 使用示例

### 场景1: 快速资产发现
```bash
# 扫描单个目标
./basic_network_scan.sh example.com

# 输出: scan_20260326_120000_example.com.json
# 包含: 开放端口、服务版本、扫描统计
```

### 场景2: 深度安全评估
```bash
# 完整端口扫描
./full_port_scan.sh 192.168.1.0/24

# 输出: 完整JSON + HTML报告 + 文本摘要
```

### 场景3: 批量资产盘点
```bash
# 准备目标列表
echo "server1.example.com" > targets.txt
echo "server2.example.com" >> targets.txt
echo "192.168.1.100" >> targets.txt

# 批量扫描
./batch_target_scan.sh targets.txt service

# 输出: 批量JSON文件 + 汇总报告
```

### 场景4: 数据分析
```bash
# 提取开放端口
./extract_open_ports.sh scan.json list

# 生成CSV报告
./extract_open_ports.sh scan.json csv > report.csv

# 生成HTML表格
./extract_open_ports.sh scan.json html > report.html
```

---

## ⚙️ 配置选项

### 扫描参数 (编辑 `nmap_config.conf`)
```ini
DEFAULT_SCAN_TYPE="fast"
DEFAULT_TIMEOUT=1800
SCAN_SPEED="T4"
MAX_RETRIES=2
PARALLEL_SCANS=5
```

### 输出配置
```ini
ENABLE_HTML_REPORT=true
ENABLE_JSON_OUTPUT=true
ENABLE_TEXT_SUMMARY=true
```

### 安全配置
```ini
REQUIRE_ROOT=false
VALIDATE_TARGETS=true
CHECK_LEGAL_COMPLIANCE=true
```

---

## 📊 输出示例

### JSON结构
```json
{
  "nmaprun": {
    "scanner": "nmap",
    "args": "nmap -T4 -F -oJ scan.json target.com",
    "startstr": "Thu Mar 26 12:00:00 2026",
    "host": {
      "status": {"state": "up"},
      "address": {"addr": "93.184.216.34"},
      "ports": {
        "port": [
          {
            "protocol": "tcp",
            "portid": "80",
            "state": {"state": "open"},
            "service": {"name": "http", "product": "nginx"}
          }
        ]
      }
    }
  }
}
```

### 报告示例
```
========================================
🔍 Nmap扫描报告
========================================
目标: example.com
状态: up
开放端口: 3个
  80/tcp - http (nginx)
  443/tcp - https (OpenSSL)
  22/tcp - ssh (OpenSSH)
扫描时间: 45秒
========================================
```

---

## 🛡️ 安全与合规

### 重要提醒
1. **授权第一**: 必须获得书面授权才能扫描
2. **范围明确**: 严格遵守测试范围
3. **避免影响**: 使用适当的扫描速度
4. **数据保护**: 妥善保管扫描结果

### 合规检查
- 扫描前验证授权状态
- 记录扫描时间和范围
- 生成合规报告
- 定期清理历史数据

---

## 🔍 集成使用

### 渗透测试流程
```bash
# 阶段1: 资产收集
./basic_network_scan.sh target.com > phase1.json

# 阶段2: 漏洞扫描 (基于开放端口)
# 阶段3: 深度测试
# 阶段4: 报告生成
```

### 自动化集成
```bash
#!/bin/bash
# 自动化安全监控脚本

# 1. 资产扫描
./batch_target_scan.sh assets.txt fast

# 2. 变化检测
diff previous_scan.json current_scan.json

# 3. 告警通知
if [ $? -ne 0 ]; then
    echo "端口变化检测!" | mail -s "安全告警" admin@example.com
fi
```

---

## 🐛 故障排除

### 常见问题
| 问题 | 解决方案 |
|------|----------|
| "nmap未找到" | 运行 `./install.sh` |
| 权限不足 | 使用 `sudo` 运行 |
| 扫描超时 | 调整 `DEFAULT_TIMEOUT` |
| 内存不足 | 减少 `PARALLEL_SCANS` |
| JSON解析错误 | 安装 `jq` 工具 |

### 错误代码
- `0`: 成功
- `1`: 一般错误
- `2`: 参数错误
- `3`: 网络错误
- `4`: 权限错误
- `124`: 超时

---

## 📚 学习资源

### Nmap官方文档
```bash
# 查看帮助
nmap --help

# 查看脚本
ls /usr/share/nmap/scripts/

# 学习扫描技术
man nmap
```

### 进阶技巧
1. **隐蔽扫描**: `-sS -T2 -f --data-length 100`
2. **服务识别**: `-sV --version-intensity 9`
3. **脚本扫描**: `-sC --script=vuln`
4. **输出管理**: `-oA basename` (所有格式)

### 社区资源
- Nmap官方手册
- NSE脚本库
- 安全社区论坛
- CTF挑战平台

---

## 📞 支持与反馈

### 获取帮助
1. 查看完整文档: `cat SKILL.md`
2. 运行测试: `./basic_network_scan.sh scanme.nmap.org`
3. 检查配置: `cat nmap_config.conf`

### 报告问题
- 检查日志文件
- 验证依赖安装
- 提供错误信息
- 附上配置文件

### 功能建议
- 扫描性能优化
- 输出格式扩展
- 集成其他工具
- 自动化流程改进

---

## 🎉 开始使用

### 第一步: 安装
```bash
chmod +x *.sh
./install.sh
```

### 第二步: 测试
```bash
./basic_network_scan.sh scanme.nmap.org
```

### 第三步: 实战
```bash
# 创建目标列表
echo "your-target.com" > my_targets.txt

# 执行扫描
./batch_target_scan.sh my_targets.txt fast

# 分析结果
./extract_open_ports.sh batch_scan_*/json/*.json list
```

### 第四步: 集成
- 添加到CI/CD流水线
- 集成到监控系统
- 自动化安全审计
- 定期资产盘点

---

## 📝 版本历史

### v1.0 (2026-03-26)
- ✅ 基础网络扫描功能
- ✅ 完整端口扫描
- ✅ 批量目标处理
- ✅ 多种输出格式
- ✅ 数据提取工具
- ✅ 安装配置脚本
- ✅ 完整文档

### 计划功能
- 🔄 Web界面
- 🔄 实时监控
- 🔄 漏洞关联
- 🔄 风险评估
- 🔄 API接口

---

**维护者**: 高级安全渗透测试专家  
**状态**: ✅ 生产就绪  
**更新**: 根据需求持续优化  

> 💡 **提示**: 始终遵守法律法规，仅在授权范围内进行测试。