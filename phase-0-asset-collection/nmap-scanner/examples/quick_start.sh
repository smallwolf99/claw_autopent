#!/bin/bash
# quick_start.sh
# OpenClaw Nmap Scanner 快速开始示例

# ========================================
# 快速开始指南 - 示例脚本
# ========================================

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 脚本目录
EXAMPLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$EXAMPLE_DIR")"

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}🚀 OpenClaw Nmap Scanner 快速开始${NC}"
echo -e "${CYAN}========================================${NC}"

# ========================================
# 步骤1: 安装依赖
# ========================================
echo -e "${BLUE}步骤1: 安装依赖${NC}"
echo -e "运行安装脚本检查并安装必要依赖..."
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/scripts/install.sh"
echo ""

# 检查是否已安装
if command -v nmap &>/dev/null; then
    echo -e "${GREEN}[✓] nmap已安装${NC}"
else
    echo -e "${YELLOW}[!] nmap未安装，请先安装${NC}"
    echo -e "安装命令:"
    echo -e "  Ubuntu/Debian: sudo apt-get install nmap"
    echo -e "  CentOS/RHEL: sudo yum install nmap"
    echo -e "  macOS: brew install nmap"
    echo ""
fi

# ========================================
# 步骤2: 配置技能
# ========================================
echo -e "${BLUE}步骤2: 配置技能${NC}"
echo -e "生成用户配置文件..."
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/scripts/config_loader.sh generate"
echo ""

# 检查配置文件
if [ -f "${HOME}/.config/openclaw/nmap-scanner.yaml" ]; then
    echo -e "${GREEN}[✓] 用户配置文件已存在${NC}"
else
    echo -e "${YELLOW}[!] 用户配置文件不存在，将自动生成${NC}"
    echo ""
fi

# ========================================
# 步骤3: 基本使用示例
# ========================================
echo -e "${BLUE}步骤3: 基本使用示例${NC}"
echo ""

# 示例1: 快速扫描
echo -e "${CYAN}示例1: 快速扫描单个目标${NC}"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh scan --target scanme.nmap.org"
echo -e "${YELLOW}或:${NC} ${SKILL_ROOT}/scripts/basic_network_scan.sh scanme.nmap.org"
echo ""

# 示例2: 完整扫描
echo -e "${CYAN}示例2: 完整端口扫描${NC}"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh scan --target scanme.nmap.org --full"
echo -e "${YELLOW}或:${NC} ${SKILL_ROOT}/scripts/full_port_scan.sh scanme.nmap.org"
echo ""

# 示例3: 批量扫描
echo -e "${CYAN}示例3: 批量扫描${NC}"
echo -e "首先创建目标列表文件:"
echo -e "${YELLOW}命令:${NC} echo 'scanme.nmap.org' > targets.txt"
echo -e "${YELLOW}命令:${NC} echo 'localhost' >> targets.txt"
echo -e "然后执行批量扫描:"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh batch --file targets.txt --type fast"
echo ""

# 示例4: 数据提取
echo -e "${CYAN}示例4: 数据提取${NC}"
echo -e "扫描完成后提取开放端口信息:"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh extract --file scan.json --format list"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh extract --file scan.json --format csv > ports.csv"
echo ""

# ========================================
# 步骤4: 高级用法
# ========================================
echo -e "${BLUE}步骤4: 高级用法${NC}"
echo ""

# 环境变量配置
echo -e "${CYAN}使用环境变量配置:${NC}"
echo -e "export NMAP_OUTPUT_DIR=\"/tmp/scan-results\""
echo -e "export NMAP_SCAN_TYPE=\"web\""
echo -e "export NMAP_TIMEOUT=300"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh scan --target example.com"
echo ""

# 自定义配置
echo -e "${CYAN}自定义配置文件:${NC}"
echo -e "编辑配置文件: ~/.config/openclaw/nmap-scanner.yaml"
echo -e "修改以下配置:"
echo -e "  scan:"
echo -e "    default_type: \"web\""
echo -e "    timing_template: \"T3\""
echo -e "    timeout_seconds: 600"
echo ""

