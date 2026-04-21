#!/bin/bash
# OpenClaw 端口检查和配置脚本

set -e

echo "=========================================="
echo "  OpenClaw 端口检查和配置"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查端口占用
echo -e "${BLUE}📡 检查端口占用情况...${NC}"
echo ""

PORTS=(9000 18789 8080 5000)
for port in "${PORTS[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✅ 端口 $port 正在监听${NC}"
        netstat -tlnp 2>/dev/null | grep ":$port " | head -1
    else
        echo -e "${YELLOW}⚠️  端口 $port 未使用${NC}"
    fi
done
echo ""

# 检查 OpenClaw 进程
echo -e "${BLUE}🔍 检查 OpenClaw 进程...${NC}"
echo ""

if command -v pm2 &> /dev/null; then
    echo "PM2 管理的进程:"
    pm2 list | grep -i openclaw || echo -e "${YELLOW}  未找到 OpenClaw 进程${NC}"
else
    echo -e "${YELLOW}  PM2 未安装${NC}"
fi
echo ""

# 测试端口连通性
echo -e "${BLUE}🌐 测试端口连通性...${NC}"
echo ""

for port in "${PORTS[@]}"; do
    if curl -s --connect-timeout 2 http://localhost:$port/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 端口 $port 可访问（OpenClaw 运行中）${NC}"
        
        # 获取版本信息
        response=$(curl -s http://localhost:$port/health)
        echo "  健康检查响应：$response"
        
        # 设置环境变量
        echo ""
        echo -e "${GREEN}📌 建议设置环境变量:${NC}"
        echo "  export OPENCLAW_PORT=$port"
        
        OPENCLAW_PORT=$port
        break
    else
        echo -e "${YELLOW}⚠️  端口 $port 无法访问${NC}"
    fi
done
echo ""

# 检查环境变量
echo -e "${BLUE}📋 检查当前环境变量...${NC}"
echo ""

if [ -n "$OPENCLAW_PORT" ]; then
    echo -e "${GREEN}✅ OPENCLAW_PORT 已设置：$OPENCLAW_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  OPENCLAW_PORT 未设置${NC}"
fi
echo ""

# 检查配置文件
echo -e "${BLUE}📄 检查 OpenClaw 配置文件...${NC}"
echo ""

CONFIG_FILES=(
    "/home/ubuntu/.openclaw/config.json"
    "/home/ubuntu/.openclaw/config.yaml"
    "/home/ubuntu/.openclaw/.env"
)

for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        echo -e "${GREEN}找到配置文件：$config${NC}"
        echo "端口配置:"
        grep -i "port" "$config" 2>/dev/null || echo "  未找到端口配置"
        echo ""
    fi
done
echo ""

# 提供配置建议
echo "=========================================="
echo "  配置建议"
echo "=========================================="
echo ""

if [ -n "$OPENCLAW_PORT" ]; then
    echo -e "${GREEN}✅ OpenClaw 运行在端口 $OPENCLAW_PORT${NC}"
    echo ""
    echo "临时配置（当前会话）:"
    echo -e "  ${BLUE}export OPENCLAW_PORT=$OPENCLAW_PORT${NC}"
    echo ""
    echo "永久配置（添加到 ~/.bashrc）:"
    echo -e "  ${BLUE}echo \"export OPENCLAW_PORT=$OPENCLAW_PORT\" >> ~/.bashrc${NC}"
    echo -e "  ${BLUE}source ~/.bashrc${NC}"
    echo ""
    
    # 询问是否自动配置
    read -p "是否现在设置环境变量？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        export OPENCLAW_PORT=$OPENCLAW_PORT
        echo -e "${GREEN}✅ 已设置 OPENCLAW_PORT=$OPENCLAW_PORT${NC}"
        echo -e "${YELLOW}⚠️  注意：此设置仅在当前会话有效${NC}"
        echo ""
        echo "如需永久设置，请执行:"
        echo -e "  ${BLUE}echo \"export OPENCLAW_PORT=$OPENCLAW_PORT\" >> ~/.bashrc${NC}"
        echo -e "  ${BLUE}source ~/.bashrc${NC}"
    fi
else
    echo -e "${RED}❌ 未找到运行中的 OpenClaw${NC}"
    echo ""
    echo "启动 OpenClaw:"
    echo -e "  ${BLUE}cd /home/ubuntu/.openclaw${NC}"
    echo -e "  ${BLUE}pm2 start openclaw${NC}"
    echo ""
fi
echo ""

echo "=========================================="
echo "  检查完成"
echo "=========================================="
