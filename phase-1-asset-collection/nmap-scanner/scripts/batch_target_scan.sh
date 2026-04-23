#!/bin/bash
# batch_target_scan.sh
# 批量扫描目标列表

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}🎯 Nmap批量扫描工具 v1.0${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}使用方法: $0 <目标列表文件> [扫描类型]${NC}"
    echo -e ""
    echo -e "扫描类型选项:"
    echo -e "  fast    - 快速扫描 (-F) [默认]"
    echo -e "  full    - 完整端口扫描 (-p-)"
    echo -e "  web     - Web服务扫描 (80,443,8080等)"
    echo -e "  service - 服务版本扫描 (-sV)"
    echo -e ""
    echo -e "目标列表文件格式:"
    echo -e "  每行一个IP地址或域名"
    echo -e "  支持注释行 (#开头)"
    echo -e "  支持空行"
    echo -e ""
    echo -e "示例:"
    echo -e "  $0 targets.txt fast"
    echo -e "  $0 domains.txt web"
    echo -e "  $0 ips.txt full"
    echo -e "${CYAN}========================================${NC}"
    exit 1
fi

TARGETS_FILE=$1
SCAN_TYPE=${2:-fast}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="batch_scan_${SCAN_TYPE}_${TIMESTAMP}"

# 检查目标文件
if [ ! -f "$TARGETS_FILE" ]; then
    echo -e "${RED}[✗] 错误: 目标文件不存在: $TARGETS_FILE${NC}"
    exit 1
fi

# 检查nmap是否安装
if ! command -v nmap &>/dev/null; then
    echo -e "${RED}[✗] 错误: nmap未安装${NC}"
    echo "请先安装nmap:"
    echo "  Ubuntu/Debian: sudo apt-get install nmap"
    echo "  CentOS/RHEL: sudo yum install nmap"
    echo "  macOS: brew install nmap"
    exit 1
fi

# 创建输出目录
mkdir -p $OUTPUT_DIR
mkdir -p "$OUTPUT_DIR/json"
mkdir -p "$OUTPUT_DIR/reports"
mkdir -p "$OUTPUT_DIR/logs"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🎯 Nmap批量扫描工具 v1.0${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "[*] 目标文件: ${GREEN}$TARGETS_FILE${NC}"
echo -e "[*] 扫描类型: ${GREEN}$SCAN_TYPE${NC}"
echo -e "[*] 输出目录: ${GREEN}$OUTPUT_DIR${NC}"
echo -e "[*] 开始时间: $(date)"
echo -e "${CYAN}========================================${NC}"

# 统计目标数量
TOTAL_TARGETS=$(grep -v '^#' "$TARGETS_FILE" | grep -v '^$' | wc -l)
if [ $TOTAL_TARGETS -eq 0 ]; then
    echo -e "${RED}[✗] 错误: 目标文件中没有有效目标${NC}"
    echo -e "[!] 请确保文件包含IP地址或域名（非注释行）"
    exit 1
fi

echo -e "[📊] 发现有效目标: ${GREEN}$TOTAL_TARGETS${NC} 个"

# 扫描配置
case $SCAN_TYPE in
    fast)
        SCAN_ARGS="-T4 -F"
        SCAN_NAME="快速扫描"
        ;;
    full)
        SCAN_ARGS="-p- -T4"
        SCAN_NAME="完整端口扫描"
        echo -e "${YELLOW}[⚠] 警告: 完整扫描可能需要很长时间${NC}"
        ;;
    web)
        SCAN_ARGS="-p 80,443,8080,8443,3000,5000,8000,8008,8081,8090 -T4"
        SCAN_NAME="Web服务扫描"
        ;;
    service)
        SCAN_ARGS="-T4 -sV -F"
        SCAN_NAME="服务版本扫描"
        ;;
    *)
        echo -e "${RED}[✗] 错误: 未知扫描类型: $SCAN_TYPE${NC}"
        echo -e "[!] 可用类型: fast, full, web, service"
        exit 1
        ;;
esac

echo -e "[⚙️] 扫描配置: ${GREEN}$SCAN_NAME${NC}"
echo -e "[⚙️] 扫描参数: ${GREEN}nmap $SCAN_ARGS${NC}"

# 创建摘要文件
SUMMARY_FILE="$OUTPUT_DIR/scan_summary_${TIMESTAMP}.txt"
echo "Nmap批量扫描摘要报告" > $SUMMARY_FILE
echo "========================================" >> $SUMMARY_FILE
echo "扫描时间: $(date)" >> $SUMMARY_FILE
echo "目标文件: $TARGETS_FILE" >> $SUMMARY_FILE
echo "扫描类型: $SCAN_TYPE ($SCAN_NAME)" >> $SUMMARY_FILE
echo "扫描参数: nmap $SCAN_ARGS" >> $SUMMARY_FILE
echo "目标总数: $TOTAL_TARGETS" >> $SUMMARY_FILE
echo "========================================" >> $SUMMARY_FILE

# 创建进度日志
PROGRESS_LOG="$OUTPUT_DIR/logs/progress.log"
echo "批量扫描进度日志 - $(date)" > $PROGRESS_LOG

