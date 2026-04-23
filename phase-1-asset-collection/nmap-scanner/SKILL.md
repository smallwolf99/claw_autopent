# 🔍 OpenClaw Nmap Scanner Skill

## 📋 技能概述

**nmap-scanner** - 一个符合OpenClaw规范的网络资产发现和端口扫描技能包，支持多种扫描类型并将结果保存为JSON格式，便于自动化处理和数据分析。

**技能类型**: 网络侦察 / 资产发现  
**所属阶段**: Phase 1 - Asset Collection（资产收集阶段）  
**输出格式**: JSON, HTML, CSV, Text  
**依赖工具**: nmap (必须), jq (推荐)  
**OpenClaw版本**: ≥ 2026.3.0  
**技能版本**: 1.0.0

---

## 🏗️ OpenClaw规范符合性

### 技能架构
```
nmap-scanner/
├── manifest.json              # 技能元数据 (符合OpenClaw规范)
├── SKILL.md                   # 技能文档 (本文件)
├── nmap-scanner.sh           # 主入口脚本
├── configs/                  # 配置文件目录
│   └── default.yaml          # 默认配置
├── scripts/                  # 可执行脚本目录
│   ├── basic_network_scan.sh # 基础扫描脚本
│   ├── full_port_scan.sh     # 完整端口扫描
│   ├── batch_target_scan.sh  # 批量扫描
│   ├── extract_open_ports.sh # 数据提取
│   ├── config_loader.sh      # 配置管理
│   └── install.sh           # 安装脚本
├── tests/                    # 测试套件
│   └── test_basic.sh        # 基础测试
├── examples/                 # 使用示例
│   └── quick_start.sh       # 快速开始
├── templates/               # 模板文件 (预留)
└── docs/                    # 文档目录 (预留)
```

### 技能元数据 (manifest.json)
```json
{
  "name": "nmap-scanner",
  "version": "1.0.0",
  "description": "Professional network security scanner with JSON output format support",
  "author": "高级安全渗透测试专家",
  "category": "penetration-testing",
  "subcategory": "asset-discovery",
  "phase": "phase-1-asset-collection",
  "platforms": ["linux", "macos", "windows-wsl"],
  "dependencies": {
    "required": ["nmap"],
    "recommended": ["jq", "curl", "python3"]
  }
}
```

---

## 🚀 快速开始

### 1. 安装依赖
```bash
# 运行安装脚本
./scripts/install.sh

# 或手动安装
sudo apt-get install nmap jq curl  # Ubuntu/Debian
sudo yum install nmap jq curl      # CentOS/RHEL
brew install nmap jq curl          # macOS
```

### 2. 配置技能
```bash
# 生成用户配置
./scripts/config_loader.sh generate

# 查看当前配置
./nmap-scanner.sh config show
```

### 3. 基本使用
```bash
# 使用主入口脚本
./nmap-scanner.sh scan --target scanme.nmap.org

# 或直接使用脚本
./scripts/basic_network_scan.sh scanme.nmap.org
```

### 4. 测试技能
```bash
# 运行测试套件
./tests/test_basic.sh

# 查看技能信息
./nmap-scanner.sh info
```

---

## 🎯 核心功能

### 1. 扫描类型

#### 基础扫描
```bash
# 快速扫描 - 最常用的1000个TCP端口
./nmap-scanner.sh scan --target example.com --quick

# 完整端口扫描 - 所有65535个端口
./nmap-scanner.sh scan --target example.com --full

# Web服务扫描 - 常见Web端口
./nmap-scanner.sh scan --target example.com --web

# 服务版本扫描 - 深度服务识别
./nmap-scanner.sh scan --target example.com --service
```

#### 高级扫描技术
```bash
# TCP SYN扫描（半开放扫描）
nmap -sS -T4 -oJ syn_scan.json <target>

# UDP端口扫描
nmap -sU -T4 --top-ports 100 -oJ udp_scan.json <target>

# 操作系统识别
nmap -O -T4 -oJ os_scan.json <target>

# 服务版本探测
nmap -sV -T4 -oJ service_scan.json <target>
```

