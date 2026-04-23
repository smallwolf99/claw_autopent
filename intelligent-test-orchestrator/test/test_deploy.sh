#!/bin/bash

# ==========================================
# 服务器部署验证测试脚本
# ==========================================

set -e

echo ""
echo "╔==========================================================╗"
echo "║              服务器部署验证测试                  ║"
echo "╚==========================================================╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0
TOTAL=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL=$((TOTAL + 1))
    echo -n "测试 $TOTAL: $test_name ... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 设置路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

echo "项目目录：$PROJECT_DIR"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

# ==========================================
# 文件检查
# ==========================================
echo "============================================================"
echo "阶段 1: 文件检查"
echo "============================================================"
echo ""

FILES=(
    "utils/cache.py"
    "utils/performance_monitor.py"
    "utils/health_checker.py"
    "utils/memory_optimizer.py"
    "utils/logger.py"
    "adapters/base_tool_adapter.py"
    "core/config_optimized.py"
    "core/config_validation.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        FAILED=$((FAILED + 1))
    fi
done

echo ""

# ==========================================
# 依赖检查
# ==========================================
echo "============================================================"
echo "阶段 2: 依赖检查"
echo "============================================================"
echo ""

run_test "Python3 已安装" "command -v python3"
run_test "pip3 已安装" "command -v pip3"
run_test "psutil 已安装" "python3 -c 'import psutil'"
run_test "pydantic 已安装" "python3 -c 'import pydantic'"

echo ""

# ==========================================
# 导入测试
# ==========================================
echo "============================================================"
echo "阶段 3: 导入测试"
echo "============================================================"
echo ""

run_test "导入缓存模块" "python3 -c 'from utils.cache import MemoryCache'"
run_test "导入性能监控" "python3 -c 'from utils.performance_monitor import PerformanceMonitor'"
run_test "导入健康检查" "python3 -c 'from utils.health_checker import HealthChecker'"
run_test "导入内存优化" "python3 -c 'from utils.memory_optimizer import VulnerabilityStream'"
run_test "导入基类适配器" "python3 -c 'from adapters.base_tool_adapter import BaseToolAdapter'"

echo ""

# ==========================================
# 功能测试
# ==========================================
echo "============================================================"
echo "阶段 4: 功能测试"
echo "============================================================"
echo ""

# 缓存功能测试
run_test "缓存基本操作" "python3 -c \"
from utils.cache import MemoryCache
cache = MemoryCache()
cache.set('test', 'value')
assert cache.get('test') == 'value'
\""

# 缓存装饰器测试
run_test "缓存装饰器" "python3 -c \"
from utils.cache import cached, MemoryCache
cache = MemoryCache()
@cached(cache=cache, ttl=3600)
def test_func(x): return x * 2
result = test_func(5)
assert result == 10
\""

# 内存优化测试
run_test "流式处理" "python3 -c \"
from utils.memory_optimizer import VulnerabilityStream
data = [{'id': i} for i in range(100)]
stream = VulnerabilityStream(data)
result = stream.limit(10).to_list()
assert len(result) == 10
\""

echo ""

# ==========================================
# 运行单元测试
# ==========================================
echo "============================================================"
echo "阶段 5: 单元测试"
echo "============================================================"
echo ""

if [ -f "$PROJECT_DIR/test/test_phase3_optimization.py" ]; then
    echo "运行阶段 3 单元测试..."
    cd "$PROJECT_DIR"
    python3 test/test_phase3_optimization.py && {
        echo -e "${GREEN}✅ 单元测试通过${NC}"
        PASSED=$((PASSED + 1))
    } || {
        echo -e "${RED}❌ 单元测试失败${NC}"
        FAILED=$((FAILED + 1))
    }
    TOTAL=$((TOTAL + 1))
else
    echo -e "${YELLOW}⚠️  单元测试文件不存在，跳过${NC}"
fi

echo ""

# ==========================================
# 总结
# ==========================================
echo "============================================================"
echo "测试总结"
echo "============================================================"
echo ""
echo "总测试数：$TOTAL"
echo -e "${GREEN}通过：$PASSED${NC}"
echo -e "${RED}失败：$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔==========================================================╗${NC}"
    echo -e "${GREEN}║              ✅ 所有测试通过！                 ║${NC}"
    echo -e "${GREEN}╚==========================================================╝${NC}"
    echo ""
    echo "🎉 部署成功！优化代码已正常工作。"
    echo ""
    echo "下一步:"
    echo "  1. 测试 OpenClaw 智能编排功能"
    echo "  2. 运行性能基准测试：python3 test/test_benchmark.py"
    echo "  3. 在真实环境中使用"
    echo ""
    exit 0
else
    echo -e "${RED}╔==========================================================╗${NC}"
    echo -e "${RED}║              ❌ 部分测试失败                   ║${NC}"
    echo -e "${RED}╚==========================================================╝${NC}"
    echo ""
    echo "请检查上方的错误信息。"
    echo ""
    echo "常见问题:"
    echo "  1. 依赖缺失：pip3 install psutil pydantic"
    echo "  2. 路径问题：export PYTHONPATH=\"\$PWD:\$PYTHONPATH\""
    echo "  3. 权限问题：chmod 644 utils/*.py"
    echo ""
    exit 1
fi
