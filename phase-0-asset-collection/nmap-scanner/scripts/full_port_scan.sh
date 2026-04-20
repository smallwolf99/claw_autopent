#!/bin/bash
# full_port_scan.sh
# 完整端口扫描并生成详细报告

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${YELLOW}使用方法: $0 <目标IP/域名> [输出文件名前缀]${NC}"
    echo "示例: $0 192.168.1.1"
    echo "示例: $0 target.com myscan"
    exit 1
fi

TARGET=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 设置输出文件名前缀
if [ $# -ge 2 ]; then
    PREFIX=$2
else
    PREFIX="full_scan_${TARGET//[^a-zA-Z0-9]/_}"
fi

JSON_FILE="${PREFIX}_${TIMESTAMP}.json"
HTML_FILE="${PREFIX}_${TIMESTAMP}.html"
TXT_FILE="${PREFIX}_${TIMESTAMP}.txt"

# 设置扫描超时（默认30分钟）
SCAN_TIMEOUT=1800

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 Nmap完整端口扫描工具 v1.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "[*] 目标: ${GREEN}$TARGET${NC}"
echo -e "[*] 开始时间: $(date)"
echo -e "[*] 输出文件:"
echo -e "    JSON: ${JSON_FILE}"
echo -e "    HTML: ${HTML_FILE}"
echo -e "    Text: ${TXT_FILE}"
echo -e "${BLUE}========================================${NC}"

# 检查nmap是否安装
if ! command -v nmap &>/dev/null; then
    echo -e "${RED}[✗] 错误: nmap未安装${NC}"
    echo "请先安装nmap:"
    echo "  Ubuntu/Debian: sudo apt-get install nmap"
    echo "  CentOS/RHEL: sudo yum install nmap"
    echo "  macOS: brew install nmap"
    exit 1
fi

# 检查权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}[!] 警告: 非root用户运行，某些扫描功能可能受限${NC}"
    echo -e "${YELLOW}[!] 建议: sudo $0 <target>${NC}"
    echo -e "${YELLOW}[!] 如果目标需要root权限扫描，请用sudo重新运行${NC}"
    echo -e "${YELLOW}[.] 继续普通用户扫描...${NC}"
fi

# 目标验证
echo -e "[.] 验证目标可达性..."
ping -c 2 -W 2 $TARGET >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] 目标可达${NC}"
else
    echo -e "${YELLOW}[!] 目标不可达或禁止ping，继续扫描...${NC}"
fi

echo -e "[.] 开始完整端口扫描..."
echo -e "[.] 扫描类型: 所有TCP端口 (1-65535)"
echo -e "[.] 扫描技术: TCP SYN扫描 (-sS)"
echo -e "[.] 服务识别: 启用 (-sV)"
echo -e "[.] 脚本扫描: 启用 (-sC)"
echo -e "[.] 输出格式: JSON+HTML+Normal"
echo -e "${YELLOW}[⚠] 警告: 完整扫描可能需要较长时间${NC}"
echo -e "${YELLOW}[⏳] 预计时间: 10-30分钟 (取决于网络速度)${NC}"
echo -e "${YELLOW}[📢] 超时设置: ${SCAN_TIMEOUT}秒 (30分钟)${NC}"

# 执行完整扫描 (使用timeout控制最长运行时间)
timeout $SCAN_TIMEOUT nmap -p- -T4 -sS -sV -sC -oA $PREFIX $TARGET
SCAN_RESULT=$?

# 如果timeout触发
if [ $? -eq 124 ]; then
    echo -e "${RED}[⏰] 扫描超时 (${SCAN_TIMEOUT}秒)${NC}"
    echo -e "[!] 扫描未完成，可能的原因:"
    echo -e "    1. 目标响应慢或过滤严格"
    echo -e "    2. 网络延迟高"
    echo -e "    3. 目标端口过多"
    echo -e "[💡] 建议: 使用 -F 参数进行快速扫描"
    TIMEOUT_OCCURRED=1
fi