### 2. 输出格式控制
```bash
# JSON格式输出（推荐）
nmap -oJ result.json <target>

# 结合多种输出格式
nmap -oA scan_name <target>  # 生成所有格式：XML、grepable、normal格式

# 时间控制
nmap -T0  # 偏执狂（非常慢）
nmap -T1  # 猥琐的
nmap -T2  # 礼貌的
nmap -T3  # 正常的（默认）
nmap -T4  # 激进的（推荐）
nmap -T5  # 疯狂的
```

### 3. 批量处理
```bash
# 创建目标列表
echo "scanme.nmap.org" > targets.txt
echo "localhost" >> targets.txt

# 批量快速扫描
./nmap-scanner.sh batch --file targets.txt --type fast

# 批量Web服务扫描
./nmap-scanner.sh batch --file targets.txt --type web
```

### 4. 数据提取与分析
```bash
# 提取开放端口列表
./nmap-scanner.sh extract --file scan.json --format list

# 生成CSV报告
./nmap-scanner.sh extract --file scan.json --format csv > report.csv

# 生成HTML报告
./nmap-scanner.sh extract --file scan.json --format html > report.html

# 生成Markdown表格
./nmap-scanner.sh extract --file scan.json --format markdown
```

---

## ⚙️ 配置系统

### 配置文件层级
1. **环境变量**: `NMAP_SCAN_CONFIG`, `NMAP_OUTPUT_DIR`, `NMAP_TIMEOUT`
2. **用户配置**: `~/.config/openclaw/nmap-scanner.yaml`
3. **默认配置**: `configs/default.yaml`

### 配置示例
```yaml
# ~/.config/openclaw/nmap-scanner.yaml
scan:
  default_type: "fast"
  timing_template: "T4"
  timeout_seconds: 1800
  max_parallel_scans: 5
  validate_targets: true

output:
  directory: "./scan-results"
  organize_by_date: true
  generate_html: true
  generate_summary: true

security:
  legal_compliance_check: true
  show_warnings: true
  activity_logging: true
```

### 环境变量覆盖
```bash
# 临时覆盖配置
export NMAP_OUTPUT_DIR="/tmp/scan-results"
export NMAP_SCAN_TYPE="web"
export NMAP_TIMEOUT=300

# 使用覆盖后的配置
./nmap-scanner.sh scan --target example.com
```

---

## 📊 输出格式解析

### JSON格式结构
```json
{
  "nmaprun": {
    "scanner": "nmap",
    "args": "nmap -T4 -F -oJ scan.json 192.168.1.1",
    "start": "1742928000",
    "startstr": "Thu Mar 26 08:00:00 2026",
    
    "host": {
      "status": {"state": "up", "reason": "echo-reply"},
      "address": {"addr": "192.168.1.1", "addrtype": "ipv4"},
      "hostnames": {"hostname": [{"name": "router.local", "type": "PTR"}]},
      
      "ports": {
        "port": [
          {
            "protocol": "tcp",
            "portid": "80",
            "state": {"state": "open", "reason": "syn-ack"},
            "service": {"name": "http", "product": "nginx", "version": "1.18.0"}
          }
        ]
      }
    },
    
    "runstats": {
      "finished": {"time": "1742928030", "timestr": "Thu Mar 26 08:00:30 2026"},
      "hosts": {"up": "1", "down": "0", "total": "1"}
    }
  }
}
```

### 关键字段说明
- `host.status.state`: 主机状态（up/down）
- `host.address.addr`: IP地址
- `ports.port[]`: 端口数组，每个端口包含：
  - `protocol`: 协议类型（tcp/udp）
  - `portid`: 端口号
  - `state.state`: 端口状态（open/closed/filtered）
  - `service`: 服务信息（名称、产品、版本）

---

## 🛠️ 脚本使用指南

