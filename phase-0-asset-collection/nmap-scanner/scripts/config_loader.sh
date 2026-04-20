#!/bin/bash
# config_loader.sh
# OpenClaw Nmap Scanner Configuration Loader

# ========================================
# 配置管理系统
# ========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

# 默认配置文件路径
DEFAULT_CONFIG="${SKILL_ROOT}/configs/default.yaml"
USER_CONFIG="${HOME}/.config/openclaw/nmap-scanner.yaml"
ENV_CONFIG="${NMAP_SCAN_CONFIG:-}"

# 加载配置文件
load_config() {
    local config_file=""
    
    # 确定使用哪个配置文件
    if [ -n "$ENV_CONFIG" ] && [ -f "$ENV_CONFIG" ]; then
        config_file="$ENV_CONFIG"
        echo -e "${GREEN}[✓] 使用环境变量配置: $config_file${NC}"
    elif [ -f "$USER_CONFIG" ]; then
        config_file="$USER_CONFIG"
        echo -e "${GREEN}[✓] 使用用户配置: $config_file${NC}"
    elif [ -f "$DEFAULT_CONFIG" ]; then
        config_file="$DEFAULT_CONFIG"
        echo -e "${YELLOW}[!] 使用默认配置: $config_file${NC}"
    else
        echo -e "${RED}[✗] 错误: 未找到配置文件${NC}"
        return 1
    fi
    
    # 解析YAML配置文件（简化版本，实际应使用yq或类似工具）
    parse_yaml_config "$config_file"
    
    # 应用环境变量覆盖
    apply_env_overrides
    
    # 验证配置
    validate_config
    
    return 0
}

