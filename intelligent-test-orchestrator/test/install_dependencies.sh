#!/bin/bash

# ==========================================
# 安装阶段 3 优化依赖
# ==========================================

set -e

echo "=========================================="
echo "  安装阶段 3 优化依赖"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，请先安装 pip3"
    exit 1
fi

echo "✅ pip3 已安装"
echo ""

# 安装 psutil
echo "正在安装 psutil..."
pip3 install psutil --quiet
if [ $? -eq 0 ]; then
    echo "✅ psutil 安装成功"
else
    echo "❌ psutil 安装失败"
    exit 1
fi

# 安装 pydantic（可选，用于配置验证）
echo ""
echo "正在安装 pydantic..."
pip3 install pydantic --quiet
if [ $? -eq 0 ]; then
    echo "✅ pydantic 安装成功"
else
    echo "⚠️  pydantic 安装失败（可选依赖）"
fi

echo ""
echo "=========================================="
echo "  依赖安装完成！"
echo "=========================================="
echo ""
echo "已安装的包:"
pip3 list | grep -E "psutil|pydantic"
echo ""
echo "现在可以运行测试:"
echo "  python3 test/test_phase3_optimization.py"
echo ""
