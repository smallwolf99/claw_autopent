#!/bin/bash
# 智能编排功能 - 服务器端手动测试脚本
# 用途：在 OpenClaw 服务器上直接测试智能编排功能

set -e

echo "=========================================="
echo "  智能编排功能 - 服务器端测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 测试目录
SKILL_DIR="/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator"
TEST_DIR="/tmp/intelligent-test-orchestrator-test"

echo -e "${YELLOW}📂 技能目录：$SKILL_DIR${NC}"
echo ""

# 步骤 1: 检查技能文件
echo -e "${YELLOW}📋 步骤 1/6: 检查技能文件完整性${NC}"
echo ""

if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}❌ 错误：技能目录不存在${NC}"
    echo "请先部署代码到服务器"
    exit 1
fi

cd "$SKILL_DIR"

# 检查关键文件
FILES=("manifest.json" "main.py" "SKILL.md" "adapters/phase2_adapter.py" "core/risk_profiler.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file 缺失"
        exit 1
    fi
done
echo ""

# 步骤 2: 检查工具集成
echo -e "${YELLOW}🔧 步骤 2/6: 检查工具集成情况${NC}"
echo ""

echo "检查 SQLMap 集成:"
if grep -q "sqlmap" adapters/phase2_adapter.py; then
    echo -e "${GREEN}  ✅ SQLMap 已集成${NC}"
    grep -n "sqlmap" adapters/phase2_adapter.py | head -3
else
    echo -e "${RED}  ❌ SQLMap 未集成${NC}"
fi
echo ""

echo "检查 ZAP 集成:"
if grep -q "zap" adapters/phase2_adapter.py; then
    echo -e "${GREEN}  ✅ ZAP 已集成${NC}"
    grep -n "zap" adapters/phase2_adapter.py | head -3
else
    echo -e "${RED}  ❌ ZAP 未集成${NC}"
fi
echo ""

# 步骤 3: 检查 Python 依赖
echo -e "${YELLOW}📦 步骤 3/6: 检查 Python 依赖${NC}"
echo ""

if [ -f "requirements.txt" ]; then
    echo "安装依赖..."
    pip3 install -q -r requirements.txt
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${RED}❌ requirements.txt 不存在${NC}"
    exit 1
fi
echo ""

# 步骤 4: 运行单元测试
echo -e "${YELLOW}🧪 步骤 4/6: 运行单元测试${NC}"
echo ""

echo "测试 1: SQLMap 集成测试..."
if [ -f "test_sqlmap_integration.py" ]; then
    python3 test_sqlmap_integration.py > /tmp/sqlmap_test.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ SQLMap 测试通过${NC}"
        grep "发现漏洞数" /tmp/sqlmap_test.log
    else
        echo -e "${RED}  ❌ SQLMap 测试失败${NC}"
        tail -20 /tmp/sqlmap_test.log
    fi
else
    echo -e "${YELLOW}  ⚠️  测试文件不存在，跳过${NC}"
fi
echo ""

echo "测试 2: ZAP 集成测试..."
if [ -f "test_zap_integration.py" ]; then
    python3 test_zap_integration.py > /tmp/zap_test.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ ZAP 测试通过${NC}"
        grep "发现漏洞数" /tmp/zap_test.log
    else
        echo -e "${RED}  ❌ ZAP 测试失败${NC}"
        tail -20 /tmp/zap_test.log
    fi
else
    echo -e "${YELLOW}  ⚠️  测试文件不存在，跳过${NC}"
fi
echo ""

# 步骤 5: 运行完整流程测试
echo -e "${YELLOW}🎯 步骤 5/6: 运行完整流程测试${NC}"
echo ""

if [ -f "test_simple.py" ]; then
    echo "使用模拟目标测试完整流程..."
    
    # 创建测试输入
    cat > /tmp/test_input.json << 'EOF'
{
    "target": "http://demo-test.example.com",
    "test_mode": "full",
    "time_limit": 120,
    "report_format": "html"
}
EOF
    
    # 运行测试
    python3 test_simple.py > /tmp/full_test.log 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ 完整流程测试通过${NC}"
        echo ""
        echo "📊 测试结果摘要:"
        grep "vulnerabilities_found" /tmp/full_test.log | head -1
        grep "verified_vulns" /tmp/full_test.log | head -1
        grep "risk_score" /tmp/full_test.log | head -1
        echo ""
        echo "📁 报告生成位置:"
        grep "report_path" /tmp/full_test.log | head -1
    else
        echo -e "${RED}❌ 完整流程测试失败${NC}"
        echo ""
        echo "错误日志:"
        tail -50 /tmp/full_test.log
    fi
else
    echo -e "${YELLOW}⚠️  测试文件不存在，跳过${NC}"
fi
echo ""

# 步骤 6: 测试 OpenClaw 调用
echo -e "${YELLOW}🤖 步骤 6/6: 测试 OpenClaw 调用${NC}"
echo ""

echo "检查 OpenClaw 状态..."

# 检查是否在 9000 端口运行
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OpenClaw 正在运行（端口 9000）${NC}"
    OPENCLAW_PORT=9000
elif curl -s http://localhost:18789/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OpenClaw 正在运行（端口 18789）${NC}"
    OPENCLAW_PORT=18789
elif pm2 list | grep -q openclaw; then
    echo -e "${GREEN}✅ OpenClaw 正在运行（PM2 管理）${NC}"
    pm2 list | grep openclaw
    OPENCLAW_PORT="unknown"
else
    echo -e "${YELLOW}⚠️  OpenClaw 未运行${NC}"
    echo "是否需要启动 OpenClaw? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        cd /home/ubuntu/.openclaw
        pm2 start openclaw
        echo -e "${GREEN}✅ OpenClaw 已启动${NC}"
        OPENCLAW_PORT=9000
    else
        OPENCLAW_PORT="unknown"
    fi
fi
echo ""

# 设置环境变量（如果端口是 9000）
if [ "$OPENCLAW_PORT" = "9000" ]; then
    export OPENCLAW_PORT=9000
    echo "📌 OpenClaw 端口：$OPENCLAW_PORT"
    echo ""
fi

echo "查看最近的 OpenClaw 日志:"
tail -20 /home/ubuntu/.openclaw/logs/openclaw.log | grep -i "intelligent-test" || echo "暂无相关日志"
echo ""

# 测试总结
echo "=========================================="
echo "  测试总结"
echo "=========================================="
echo ""

# 统计通过的测试
PASSED=0
TOTAL=0

if grep -q "sqlmap" adapters/phase2_adapter.py; then
    ((PASSED++))
fi
((TOTAL++))

if grep -q "zap" adapters/phase2_adapter.py; then
    ((PASSED++))
fi
((TOTAL++))

if [ -f "/tmp/sqlmap_test.log" ] && grep -q "✅" /tmp/sqlmap_test.log 2>/dev/null; then
    ((PASSED++))
fi
((TOTAL++))

if [ -f "/tmp/zap_test.log" ] && grep -q "✅" /tmp/zap_test.log 2>/dev/null; then
    ((PASSED++))
fi
((TOTAL++))

if [ -f "/tmp/full_test.log" ] && [ $EXIT_CODE -eq 0 ]; then
    ((PASSED++))
fi
((TOTAL++))

echo "通过测试：$PASSED/$TOTAL"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 所有测试通过！智能编排功能正常！${NC}"
else
    echo -e "${YELLOW}⚠️  部分测试未通过，请检查上方的错误信息${NC}"
fi
echo ""

echo "下一步操作:"
echo "1. 在飞书中测试：帮我测试 http://demo.test.com"
echo "2. 查看实时日志：tail -f /home/ubuntu/.openclaw/logs/openclaw.log"
echo "3. 重启 OpenClaw: pm2 restart openclaw"
echo ""

# 清理临时文件
echo "清理临时文件..."
rm -f /tmp/sqlmap_test.log /tmp/zap_test.log /tmp/full_test.log /tmp/test_input.json
echo -e "${GREEN}✅ 清理完成${NC}"
echo ""

echo "=========================================="
echo "  测试完成"
echo "=========================================="
