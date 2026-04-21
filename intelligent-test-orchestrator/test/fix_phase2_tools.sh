#!/bin/bash
# Phase-2 工具修复脚本
# 用途：自动安装和配置 Phase-2 所需的安全工具

set -e

echo "=========================================="
echo "  Phase-2 工具修复脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}提示：建议使用 sudo 运行此脚本以获得更好的安装效果${NC}"
    echo ""
fi

# 1. 检查 Nikto
echo "[-] 检查 Nikto..."
if command -v nikto &> /dev/null; then
    echo -e "${GREEN}✅ Nikto 已安装${NC}"
    nikto -Version 2>&1 | head -1
else
    echo -e "${YELLOW}❌ Nikto 未安装${NC}"
    echo "    正在安装 Nikto..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y nikto
        echo -e "${GREEN}✅ Nikto 安装完成${NC}"
    else
        echo -e "${RED}❌ 无法自动安装 Nikto，请手动安装${NC}"
        echo "    参考：https://github.com/sullo/nikto"
    fi
fi
echo ""

# 2. 检查 Nuclei
echo "[-] 检查 Nuclei..."
if command -v nuclei &> /dev/null; then
    echo -e "${GREEN}✅ Nuclei 已安装${NC}"
    nuclei -version
else
    echo -e "${YELLOW}❌ Nuclei 未安装${NC}"
    echo "    正在安装 Nuclei..."
    
    # 检查 Go 是否安装
    if command -v go &> /dev/null; then
        echo "    检测到 Go，正在通过 Go 安装..."
        go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
        
        # 添加到 PATH（如果必要）
        if [ ! -f "$HOME/go/bin/nuclei" ]; then
            echo -e "${RED}❌ Nuclei 安装失败${NC}"
        else
            echo "    正在初始化 Nuclei 模板..."
            $HOME/go/bin/nuclei -ut
            echo -e "${GREEN}✅ Nuclei 安装完成${NC}"
            echo "    提示：请确保 \$HOME/go/bin 在 PATH 中"
            echo "    执行：export PATH=\$PATH:\$HOME/go/bin"
        fi
    else
        echo -e "${YELLOW}    Go 未安装，尝试下载二进制文件...${NC}"
        wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
        unzip -q nuclei_linux_amd64.zip
        sudo mv nuclei /usr/local/bin/
        rm nuclei_linux_amd64.zip
        
        if command -v nuclei &> /dev/null; then
            nuclei -ut
            echo -e "${GREEN}✅ Nuclei 安装完成${NC}"
        else
            echo -e "${RED}❌ Nuclei 安装失败${NC}"
        fi
    fi
fi
echo ""

# 3. 检查 Afrog
echo "[-] 检查 Afrog..."
if command -v afrog &> /dev/null; then
    echo -e "${GREEN}✅ Afrog 已安装${NC}"
else
    echo -e "${YELLOW}❌ Afrog 未安装${NC}"
    echo "    正在安装 Afrog..."
    
    if command -v go &> /dev/null; then
        go install github.com/zan8in/afrog/v2@latest
        
        if [ -f "$HOME/go/bin/afrog" ]; then
            echo -e "${GREEN}✅ Afrog 安装完成${NC}"
            echo "    提示：请确保 \$HOME/go/bin 在 PATH 中"
        else
            echo -e "${RED}❌ Afrog 安装失败${NC}"
        fi
    else
        echo -e "${RED}❌ 需要安装 Go 才能安装 Afrog${NC}"
    fi
fi
echo ""

# 4. 检查 ZAP-CLI
echo "[-] 检查 ZAP-CLI..."
if command -v zap-cli &> /dev/null; then
    echo -e "${GREEN}✅ ZAP-CLI 已安装${NC}"
    zap-cli --version
else
    echo -e "${YELLOW}❌ ZAP-CLI 未安装${NC}"
    echo "    正在安装 ZAP-CLI..."
    
    if command -v pip3 &> /dev/null; then
        pip3 install zap-cli
        
        if command -v zap-cli &> /dev/null; then
            echo -e "${GREEN}✅ ZAP-CLI 安装完成${NC}"
        else
            echo -e "${RED}❌ ZAP-CLI 安装失败${NC}"
        fi
    else
        echo -e "${RED}❌ pip3 未安装，无法安装 ZAP-CLI${NC}"
    fi
