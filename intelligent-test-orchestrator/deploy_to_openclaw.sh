#!/bin/bash

# ==========================================
# OpenClaw 集成部署脚本
# ==========================================

set -e

echo ""
echo "╔==========================================================╗"
echo "║           OpenClaw 集成部署脚本                  ║"
echo "╚==========================================================╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SKILL_NAME="intelligent-test-orchestrator"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
SKILLS_DIR="$OPENCLAW_DIR/skills"

echo "项目目录：$PROJECT_DIR"
echo "OpenClaw 目录：$OPENCLAW_DIR"
echo "技能目录：$SKILLS_DIR"
echo ""

# 步骤 1: 检查 OpenClaw
echo "============================================================"
echo "步骤 1: 检查 OpenClaw 安装"
echo "============================================================"

if [ ! -d "$OPENCLAW_DIR" ]; then
    echo -e "${RED}❌ OpenClaw 未安装${NC}"
    echo ""
    echo "请先安装 OpenClaw:"
    echo "  pip3 install openclaw"
    exit 1
fi

echo -e "${GREEN}✅ OpenClaw 已安装${NC}"
echo ""

# 步骤 2: 创建技能目录
echo "============================================================"
echo "步骤 2: 创建技能目录"
echo "============================================================"

if [ ! -d "$SKILLS_DIR" ]; then
    echo "创建技能目录..."
    mkdir -p "$SKILLS_DIR"
fi

echo -e "${GREEN}✅ 技能目录已准备${NC}"
echo ""

# 步骤 3: 复制 Skill 文件
echo "============================================================"
echo "步骤 3: 复制 Skill 文件"
echo "============================================================"

TARGET_DIR="$SKILLS_DIR/$SKILL_NAME"

echo "目标目录：$TARGET_DIR"
echo ""

# 删除旧版本
if [ -d "$TARGET_DIR" ]; then
    echo "删除旧版本..."
    rm -rf "$TARGET_DIR"
fi

# 创建新目录
mkdir -p "$TARGET_DIR"

# 复制文件
echo "复制 Skill 文件..."
cp -r "$PROJECT_DIR"/* "$TARGET_DIR/"

# 验证文件
echo ""
echo "验证文件..."
required_files=("manifest.json" "main.py" "core" "adapters")
for file in "${required_files[@]}"; do
    if [ -e "$TARGET_DIR/$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (缺失)"
    fi
done

echo ""
echo -e "${GREEN}✅ Skill 文件已复制${NC}"
echo ""

# 步骤 4: 验证 manifest.json
echo "============================================================"
echo "步骤 4: 验证 manifest.json"
echo "============================================================"

if python3 -m json.tool "$TARGET_DIR/manifest.json" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ manifest.json 格式正确${NC}"
else
    echo -e "${RED}❌ manifest.json 格式错误${NC}"
    exit 1
fi

echo ""

# 步骤 5: 注册技能
echo "============================================================"
echo "步骤 5: 注册技能"
echo "============================================================"

# 检查 OpenClaw 配置
OPENCLAW_CONFIG="$OPENCLAW_DIR/config.json"

if [ ! -f "$OPENCLAW_CONFIG" ]; then
    echo "创建 OpenClaw 配置..."
    cat > "$OPENCLAW_CONFIG" << EOF
{
    "skills": [
        {
            "name": "$SKILL_NAME",
            "path": "$TARGET_DIR",
            "enabled": true,
            "priority": 1
        }
    ],
    "log_level": "INFO",
    "enable_caching": true
}
EOF
    echo -e "${GREEN}✅ OpenClaw 配置已创建${NC}"
else
    echo "OpenClaw 配置已存在"
    
    # 检查技能是否已注册
    if grep -q "$SKILL_NAME" "$OPENCLAW_CONFIG"; then
        echo -e "${GREEN}✅ 技能已注册${NC}"
    else
        echo "添加技能到配置..."
        # 这里可以添加 JSON 修改逻辑
        echo -e "${YELLOW}⚠️  请手动添加技能到 $OPENCLAW_CONFIG${NC}"
    fi
fi

echo ""

# 步骤 6: 重启 OpenClaw
echo "============================================================"
echo "步骤 6: 重启 OpenClaw"
echo "============================================================"

echo "重启 OpenClaw 服务..."
echo ""
echo "请执行以下命令重启 OpenClaw:"
echo "  openclaw restart"
echo ""
echo "或者手动重启:"
echo "  pkill -f openclaw"
echo "  openclaw start"
echo ""

# 步骤 7: 验证部署
echo "============================================================"
echo "步骤 7: 验证部署"
echo "============================================================"

echo "验证技能列表..."
echo ""
echo "请执行以下命令验证:"
echo "  openclaw skills list"
echo ""
echo "应该看到 $SKILL_NAME 在列表中"
echo ""

# 步骤 8: 测试调用
echo "============================================================"
echo "步骤 8: 测试调用"
echo "============================================================"

echo "测试技能调用..."
echo ""
echo "请执行以下命令测试:"
echo "  cd $TARGET_DIR"
echo "  python3 main.py '{\"target\": \"http://demo.testfire.net\", \"test_mode\": \"full\"}'"
echo ""

# 完成
echo "============================================================"
echo "部署完成！"
echo "============================================================"
echo ""
echo -e "${GREEN}╔==========================================================╗${NC}"
echo -e "${GREEN}║              ✅ Skill 部署成功！               ║${NC}"
echo -e "${GREEN}╚==========================================================╝${NC}"
echo ""
echo "下一步:"
echo "  1. 重启 OpenClaw: openclaw restart"
echo "  2. 验证技能：openclaw skills list"
echo "  3. 测试调用：python3 main.py '{\"target\": \"http://demo.testfire.net\"}'"
echo "  4. 开始使用：对 OpenClaw 说 '帮我测试 http://demo.testfire.net'"
echo ""
echo "技能位置：$TARGET_DIR"
echo "配置文件：$OPENCLAW_CONFIG"
echo ""