# 解析YAML配置文件（简化实现）
parse_yaml_config() {
    local config_file="$1"
    
    echo -e "${BLUE}[.] 加载配置文件: $(basename "$config_file")${NC}"
    
    # 读取配置到变量（简化实现，实际应使用yq）
    if command -v yq &>/dev/null; then
        # 使用yq解析
        echo -e "${GREEN}[✓] 使用yq解析YAML${NC}"
        
        # 加载扫描配置
        CONFIG_SCAN_TYPE=$(yq e '.scan.default_type // "fast"' "$config_file")
        CONFIG_TIMING=$(yq e '.scan.timing_template // "T4"' "$config_file")
        CONFIG_TIMEOUT=$(yq e '.scan.timeout_seconds // 1800' "$config_file")
        CONFIG_VALIDATE=$(yq e '.scan.validate_targets // true' "$config_file")
        
        # 加载输出配置
        CONFIG_OUTPUT_DIR=$(yq e '.output.directory // "./scan-results"' "$config_file")
        CONFIG_GENERATE_HTML=$(yq e '.output.generate_html // true' "$config_file")
        
        # 加载安全配置
        CONFIG_LEGAL_CHECK=$(yq e '.security.legal_compliance_check // true' "$config_file")
        
        # 加载网络配置
        CONFIG_MAX_RATE=$(yq e '.network.max_rate // 100' "$config_file")
        
    elif command -v python3 &>/dev/null; then
        # 使用Python解析
        echo -e "${GREEN}[✓] 使用Python解析YAML${NC}"
        
        read -r -d '' PYTHON_CODE << 'EOF'
import yaml, sys, os, json
try:
    with open(sys.argv[1], 'r') as f:
        config = yaml.safe_load(f)
        
    # 默认值
    defaults = {
        'scan': {'default_type': 'fast', 'timing_template': 'T4', 'timeout_seconds': 1800},
        'output': {'directory': './scan-results', 'generate_html': True},
        'security': {'legal_compliance_check': True},
        'network': {'max_rate': 100}
    }
    
    # 合并配置
    def get_value(config_dict, key_path, default_dict):
        keys = key_path.split('.')
        current = config_dict
        default_current = default_dict
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
                if isinstance(default_current, dict) and key in default_current:
                    default_current = default_current[key]
                else:
                    default_current = None
            else:
                return default_current if default_current is not None else None
        
        return current
    
    configs = {}
    configs['scan_type'] = get_value(config, 'scan.default_type', defaults)
    configs['timing'] = get_value(config, 'scan.timing_template', defaults)
    configs['timeout'] = get_value(config, 'scan.timeout_seconds', defaults)
    configs['output_dir'] = get_value(config, 'output.directory', defaults)
    
    print(json.dumps(configs))
except Exception as e:
    print(json.dumps({'error': str(e)}))
EOF
        
        PYTHON_OUTPUT=$(python3 -c "$PYTHON_CODE" "$config_file" 2>/dev/null)
        
        if echo "$PYTHON_OUTPUT" | grep -q "error"; then
            echo -e "${YELLOW}[!] Python YAML解析失败，使用默认值${NC}"
            load_default_config
        else
            CONFIG_SCAN_TYPE=$(echo "$PYTHON_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('scan_type', 'fast'))")
            CONFIG_TIMING=$(echo "$PYTHON_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('timing', 'T4'))")
            CONFIG_TIMEOUT=$(echo "$PYTHON_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('timeout', 1800))")
            CONFIG_OUTPUT_DIR=$(echo "$PYTHON_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('output_dir', './scan-results'))")
        fi
        
    else
        # 简单文本解析（仅支持基本配置）
        echo -e "${YELLOW}[!] 未找到yq或python，使用简单文本解析${NC}"
        
        CONFIG_SCAN_TYPE=$(grep -A1 "default_type:" "$config_file" | tail -1 | tr -d ' ' | cut -d: -f2 | tr -d '\"')
        CONFIG_TIMING=$(grep -A1 "timing_template:" "$config_file" | tail -1 | tr -d ' ' | cut -d: -f2 | tr -d '\"')
        CONFIG_TIMEOUT=$(grep -A1 "timeout_seconds:" "$config_file" | tail -1 | tr -d ' ' | cut -d: -f2)
        CONFIG_OUTPUT_DIR=$(grep -A1 "directory:" "$config_file" | tail -1 | tr -d ' ' | cut -d: -f2 | tr -d '\"')
        
        # 设置默认值
        CONFIG_SCAN_TYPE=${CONFIG_SCAN_TYPE:-"fast"}
        CONFIG_TIMING=${CONFIG_TIMING:-"T4"}
        CONFIG_TIMEOUT=${CONFIG_TIMEOUT:-1800}
        CONFIG_OUTPUT_DIR=${CONFIG_OUTPUT_DIR:-"./scan-results"}
    fi
    
    # 确保输出目录存在
    mkdir -p "$CONFIG_OUTPUT_DIR"
    
    echo -e "${CYAN}[✓] 配置加载完成${NC}"
}

# 加载默认配置
load_default_config() {
    echo -e "${YELLOW}[!] 使用硬编码默认配置${NC}"
    
    CONFIG_SCAN_TYPE="fast"
    CONFIG_TIMING="T4"
    CONFIG_TIMEOUT=1800
    CONFIG_VALIDATE=true
    CONFIG_OUTPUT_DIR="./scan-results"
    CONFIG_GENERATE_HTML=true
    CONFIG_LEGAL_CHECK=true
    CONFIG_MAX_RATE=100
}

# 应用环境变量覆盖
apply_env_overrides() {
    # 扫描类型覆盖
    if [ -n "$NMAP_SCAN_TYPE" ]; then
        CONFIG_SCAN_TYPE="$NMAP_SCAN_TYPE"
        echo -e "${CYAN}[⚙️] 环境变量覆盖扫描类型: $CONFIG_SCAN_TYPE${NC}"
    fi
    
    # 输出目录覆盖
    if [ -n "$NMAP_OUTPUT_DIR" ]; then
        CONFIG_OUTPUT_DIR="$NMAP_OUTPUT_DIR"
        echo -e "${CYAN}[⚙️] 环境变量覆盖输出目录: $CONFIG_OUTPUT_DIR${NC}"
    fi
    
    # 超时覆盖
    if [ -n "$NMAP_TIMEOUT" ]; then
        CONFIG_TIMEOUT="$NMAP_TIMEOUT"
        echo -e "${CYAN}[⚙️] 环境变量覆盖超时: $CONFIG_TIMEOUT秒${NC}"
    fi
}

