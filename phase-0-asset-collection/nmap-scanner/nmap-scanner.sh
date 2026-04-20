#!/bin/bash
# nmap-scanner.sh
# OpenClaw Nmap Scanner - Main Entry Point

# ========================================
# OpenClaw技能包主入口
# ========================================

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"

# ========================================
# 颜色定义
# ========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ========================================
# 技能信息
# ========================================
SKILL_NAME="nmap-scanner"
SKILL_VERSION="1.0.0"
SKILL_DESCRIPTION="Professional network security scanner with JSON output"
SKILL_AUTHOR="高级安全渗透测试专家"

# ========================================
# 显示技能信息
# ========================================
show_skill_info() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${MAGENTA}🔍 OpenClaw Nmap Scanner${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e "${GREEN}技能名称:${NC} $SKILL_NAME"
    echo -e "${GREEN}版本:${NC} $SKILL_VERSION"
    echo -e "${GREEN}描述:${NC} $SKILL_DESCRIPTION"
    echo -e "${GREEN}作者:${NC} $SKILL_AUTHOR"
    echo -e "${CYAN}========================================${NC}"
}

# ========================================
# 显示帮助
# ========================================
show_help() {
    show_skill_info
    
    echo -e "${YELLOW}使用方法:${NC}"
    echo -e "  $0 [命令] [选项]"
    echo -e ""
    echo -e "${YELLOW}命令:${NC}"
    echo -e "  scan        - 执行网络扫描"
    echo -e "  batch       - 批量扫描"
    echo -e "  extract     - 提取扫描数据"
    echo -e "  config      - 配置管理"
    echo -e "  install     - 安装依赖"
    echo -e "  info        - 显示技能信息"
    echo -e "  help        - 显示此帮助"
    echo -e ""
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  $0 scan --target scanme.nmap.org"
    echo -e "  $0 batch --file targets.txt --type fast"
    echo -e "  $0 extract --file scan.json --format csv"
    echo -e "  $0 config --show"
    echo -e "  $0 install"
    echo -e ""
    echo -e "${YELLOW}详细命令帮助:${NC}"
    echo -e "  $0 scan --help"
    echo -e "  $0 batch --help"
    echo -e "  $0 extract --help"
    echo -e "${CYAN}========================================${NC}"
}

# ========================================
# 扫描命令
# ========================================
cmd_scan() {
    if [ ! -f "${SCRIPTS_DIR}/basic_network_scan.sh" ]; then
        echo -e "${RED}[✗] 错误: 扫描脚本不存在${NC}"
        return 1
    fi
    
    "${SCRIPTS_DIR}/basic_network_scan.sh" "$@"
}

# ========================================
# 批量扫描命令
# ========================================
cmd_batch() {
    if [ ! -f "${SCRIPTS_DIR}/batch_target_scan.sh" ]; then
        echo -e "${RED}[✗] 错误: 批量扫描脚本不存在${NC}"
        return 1
    fi
    
    "${SCRIPTS_DIR}/batch_target_scan.sh" "$@"
}

# ========================================
# 数据提取命令
# ========================================
cmd_extract() {
    if [ ! -f "${SCRIPTS_DIR}/extract_open_ports.sh" ]; then
        echo -e "${RED}[✗] 错误: 数据提取脚本不存在${NC}"
        return 1
    fi
    
    "${SCRIPTS_DIR}/extract_open_ports.sh" "$@"
}

# ========================================
# 配置管理命令
# ========================================
cmd_config() {
    if [ ! -f "${SCRIPTS_DIR}/config_loader.sh" ]; then
        echo -e "${RED}[✗] 错误: 配置加载脚本不存在${NC}"
        return 1
    fi
    
    "${SCRIPTS_DIR}/config_loader.sh" "$@"
}

# ========================================
# 安装命令
# ========================================
cmd_install() {
    if [ ! -f "${SCRIPTS_DIR}/install.sh" ]; then
        echo -e "${RED}[✗] 错误: 安装脚本不存在${NC}"
        return 1
    fi
    
    "${SCRIPTS_DIR}/install.sh" "$@"
}

