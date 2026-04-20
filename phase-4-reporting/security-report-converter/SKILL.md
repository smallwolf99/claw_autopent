# 安全报告转换器 Skill

将安全扫描报告（Markdown格式）转换为 **PDF** 和 **HTML** 专业格式报告。

## ✨ 功能特性

- 📄 **Markdown → HTML** - 生成美观的HTML网页报告
- 📊 **Markdown → PDF** - 生成可打印的PDF专业报告
- 🎨 **专业模板** - 使用企业级安全报告模板
- ⚡ **一键转换** - 简单命令行接口
- 🔄 **批量处理** - 支持多个报告文件转换

## 🚀 快速开始

### 1. 安装依赖（仅首次使用）

```bash
# 进入skill目录
cd /home/ubuntu/.openclaw/workspace/skills/security-report-converter

# 安装Python依赖
pip3 install -r requirements.txt
```

### 2. 基本使用

```bash
# 转换单个Markdown文件
python3 scripts/convert_report.py -i report.md -o report

# 指定输出目录
python3 scripts/convert_report.py -i report.md -o /path/to/output/report

# 仅生成HTML
python3 scripts/convert_report.py -i report.md -o report --format html

# 仅生成PDF  
python3 scripts/convert_report.py -i report.md -o report --format pdf

# 指定模板
python3 scripts/convert_report.py -i report.md -o report --template professional
```

### 3. 在OpenClaw中使用

```bash
# 执行扫描后，自动生成多格式报告
python3 scripts/convert_report.py -i zap_summary.md -o security_report
```

## 📋 参数说明

| 参数 | 简写 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--input` | `-i` | ✅ | - | 输入Markdown文件路径 |
| `--output` | `-o` | ✅ | - | 输出文件前缀（不含扩展名） |
| `--format` | `-f` | ❌ | `all` | 输出格式：`html`, `pdf`, `all` |
| `--template` | `-t` | ❌ | `professional` | 模板类型：`professional`, `simple`, `executive` |
| `--title` | | ❌ | 从文件提取 | 报告标题 |
| `--author` | | ❌ | "安全团队" | 报告作者 |
| `--date` | | ❌ | 当前日期 | 报告日期 |

## 🎨 模板系统

### 内置模板

1. **professional** (默认) - 专业安全团队报告
   - 风险等级彩色标识（🔴🟡🟢）
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
在 `templates/` 目录中添加自己的HTML模板：
- `template_{name}.html` - HTML模板
- `style_{name}.css` - CSS样式文件

## 📁 输入文件格式要求

输入Markdown文件应包含标准Markdown语法，支持：

- 标题（#, ##, ###）
- 表格（| 列1 | 列2 |）
- 代码块（```）
- 列表（*, -, 1.）
- 链接和图片
- 风险等级表情符号（🔴, 🟡, 🟢）

**推荐结构**：
```
# 扫描报告标题

## 执行摘要
...

## 风险统计
| 风险等级 | 数量 | 说明 |
|----------|------|------|
| 🔴 高风险 | 10 | SQL注入 |

## 详细漏洞
...
```

## 🔧 技术实现

### 转换流程
1. **解析Markdown** - 使用Python-Markdown库
2. **应用模板** - 将内容注入HTML模板
3. **生成HTML** - 输出完整HTML文件
4. **生成PDF** - 使用WeasyPrint渲染PDF

### 依赖库
- `markdown` - Markdown解析
- `weasyprint` - HTML转PDF
- `jinja2` - 模板引擎
- `PyYAML` - 配置文件解析

## 📊 输出文件

转换后生成的文件：

```
security_report.html      # HTML网页报告
security_report.pdf       # PDF打印报告
security_report/          # 资源目录（可选）
├── images/              # 嵌入图片
└── styles/              # CSS样式文件
```

## ⚠️ 注意事项

1. **字体支持** - PDF生成需要中文字体，确保系统已安装
2. **图片路径** - Markdown中的图片需使用绝对路径或相对路径
3. **文件大小** - 大报告可能需要更多内存
4. **特殊字符** - 确保Markdown使用UTF-8编码

## 🔍 示例用例

### 示例1：ZAP扫描报告转换

```bash
# 从coder任务目录获取报告
python3 scripts/convert_report.py \
  -i /home/ubuntu/.openclaw/workspace-coder/tasks/2026-04-15__001__zap-cli_demo-testfire/deliverables/zap_summary.md \
  -o /tmp/zap_security_report
```

### 示例2：集成到扫描脚本

```python
import subprocess

# 扫描完成后自动生成多格式报告
subprocess.run([
    "python3", "scripts/convert_report.py",
    "-i", "scan_results.md",
    "-o", "security_report",
    "--format", "all",
    "--template", "professional"
])
```

## 🛠️ 故障排除

### 常见问题

**Q: PDF生成失败，提示缺少字体**
```
A: 安装中文字体
sudo apt-get install fonts-noto-cjk
```

**Q: HTML显示乱码**
```
A: 确保输入文件是UTF-8编码
file -i report.md  # 检查编码
```

**Q: 模板找不到**
```
A: 检查templates目录结构
ls templates/      # 应包含template_professional.html等
```

**Q: 缺少依赖库**
```
A: 重新安装requirements
pip3 install -r requirements.txt --upgrade
```

### 调试模式

```bash
# 启用详细日志
python3 scripts/convert_report.py -i report.md -o output --debug
```

## 📈 高级功能

### 自定义CSS样式
在 `templates/custom.css` 中添加自定义样式：

```css
/* 自定义风险等级颜色 */
.risk-high { color: #d32f2f; }
.risk-medium { color: #f57c00; }
.risk-low { color: #388e3c; }
```

### 批量处理
```bash
# 批量转换多个报告
python3 scripts/batch_convert.py reports/*.md
```

### API调用
```python
from report_converter import convert_report

# 程序化调用
result = convert_report(
    input_file="report.md",
    output_prefix="output",
    format="all",
    template="professional"
)
```

## 🔄 更新日志

### v1.0.0 (2026-04-15)
- ✅ 基础Markdown到HTML/PDF转换
- ✅ 三种内置模板
- ✅ 命令行接口
- ✅ 错误处理和日志

## 📝 许可证

MIT License - 详见LICENSE文件

---

**技能维护**：高级安全渗透测试专家团队  
**适用场景**：安全扫描报告、渗透测试报告、合规审计报告  
**输出格式**：HTML (网页查看)、PDF (打印存档)