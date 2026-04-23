#!/bin/bash
# extract_open_ports.sh
# 从Nmap JSON文件提取开放端口信息

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}🔍 Nmap JSON数据提取工具 v1.0${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}使用方法:${NC}"
    echo -e "  $0 <nmap_json_file> [输出格式]"
    echo -e ""
    echo -e "${YELLOW}输出格式选项:${NC}"
    echo -e "  list     - 简单列表 (默认)"
    echo -e "  detail   - 详细列表"
    echo -e "  csv      - CSV格式"
    echo -e "  markdown - Markdown表格"
    echo -e "  html     - HTML表格"
    echo -e "  json     - 重新格式化的JSON"
    echo -e ""
    echo -e "${YELLOW}批量处理:${NC}"
    echo -e "  $0 *.json [格式]"
    echo -e "  $0 directory/ [格式]"
    echo -e ""
    echo -e "${YELLOW}示例:${NC}"
    echo -e "  $0 scan.json detail"
    echo -e "  $0 scan.json csv > ports.csv"
    echo -e "  $0 results/*.json markdown"
    echo -e "${CYAN}========================================${NC}"
    exit 1
fi

INPUT=$1
FORMAT=${2:-list}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 检查jq是否安装
if ! command -v jq &>/dev/null; then
    echo -e "${RED}[✗] 错误: jq未安装${NC}"
    echo -e "[!] jq是处理JSON数据的必要工具"
    echo -e "[!] 安装命令:"
    echo -e "    Ubuntu/Debian: sudo apt-get install jq"
    echo -e "    CentOS/RHEL: sudo yum install jq"
    echo -e "    macOS: brew install jq"
    echo -e ""
    echo -e "${YELLOW}[!] 将使用简单文本提取（功能受限）${NC}"
    JQ_AVAILABLE=0
else
    JQ_AVAILABLE=1
fi