# ========================================
# 技能信息命令
# ========================================
cmd_info() {
    show_skill_info
    
    # 显示技能元数据
    if [ -f "${SCRIPT_DIR}/manifest.json" ]; then
        echo -e "${BLUE}技能元数据:${NC}"
        echo -e "  文件: ${SCRIPT_DIR}/manifest.json"
        
        if command -v jq &>/dev/null; then
            echo -e "  平台: $(jq -r '.platforms | join(", ")' "${SCRIPT_DIR}/manifest.json")"
            echo -e "  依赖: $(jq -r '.dependencies.required | join(", ")' "${SCRIPT_DIR}/manifest.json")"
            echo -e "  分类: $(jq -r '.category' "${SCRIPT_DIR}/manifest.json")"
        fi
    fi
    
    # 显示可用脚本
    echo -e "${BLUE}可用脚本:${NC}"
    if [ -d "${SCRIPTS_DIR}" ]; then
        for script in "${SCRIPTS_DIR}"/*.sh; do
            if [ -f "$script" ] && [ -x "$script" ]; then
                script_name=$(basename "$script" .sh)
                echo -e "  ${GREEN}•${NC} $script_name"
            fi
        done
    fi
    
    # 显示配置文件
    echo -e "${BLUE}配置文件:${NC}"
    if [ -d "${SCRIPT_DIR}/configs" ]; then
        for config in "${SCRIPT_DIR}/configs"/*; do
            if [ -f "$config" ]; then
                config_name=$(basename "$config")
                echo -e "  ${CYAN}•${NC} $config_name"
            fi
        done
    fi
    
    echo -e "${CYAN}========================================${NC}"
}

# ========================================
# 检查技能完整性
# ========================================
check_skill_integrity() {
    echo -e "${BLUE}[.] 检查技能完整性...${NC}"
    
    local missing_files=()
    local required_files=(
        "manifest.json"
        "SKILL.md"
        "scripts/basic_network_scan.sh"
        "scripts/config_loader.sh"
        "configs/default.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "${SCRIPT_DIR}/${file}" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo -e "${RED}[✗] 技能文件不完整${NC}"
        echo -e "缺失文件:"
        for file in "${missing_files[@]}"; do
            echo -e "  ${RED}•${NC} $file"
        done
        return 1
    fi
    
    # 检查脚本执行权限
    local missing_executable=()
    for script in "${SCRIPTS_DIR}"/*.sh; do
        if [ -f "$script" ] && [ ! -x "$script" ]; then
            missing_executable+=("$(basename "$script")")
        fi
    done
    
    if [ ${#missing_executable[@]} -gt 0 ]; then
        echo -e "${YELLOW}[!] 缺少执行权限的脚本:${NC}"
        for script in "${missing_executable[@]}"; do
            echo -e "  ${YELLOW}•${NC} $script"
        done
        echo -e "${YELLOW}[💡] 运行: chmod +x ${SCRIPTS_DIR}/*.sh${NC}"
    fi
    
    echo -e "${GREEN}[✓] 技能完整性检查通过${NC}"
    return 0
}

# ========================================
# 主函数
# ========================================
main() {
    local command="${1:-help}"
    
    case "$command" in
        scan)
            shift
            cmd_scan "$@"
            ;;
        batch)
            shift
            cmd_batch "$@"
            ;;
        extract)
            shift
            cmd_extract "$@"
            ;;
        config)
            shift
            cmd_config "$@"
            ;;
        install)
            shift
            cmd_install "$@"
            ;;
        info)
            cmd_info
            ;;
        integrity)
            check_skill_integrity
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}[✗] 未知命令: $command${NC}"
            show_help
            return 1
            ;;
    esac
}

# ========================================
# 脚本入口
# ========================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 设置错误处理
    set -euo pipefail
    
    # 运行主函数
    main "$@"
fi