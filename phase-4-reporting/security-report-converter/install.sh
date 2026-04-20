#!/bin/bash
# 安全报告转换器安装脚本

set -e

echo "🔄 安装安全报告转换器..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查是否已安装pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请先安装pip3"
    exit 1
fi

# 安装系统依赖（针对WeasyPrint）
echo "📦 安装系统依赖..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y \
        python3-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info \
        fonts-noto-cjk
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y \
        python3-devel \
        cairo \
        cairo-devel \
        pango \
        pango-devel \
        libffi-devel \
        gdk-pixbuf2 \
        liberation-fonts
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf install -y \
        python3-devel \
        cairo \
        cairo-devel \
        pango \
        pango-devel \
        libffi-devel \
        gdk-pixbuf2 \
        google-noto-cjk-fonts
else
    echo "⚠️  无法识别包管理器，请手动安装系统依赖"
fi

# 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 设置可执行权限
echo "🔧 设置脚本权限..."
chmod +x scripts/convert_report.py

# 创建示例报告
echo "📄 创建示例..."
if [ ! -d "examples" ]; then
    mkdir examples
    cat > examples/sample_report.md << 'EOF'
# 📊 安全扫描示例报告

**扫描目标**: example.com  
**扫描时间**: $(date +%Y-%m-%d)  
**扫描工具**: OWASP ZAP

## 风险统计

| 风险等级 | 数量 | 说明 |
|----------|------|------|
| 🔴 高风险 | 2 | SQL注入、XSS |
| 🟡 中风险 | 5 | CSP缺失、CSRF令牌缺失 |
| 🟢 低风险 | 8 | Cookie安全、服务器版本泄露 |
| ℹ️ 信息类 | 12 | 技术栈信息、会话管理 |

## 关键发现

### SQL注入漏洞
在登录接口发现SQL注入漏洞，攻击载荷: `admin' OR '1'='1`

### 反射型XSS
搜索页面存在反射型XSS，可窃取用户会话Cookie

## 建议

1. 立即修复SQL注入漏洞
2. 实施输入验证和输出编码
3. 部署安全响应头
EOF
fi

# 测试安装
echo "🧪 测试安装..."
if python3 scripts/convert_report.py --help &> /dev/null; then
    echo "✅ 安装成功!"
    
    # 生成示例报告
    echo "📊 生成示例报告..."
    python3 scripts/convert_report.py -i examples/sample_report.md -o examples/sample_report --format all
    
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "使用方法:"
    echo "  python3 scripts/convert_report.py -i report.md -o output_name"
    echo ""
    echo "示例文件:"
    echo "  examples/sample_report.md   # 示例Markdown报告"
    echo "  examples/sample_report.html # 生成的HTML报告"
    echo "  examples/sample_report.pdf  # 生成的PDF报告"
else
    echo "❌ 安装测试失败，请检查错误信息"
    exit 1
fi