# 验证配置
validate_config() {
    local errors=0
    
    echo -e "${BLUE}[.] 验证配置...${NC}"
    
    # 验证扫描类型
    case "$CONFIG_SCAN_TYPE" in
        fast|full|web|service)
            echo -e "${GREEN}[✓] 扫描类型有效: $CONFIG_SCAN_TYPE${NC}"
            ;;
        *)
            echo -e "${RED}[✗] 无效的扫描类型: $CONFIG_SCAN_TYPE${NC}"
            echo -e "${YELLOW}[!] 使用默认值: fast${NC}"
            CONFIG_SCAN_TYPE="fast"
            errors=$((errors+1))
            ;;
    esac
    
    # 验证定时模板
    case "$CONFIG_TIMING" in
        T0|T1|T2|T3|T4|T5)
            echo -e "${GREEN}[✓] 定时模板有效: $CONFIG_TIMING${NC}"
            ;;
        *)
            echo -e "${RED}[✗] 无效的定时模板: $CONFIG_TIMING${NC}"
            echo -e "${YELLOW}[!] 使用默认值: T4${NC}"
            CONFIG_TIMING="T4"
            errors=$((errors+1))
            ;;
    esac
    
    # 验证超时值
    if [[ "$CONFIG_TIMEOUT" =~ ^[0-9]+$ ]] && [ "$CONFIG_TIMEOUT" -ge 60 ]; then
        echo -e "${GREEN}[✓] 超时值有效: ${CONFIG_TIMEOUT}秒${NC}"
    else
        echo -e "${RED}[✗] 无效的超时值: $CONFIG_TIMEOUT${NC}"
        echo -e "${YELLOW}[!] 使用默认值: 1800秒${NC}"
        CONFIG_TIMEOUT=1800
        errors=$((errors+1))
    fi
    
    # 验证输出目录
    if mkdir -p "$CONFIG_OUTPUT_DIR" 2>/dev/null; then
        echo -e "${GREEN}[✓] 输出目录有效: $CONFIG_OUTPUT_DIR${NC}"
    else
        echo -e "${RED}[✗] 无法创建输出目录: $CONFIG_OUTPUT_DIR${NC}"
        echo -e "${YELLOW}[!] 使用当前目录${NC}"
        CONFIG_OUTPUT_DIR="."
        errors=$((errors+1))
    fi
    
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}[✓] 配置验证通过${NC}"
    else
        echo -e "${YELLOW}[⚠] 配置验证发现 $errors 个问题，已应用默认值${NC}"
    fi
}

# 显示当前配置
show_config() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${MAGENTA}🔧 当前Nmap扫描器配置${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    echo -e "${BLUE}扫描配置:${NC}"
    echo -e "  类型: ${CONFIG_SCAN_TYPE}"
    echo -e "  定时模板: ${CONFIG_TIMING}"
    echo -e "  超时: ${CONFIG_TIMEOUT}秒"
    echo -e "  验证目标: ${CONFIG_VALIDATE}"
    echo -e "  最大速率: ${CONFIG_MAX_RATE}包/秒"
    
    echo -e "${BLUE}输出配置:${NC}"
    echo -e "  输出目录: ${CONFIG_OUTPUT_DIR}"
    echo -e "  生成HTML: ${CONFIG_GENERATE_HTML}"
    
    echo -e "${BLUE}安全配置:${NC}"
    echo -e "  法律合规检查: ${CONFIG_LEGAL_CHECK}"
    
    echo -e "${CYAN}========================================${NC}"
}

