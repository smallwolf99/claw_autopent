# security-report-converter Skill 快速指南

## 安装依赖

### 自动安装（推荐）
```bash
python main.py --install-deps
```

### 手动安装
```bash
pip install markdown jinja2 weasyprint pyyaml
```

### 系统依赖（PDF 生成需要）
```bash
# Windows: 无需额外安装
# Linux:
sudo apt-get install fonts-noto-cjk

# macOS:
brew install pango
```

---

## 基本使用

### 转换单个 Markdown 文件（生成 HTML+PDF）
```bash
python main.py -i report.md -o report
```

### 仅生成 HTML
```bash
python main.py -i report.md -o report --format html
```

### 仅生成 PDF
```bash
python main.py -i report.md -o report --format pdf
```

### 指定模板
```bash
python main.py -i report.md -o report --template professional
```

### 自定义标题和作者
```bash
python main.py -i report.md -o report --title "渗透测试报告" --author "安全团队"
```

### 指定输出目录
```bash
python main.py -i report.md -o /path/to/output/report
```

### 指定报告日期
```bash
python main.py -i report.md -o report --date "2024-01-01"
```

### 调试模式
```bash
python main.py -i report.md -o report --debug
```

---

## 参数说明

| 参数 | 简写 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--input` | `-i` | ✅ | - | 输入 Markdown 文件路径 |
| `--output` | `-o` | ✅ | - | 输出文件前缀（不含扩展名） |
| `--format` | `-f` | ❌ | `all` | 输出格式：`html`, `pdf`, `all` |
| `--template` | `-t` | ❌ | `professional` | 模板类型：`professional`, `simple`, `executive` |
| `--title` | | ❌ | 从文件提取 | 报告标题 |
| `--author` | | ❌ | "安全团队" | 报告作者 |
| `--date` | | ❌ | 当前日期 | 报告日期 |
| `--config` | | ❌ | 自动查找 | 配置文件路径 |
| `--install-deps` | | ❌ | - | 自动安装依赖 |
| `--debug` | | ❌ | False | 启用调试模式 |

---

## 模板系统

### 内置模板

1. **professional** (默认) - 专业安全团队报告
   - 风险等级彩色标识
   - 详细技术细节表格
   - 修复建议代码块

2. **simple** - 简洁易读报告
   - 简约设计，突出重点
   - 适合非技术人员阅读

3. **executive** - 高管摘要报告
   - 业务影响分析
   - 风险量化指标
   - 修复成本估算

### 自定义模板

在 `templates/` 目录中添加自己的 HTML 模板：
- `template_{name}.html` - HTML 模板
- `style_{name}.css` - CSS 样式文件

---

## 程序化调用

```python
from main import scan

# 基础转换
result = scan(
    input_file="report.md",
    output_prefix="security_report",
    output_format="all",
    template_name="professional"
)

if result["status"] in ("success", "partial_success"):
    print(f"报告生成成功")
    print(f"  标题：{result['title']}")
    print(f"  输出文件：{result['output_files']}")
else:
    print(f"报告生成失败：{result['errors']}")

# 自定义参数
result = scan(
    input_file="zap_report.md",
    output_prefix="/tmp/reports/zap",
    output_format="html",
    template_name="simple",
    title="ZAP 扫描报告",
    author="安全测试团队",
    report_date="2024-01-01"
)
```

---

## 运行测试

```bash
python tests/test_report_converter_skill.py
```

---

## 输入文件格式

### 推荐 Markdown 结构

```markdown
# 渗透测试报告

## 执行摘要

本次渗透测试发现 3 个高风险漏洞、5 个中风险漏洞。

## 风险统计

| 风险等级 | 数量 | 说明 |
|----------|------|------|
| 🔴 高风险 | 3 | SQL 注入、命令执行 |
| 🟡 中风险 | 5 | XSS、CSRF |
| 🟢 低风险 | 10 | 信息泄露 |

## 详细漏洞

### SQL 注入漏洞

**风险等级**: 🔴 高

**描述**: 登录页面存在 SQL 注入漏洞

**修复建议**:
```python
# 使用参数化查询
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

### XSS 跨站脚本

**风险等级**: 🟡 中

**描述**: 搜索框存在反射型 XSS

**修复建议**:
- 添加输入验证
- 输出编码
- 设置 Content-Security-Policy
```

---

## 输出文件

转换后生成的文件：

```
security_report.html      # HTML 网页报告
security_report.pdf       # PDF 打印报告
```

---

## 常见用例

### 用例 1：ZAP 扫描报告转换

```bash
python main.py -i zap_summary.md -o zap_security_report
```

### 用例 2：Nuclei 扫描报告转换

```bash
python main.py -i nuclei_report.md -o nuclei_report --template simple
```

### 用例 3：综合渗透测试报告

```bash
python main.py -i pentest_report.md -o final_report --template professional --title "2024 年度渗透测试报告"
```

### 用例 4：批量转换多个报告

```bash
for file in reports/*.md; do
    python main.py -i "$file" -o "output/$(basename "$file" .md)"
done
```

---

## 注意事项

1. **字体支持** - PDF 生成需要中文字体，确保系统已安装
   - Windows: 默认已安装
   - Linux: `sudo apt-get install fonts-noto-cjk`
   - macOS: `brew install pango`

2. **图片路径** - Markdown 中的图片需使用绝对路径或相对路径

3. **文件大小** - 大报告可能需要更多内存

4. **特殊字符** - 确保 Markdown 使用 UTF-8 编码

5. **依赖安装** - 首次使用建议运行 `--install-deps` 自动安装依赖

---

## 故障排查

### 问题 1：PDF 生成失败
```bash
# 安装中文字体
sudo apt-get install fonts-noto-cjk

# 或使用简单模板（不需要 PDF）
python main.py -i report.md -o report --format html
```

### 问题 2：模板找不到
```bash
# 检查模板目录
ls templates/

# 或使用内置模板
python main.py -i report.md -o report --template simple
```

### 问题 3：依赖缺失
```bash
# 自动安装
python main.py --install-deps

# 或手动安装
pip install markdown jinja2 weasyprint pyyaml
```

### 问题 4：中文乱码
```bash
# 确保 Markdown 文件使用 UTF-8 编码
# 在编辑器中另存为 UTF-8 格式
```