fi
echo ""

# 5. 检查 SQLMap
echo "[-] 检查 SQLMap..."
if command -v sqlmap &> /dev/null; then
    echo -e "${GREEN}✅ SQLMap 已安装${NC}"
    sqlmap --version 2>&1 | head -1
else
    echo -e "${YELLOW}⚠️  SQLMap 未安装（可选）${NC}"
    echo "    如需安装，请执行："
    echo "    git clone https://github.com/sqlmapproject/sqlmap.git"
    echo "    export PATH=\$PATH:/path/to/sqlmap"
fi
echo ""

# 6. 启动 ZAP 代理服务
echo "[-] 检查 ZAP 代理服务..."
if command -v zap-cli &> /dev/null; then
    if zap-cli status &> /dev/null; then
        echo -e "${GREEN}✅ ZAP 代理服务正在运行${NC}"
    else
        echo -e "${YELLOW}⚠️  ZAP 代理服务未启动${NC}"
        echo "    正在启动 ZAP..."
        
        # 尝试启动 ZAP
        if command -v java &> /dev/null; then
            zap-cli start &
            sleep 5
            
            if zap-cli status &> /dev/null; then
                echo -e "${GREEN}✅ ZAP 代理服务已启动${NC}"
            else
                echo -e "${YELLOW}⚠️  无法自动启动 ZAP，请手动启动${NC}"
                echo "    方法 1: 下载 OWASP ZAP: https://www.zaproxy.org/download/"
                echo "    方法 2: 使用 Docker: docker run -u zap -p 8090:8090 -i owasp/zap:stable zap-daemon.sh"
            fi
        else
            echo -e "${RED}❌ Java 未安装，无法启动 ZAP${NC}"
        fi
    fi
fi
echo ""

# 7. 测试工具
echo "=========================================="
echo "  测试工具"
echo "=========================================="
echo ""

TEST_TARGET="http://demo.testfire.net"

# 测试 Nikto
if command -v nikto &> /dev/null; then
    echo "[-] 测试 Nikto（快速测试）..."
    timeout 10 nikto -h $TEST_TARGET -timeout 5 2>&1 | head -3 || echo "    测试完成或超时"
    echo ""
fi

# 测试 Nuclei
if command -v nuclei &> /dev/null; then
    echo "[-] 测试 Nuclei（快速测试）..."
    timeout 10 nuclei -u $TEST_TARGET -json -silent -timeout 5 2>&1 | head -3 || echo "    测试完成或超时"
    echo ""
fi

# 测试 ZAP-CLI
if command -v zap-cli &> /dev/null; then
    echo "[-] 测试 ZAP-CLI..."
    zap-cli status 2>&1 | head -3 || echo "    状态检查失败"
    echo ""
fi

# 总结
echo "=========================================="
echo "  修复总结"
echo "=========================================="
echo ""

# 检查所有工具
TOOLS_OK=0
TOOLS_TOTAL=0

for tool in nikto nuclei afrog zap-cli; do
    TOOLS_TOTAL=$((TOOLS_TOTAL + 1))
    if command -v $tool &> /dev/null; then
        TOOLS_OK=$((TOOLS_OK + 1))
    fi
done

echo "已安装工具：$TOOLS_OK/$TOOLS_TOTAL"
echo ""

if [ $TOOLS_OK -eq $TOOLS_TOTAL ]; then
    echo -e "${GREEN}✅ 所有工具已就绪！${NC}"
    echo ""
    echo "现在可以运行测试："
    echo "  python3 test/test_phase2_phase3_real.py"
else
    echo -e "${YELLOW}⚠️  部分工具未安装成功${NC}"
    echo ""
    echo "请查看上方输出，手动安装缺失的工具"
    echo "或参考文档：test/FIX_PHASE2_ERRORS.md"
fi

echo ""
echo "=========================================="