# 检查扫描结果文件
if [ -f "${PREFIX}.xml" ] && [ -f "${PREFIX}.gnmap" ]; then
    # 转换XML到JSON (如果没有直接生成JSON)
    if [ ! -f "$JSON_FILE" ]; then
        echo -e "[.] 转换扫描结果到JSON格式..."
        # 尝试使用nmap的转换工具
        if [ -f "${PREFIX}.xml" ]; then
            # 这里可以添加XML到JSON转换逻辑
            # 简单复制XML，因为nmap的-oJ需要重新扫描
            echo -e "${YELLOW}[!] 注意: 未直接生成JSON，使用XML结果${NC}"
            cp "${PREFIX}.xml" "$JSON_FILE"
        fi
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "[*] 扫描完成时间: $(date)"

if [ $SCAN_RESULT -eq 0 ] || [ -f "${PREFIX}.xml" ]; then
    echo -e "${GREEN}[✓] 扫描完成！${NC}"
    
    # 列出生成的文件
    echo -e "[📁] 生成的文件:"
    ls -la ${PREFIX}.* 2>/dev/null | while read file; do
        SIZE=$(echo $file | awk '{print $5}')
        NAME=$(echo $file | awk '{print $9}')
        echo -e "    ${NAME} (${SIZE} bytes)"
    done
    
    # 生成详细报告
    echo -e "[📊] 正在生成详细报告..."
    
    # 创建文本报告
    cat > $TXT_FILE << EOF
========================================
Nmap完整端口扫描报告
========================================
目标: $TARGET
扫描时间: $(date)
扫描命令: nmap -p- -T4 -sS -sV -sC -oA $PREFIX $TARGET