# 创建CSV摘要
CSV_SUMMARY="$OUTPUT_DIR/summary_${TIMESTAMP}.csv"
echo "目标,状态,开放端口,发现服务,扫描时间,结果文件" > $CSV_SUMMARY

CURRENT=0
SUCCESS=0
FAILED=0

echo -e "[⏳] 开始批量扫描..."
echo -e "${CYAN}========================================${NC}"

# 读取目标文件
while IFS= read -r TARGET || [ -n "$TARGET" ]; do
    # 跳过空行和注释
    if [[ -z "$TARGET" ]] || [[ "$TARGET" =~ ^# ]]; then
        continue
    fi
    
    CURRENT=$((CURRENT+1))
    
    # 清理目标名称用于文件名
    SAFE_TARGET=$(echo "$TARGET" | tr -cd '[:alnum:]._-')
    JSON_FILE="$OUTPUT_DIR/json/scan_${SAFE_TARGET}.json"
    LOG_FILE="$OUTPUT_DIR/logs/scan_${SAFE_TARGET}.log"
    
    echo -e "[$CURRENT/$TOTAL_TARGETS] ${BLUE}扫描目标:${NC} ${GREEN}$TARGET${NC}"
    echo "========================================"
    
    # 记录开始时间
    START_TIME=$(date +%s)
    
    # 执行扫描并记录日志
    echo "开始时间: $(date)" > $LOG_FILE
    echo "目标: $TARGET" >> $LOG_FILE
    echo "扫描参数: nmap $SCAN_ARGS -oJ $JSON_FILE" >> $LOG_FILE
    echo "========================================" >> $LOG_FILE
    
    # 执行扫描
    echo -e "[.] 执行扫描..."
    nmap $SCAN_ARGS -oJ "$JSON_FILE" "$TARGET" >> $LOG_FILE 2>&1
    SCAN_RESULT=$?
    
    # 记录结束时间
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # 更新日志
    echo "========================================" >> $LOG_FILE
    echo "结束时间: $(date)" >> $LOG_FILE
    echo "耗时: ${DURATION}秒" >> $LOG_FILE
    echo "退出代码: $SCAN_RESULT" >> $LOG_FILE
    
    # 处理扫描结果
    if [ $SCAN_RESULT -eq 0 ] && [ -f "$JSON_FILE" ] && [ -s "$JSON_FILE" ]; then
        echo -e "${GREEN}[✓] 扫描成功 (${DURATION}秒)${NC}"
        echo "[📁] 结果文件: $JSON_FILE"
        
        SUCCESS=$((SUCCESS+1))
        STATUS="成功"
        
        # 提取扫描结果信息
        if command -v jq &>/dev/null; then
            # 使用jq提取信息
            OPEN_PORTS=$(jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "open") | .portid' "$JSON_FILE" 2>/dev/null | wc -l)
            SERVICES=$(jq -r '.nmaprun.host.ports.port[]? | select(.service.product) | .service.product' "$JSON_FILE" 2>/dev/null | wc -l)
            HOST_STATE=$(jq -r '.nmaprun.host.status.state // "unknown"' "$JSON_FILE" 2>/dev/null)
        else
            # 使用grep简单提取
            OPEN_PORTS=$(grep -c '"state":"open"' "$JSON_FILE" 2>/dev/null || echo "0")
            SERVICES=$(grep -c '"service"' "$JSON_FILE" 2>/dev/null || echo "0")
            HOST_STATE="unknown"
        fi
        
        echo -e "[📊] 发现: ${OPEN_PORTS}个开放端口, ${SERVICES}个服务"
        
        # 生成简单报告
        REPORT_FILE="$OUTPUT_DIR/reports/report_${SAFE_TARGET}.txt"
        cat > $REPORT_FILE << EOF
========================================
扫描报告: $TARGET
========================================
扫描时间: $(date)
扫描类型: $SCAN_NAME
扫描参数: nmap $SCAN_ARGS

结果摘要:
- 主机状态: $HOST_STATE
- 开放端口: $OPEN_PORTS 个
- 识别服务: $SERVICES 个

文件位置:
- JSON数据: $JSON_FILE
- 扫描日志: $LOG_FILE
- 本报告: $REPORT_FILE

开放端口详情:
EOF
        
        # 添加端口详情
        if [ $OPEN_PORTS -gt 0 ]; then
            if command -v jq &>/dev/null; then
                jq -r '.nmaprun.host.ports.port[]? | select(.state.state == "open") | "  \(.protocol)/\(.portid) - \(.service.name // "unknown") (\(.service.product // ""))"' "$JSON_FILE" 2>/dev/null >> $REPORT_FILE
            else
                grep -A3 '"state":"open"' "$JSON_FILE" | grep '"portid"' | sed 's/.*"\([0-9]*\)".*/  \1/' 2>/dev/null >> $REPORT_FILE
            fi
        fi
        
        echo "========================================" >> $REPORT_FILE
        
        # 添加到CSV摘要
        echo "\"$TARGET\",\"$STATUS\",\"$OPEN_PORTS\",\"$SERVICES\",\"${DURATION}秒\",\"$JSON_FILE\"" >> $CSV_SUMMARY
        
    else
        echo -e "${RED}[✗] 扫描失败 (${DURATION}秒)${NC}"
        echo "[!] 退出代码: $SCAN_RESULT"
        
        FAILED=$((FAILED+1))
        STATUS="失败"
        
        # 添加到CSV摘要
        echo "\"$TARGET\",\"$STATUS\",\"0\",\"0\",\"${DURATION}秒\",\"$LOG_FILE\"" >> $CSV_SUMMARY
        
        # 记录失败原因
        if [ $SCAN_RESULT -eq 1 ]; then
            FAIL_REASON="一般错误"
        elif [ $SCAN_RESULT -eq 2 ]; then
            FAIL_REASON="无效参数"
        elif [ $SCAN_RESULT -eq 3 ]; then
            FAIL_REASON="网络错误"
        elif [ $SCAN_RESULT -eq 4 ]; then
            FAIL_REASON="权限不足"
        else
            FAIL_REASON="未知错误"
        fi
        
        echo "[!] 失败原因: $FAIL_REASON"
    fi
    
    # 更新进度日志
    echo "[$(date)] 目标 $CURRENT/$TOTAL_TARGETS: $TARGET - $STATUS (${DURATION}秒)" >> $PROGRESS_LOG
    
    # 进度间隔，避免过快扫描
    if [ $CURRENT -lt $TOTAL_TARGETS ]; then
        echo -e "[⏱️] 等待2秒继续下一个目标..."
        sleep 2
    fi
    
    echo ""
    
done < "$TARGETS_FILE"

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}[✅] 批量扫描完成！${NC}"
echo -e "${CYAN}========================================${NC}"

# 更新摘要文件
echo "" >> $SUMMARY_FILE
echo "扫描统计:" >> $SUMMARY_FILE
echo "  总目标数: $TOTAL_TARGETS" >> $SUMMARY_FILE
echo "  成功扫描: $SUCCESS" >> $SUMMARY_FILE
echo "  失败扫描: $FAILED" >> $SUMMARY_FILE
echo "  成功率: $((SUCCESS * 100 / TOTAL_TARGETS))%" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "输出目录结构:" >> $SUMMARY_FILE
echo "  $OUTPUT_DIR/" >> $SUMMARY_FILE
echo "    ├── json/          # JSON格式扫描结果" >> $SUMMARY_FILE
echo "    ├── reports/       # 文本格式报告" >> $SUMMARY_FILE
echo "    ├── logs/          # 扫描过程日志" >> $SUMMARY_FILE
echo "    ├── scan_summary_${TIMESTAMP}.txt" >> $SUMMARY_FILE
echo "    └── summary_${TIMESTAMP}.csv" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "扫描时间: $(date)" >> $SUMMARY_FILE
echo "总耗时: 约$((END_TIME - $(date +%s) + DURATION))秒" >> $SUMMARY_FILE
echo "========================================" >> $SUMMARY_FILE

# 显示最终统计
echo -e "[📊] ${CYAN}扫描统计:${NC}"
echo -e "   总目标数: ${GREEN}$TOTAL_TARGETS${NC}"
echo -e "   成功扫描: ${GREEN}$SUCCESS${NC}"
echo -e "   失败扫描: ${RED}$FAILED${NC}"
echo -e "   成功率: ${GREEN}$((SUCCESS * 100 / TOTAL_TARGETS))%${NC}"

# 显示目录结构
echo -e ""
echo -e "[📁] ${CYAN}输出目录结构:${NC}"
echo -e "   ${OUTPUT_DIR}/"
echo -e "   ├── ${GREEN}json/${NC}          # JSON格式扫描结果"
echo -e "   ├── ${GREEN}reports/${NC}       # 文本格式报告"
echo -e "   ├── ${GREEN}logs/${NC}          # 扫描过程日志"
echo -e "   ├── ${GREEN}scan_summary_${TIMESTAMP}.txt${NC}"
echo -e "   └── ${GREEN}summary_${TIMESTAMP}.csv${NC}"

# 提供使用建议
echo -e ""
echo -e "[💡] ${CYAN}使用建议:${NC}"
echo -e "   1. 查看摘要报告: ${SUMMARY_FILE}"
echo -e "   2. 查看详细结果: ${OUTPUT_DIR}/json/"
echo -e "   3. 分析失败原因: ${OUTPUT_DIR}/logs/"
echo -e "   4. 使用jq分析JSON: jq . ${OUTPUT_DIR}/json/*.json"

# 如果有失败，显示失败目标
if [ $FAILED -gt 0 ]; then
    echo -e ""
    echo -e "${YELLOW}[⚠] 失败目标列表:${NC}"
    grep -B1 "失败" $PROGRESS_LOG | grep "目标" | sed 's/.*目标 //'
    echo -e "${YELLOW}[💡] 建议:${NC}"
    echo -e "   检查网络连接"
    echo -e "   验证目标是否可达"
    echo -e "   使用更简单的扫描参数重试"
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}[🎉] 批量扫描任务完成！${NC}"
echo -e "${CYAN}========================================${NC}"

exit 0