# 处理输入参数
if [ -d "$INPUT" ]; then
    # 目录模式
    FILES=("$INPUT"/*.json)
    MODE="directory"
elif [[ "$INPUT" == *.json ]] && [ -f "$INPUT" ]; then
    # 单个文件
    FILES=("$INPUT")
    MODE="single"
elif [[ "$INPUT" == *.json ]]; then
    # 通配符模式
    FILES=($INPUT)
    MODE="wildcard"
else
    echo -e "${RED}[✗] 错误: 输入必须是JSON文件或包含JSON文件的目录${NC}"
    exit 1
fi

# 检查文件是否存在
VALID_FILES=()
for file in "${FILES[@]}"; do
    if [ -f "$file" ] && [[ "$file" == *.json ]]; then
        VALID_FILES+=("$file")
    fi
done

if [ ${#VALID_FILES[@]} -eq 0 ]; then
    echo -e "${RED}[✗] 错误: 未找到有效的JSON文件${NC}"
    exit 1
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🔍 Nmap JSON数据提取工具 v1.0${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "[*] 输入: ${GREEN}$INPUT${NC}"
echo -e "[*] 模式: ${GREEN}$MODE${NC}"
echo -e "[*] 格式: ${GREEN}$FORMAT${NC}"
echo -e "[*] 文件数: ${GREEN}${#VALID_FILES[@]}${NC}"
echo -e "[*] 时间: $(date)"
echo -e "${CYAN}========================================${NC}"

# 根据格式输出
case $FORMAT in
    list)
        extract_simple_list() {
            local file=$1
            echo -e "${BLUE}========================================${NC}"
            echo -e "${GREEN}文件: $(basename $file)${NC}"
            echo -e "${BLUE}========================================${NC}"
            
            if [ $JQ_AVAILABLE -eq 1 ]; then
                # 使用jq提取
                TARGET=$(jq -r '.nmaprun.host.address.addr // .nmaprun.host.address[0].addr // "unknown"' "$file" 2>/dev/null)
                HOST_STATE=$(jq -r '.nmaprun.host.status.state // "unknown"' "$file" 2>/dev/null)
                SCAN_TIME=$(jq -r '.nmaprun.startstr // "unknown"' "$file" 2>/dev/null)
                
                echo -e "[🎯] 目标: $TARGET"
                echo -e "[📊] 状态: $HOST_STATE"
                echo -e "[🕐] 扫描时间: $SCAN_TIME"
                
                # 提取开放端口
                OPEN_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "open") | "\(.protocol)/\(.portid) - \(.service.name // "unknown")"' "$file" 2>/dev/null)
                
                if [ -n "$OPEN_PORTS" ]; then
                    echo -e "[🔓] 开放端口 ($(echo "$OPEN_PORTS" | wc -l)个):"
                    echo "$OPEN_PORTS" | while read port; do
                        echo -e "  ${GREEN}✓${NC} $port"
                    done
                else
                    echo -e "[🔒] 无开放端口"
                fi
                
                # 服务版本统计
                SERVICES=$(jq -r '.nmaprun.host.ports.port[]? | select(.service.product) | "\(.service.product) \(.service.version // "")"' "$file" 2>/dev/null)
                if [ -n "$SERVICES" ]; then
                    echo -e "[🔧] 识别服务 ($(echo "$SERVICES" | wc -l)个):"
                    echo "$SERVICES" | sort -u | while read service; do
                        echo -e "  ${CYAN}•${NC} $service"
                    done
                fi
                
            else
                # 使用grep简单提取
                echo -e "${YELLOW}[!] 使用简单文本提取${NC}"
                
                # 提取开放端口
                OPEN_PORTS=$(grep -A2 '"state":"open"' "$file" | grep '"portid"' | sed 's/.*"\([0-9]*\)".*/\1/' 2>/dev/null)
                
                if [ -n "$OPEN_PORTS" ]; then
                    echo -e "[🔓] 开放端口 ($(echo "$OPEN_PORTS" | wc -l)个):"
                    echo "$OPEN_PORTS" | while read port; do
                        echo -e "  ${GREEN}✓${NC} $port"
                    done
                else
                    echo -e "[🔒] 无开放端口"
                fi
            fi
        }
        
        for file in "${VALID_FILES[@]}"; do
            extract_simple_list "$file"
            echo ""
        done
        ;;
        
    detail)
        extract_detailed_list() {
            local file=$1
            
            if [ $JQ_AVAILABLE -eq 1 ]; then
                # 使用jq提取详细信息
                TARGET=$(jq -r '.nmaprun.host.address.addr // .nmaprun.host.address[0].addr // "unknown"' "$file" 2>/dev/null)
                HOST_STATE=$(jq -r '.nmaprun.host.status.state // "unknown"' "$file" 2>/dev/null)
                SCAN_TIME=$(jq -r '.nmaprun.startstr // "unknown"' "$file" 2>/dev/null)
                SCAN_ARGS=$(jq -r '.nmaprun.args // "unknown"' "$file" 2>/dev/null)
                
                echo -e "${BLUE}========================================${NC}"
                echo -e "${MAGENTA}📋 详细扫描报告${NC}"
                echo -e "${BLUE}========================================${NC}"
                echo -e "${GREEN}文件:${NC} $(basename $file)"
                echo -e "${GREEN}目标:${NC} $TARGET"
                echo -e "${GREEN}状态:${NC} $HOST_STATE"
                echo -e "${GREEN}扫描时间:${NC} $SCAN_TIME"
                echo -e "${GREEN}扫描命令:${NC} $SCAN_ARGS"
                echo -e "${BLUE}----------------------------------------${NC}"
                
                # 提取所有端口详细信息
                echo -e "${CYAN}📊 端口详情:${NC}"
                jq -r '.nmaprun.host.ports.port[]? | 
                    "端口: \(.protocol)/\(.portid)\n状态: \(.state.state)\n原因: \(.state.reason // "N/A")\n服务: \(.service.name // "unknown")\n产品: \(.service.product // "N/A")\n版本: \(.service.version // "N/A")\n额外: \(.service.extrainfo // "N/A")\n脚本: \(.script // "N/A")\n' "$file" 2>/dev/null | \
                    while IFS= read -r line; do
                        if [[ "$line" == "端口:"* ]]; then
                            echo -e "${BLUE}----------------------------------------${NC}"
                        fi
                        echo -e "  $line"
                    done
                
                # 统计信息
                echo -e "${BLUE}----------------------------------------${NC}"
                echo -e "${CYAN}📈 统计信息:${NC}"
                TOTAL_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | .portid' "$file" 2>/dev/null | wc -l)
                OPEN_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "open") | .portid' "$file" 2>/dev/null | wc -l)
                FILTERED_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "filtered") | .portid' "$file" 2>/dev/null | wc -l)
                CLOSED_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "closed") | .portid' "$file" 2>/dev/null | wc -l)
                
                echo -e "  总检查端口: $TOTAL_PORTS"
                echo -e "  开放端口: $OPEN_PORTS"
                echo -e "  过滤端口: $FILTERED_PORTS"
                echo -e "  关闭端口: $CLOSED_PORTS"
                
                # 服务版本统计
                echo -e "${CYAN}🔧 服务版本统计:${NC}"
                jq -r '.nmaprun.host.ports.port[]? | select(.service.product) | "\(.service.product) \(.service.version // "")"' "$file" 2>/dev/null | sort -u | while read service; do
                    echo -e "  • $service"
                done
                
            else
                echo -e "${RED}[✗] 详细模式需要jq工具${NC}"
                echo -e "[!] 请安装jq或使用list模式"
            fi
        }
        
        for file in "${VALID_FILES[@]}"; do
            extract_detailed_list "$file"
            echo ""
        done
        ;;
        
    csv)
        # CSV格式输出
        if [ $JQ_AVAILABLE -eq 1 ]; then
            echo "文件,目标,端口,协议,状态,服务名称,服务产品,服务版本,扫描时间"
            
            for file in "${VALID_FILES[@]}"; do
                FILENAME=$(basename "$file")
                TARGET=$(jq -r '.nmaprun.host.address.addr // .nmaprun.host.address[0].addr // "unknown"' "$file" 2>/dev/null)
                SCAN_TIME=$(jq -r '.nmaprun.startstr // "unknown"' "$file" 2>/dev/null)
                
                # 提取所有端口信息
                jq -r --arg filename "$FILENAME" --arg target "$TARGET" --arg scan_time "$SCAN_TIME" '
                    .nmaprun.host.ports.port[]? | 
                    [
                        $filename,
                        $target,
                        .portid,
                        .protocol,
                        .state.state,
                        (.service.name // ""),
                        (.service.product // ""),
                        (.service.version // ""),
                        $scan_time
                    ] | @csv' "$file" 2>/dev/null
            done
        else
            echo -e "${RED}[✗] CSV格式需要jq工具${NC}"
        fi
        ;;
        
    markdown)
        # Markdown表格输出
        if [ $JQ_AVAILABLE -eq 1 ]; then
            echo "| 目标 | 端口 | 协议 | 状态 | 服务 | 产品 | 版本 |"
            echo "|------|------|------|------|------|------|------|"
            
            for file in "${VALID_FILES[@]}"; do
                TARGET=$(jq -r '.nmaprun.host.address.addr // .nmaprun.host.address[0].addr // "unknown"' "$file" 2>/dev/null)
                
                jq -r --arg target "$TARGET" '
                    .nmaprun.host.ports.port[]? | 
                    "| \($target) | \(.portid) | \(.protocol) | \(.state.state) | \(.service.name // "") | \(.service.product // "") | \(.service.version // "") |"' "$file" 2>/dev/null
            done
        else
            echo -e "${RED}[✗] Markdown格式需要jq工具${NC}"
        fi
        ;;
        
    html)
        # HTML表格输出
        if [ $JQ_AVAILABLE -eq 1 ]; then
            cat << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Nmap扫描结果</title>
    <style>
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .open { color: green; font-weight: bold; }
        .filtered { color: orange; }
        .closed { color: gray; }
    </style>
</head>
<body>
    <h1>Nmap扫描结果报告</h1>
    <p>生成时间: $(date)</p>
    <table>
        <tr>
            <th>目标</th>
            <th>端口</th>
            <th>协议</th>
            <th>状态</th>
            <th>服务</th>
            <th>产品</th>
            <th>版本</th>
        </tr>
EOF
            
            for file in "${VALID_FILES[@]}"; do
                TARGET=$(jq -r '.nmaprun.host.address.addr // .nmaprun.host.address[0].addr // "unknown"' "$file" 2>/dev/null)
                
                jq -r --arg target "$TARGET" '
                    .nmaprun.host.ports.port[]? | 
                    "<tr>" +
                    "<td>\($target)</td>" +
                    "<td>\(.portid)</td>" +
                    "<td>\(.protocol)</td>" +
                    "<td class=\"\(.state.state)\">\(.state.state)</td>" +
                    "<td>\(.service.name // "")</td>" +
                    "<td>\(.service.product // "")</td>" +
                    "<td>\(.service.version // "")</td>" +
                    "</tr>"' "$file" 2>/dev/null
            done
            
            cat << EOF
    </table>
    <p>文件总数: ${#VALID_FILES[@]}</p>
</body>
</html>
EOF
        else
            echo -e "${RED}[✗] HTML格式需要jq工具${NC}"
        fi
        ;;
        
    json)
        # 重新格式化的JSON输出
        if [ $JQ_AVAILABLE -eq 1 ]; then
            OUTPUT_JSON="extracted_ports_${TIMESTAMP}.json"
            echo "[" > $OUTPUT_JSON
            
            FIRST_FILE=true
            for file in "${VALID_FILES[@]}"; do
                if [ "$FIRST_FILE" = false ]; then
                    echo "," >> $OUTPUT_JSON
                fi
                FIRST_FILE=false
                
                jq '{
                    target: .nmaprun.host.address.addr // .nmaprun.host.address[0].addr,
                    host_state: .nmaprun.host.status.state,
                    scan_time: .nmaprun.startstr,
                    scan_args: .nmaprun.args,
                    ports: [.nmaprun.host.ports.port[]? | {
                        port: .portid,
                        protocol: .protocol,
                        state: .state.state,
                        service: .service.name // null,
                        product: .service.product // null,
                        version: .service.version // null
                    }]
                }' "$file" 2>/dev/null >> $OUTPUT_JSON
            done
            
            echo "]" >> $OUTPUT_JSON
            echo -e "${GREEN}[✓] JSON输出保存到: $OUTPUT_JSON${NC}"
        else
            echo -e "${RED}[✗] JSON格式需要jq工具${NC}"
        fi
        ;;
        
    *)
        echo -e "${RED}[✗] 错误: 未知输出格式: $FORMAT${NC}"
        echo -e "[!] 可用格式: list, detail, csv, markdown, html, json"
        exit 1
        ;;
esac

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}[✅] 数据提取完成${NC}"
echo -e "${CYAN}========================================${NC}"

# 显示统计信息
if [ ${#VALID_FILES[@]} -gt 1 ]; then
    echo -e "[📊] 处理统计:"
    echo -e "   文件总数: ${#VALID_FILES[@]}"
    
    if [ $JQ_AVAILABLE -eq 1 ] && [ "$FORMAT" != "json" ]; then
        TOTAL_PORTS=0
        OPEN_PORTS=0
        
        for file in "${VALID_FILES[@]}"; do
            FILE_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | .portid' "$file" 2>/dev/null | wc -l)
            FILE_OPEN=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "open") | .portid' "$file" 2>/dev/null | wc -l)
            
            TOTAL_PORTS=$((TOTAL_PORTS + FILE_PORTS))
            OPEN_PORTS=$((OPEN_PORTS + FILE_OPEN))
        done
        
        echo -e "   总端口数: $TOTAL_PORTS"
        echo -e "   开放端口: $OPEN_PORTS"
        echo -e "   开放率: $((OPEN_PORTS * 100 / (TOTAL_PORTS > 0 ? TOTAL_PORTS : 1)))%"
    fi
fi

exit 0