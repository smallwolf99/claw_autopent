#!/bin/bash
# 智能测试编排器 - 部署到 OpenClaw 服务器
# 服务器：119.45.255.144
# 用户：ubuntu
# 路径：/home/ubuntu/.openclaw/workspace/skills

set -e

echo "=========================================="
echo "  智能测试编排器 - 部署脚本"
echo "=========================================="
echo ""
echo "📦 目标服务器：119.45.255.144"
echo "👤 用户：ubuntu"
echo "📁 部署路径：/home/ubuntu/.openclaw/workspace/skills"
echo ""

# 步骤 1: 上传代码
echo "📤 步骤 1/4: 上传代码到服务器..."
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
echo "✅ 代码上传完成"
echo ""

# 步骤 2: SSH 连接并安装依赖
echo "🔧 步骤 2/4: 安装依赖..."
ssh ubuntu@119.45.255.144 << 'ENDSSH'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 安装 Python 依赖..."
pip3 install -r requirements.txt
echo "✅ 依赖安装完成"
ENDSSH
echo ""

# 步骤 3: 验证部署
echo "🔍 步骤 3/4: 验证部署..."
ssh ubuntu@119.45.255.144 << 'ENDSSH'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 检查文件完整性..."
ls -la manifest.json main.py SKILL.md
echo "  • 检查目录结构..."
ls -d core/ adapters/
echo "✅ 文件结构验证完成"
ENDSSH
echo ""

# 步骤 4: 测试运行
echo "🧪 步骤 4/4: 测试运行..."
ssh ubuntu@119.45.255.144 << 'ENDSSH'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 运行简单测试..."
python3 test_simple.py
echo "✅ 测试完成"
ENDSSH
echo ""

echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 在飞书中测试：帮我测试 http://demo.test.com"
echo "2. 查看 OpenClaw 日志：ssh ubuntu@119.45.255.144 'tail -f /home/ubuntu/.openclaw/logs/openclaw.log'"
echo ""