生成的文件:
EOF
    
    ls ${PREFIX}.* 2>/dev/null >> $TXT_FILE
    
    # 添加统计信息
    if [ -f "${PREFIX}.gnmap" ]; then
        echo -e "\n扫描统计:" >> $TXT_FILE
        OPEN_PORTS=$(grep -o "Ports: " "${PREFIX}.gnmap" | wc -l)
        TOTAL_PORTS=$((OPEN_PORTS * 1000))  # 近似值，快速扫描
        
        # 提取开放端口详情
        echo -e "\n开放端口详情:" >> $TXT_FILE
        grep "open" "${PREFIX}.gnmap" | sed 's/.*Ports: //' | tr ',' '\n' | grep "open" | head -20 >> $TXT_FILE
    fi
    
    # 创建HTML报告
    cat > $HTML_FILE << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nmap完整扫描报告 - $TARGET</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header h1 svg {
            width: 32px;
            height: 32px;
        }
        .meta-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .info-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .info-card h3 {
            color: #555;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .info-card p {
            color: #333;
            font-size: 16px;
            font-weight: 500;
        }
        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .port-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .port-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }
        .port-table td {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .port-table tr:hover {
            background: #f5f7ff;
        }
        .status-open { color: #27ae60; font-weight: bold; }
        .status-filtered { color: #f39c12; }
        .status-closed { color: #7f8c8d; }
        .highlight {
            background: #fffde7;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
        .security-tips {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .tip {
            background: #f0f7ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4dabf7;
        }
        .tip h4 {
            color: #1971c2;
            margin-bottom: 8px;
        }
        .files-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        .file-name {
            font-family: monospace;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .file-size {
            color: #6c757d;
            font-size: 14px;
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header { padding: 20px; }
            .section { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L1 21h22L12 2zm0 3.84L19.36 19H4.64L12 5.84z"/>
                    <path d="M7 10h10v2H7z"/>
                </svg>
                Nmap完整端口扫描报告
            </h1>
            
            <div class="meta-info">
                <div class="info-card">
                    <h3>目标</h3>
                    <p>$TARGET</p>
                </div>
                <div class="info-card">
                    <h3>扫描时间</h3>
                    <p>$(date)</p>
                </div>
                <div class="info-card">
                    <h3>扫描命令</h3>
                    <p>nmap -p- -T4 -sS -sV -sC</p>
                </div>
                <div class="info-card">
                    <h3>报告版本</h3>
                    <p>v1.0</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 扫描摘要</h2>
            <div class="highlight">
                <h3>重要提示</h3>
                <p>本次扫描对所有TCP端口(1-65535)进行了检查，包括服务版本识别和默认脚本扫描。</p>
EOF

    # 动态添加扫描状态
    if [ "$TIMEOUT_OCCURRED" = "1" ]; then
        echo "<p style='color: #f39c12;'><strong>⚠ 注意: 扫描超时未完成</strong></p>" >> $HTML_FILE
    fi
    
    # 添加统计信息
    if [ -f "${PREFIX}.gnmap" ]; then
        echo "<p><strong>扫描状态: 已完成</strong></p>" >> $HTML_FILE
    fi

cat >> $HTML_FILE << EOF
            </div>
        </div>

        <div class="section">
            <h2>📁 生成文件</h2>
            <div class="files-list">
EOF

# 动态添加文件列表
for file in ${PREFIX}.*; do
    if [ -f "$file" ]; then
        SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        SIZE_KB=$((SIZE / 1024))
        echo "<div class='file-item'>
                <div class='file-name'>$(basename $file)</div>
                <div class='file-size'>${SIZE_KB} KB</div>
              </div>" >> $HTML_FILE
    fi
done

cat >> $HTML_FILE << EOF
            </div>
        </div>

        <div class="section">
            <h2>🛡️ 安全建议</h2>
            <div class="security-tips">
                <div class="tip">
                    <h4>端口管理</h4>
                    <p>关闭所有不必要的端口，只开放业务需要的端口。</p>
                </div>
                <div class="tip">
                    <h4>服务更新</h4>
                    <p>定期更新服务到最新版本，修补已知漏洞。</p>
                </div>
                <div class="tip">
                    <h4>访问控制</h4>
                    <p>配置防火墙，限制访问来源IP。</p>
                </div>
                <div class="tip">
                    <h4>日志监控</h4>
                    <p>开启服务日志，定期检查异常访问。</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📋 后续步骤建议</h2>
            <ol style="margin-left: 20px; line-height: 2;">
                <li>检查开放端口对应的服务是否需要对外暴露</li>
                <li>验证服务版本是否存在已知安全漏洞</li>
                <li>配置适当的防火墙规则</li>
                <li>定期复查端口开放情况</li>
                <li>对关键服务进行深度安全测试</li>
            </ol>
        </div>

        <div class="footer">
            <p>生成时间: $(date)</p>
            <p>本报告由Nmap扫描工具自动生成，仅供安全评估使用</p>
        </div>
    </div>
</body>
</html>
EOF

    echo -e "${GREEN}[✓] HTML报告生成: ${HTML_FILE}${NC}"
    echo -e "${GREEN}[✓] 文本报告生成: ${TXT_FILE}${NC}"
    
    # 提供使用建议
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}[💡] 使用建议:${NC}"
    echo -e "    查看HTML报告: ${HTML_FILE}"
    echo -e "    查看详细结果: ${PREFIX}.gnmap"
    echo -e "    原始XML数据: ${PREFIX}.xml"
    echo -e "    下次快速扫描: nmap -F -T4 $TARGET"
    
else
    echo -e "${RED}[✗] 扫描失败或未产生有效结果${NC}"
    echo -e "[!] 可能的原因:"
    echo -e "    1. 目标不存在或无法访问"
    echo -e "    2. 网络连接问题"
    echo -e "    3. 防火墙/IDS阻止扫描"
    echo -e "[💡] 建议:"
    echo -e "    1. 检查网络连接"
    echo -e "    2. 使用更简单的扫描: nmap -sn $TARGET"
    echo -e "    3. 验证目标IP/域名是否正确"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}[✅] 脚本执行完成${NC}"

if [ "$TIMEOUT_OCCURRED" = "1" ]; then
    exit 124
else
    exit $SCAN_RESULT
fi