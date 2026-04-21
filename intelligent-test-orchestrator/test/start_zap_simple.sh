#!/bin/bash
# 一键启动 ZAP 并验证

echo "=========================================="
echo "  ZAP 服务启动脚本"
echo "=========================================="
echo ""

ZAP_PATH="/home/ubuntu/tools/zap/ZAP_2.17.0"
ZAP_JAR="$ZAP_PATH/zap-2.17.0.jar"
ZAP_PORT=8080

# 检查是否已经在运行
echo "[-] 检查 ZAP 是否运行..."
if ps aux | grep -i "zap.*jar.*daemon" | grep -v grep > /dev/null 2>&1; then
    echo "✅ ZAP 已经在运行"
    ps aux | grep -i "zap.*jar" | grep -v grep
    exit 0
fi

# 检查端口
if netstat -tlnp 2>/dev/null | grep -q ":$ZAP_PORT "; then
    echo "⚠️  端口 $ZAP_PORT 已被占用"
    netstat -tlnp | grep ":$ZAP_PORT "
    echo ""
    echo "杀掉占用进程..."
    sudo fuser -k $ZAP_PORT/tcp 2>/dev/null
    sleep 2
fi

# 检查文件
if [ ! -f "$ZAP_JAR" ]; then
    echo "❌ ZAP JAR 文件不存在：$ZAP_JAR"
    echo ""
    echo "查找系统中的 zap jar 文件:"
    find /home/ubuntu -name "zap*.jar" 2>/dev/null
    exit 1
fi

echo "✅ ZAP 文件存在：$ZAP_JAR"
echo ""

# 启动 ZAP
echo "[-] 启动 ZAP..."
echo "    命令：java -Xmx512m -jar $ZAP_JAR -daemon -port $ZAP_PORT"
echo ""

cd "$ZAP_PATH"

# 清除旧日志
> /tmp/zap_startup.log

# 启动
nohup java -Xmx512m -jar "$ZAP_JAR" -daemon -port $ZAP_PORT > /tmp/zap.log 2>&1 &
ZAP_PID=$!

echo "    PID: $ZAP_PID"
echo ""

# 等待并检查
echo "[-] 等待 ZAP 启动 (最多 30 秒)..."
for i in $(seq 1 15); do
    sleep 2
    
    # 检查进程
    if ! ps -p $ZAP_PID > /dev/null 2>&1; then
        echo ""
        echo "❌ ZAP 进程已退出!"
        echo ""
        echo "错误日志:"
        cat /tmp/zap.log
        exit 1
    fi
    
    # 检查端口
    if netstat -tlnp 2>/dev/null | grep -q ":$ZAP_PORT "; then
        echo ""
        echo "✅ ZAP 启动成功!"
        echo ""
        echo "=========================================="
        echo "  ZAP 服务信息"
        echo "=========================================="
        echo "  PID: $ZAP_PID"
        echo "  端口：$ZAP_PORT"
        echo "  路径：$ZAP_PATH"
        echo ""
        echo "验证命令:"
        echo "  ps aux | grep -i zap"
        echo "  netstat -tlnp | grep $ZAP_PORT"
        echo "  zap-cli -p $ZAP_PORT status"
        echo ""
        
        # 测试 zap-cli
        echo "[-] 测试 zap-cli..."
        if command -v zap-cli &> /dev/null; then
            if zap-cli -p $ZAP_PORT status &> /dev/null; then
                echo "✅ zap-cli 连接成功"
            else
                echo "⚠️  zap-cli 连接失败，但 ZAP 已启动"
                echo "   可能需要等待几秒"
            fi
        fi
        
        exit 0
    fi
    
    echo "    等待中... ($i/15)"
done

# 超时
echo ""
echo "❌ ZAP 启动超时"
echo ""
echo "进程状态:"
ps aux | grep -i zap | grep -v grep
echo ""
echo "端口状态:"
netstat -tlnp 2>/dev/null | grep -i java
echo ""
echo "日志内容:"
tail -50 /tmp/zap.log
echo ""
echo "=========================================="
echo "  手动启动命令"
echo "=========================================="
echo "  cd $ZAP_PATH"
echo "  java -jar $ZAP_JAR -daemon -port $ZAP_PORT"
echo ""

exit 1
