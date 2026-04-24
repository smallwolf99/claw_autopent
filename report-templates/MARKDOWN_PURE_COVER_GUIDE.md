# 纯 Markdown 封面方案

## 📋 方案说明

使用**纯 Markdown 语法**编写封面，优势：

### ✅ 优势
1. **纯 Markdown**：完全使用 Markdown 语法，无 HTML 标签
2. **简洁易读**：源文件保持 Markdown 的可读性
3. **CSS 美化**：通过 CSS 在转换时添加样式
4. **工具友好**：所有 Markdown 工具都能正常处理
5. **易于维护**：只需维护 Markdown 和 CSS 两个文件

## 📄 文件结构

```
report-templates/
├── markdown-cover-template.md    # Markdown 封面模板
├── markdown-cover-styles.css     # 封面样式文件
└── MARKDOWN_PURE_COVER_GUIDE.md  # 本指南
```

## 🎨 封面设计

### 封面内容（Markdown 语法）

```markdown
# 安全渗透测试报告

## Security Penetration Testing Report

---

### 📋 报告信息

| 项目 | 内容 |
|------|------|
| **目标系统** | {{ report.target_name }} |
| **目标 URL** | {{ report.target_url }} |
| **测试时间** | {{ report.test_time }} |
| **测试人员** | 安小易 (安全测试数字员工) |
| **风险等级** | **{{ report.risk_level }}** |

---

> **机密文件 · 授权访问 · 严禁外传**
> 
> CONFIDENTIAL - AUTHORIZED PERSONNEL ONLY
```

### CSS 样式美化

通过 CSS 添加：
- ✅ 渐变背景
- ✅ 毛玻璃效果表格
- ✅ 阴影效果
- ✅ 颜色和字体
- ✅ 分页控制

## 🚀 使用方法

### 方法 1：使用 Pandoc + CSS

```bash
pandoc report-templates/markdown-cover-template.md \
  -o report.pdf \
  --css report-templates/markdown-cover-styles.css \
  --pdf-engine=wkhtmltopdf \
  --variable paper-size=a4 \
  --variable margin-top=0mm \
  --variable margin-bottom=0mm \
  --variable margin-left=0mm \
  --variable margin-right=0mm
```

### 方法 2：Python 脚本处理

```python
from pathlib import Path
import subprocess

def render_markdown_cover(template_path, css_path, output_path, context):
    """渲染纯 Markdown 封面报告"""
    
    # 读取模板
    template = Path(template_path).read_text(encoding='utf-8')
    
    # 替换变量
    for key, value in context.items():
        template = template.replace(f'{{{{ {key} }}}}', str(value))
    
    # 保存临时文件
    temp_file = Path(output_path)
    temp_file.write_text(template, encoding='utf-8')
    
    # 转换为 PDF
    subprocess.run([
        'pandoc',
        str(temp_file),
        '-o', str(temp_file.with_suffix('.pdf')),
        '--css', str(css_path),
        '--pdf-engine=wkhtmltopdf',
        '--variable', 'paper-size=a4',
        '--variable', 'margin-top=0mm',
        '--variable', 'margin-bottom=0mm',
        '--variable', 'margin-left=0mm',
        '--variable', 'margin-right=0mm'
    ], check=True)
    
    return temp_file.with_suffix('.pdf')

# 使用示例
context = {
    'report.target_name': 'DVWA 系统',
    'report.target_url': 'http://dvwa.example.com',
    'report.target_ip': '192.168.1.100',
    'report.target_port': '80',
    'report.test_time': '2026-04-23 10:00:00',
    'report.report_date': '2026-04-23',
    'report.overall_risk': '极度危险',
    'report.risk_level': '危急',
    'report.total_vulnerabilities': '18',
    'report.high_count': '12',
    'report.medium_count': '2',
    'report.low_count': '3',
    'report.info_count': '4'
}

render_markdown_cover(
    'report-templates/markdown-cover-template.md',
    'report-templates/markdown-cover-styles.css',
    'reports/test-report.md',
    context
)
```

## 🎨 CSS 样式说明

### 封面背景
```css
.cover-page {
    background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 50%, #ede7f6 100%);
    padding: 40mm 20mm;
    min-height: 297mm;
    page-break-after: always;
}
```

