#!/bin/bash
# install.sh
# nmap技能包安装脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🔧 Nmap技能包安装脚本 v1.0${NC}"
echo -e "${CYAN}========================================${NC}"

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "[*] 脚本目录: $SCRIPT_DIR"

# 检查依赖工具
echo -e "[.] 检查依赖工具..."
MISSING_DEPS=()

# 检查nmap
if ! command -v nmap &>/dev/null; then
    echo -e "${RED}[✗] nmap未安装${NC}"
    MISSING_DEPS+=("nmap")
else
    NMAP_VERSION=$(nmap --version | head -1 | awk '{print $3}')
    echo -e "${GREEN}[✓] nmap已安装 (版本: $NMAP_VERSION)${NC}"
fi

# 检查jq
if ! command -v jq &>/dev/null; then
    echo -e "${YELLOW}[!] jq未安装 (可选但推荐)${NC}"
    MISSING_DEPS+=("jq")
else
    JQ_VERSION=$(jq --version 2>/dev/null | cut -d'-' -f2)
    echo -e "${GREEN}[✓] jq已安装 (版本: $JQ_VERSION)${NC}"
fi

# 检查curl
if ! command -v curl &>/dev/null; then
    echo -e "${YELLOW}[!] curl未安装${NC}"
    MISSING_DEPS+=("curl")
else
    echo -e "${GREEN}[✓] curl已安装${NC}"
fi

# 检查Python3
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}[!] python3未安装 (可选)${NC}"
else
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}[✓] python3已安装 (版本: $PYTHON_VERSION)${NC}"
fi

# 安装缺失的依赖
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e ""
    echo -e "${YELLOW}[⚠] 发现缺失的依赖: ${MISSING_DEPS[@]}${NC}"
    
    # 检测操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        OS=$(uname -s)
    fi
    
    echo -e "[*] 检测到操作系统: $OS"
    
    # 提供安装命令
    case $OS in
        ubuntu|debian)
            echo -e "[💡] 安装命令:"
            echo -e "    sudo apt-get update"
            for dep in "${MISSING_DEPS[@]}"; do
                echo -e "    sudo apt-get install -y $dep"
            done
            ;;
        centos|rhel|fedora)
            echo -e "[💡] 安装命令:"
            for dep in "${MISSING_DEPS[@]}"; do
                if [ "$dep" = "nmap" ]; then
                    echo -e "    sudo yum install -y nmap"
                elif [ "$dep" = "jq" ]; then
                    echo -e "    sudo yum install -y jq"
                elif [ "$dep" = "curl" ]; then
                    echo -e "    sudo yum install -y curl"
                fi
            done
            ;;
        macos|darwin)
            echo -e "[💡] 安装命令:"
            echo -e "    brew update"
            for dep in "${MISSING_DEPS[@]}"; do
                echo -e "    brew install $dep"
            done
            ;;
        *)
            echo -e "${YELLOW}[!] 未知操作系统，请手动安装依赖${NC}"
            ;;
    esac
    
    echo -e ""
    read -p "是否自动安装缺失依赖? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $OS in
            ubuntu|debian)
                sudo apt-get update
                sudo apt-get install -y "${MISSING_DEPS[@]}"
                ;;
            centos|rhel)
                sudo yum install -y "${MISSING_DEPS[@]}"
                ;;
            macos|darwin)
                brew update
                brew install "${MISSING_DEPS[@]}"
                ;;
        esac
    else
        echo -e "${YELLOW}[!] 跳过依赖安装，某些功能可能受限${NC}"
    fi
fi

# 设置脚本权限
echo -e ""
echo -e "[.] 设置脚本执行权限..."
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] 脚本权限设置成功${NC}"
else
    echo -e "${RED}[✗] 权限设置失败${NC}"
fi