### 主入口脚本
```bash
# 显示帮助
./nmap-scanner.sh help

# 显示技能信息
./nmap-scanner.sh info

# 扫描命令
./nmap-scanner.sh scan --target example.com --full

# 批量扫描
./nmap-scanner.sh batch --file targets.txt --type fast

# 数据提取
./nmap-scanner.sh extract --file scan.json --format csv

# 配置管理
./nmap-scanner.sh config show
./nmap-scanner.sh config generate

# 安装依赖
./nmap-scanner.sh install
```

### 独立脚本
```bash
# 基础网络扫描
./scripts/basic_network_scan.sh --target example.com --quick

# 完整端口扫描
./scripts/full_port_scan.sh 192.168.1.1

# 批量目标扫描
./scripts/batch_target_scan.sh targets.txt fast

# 数据提取工具
./scripts/extract_open_ports.sh scan.json list

# 配置加载器
./scripts/config_loader.sh show
./scripts/config_loader.sh generate

# 安装脚本
./scripts/install.sh
```

---

## 🎨 扫描配置组合

### Web服务器扫描
```bash
# Web应用完整扫描
./nmap-scanner.sh scan --target example.com --web

# HTTP/HTTPS服务版本识别
nmap -p 80,443 --script http-title,http-headers -oJ http_info.json <target>
```

### 数据库服务扫描
```bash
# 常见数据库端口
nmap -p 1433,1521,3306,5432,27017 -sV -oJ database_scan.json <target>

# MySQL扫描
nmap -p 3306 --script mysql-info -oJ mysql_scan.json <target>
```

### 网络设备扫描
```bash
# 路由器/交换机端口
nmap -p 22,23,161,443,80 -sV -oJ network_device.json <target>

# SNMP扫描
nmap -p 161 --script snmp-info -oJ snmp_scan.json <target>
```

---

## 🔧 集成使用

### 渗透测试流程集成
```bash
#!/bin/bash
# 集成扫描流程

# 1. 资产收集
./nmap-scanner.sh scan --target $TARGET --full

# 2. 数据分析
./nmap-scanner.sh extract --file scan_*.json --format csv > open_ports.csv

# 3. 漏洞扫描（基于开放端口）
# 4. 报告生成
```

### 自动化安全监控
```bash
#!/bin/bash
# 自动化安全监控脚本

# 1. 定期资产扫描
./nmap-scanner.sh batch --file assets.txt --type fast

# 2. 变化检测
diff previous_scan.json current_scan.json

# 3. 告警通知
if [ $? -ne 0 ]; then
    echo "端口变化检测!" | mail -s "安全告警" admin@example.com
fi
```

### CI/CD流水线集成
```yaml
# .gitlab-ci.yml 示例
security_scan:
  stage: test
  script:
    - ./nmap-scanner.sh scan --target $DEPLOYMENT_TARGET --web
    - ./nmap-scanner.sh extract --file scan_*.json --format csv > security_report.csv
  artifacts:
    paths:
      - scan_*.json
      - security_report.csv
```

---

## ⚠️ 安全与合规

### 法律合规要求
1. **授权第一**: 必须获得书面授权才能扫描
2. **范围明确**: 严格遵守测试范围
3. **避免影响**: 使用适当的扫描速度
4. **数据保护**: 妥善保管扫描结果

### 合规检查
```bash
# 技能内置合规检查
export NMAP_LEGAL_COMPLIANCE_CHECK=true
./nmap-scanner.sh scan --target example.com
```

### 安全建议
- 仅扫描授权目标
- 使用非破坏性扫描技术
- 记录所有扫描活动
- 定期清理历史数据
- 加密存储敏感结果

---

## 📈 性能优化

### 扫描优化策略
```bash
# 控制扫描速度
nmap -T2  # 礼貌模式，降低扫描速度
nmap --max-rate 100  # 限制每秒100个包

# 避免触发IDS/IPS
nmap -f  # 分片
nmap -D RND:10  # 诱饵扫描
nmap --data-length 100  # 添加随机数据

# 资源优化
nmap --min-rate 10  # 最小速率
nmap --max-retries 2  # 最大重试
```