### 标题样式
```css
.cover-page h1 {
    font-size: 3em;
    font-weight: bold;
    text-align: center;
    color: #1a2332;
    margin-top: 80px;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(26, 35, 50, 0.3);
}
```

### 信息表格（毛玻璃效果）
```css
.cover-page table {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(26, 35, 50, 0.2);
    border-radius: 12px;
    padding: 30px;
    margin: 40px auto;
    box-shadow: 0 2px 8px rgba(26, 35, 50, 0.04);
    width: 80%;
}
```

### 机密警告（红色引用块）
```css
.cover-page blockquote {
    background: rgba(211, 47, 47, 0.1);
    border-left: 4px solid #d32f2f;
    color: #d32f2f;
    font-weight: 700;
    text-align: center;
    padding: 20px;
    margin: 60px auto;
}
```

## 📊 分页控制

### 强制封面独立一页
```css
.cover-page {
    page-break-after: always;
}
```

### 避免内容分离
```css
h1, h2, h3 {
    page-break-after: avoid;
}

table, pre, code {
    page-break-inside: avoid;
}
```

## 🔧 自定义选项

### 修改背景颜色

**更蓝的色调：**
```css
.cover-page {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #e1f5fe 100%);
}
```

**更紫的色调：**
```css
.cover-page {
    background: linear-gradient(135deg, #ede7f6 0%, #e8eaf6 50%, #f3e5f5 100%);
}
```

**更浅的色调：**
```css
.cover-page {
    background: linear-gradient(135deg, #f5f7fa 0%, #f0f4f8 50%, #f9fafb 100%);
}
```

### 修改表格样式

**更深的阴影：**
```css
.cover-page table {
    box-shadow: 0 4px 12px rgba(26, 35, 50, 0.1);
}
```

**无毛玻璃效果：**
```css
.cover-page table {
    background: white;
    backdrop-filter: none;
}
```

## 📝 Markdown 语法对照

| 效果 | Markdown 语法 | CSS 类名 |
|------|--------------|----------|
| 主标题 | `# 标题` | `.cover-page h1` |
| 副标题 | `## 副标题` | `.cover-page h2` |
| 表格 | `\| 列 1 \| 列 2 \|` | `.cover-page table` |
| 引用块 | `> 文字` | `.cover-page blockquote` |
| 粗体 | `**文字**` | - |
| 分隔线 | `---` | - |

## ✅ 验证清单

- [x] 纯 Markdown 语法编写封面
- [x] 使用表格展示信息
- [x] 使用引用块显示警告
- [x] 使用分隔线划分区域
- [x] CSS 文件独立
- [x] 支持 Pandoc 转换
- [x] 分页控制正确
- [x] 打印友好

## 📊 示例效果

### 封面结构
```
# 安全渗透测试报告          ← 大标题（居中，藏青色，阴影）
## Security Penetration...  ← 副标题（居中，淡紫色）
---                         ← 分隔线
### 📋 报告信息             ← 小标题
| 项目 | 内容 |             ← 表格（毛玻璃效果）
|------|------|
| 目标系统 | XXX |
---                         ← 分隔线
> 机密文件...               ← 引用块（红色警告）
```

### PDF 输出
```
第 1 页：封面（渐变背景 + 样式化内容）
第 2 页起：报告正文
```

## 💡 最佳实践

1. **保持简洁**：使用基础 Markdown 语法
2. **结构清晰**：使用分隔线划分区域
3. **表格对齐**：使用 Markdown 表格展示信息
4. **强调重点**：使用粗体和引用块
5. **样式分离**：内容用 Markdown，样式用 CSS

## 📞 技术支持

如有问题，请参考：
- Pandoc 官方文档：https://pandoc.org/
- Markdown 语法指南：https://commonmark.org/help/
- wkhtmltopdf 文档：https://wkhtmltopdf.org/

## 🎯 与 HTML 方案对比

| 特性 | 纯 Markdown 方案 | HTML+Markdown 方案 |
|------|-----------------|-------------------|
| **语法** | 纯 Markdown | HTML + Markdown 混合 |
| **可读性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **维护性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **样式控制** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **工具兼容** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **学习曲线** | 低 | 中 |

**推荐使用场景：**
- ✅ 纯 Markdown 方案：日常报告、团队协作、版本控制
- ✅ HTML 方案：复杂布局、精确控制、特殊效果