# 生成配置模板
generate_config_template() {
    local output_file="${1:-${HOME}/.config/openclaw/nmap-scanner.yaml}"
    
    echo -e "${BLUE}[.] 生成配置模板: $output_file${NC}"
    
    mkdir -p "$(dirname "$output_file")"
    
    cat > "$output_file" << 'EOF'
# Nmap Scanner User Configuration
# Generated: $(date)

scan:
  default_type: "fast"
  timing_template: "T4"
  timeout_seconds: 1800
  max_parallel_scans: 5
  max_retries: 2
  validate_targets: true
  ping_targets: true

output:
  formats:
    - json
    - text
  directory: "./scan-results"
  organize_by_date: true
  generate_html: true
  generate_summary: true
  auto_open_report: false

security:
  require_root: false
  legal_compliance_check: true
  show_warnings: true
  activity_logging: true
  encrypt_sensitive: false

network:
  max_rate: 100
  min_rate: 10
  dns_resolution: true
  reverse_dns: true
  assume_hosts_up: false

# 更多配置选项请参考 configs/default.yaml
EOF
    
    if [ -f "$output_file" ]; then
        echo -e "${GREEN}[✓] 配置模板生成成功: $output_file${NC}"
        echo -e "${YELLOW}[💡] 编辑此文件来自定义扫描行为${NC}"
    else
        echo -e "${RED}[✗] 配置模板生成失败${NC}"
    fi
}

# 检查配置工具依赖
check_dependencies() {
    echo -e "${BLUE}[.] 检查配置工具依赖...${NC}"
    
    local missing=()
    
    # 检查YAML解析工具
    if ! command -v yq &>/dev/null && ! command -v python3 &>/dev/null; then
        echo -e "${YELLOW}[!] 建议安装yq或python3以支持完整YAML解析${NC}"
        echo -e "${YELLOW}[!] 安装命令:${NC}"
        echo -e "    Ubuntu/Debian: sudo apt-get install yq python3"
        echo -e "    CentOS/RHEL: sudo yum install yq python3"
        echo -e "    macOS: brew install yq python"
    fi
    
    return 0
}

# 主函数
main() {
    local action="${1:-load}"
    
    case "$action" in
        load)
            load_config
            if [ $? -eq 0 ]; then
                show_config
            fi
            ;;
        show)
            load_config
            show_config
            ;;
        generate)
            generate_config_template "$2"
            ;;
        validate)
            load_config
            ;;
        dependencies)
            check_dependencies
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}[✗] 未知操作: $action${NC}"
            show_help
            return 1
            ;;
    esac
}

# 显示帮助
show_help() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${MAGENTA}📖 Nmap扫描器配置加载器${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e ""
    echo -e "${YELLOW}使用方法:${NC}"
    echo -e "  $0 [命令]"
    echo -e ""
    echo -e "${YELLOW}命令:${NC}"
    echo -e "  load      - 加载并显示配置 (默认)"
    echo -e "  show      - 显示当前配置"
    echo -e "  generate  - 生成用户配置模板"
    echo -e "  validate  - 验证配置"
    echo -e "  dependencies - 检查依赖"
    echo -e "  help      - 显示此帮助"
    echo -e ""
    echo -e "${YELLOW}环境变量:${NC}"
    echo -e "  NMAP_SCAN_CONFIG   - 自定义配置文件路径"
    echo -e "  NMAP_OUTPUT_DIR    - 覆盖输出目录"
    echo -e "  NMAP_TIMEOUT       - 覆盖超时设置"
    echo -e "  NMAP_SCAN_TYPE     - 覆盖扫描类型"
    echo -e ""
    echo -e "${YELLOW}配置文件位置:${NC}"
    echo -e "  1. 环境变量指定: \$NMAP_SCAN_CONFIG"
    echo -e "  2. 用户配置: ~/.config/openclaw/nmap-scanner.yaml"
    echo -e "  3. 默认配置: configs/default.yaml"
    echo -e "${CYAN}========================================${NC}"
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

# 导出配置变量供其他脚本使用
export CONFIG_SCAN_TYPE CONFIG_TIMING CONFIG_TIMEOUT CONFIG_OUTPUT_DIR
export CONFIG_GENERATE_HTML CONFIG_LEGAL_CHECK CONFIG_MAX_RATE

echo -e "${GREEN}[✓] 配置加载器就绪${NC}"