# ========================================
# 步骤5: 集成到渗透测试流程
# ========================================
echo -e "${BLUE}步骤5: 集成到渗透测试流程${NC}"
echo ""

echo -e "${CYAN}渗透测试第一阶段 - 资产收集:${NC}"
cat << 'EOF'
#!/bin/bash
# phase1_asset_collection.sh

# 1. 扫描目标网络
${SKILL_ROOT}/nmap-scanner.sh scan --target $TARGET --full

# 2. 提取开放端口
${SKILL_ROOT}/nmap-scanner.sh extract --file scan_*.json --format csv > open_ports.csv

# 3. 分析服务版本
grep -E "http|ssh|ftp|mysql" open_ports.csv > critical_services.csv

# 4. 生成报告
echo "资产收集完成" > report.txt
echo "发现开放端口: $(wc -l < open_ports.csv)" >> report.txt
EOF
echo ""

# ========================================
# 步骤6: 安全合规提醒
# ========================================
echo -e "${BLUE}步骤6: 安全合规提醒${NC}"
echo ""

echo -e "${YELLOW}⚠  重要安全提醒:${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}1. 仅扫描您拥有或获得授权的目标${NC}"
echo -e "${YELLOW}2. 遵守当地网络安全法律法规${NC}"
echo -e "${YELLOW}3. 妥善保管扫描结果${NC}"
echo -e "${YELLOW}4. 避免对生产环境造成影响${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# ========================================
# 步骤7: 故障排除
# ========================================
echo -e "${BLUE}步骤7: 故障排除${NC}"
echo ""

echo -e "${CYAN}常见问题:${NC}"
echo -e "1. 权限不足: 使用 sudo 运行"
echo -e "2. 扫描超时: 增加超时时间或减少扫描范围"
echo -e "3. 输出文件问题: 检查磁盘空间和权限"
echo -e "4. 依赖缺失: 运行安装脚本"
echo ""

echo -e "${CYAN}获取帮助:${NC}"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh help"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/nmap-scanner.sh scan --help"
echo -e "${YELLOW}命令:${NC} ${SKILL_ROOT}/scripts/basic_network_scan.sh --help"
echo ""

# ========================================
# 步骤8: 实际演示
# ========================================
echo -e "${BLUE}步骤8: 实际演示${NC}"
echo ""

read -p "是否运行一个快速演示? (y/N): " -n 1 -r
echo ""
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}[▶] 开始演示...${NC}"
    echo ""
    
    # 演示1: 显示技能信息
    echo -e "${CYAN}演示1: 显示技能信息${NC}"
    "${SKILL_ROOT}/nmap-scanner.sh" info
    echo ""
    
    # 演示2: 显示配置
    echo -e "${CYAN}演示2: 显示当前配置${NC}"
    "${SKILL_ROOT}/nmap-scanner.sh" config show
    echo ""
    
    # 演示3: 测试扫描（使用本地回环地址）
    echo -e "${CYAN}演示3: 测试扫描本地主机${NC}"
    echo -e "${YELLOW}注意: 这只是一个演示，实际扫描可能需要时间${NC}"
    echo ""
    
    read -p "是否继续扫描测试? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}[⏳] 开始扫描测试...${NC}"
        "${SKILL_ROOT}/nmap-scanner.sh" scan --target localhost --quick
    else
        echo -e "${YELLOW}[⏭] 跳过扫描测试${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}[✅] 演示完成${NC}"
else
    echo -e "${YELLOW}[⏭] 跳过演示${NC}"
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}🎉 快速开始指南完成${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步建议:${NC}"
echo -e "1. 阅读完整文档: ${SKILL_ROOT}/SKILL.md"
echo -e "2. 查看示例配置: ${SKILL_ROOT}/configs/default.yaml"
echo -e "3. 运行测试套件: ${SKILL_ROOT}/tests/test_basic.sh"
echo -e "4. 开始实际扫描任务"
echo ""
echo -e "${CYAN}祝您使用愉快！${NC}"
echo -e "${CYAN}========================================${NC}"