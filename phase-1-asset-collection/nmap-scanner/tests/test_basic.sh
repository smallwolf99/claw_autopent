#!/bin/bash
# test_basic.sh
# OpenClaw Nmap Scanner 基础测试

# ========================================
# 测试脚本 - 验证技能基本功能
# ========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$TEST_DIR")"
SCRIPTS_DIR="${SKILL_ROOT}/scripts"

# 测试结果
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# ========================================
# 测试工具函数
# ========================================
log_pass() {
    echo -e "${GREEN}[✓] $1${NC}"
    PASS_COUNT=$((PASS_COUNT + 1))
}

log_fail() {
    echo -e "${RED}[✗] $1${NC}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

log_skip() {
    echo -e "${YELLOW}[⏭] $1${NC}"
    SKIP_COUNT=$((SKIP_COUNT + 1))
}

log_info() {
    echo -e "${BLUE}[.] $1${NC}"
}

# ========================================
# 测试用例
# ========================================

# 测试1: 检查技能目录结构
test_directory_structure() {
    log_info "测试1: 检查技能目录结构"
    
    local required_dirs=(
        "configs"
        "scripts"
        "tests"
        "docs"
        "examples"
    )
    
    local required_files=(
        "manifest.json"
        "SKILL.md"
        "nmap-scanner.sh"
        "configs/default.yaml"
        "scripts/config_loader.sh"
    )
    
    # 检查目录
    for dir in "${required_dirs[@]}"; do
        if [ -d "${SKILL_ROOT}/${dir}" ]; then
            log_pass "目录存在: $dir"
        else
            log_fail "目录缺失: $dir"
        fi
    done
    
    # 检查文件
    for file in "${required_files[@]}"; do
        if [ -f "${SKILL_ROOT}/${file}" ]; then
            log_pass "文件存在: $file"
        else
            log_fail "文件缺失: $file"
        fi
    done
}

# 测试2: 检查脚本执行权限
test_script_permissions() {
    log_info "测试2: 检查脚本执行权限"
    
    local scripts=(
        "nmap-scanner.sh"
        "scripts/basic_network_scan.sh"
        "scripts/config_loader.sh"
        "scripts/install.sh"
    )
    
    for script in "${scripts[@]}"; do
        script_path="${SKILL_ROOT}/${script}"
        
        if [ -f "$script_path" ]; then
            if [ -x "$script_path" ]; then
                log_pass "脚本可执行: $script"
            else
                log_fail "脚本不可执行: $script"
            fi
        else
            log_skip "脚本不存在: $script"
        fi
    done
}

# 测试3: 检查依赖工具
test_dependencies() {
    log_info "测试3: 检查依赖工具"
    
    # 必要依赖
    if command -v nmap &>/dev/null; then
        NMAP_VERSION=$(nmap --version 2>/dev/null | head -1 | awk '{print $3}')
        log_pass "nmap已安装 (版本: $NMAP_VERSION)"
    else
        log_fail "nmap未安装"
    fi
    
    # 推荐依赖
    if command -v jq &>/dev/null; then
        JQ_VERSION=$(jq --version 2>/dev/null | cut -d'-' -f2)
        log_pass "jq已安装 (版本: $JQ_VERSION)"
    else
        log_skip "jq未安装 (推荐但非必需)"
    fi
    
    # 可选依赖
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        log_pass "python3已安装 (版本: $PYTHON_VERSION)"
    else
        log_skip "python3未安装 (可选)"
    fi
}

# 测试4: 检查配置文件
test_config_files() {
    log_info "测试4: 检查配置文件"
    
    local config_file="${SKILL_ROOT}/configs/default.yaml"
    
    if [ -f "$config_file" ]; then
        # 检查基本配置项
        if grep -q "scan:" "$config_file" && grep -q "output:" "$config_file"; then
            log_pass "配置文件格式正确"
            
            # 检查具体配置值
            if grep -q "default_type:.*fast" "$config_file"; then
                log_pass "默认扫描类型配置正确"
            else
                log_fail "默认扫描类型配置不正确"
            fi
        else
            log_fail "配置文件缺少必要部分"
        fi
    else
        log_fail "配置文件不存在: $config_file"
    fi
}

# 测试5: 检查技能元数据
test_manifest() {
    log_info "测试5: 检查技能元数据"
    
    local manifest_file="${SKILL_ROOT}/manifest.json"
    
    if [ -f "$manifest_file" ]; then
        # 检查JSON格式
        if command -v jq &>/dev/null; then
            if jq empty "$manifest_file" >/dev/null 2>&1; then
                log_pass "manifest.json格式正确"
                
                # 检查必要字段
                local required_fields=("name" "version" "description" "author")
                for field in "${required_fields[@]}"; do
                    if jq -e ".${field}" "$manifest_file" >/dev/null 2>&1; then
                        log_pass "字段存在: $field"
                    else
                        log_fail "字段缺失: $field"
                    fi
                done
                
                # 显示技能信息
                log_info "技能信息:"
                echo -e "  名称: $(jq -r '.name' "$manifest_file")"
                echo -e "  版本: $(jq -r '.version' "$manifest_file")"
                echo -e "  描述: $(jq -r '.description' "$manifest_file")"
                
            else
                log_fail "manifest.json格式错误"
            fi
        else
            log_skip "跳过JSON格式检查 (需要jq工具)"
            
            # 简单文本检查
            if grep -q '"name"' "$manifest_file" && grep -q '"version"' "$manifest_file"; then
                log_pass "manifest.json包含必要字段"
            else
                log_fail "manifest.json缺少必要字段"
            fi
        fi
    else
        log_fail "manifest.json不存在"
    fi
}

# 测试6: 检查帮助系统
test_help_system() {
    log_info "测试6: 检查帮助系统"
    
    # 检查主帮助
    if [ -x "${SKILL_ROOT}/nmap-scanner.sh" ]; then
        if "${SKILL_ROOT}/nmap-scanner.sh" help 2>&1 | grep -q "使用方法:"; then
            log_pass "主帮助系统正常"
        else
            log_fail "主帮助系统异常"
        fi
        
        # 检查扫描帮助
        if "${SKILL_ROOT}/nmap-scanner.sh" scan --help 2>&1 | grep -q "目标"; then
            log_pass "扫描帮助系统正常"
        else
            log_skip "扫描帮助系统异常"
        fi
    else
        log_fail "主脚本不可执行"
    fi
}

# 测试7: 功能测试 - 配置加载
test_config_loader() {
    log_info "测试7: 测试配置加载功能"
    
    if [ -f "${SCRIPTS_DIR}/config_loader.sh" ]; then
        # 测试配置加载
        if source "${SCRIPTS_DIR}/config_loader.sh" && load_config; then
            log_pass "配置加载功能正常"
            
            # 检查配置变量
            if [ -n "${CONFIG_SCAN_TYPE:-}" ]; then
                log_pass "配置变量已设置"
            else
                log_fail "配置变量未设置"
            fi
        else
            log_fail "配置加载功能异常"
        fi
    else
        log_fail "配置加载脚本不存在"
    fi
}

# 测试8: 功能测试 - 参数解析
test_argument_parsing() {
    log_info "测试8: 测试参数解析功能"
    
    if [ -f "${SCRIPTS_DIR}/basic_network_scan.sh" ]; then
        # 测试帮助参数
        if "${SCRIPTS_DIR}/basic_network_scan.sh" --help 2>&1 | grep -q "使用方法:"; then
            log_pass "参数解析帮助正常"
        else
            log_fail "参数解析帮助异常"
        fi
    else
        log_fail "基础扫描脚本不存在"
    fi
}

# 测试9: 集成测试 - 模拟扫描
test_simulation() {
    log_info "测试9: 模拟扫描测试"
    
    # 创建测试目录
    TEST_OUTPUT_DIR="/tmp/nmap-test-$$"
    mkdir -p "$TEST_OUTPUT_DIR"
    
    # 设置环境变量
    export NMAP_OUTPUT_DIR="$TEST_OUTPUT_DIR"
    export NMAP_SCAN_TYPE="fast"
    
    # 运行配置加载测试
    if source "${SCRIPTS_DIR}/config_loader.sh" && load_config; then
        if [ "$CONFIG_OUTPUT_DIR" = "$TEST_OUTPUT_DIR" ]; then
            log_pass "环境变量覆盖配置正常"
        else
            log_fail "环境变量覆盖配置异常"
        fi
    else
        log_fail "环境变量配置测试失败"
    fi
    
    # 清理测试目录
    rm -rf "$TEST_OUTPUT_DIR"
}

# ========================================
# 运行所有测试
# ========================================
run_all_tests() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🔬 OpenClaw Nmap Scanner 测试套件${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "测试时间: $(date)"
    echo -e "技能路径: $SKILL_ROOT"
    echo -e "${BLUE}========================================${NC}"
    
    # 运行测试用例
    test_directory_structure
    echo ""
    
    test_script_permissions
    echo ""
    
    test_dependencies
    echo ""
    
    test_config_files
    echo ""
    
    test_manifest
    echo ""
    
    test_help_system
    echo ""
    
    test_config_loader
    echo ""
    
    test_argument_parsing
    echo ""
    
    test_simulation
    echo ""
    
    # 显示测试结果
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}📊 测试结果汇总${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}通过:${NC} $PASS_COUNT"
    echo -e "${RED}失败:${NC} $FAIL_COUNT"
    echo -e "${YELLOW}跳过:${NC} $SKIP_COUNT"
    echo -e "${BLUE}总计:${NC} $((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))"
    echo -e "${BLUE}========================================${NC}"
    
    # 返回测试结果
    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${GREEN}[✅] 所有测试通过${NC}"
        return 0
    else
        echo -e "${RED}[❌] 有测试失败${NC}"
        return 1
    fi
}