### 内存与CPU优化
```bash
# 减少内存使用
nmap --min-parallelism 10
nmap --max-parallelism 100

# 控制CPU使用
nmap --min-hostgroup 10
nmap --max-hostgroup 100
```

---

## 🐛 故障排除

### 常见问题
| 问题 | 解决方案 |
|------|----------|
| "nmap未找到" | 运行 `./scripts/install.sh` |
| 权限不足 | 使用 `sudo` 运行 |
| 扫描超时 | 调整 `timeout_seconds` 配置 |
| 内存不足 | 减少 `max_parallel_scans` |
| JSON解析错误 | 安装 `jq` 工具 |

### 错误代码
- `0`: 成功
- `1`: 一般错误
- `2`: 参数错误
- `3`: 网络错误
- `4`: 权限错误
- `124`: 超时

### 调试模式
```bash
# 启用详细输出
export NMAP_DEBUG=true
./nmap-scanner.sh scan --target example.com

# 查看日志
tail -f scan_*.log
```

---

## 📚 学习资源

### Nmap官方资源
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

## 🧪 测试与验证

### 运行测试套件
```bash
# 运行所有测试
./tests/test_basic.sh all

# 运行特定测试
./tests/test_basic.sh dependencies
./tests/test_basic.sh config
./tests/test_basic.sh manifest
```

### 测试覆盖率
- ✅ 目录结构测试
- ✅ 脚本权限测试
- ✅ 依赖工具测试
- ✅ 配置文件测试
- ✅ 技能元数据测试
- ✅ 帮助系统测试
- ✅ 配置加载测试
- ✅ 参数解析测试
- ✅ 模拟功能测试

### 集成测试
```bash
# 端到端测试
./examples/quick_start.sh
```

---

## 🔄 更新与维护

### 版本管理
```bash
# 查看当前版本
./nmap-scanner.sh info

# 检查更新
git pull origin main

# 更新依赖
./scripts/install.sh
```

### 贡献指南
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 运行测试套件
5. 提交Pull Request

### 问题报告
- 检查现有Issue
- 提供重现步骤
- 附上错误日志
- 说明环境信息

---

## 📞 支持与反馈

### 获取帮助
```bash
# 查看技能信息
./nmap-scanner.sh info

# 查看帮助
./nmap-scanner.sh help
./nmap-scanner.sh scan --help

# 运行示例
./examples/quick_start.sh
```

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
chmod +x scripts/*.sh
./scripts/install.sh
```

### 第二步: 配置
```bash
./scripts/config_loader.sh generate
./nmap-scanner.sh config show
```

### 第三步: 测试
```bash
./tests/test_basic.sh
./nmap-scanner.sh scan --target scanme.nmap.org --quick
```

### 第四步: 实战
```bash
# 创建目标列表
echo "your-target.com" > my_targets.txt

# 执行扫描
./nmap-scanner.sh batch --file my_targets.txt fast

# 分析结果
./nmap-scanner.sh extract --file scan_*.json list
```

### 第五步: 集成
- 添加到CI/CD流水线
- 集成到监控系统
- 自动化安全审计
- 定期资产盘点

---

## 📝 版本历史

### v1.0.0 (2026-03-26)
- ✅ 符合OpenClaw规范架构
- ✅ 完整的配置管理系统
- ✅ 多种扫描类型支持
- ✅ 批量处理能力
- ✅ 多种输出格式
- ✅ 数据提取工具
- ✅ 完整的测试套件
- ✅ 安全合规检查
- ✅ 跨平台支持

### 计划功能
- 🔄 Web管理界面
- 🔄 实时监控仪表板
- 🔄 漏洞关联分析
- 🔄 风险评估报告
- 🔄 API接口服务
- 🔄 插件扩展系统

---

**维护者**: 高级安全渗透测试专家  
**状态**: ✅ 生产就绪  
**更新策略**: 定期维护，根据需求优化  
**许可证**: MIT  
**仓库**: https://github.com/openclaw-org/skills/nmap-scanner  

> 💡 **提示**: 始终遵守法律法规，仅在授权范围内进行测试。安全是责任，不是特权。