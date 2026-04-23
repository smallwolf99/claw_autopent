#!/bin/bash

# ==========================================
# 阶段 3 优化代码 - 一键部署脚本
# ==========================================
# 用途：将优化后的代码部署到 OpenClaw 服务器
# 使用：./deploy_to_server.sh [服务器 IP]
# ==========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SERVER_USER="${SERVER_USER:-ubuntu}"
SERVER_IP="${1:-}"
PROJECT_DIR="~/.openclaw/workspace/skills/intelligent-test-orchestrator"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 打印函数
print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查参数
if [ -z "$SERVER_IP" ]; then
    print_header "部署到服务器"
    echo ""
    echo "用法：$0 <服务器 IP>"
    echo ""
    echo "示例："
    echo "  $0 192.168.1.100"
    echo "  $0 demo.testfire.net"
    echo ""
    echo "或者设置环境变量："
    echo "  export SERVER_IP=192.168.1.100"
    echo "  $0"
    echo ""
    exit 1
fi

print_header "开始部署到 $SERVER_USER@$SERVER_IP"

# 步骤 1: 检查本地文件
print_header "步骤 1: 检查本地文件"
REQUIRED_FILES=(
    "utils/cache.py"
    "utils/performance_monitor.py"
    "utils/health_checker.py"
    "utils/memory_optimizer.py"
    "utils/logger.py"
    "adapters/base_tool_adapter.py"
    "core/config_optimized.py"
    "core/config_validation.py"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$LOCAL_DIR/$file" ]; then
        print_success "$file 存在"
    else
        print_error "$file 不存在"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    print_error "缺少 ${#MISSING_FILES[@]} 个文件，请检查本地目录"
    exit 1
fi

print_success "所有必需文件检查通过"

# 步骤 2: 测试 SSH 连接
print_header "步骤 2: 测试 SSH 连接"
if ssh -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "echo '连接成功'" > /dev/null 2>&1; then
    print_success "SSH 连接正常"
else
    print_error "无法连接到服务器 $SERVER_USER@$SERVER_IP"
    print_warning "请检查："
    print_warning "  1. 服务器 IP 是否正确"
    print_warning "  2. SSH 密钥是否配置"
    print_warning "  3. 服务器是否在线"
    exit 1
fi

# 步骤 3: 检查服务器依赖
print_header "步骤 3: 检查服务器依赖"
ssh "$SERVER_USER@$SERVER_IP" << 'EOF'
    # 检查 Python 版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "✅ Python: $PYTHON_VERSION"
    else
        echo "❌ Python3 未安装"
        exit 1
    fi
    
    # 检查 pip
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3 已安装"
    else
        echo "❌ pip3 未安装"
        exit 1
    fi
EOF

# 步骤 4: 创建备份
print_header "步骤 4: 创建服务器备份"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $PROJECT_DIR
    
    # 创建备份目录
    mkdir -p $BACKUP_DIR/utils $BACKUP_DIR/adapters $BACKUP_DIR/core
    
    # 备份现有文件
    cp utils/*.py $BACKUP_DIR/utils/ 2>/dev/null || echo "ℹ️  utils 目录为空或不存在"
    cp adapters/*.py $BACKUP_DIR/adapters/ 2>/dev/null || echo "ℹ️  adapters 目录为空或不存在"
    cp core/*.py $BACKUP_DIR/core/ 2>/dev/null || echo "ℹ️  core 目录为空或不存在"
    
    echo "✅ 备份已创建：$BACKUP_DIR"
EOF

# 步骤 5: 上传文件
print_header "步骤 5: 上传优化文件"

# 创建远程目录
ssh "$SERVER_USER@$SERVER_IP" "mkdir -p $PROJECT_DIR/utils $PROJECT_DIR/adapters $PROJECT_DIR/core"

# 上传文件
FILES_TO_UPLOAD=(
    "utils/cache.py"
    "utils/performance_monitor.py"
    "utils/health_checker.py"
    "utils/memory_optimizer.py"
    "utils/logger.py"
    "adapters/base_tool_adapter.py"
    "core/config_optimized.py"
    "core/config_validation.py"
)

for file in "${FILES_TO_UPLOAD[@]}"; do
    echo -n "上传 $file ... "
    if scp "$LOCAL_DIR/$file" "$SERVER_USER@$SERVER_IP:$PROJECT_DIR/$file"; then
        print_success "已上传"
    else
        print_error "上传失败"
        exit 1
    fi
done

print_success "所有文件上传完成"

# 步骤 6: 验证文件
print_header "步骤 6: 验证文件完整性"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $PROJECT_DIR
    
    echo "检查文件:"
    ls -lh utils/cache.py
    ls -lh utils/performance_monitor.py
    ls -lh utils/health_checker.py
    ls -lh utils/memory_optimizer.py
    ls -lh adapters/base_tool_adapter.py
    ls -lh core/config_optimized.py
    ls -lh core/config_validation.py
    
    echo ""
    echo "统计行数:"
    wc -l utils/*.py adapters/*.py core/*.py | tail -1
EOF

# 步骤 7: 测试导入
print_header "步骤 7: 测试 Python 导入"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $PROJECT_DIR
    
    # 设置 Python 路径
    export PYTHONPATH="$PROJECT_DIR:\$PYTHONPATH"
    
    echo "测试导入..."
    python3 -c "from utils.cache import MemoryCache; print('✅ 缓存系统导入成功')"
    python3 -c "from utils.performance_monitor import PerformanceMonitor; print('✅ 性能监控导入成功')"
    python3 -c "from utils.health_checker import HealthChecker; print('✅ 健康检查导入成功')"
    python3 -c "from utils.memory_optimizer import VulnerabilityStream; print('✅ 内存优化导入成功')"
    python3 -c "from adapters.base_tool_adapter import BaseToolAdapter; print('✅ 基类适配器导入成功')"
    
    echo ""
    echo "所有导入测试通过！"
EOF

# 步骤 8: 运行功能测试
print_header "步骤 8: 运行功能测试"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $PROJECT_DIR
    export PYTHONPATH="$PROJECT_DIR:\$PYTHONPATH"
    
    echo "运行缓存测试..."
    python3 -c "
from utils.cache import MemoryCache
cache = MemoryCache()
cache.set('test', 'value')
assert cache.get('test') == 'value'
print('✅ 缓存功能测试通过')
"
    
    echo "运行性能监控测试..."
    python3 -c "
from utils.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
report = monitor.get_report()
assert 'metrics' in report
print('✅ 性能监控测试通过')
"
    
    echo ""
    echo "所有功能测试通过！"
EOF

# 步骤 9: 清理 Python 缓存
print_header "步骤 9: 清理 Python 缓存"
ssh "$SERVER_USER@$SERVER_IP" << EOF
    cd $PROJECT_DIR
    
    echo "清理 .pyc 文件..."
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Python 缓存已清理"
EOF

# 步骤 10: 提供重启说明
print_header "部署完成！"
echo ""
print_success "所有文件已成功部署到 $SERVER_USER@$SERVER_IP"
echo ""
echo "📝 下一步操作："
echo ""
echo "1. 重启 OpenClaw（如果需要）:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   # 找到 OpenClaw 进程并重启"
echo ""
echo "2. 验证智能编排功能:"
echo "   在 OpenClaw 中调用智能测试编排技能"
echo ""
echo "3. 检查日志:"
echo "   tail -f ~/.openclaw/logs/openclaw.log"
echo ""
echo "4. 运行完整测试（可选）:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $PROJECT_DIR"
echo "   python3 test/test_phase3_optimization.py"
echo ""
echo "📊 备份位置:"
echo "   $PROJECT_DIR/$BACKUP_DIR"
echo ""
echo "🔄 如需回滚:"
echo "   cp $BACKUP_DIR/utils/*.py utils/"
echo "   cp $BACKUP_DIR/adapters/*.py adapters/"
echo "   cp $BACKUP_DIR/core/*.py core/"
echo ""
print_success "部署成功！"