# 创建符号链接到/usr/local/bin（可选）
echo -e ""
read -p "是否创建符号链接到/usr/local/bin? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "[.] 创建符号链接..."
    
    # 检查/usr/local/bin是否在PATH中
    if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
        echo -e "${YELLOW}[!] /usr/local/bin不在PATH中${NC}"
    fi
    
    # 创建符号链接
    for script in "$SCRIPT_DIR"/*.sh; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            SCRIPT_NAME=$(basename "$script" .sh)
            sudo ln -sf "$script" "/usr/local/bin/$SCRIPT_NAME" 2>/dev/null
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}[✓] 创建链接: $SCRIPT_NAME${NC}"
            else
                echo -e "${YELLOW}[!] 创建链接失败: $SCRIPT_NAME${NC}"
            fi
        fi
    done
    
    echo -e "[💡] 现在可以直接使用命令: basic_network_scan, full_port_scan, 等"
fi

# 创建配置文件
echo -e ""
echo -e "[.] 创建配置文件..."
CONFIG_FILE="$SCRIPT_DIR/nmap_config.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOF
# Nmap技能包配置文件
# 生成时间: $(date)

# 扫描配置
DEFAULT_SCAN_TYPE="fast"          # 默认扫描类型: fast, full, web, service
DEFAULT_TIMEOUT=1800              # 默认超时时间(秒)
DEFAULT_OUTPUT_DIR="./scan_results" # 默认输出目录

# 网络配置
SCAN_SPEED="T4"                   # 扫描速度: T0-T5
MAX_RETRIES=2                     # 最大重试次数
PARALLEL_SCANS=5                  # 并行扫描数(批量扫描时)

# 输出配置
ENABLE_HTML_REPORT=true           # 是否生成HTML报告
ENABLE_JSON_OUTPUT=true           # 是否生成JSON输出
ENABLE_TEXT_SUMMARY=true          # 是否生成文本摘要

# 安全配置
REQUIRE_ROOT=false                # 是否要求root权限
VALIDATE_TARGETS=true             # 是否验证目标可达性
CHECK_LEGAL_COMPLIANCE=true       # 是否检查法律合规性

# 通知配置
SEND_NOTIFICATIONS=false          # 是否发送通知
NOTIFICATION_EMAIL=""             # 通知邮箱
NOTIFICATION_WEBHOOK=""           # Webhook URL

# 高级配置
CUSTOM_NSE_SCRIPTS=""             # 自定义NSE脚本
ADDITIONAL_ARGS=""                # 额外参数
EOF
    
    echo -e "${GREEN}[✓] 配置文件创建: $CONFIG_FILE${NC}"
else
    echo -e "${YELLOW}[!] 配置文件已存在: $CONFIG_FILE${NC}"
fi

# 创建示例目标文件
echo -e ""
echo -e "[.] 创建示例文件..."
EXAMPLE_TARGETS="$SCRIPT_DIR/example_targets.txt"
if [ ! -f "$EXAMPLE_TARGETS" ]; then
    cat > "$EXAMPLE_TARGETS" << EOF
# Nmap扫描示例目标文件
# 每行一个目标，支持IP地址或域名
# 以#开头的行是注释

# 示例目标
scanme.nmap.org
# 192.168.1.1
# example.com

# 本地测试
127.0.0.1
localhost

# 常用测试目标
testphp.vulnweb.com
demo.testfire.net
EOF
    
    echo -e "${GREEN}[✓] 示例目标文件创建: $EXAMPLE_TARGETS${NC}"
fi

# 创建使用指南
echo -e ""
echo -e "[.] 创建快速使用指南..."
GUIDE_FILE="$SCRIPT_DIR/QUICK_START.md"
if [ ! -f "$GUIDE_FILE" ]; then
    cat > "$GUIDE_FILE" << EOF
# Nmap技能包快速使用指南

## 🚀 快速开始

### 1. 基础扫描
\`\`\`bash
# 快速扫描单个目标
./basic_network_scan.sh target.com

# 完整端口扫描
./full_port_scan.sh 192.168.1.1
\`\`\`

### 2. 批量扫描
\`\`\`bash
# 批量快速扫描
./batch_target_scan.sh targets.txt fast

# 批量Web服务扫描
./batch_target_scan.sh websites.txt web
\`\`\`

### 3. 数据提取
\`\`\`bash
# 提取开放端口
./extract_open_ports.sh scan.json list

# 生成CSV报告
./extract_open_ports.sh scan.json csv > report.csv
\`\`\`

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| \`basic_network_scan.sh\` | 基础网络扫描脚本 |
| \`full_port_scan.sh\` | 完整端口扫描脚本 |
| \`batch_target_scan.sh\` | 批量目标扫描脚本 |
| \`extract_open_ports.sh\` | 数据提取工具 |
| \`nmap_config.conf\` | 配置文件 |
| \`example_targets.txt\` | 示例目标文件 |
| \`SKILL.md\` | 完整技能文档 |

## ⚙️ 常用命令

### 扫描命令
\`\`\`bash
# 快速扫描最常用的1000个端口
nmap -T4 -F -oJ result.json target.com

# 完整端口扫描
nmap -p- -T4 -sS -sV -oJ full_scan.json target.com

# Web服务扫描
nmap -p 80,443,8080,8443 -sV -oJ web_scan.json target.com
\`\`\`

### 数据提取命令
\`\`\`bash
# 使用jq提取开放端口
jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | "\(.protocol)/\(.portid)"' scan.json

# 统计开放端口数量
jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | .portid' scan.json | wc -l
\`\`\`

## 🔧 故障排除

### 常见问题
1. **权限不足**: 使用 \`sudo\` 运行脚本
2. **nmap未安装**: 运行 \`./install.sh\` 安装依赖
3. **扫描超时**: 调整配置文件中的超时时间
4. **内存不足**: 减少并行扫描数量

### 错误代码
- \`1\`: 一般错误
- \`2\`: 无效参数
- \`3\`: 网络错误
- \`4\`: 权限不足
- \`124\`: 超时

## 📞 支持

如有问题，请参考:
1. 完整文档: \`SKILL.md\`
2. 配置文件: \`nmap_config.conf\`
3. 示例文件: \`example_targets.txt\`

## 📝 更新日志

- v1.0 (2026-03-26): 初始版本发布
- 包含基础扫描、批量处理、数据提取功能

EOF
    
    echo -e "${GREEN}[✓] 快速指南创建: $GUIDE_FILE${NC}"
fi

# 测试安装
echo -e ""
echo -e "[.] 测试安装..."
TEST_RESULT=0

# 测试nmap命令
if command -v nmap &>/dev/null; then
    echo -e "${GREEN}[✓] nmap命令测试通过${NC}"
else
    echo -e "${RED}[✗] nmap命令测试失败${NC}"
    TEST_RESULT=1
fi

# 测试脚本执行
if [ -x "$SCRIPT_DIR/basic_network_scan.sh" ]; then
    echo -e "${GREEN}[✓] 脚本执行权限测试通过${NC}"
else
    echo -e "${RED}[✗] 脚本执行权限测试失败${NC}"
    TEST_RESULT=1
fi

# 显示安装完成信息
echo -e ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}[🎉] Nmap技能包安装完成！${NC}"
echo -e "${CYAN}========================================${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}[✅] 所有测试通过${NC}"
else
    echo -e "${YELLOW}[⚠] 部分测试失败，请检查依赖${NC}"
fi

echo -e ""
echo -e "${BLUE}[📚] 下一步:${NC}"
echo -e "  1. 阅读使用指南: cat $GUIDE_FILE"
echo -e "  2. 查看完整文档: cat SKILL.md"
echo -e "  3. 运行示例扫描: ./basic_network_scan.sh scanme.nmap.org"
echo -e "  4. 批量扫描测试: ./batch_target_scan.sh example_targets.txt fast"
echo -e ""
echo -e "${BLUE}[💡] 提示:${NC}"
echo -e "  • 确保有合法授权才能扫描目标"
echo -e "  • 扫描前请验证目标可达性"
echo -e "  • 使用适当的扫描速度避免影响目标"
echo -e ""
echo -e "${CYAN}========================================${NC}"

exit $TEST_RESULT