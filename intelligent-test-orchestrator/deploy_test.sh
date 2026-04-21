#!/bin/bash
# Phase-0 测试脚本快速部署

echo "======================================"
echo "  Phase-0 测试脚本部署"
echo "======================================"
echo ""

# 配置
SERVER_USER="ubuntu"
SERVER_HOST="119.45.255.144"
SERVER_PATH="/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator"

echo "📦 准备上传文件..."
echo "  目标服务器：$SERVER_USER@$SERVER_HOST"
echo "  目标路径：$SERVER_PATH"
echo ""

# 上传测试脚本
echo "📤 上传 test_phase0_real_standalone.py..."
scp test/test_phase0_real_standalone.py $SERVER_USER@$SERVER_HOST:$SERVER_PATH/test/

if [ $? -eq 0 ]; then
    echo "✅ 上传成功！"
    echo ""
    echo "======================================"
    echo "  在服务器上运行测试"
    echo "======================================"
    echo ""
    echo "SSH 登录服务器:"
    echo "  ssh $SERVER_USER@$SERVER_HOST"
    echo ""
    echo "运行测试:"
    echo "  cd $SERVER_PATH"
    echo "  python3 test/test_phase0_real_standalone.py"
    echo ""
    echo "或者直接运行:"
    echo "  ssh $SERVER_USER@$SERVER_HOST 'cd $SERVER_PATH && python3 test/test_phase0_real_standalone.py'"
    echo ""
else
    echo "❌ 上传失败"
    echo ""
    echo "请检查:"
    echo "  1. SSH 密钥配置是否正确"
    echo "  2. 服务器是否可达"
    echo "  3. 目标路径是否存在"
    echo ""
fi
