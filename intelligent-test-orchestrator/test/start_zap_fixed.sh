#!/bin/bash
# 启动 ZAP 代理服务（修正版本）

echo "=========================================="
echo "  启动 ZAP 代理服务"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ZAP 路径
ZAP_PATH="/home/ubuntu/tools/zap/ZAP_2.17.0"
ZAP_JAR="$ZAP_PATH/zap-2.17.0.jar"
ZAP_PORT=8090

# 检查 Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java 未安装${NC}"
    echo "   请执行：sudo apt install -y openjdk-11-jdk"
    exit 1
fi

# 检查 ZAP JAR 文件
if [ ! -f "$ZAP_JAR" ]; then
    echo -e "${RED}❌ ZAP JAR 文件不存在：$ZAP_JAR${NC}"
    echo "   请确认 ZAP 安装路径"
    exit 1
fi

echo "[-] ZAP 路径：$ZAP_PATH"
echo "[-] ZAP JAR: $ZAP_JAR"
echo ""

# 检查是否已经在运行
echo "[-] 检查 ZAP 状态..."
if ps aux | grep -i "zap.*daemon\|zap.*jar" | grep -v grep > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ZAP 已经在运行${NC}"
    
    # 尝试找到端口
    PORT=$(netstat -tlnp 2>/dev/null | grep -i java | grep -oP ':\K\d{4}' | head -1)
    if [ -n "$PORT" ]; then
        echo "   端口：$PORT"
    fi
    
    exit 0
fi

# 检查端口是否被占用
if netstat -tlnp 2>/dev/null | grep -q ":$ZAP_PORT "; then
    echo -e "${YELLOW}⚠️  端口 $ZAP_PORT 已被占用，尝试使用端口 8091${NC}"
    ZAP_PORT=8091
fi

# 启动 ZAP
echo "[-] 启动 ZAP..."
echo "    端口：$ZAP_PORT"
echo "    日志：/tmp/zap.log"
echo ""

cd "$ZAP_PATH"
nohup java -Xmx512m -jar "$ZAP_JAR" -daemon -port $ZAP_PORT > /tmp/zap.log 2>&1 &
ZAP_PID=$!

echo "    PID: $ZAP_PID"
echo ""

# 等待启动
echo "[-] 等待 ZAP 启动..."
for i in {1..15}; do
    sleep 2
    
    # 检查进程是否存在
    if ! ps -p $ZAP_PID > /dev/null 2>&1; then
        echo -e "${RED}❌ ZAP 进程已退出${NC}"
        echo ""
        echo "错误日志:"
        tail -20 /tmp/zap.log
        exit 1
    fi
    
    # 检查端口是否监听
    if netstat -tlnp 2>/dev/null | grep -q ":$ZAP_PORT "; then
        echo -e "${GREEN}✅ ZAP 启动成功${NC}"
        echo ""
        echo "=========================================="
        echo "  ZAP 服务信息"
        echo "=========================================="
        echo "  端口：$ZAP_PORT"
        echo "  PID: $ZAP_PID"
        echo "  路径：$ZAP_PATH"
        echo ""
        echo "使用命令:"
        echo "  zap-cli -p $ZAP_PORT status"
        echo "  zap-cli -p $ZAP_PORT quick-scan http://demo.testfire.net"
        echo ""
        
        # 保存到环境变量文件
        echo "export ZAP_PORT=$ZAP_PORT" >> ~/.bashrc
        echo "export ZAP_PATH=$ZAP_PATH"
        
        return 0
    fi
    
    echo "    等待中... ($i/15)"
done

# 超时检查
echo ""
echo -e "${YELLOW}⚠️  ZAP 启动超时，检查日志...${NC}"
echo ""
tail -30 /tmp/zap.log

echo ""
echo "=========================================="
echo "  手动启动命令"
echo "=========================================="
echo "  cd $ZAP_PATH"
echo "  java -Xmx512m -jar zap-2.17.0.jar -daemon -port $ZAP_PORT"
echo ""

exit 1
