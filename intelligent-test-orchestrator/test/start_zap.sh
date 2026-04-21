#!/bin/bash
# 启动 ZAP 代理服务

echo "=========================================="
echo "  启动 ZAP 代理服务"
echo "=========================================="
echo ""

# 检查 ZAP-CLI 是否安装
if ! command -v zap-cli &> /dev/null; then
    echo "❌ zap-cli 未安装"
    echo "   请执行：pip3 install zap-cli"
    exit 1
fi

# 检查 ZAP 是否已经在运行
echo "[-] 检查 ZAP 状态..."
if zap-cli status &> /dev/null; then
    echo "✅ ZAP 已经在运行"
    zap-cli status
    exit 0
fi

# 尝试启动 ZAP
echo "[-] 启动 ZAP..."

# 方法 1: 使用 zap-cli start
zap-cli start &
sleep 5

# 检查是否启动成功
if zap-cli status &> /dev/null; then
    echo "✅ ZAP 启动成功"
    zap-cli status
    exit 0
fi

# 方法 2: 使用 Docker（如果可用）
if command -v docker &> /dev/null; then
    echo "[-] zap-cli start 失败，尝试使用 Docker..."
    
    # 检查容器是否已存在
    if docker ps -a | grep -q zap; then
        echo "   发现已有 ZAP 容器，尝试启动..."
        docker start zap
    else
        echo "   创建新的 ZAP 容器..."
        docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh
    fi
    
    sleep 5
    
    # 设置端口
    zap-cli settings set port 8090
    
    if zap-cli status &> /dev/null; then
        echo "✅ ZAP 通过 Docker 启动成功"
        zap-cli status
        exit 0
    fi
fi

# 方法 3: 手动启动 Java ZAP（使用已知路径）
if command -v java &> /dev/null; then
    echo "[-] 尝试手动启动 ZAP..."
    
    # 首先检查已知路径
    if [ -f "/home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar" ]; then
        ZAP_JAR="/home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar"
        echo "   找到 ZAP (已知路径): $ZAP_JAR"
    else
        # 查找 ZAP jar 文件
        ZAP_JAR=$(find /home/ubuntu -name "zap*.jar" 2>/dev/null | head -1)
        if [ -n "$ZAP_JAR" ]; then
            echo "   找到 ZAP: $ZAP_JAR"
        fi
    fi
    
    if [ -n "$ZAP_JAR" ] && [ -f "$ZAP_JAR" ]; then
        echo "   正在启动 ZAP..."
        nohup java -jar "$ZAP_JAR" -daemon -port 8090 > /tmp/zap.log 2>&1 &
        sleep 8
        
        zap-cli settings set port 8090
        
        if zap-cli status &> /dev/null; then
            echo "✅ ZAP 手动启动成功"
            zap-cli status
            exit 0
        else
            echo "   ⚠️  ZAP 启动中，等待..."
            sleep 5
            if zap-cli status &> /dev/null; then
                echo "✅ ZAP 手动启动成功"
                zap-cli status
                exit 0
            fi
        fi
    else
        echo "   ⚠️  未找到 ZAP jar 文件"
    fi
fi

# 所有方法都失败
echo ""
echo "❌ 无法启动 ZAP 服务"
echo ""
echo "请尝试以下方法之一："
echo ""
echo "方法 1: 安装 OWASP ZAP"
echo "  下载地址：https://www.zaproxy.org/download/"
echo ""
echo "方法 2: 使用 Docker"
echo "  docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh"
echo ""
echo "方法 3: 如果已安装 ZAP，手动启动"
echo "  zap.sh -daemon -port 8090"
echo ""

exit 1