# ========================================
# 主函数
# ========================================
main() {
    local test_case="${1:-all}"
    
    case "$test_case" in
        all)
            run_all_tests
            ;;
        structure)
            test_directory_structure
            ;;
        permissions)
            test_script_permissions
            ;;
        dependencies)
            test_dependencies
            ;;
        config)
            test_config_files
            ;;
        manifest)
            test_manifest
            ;;
        help)
            test_help_system
            ;;
        config-loader)
            test_config_loader
            ;;
        arguments)
            test_argument_parsing
            ;;
        simulation)
            test_simulation
            ;;
        help|--help|-h)
            echo -e "${BLUE}========================================${NC}"
            echo -e "${GREEN}测试套件帮助${NC}"
            echo -e "${BLUE}========================================${NC}"
            echo -e "使用方法: $0 [测试用例]"
            echo -e ""
            echo -e "测试用例:"
            echo -e "  all            - 运行所有测试 (默认)"
            echo -e "  structure      - 目录结构测试"
            echo -e "  permissions    - 脚本权限测试"
            echo -e "  dependencies   - 依赖工具测试"
            echo -e "  config         - 配置文件测试"
            echo -e "  manifest       - 技能元数据测试"
            echo -e "  help           - 帮助系统测试"
            echo -e "  config-loader  - 配置加载测试"
            echo -e "  arguments      - 参数解析测试"
            echo -e "  simulation     - 模拟功能测试"
            echo -e ""
            echo -e "示例:"
            echo -e "  $0 all"
            echo -e "  $0 dependencies"
            echo -e "  $0 structure permissions"
            echo -e "${BLUE}========================================${NC}"
            ;;
        *)
            echo -e "${RED}[✗] 未知测试用例: $test_case${NC}"
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