# Markdown 报告封面方案

## 📋 方案说明

直接在 Markdown 报告开头插入 HTML 封面，优势：

### ✅ 优势
1. **简单直接**：不需要复杂的 HTML 模板引擎
2. **Pandoc 友好**：原生支持 HTML+Markdown 混合
3. **分页清晰**：使用 CSS `page-break-after: always`
4. **样式统一**：封面和内页使用相同的设计语言
5. **易于维护**：只需维护一个文件

## 🎨 封面设计

### 配色方案
- **背景**：淡雅蓝紫渐变 (#e8eaf6 → #e3f2fd → #ede7f6)
- **文字**：藏青色渐变 (#1a2332 → #233140 → #2a3f50)
- **警告**：红色 (#d32f2f)
- **信息框**：毛玻璃效果 + 轻微阴影

### 封面元素
1. 标题：安全渗透测试报告（藏青色渐变 + 阴影）
2. 副标题：Security Penetration Testing Report
3. 信息框：
   - 目标系统
   - 目标 URL
   - 测试时间
   - 测试人员
   - 风险等级
4. 页脚：机密文件警告（红色）

## 📄 使用方法

### 1. 模板变量
在 Markdown 文件中使用 `{{ variable }}` 语法：

```markdown
<!-- HTML 封面部分 -->
<span class="cover-info-value">{{ report.target_name }}</span>

<!-- Markdown 正文部分 -->
- **目标系统**: {{ report.target_name }}
```

### 2. 转换为 PDF

使用 Pandoc 进行转换：

```bash
pandoc markdown-with-cover.md \
  -o report.pdf \
  --pdf-engine=wkhtmltopdf \
  --variable paper-size=a4 \
  --variable margin-top=0mm \
  --variable margin-bottom=0mm \
  --variable margin-left=0mm \
  --variable margin-right=0mm \
  --css cover-styles.css
```

### 3. Python 脚本处理

```python
from pathlib import Path
import re

def render_markdown_with_cover(template_path, output_path, context):
    """渲染带封面的 Markdown 报告"""
    
    # 读取模板
    template = Path(template_path).read_text(encoding='utf-8')
    
    # 替换变量
    for key, value in context.items():
        template = template.replace(f'{{{{ {key} }}}}', str(value))
    
    # 输出渲染后的文件
    Path(output_path).write_text(template, encoding='utf-8')
    
    # 转换为 PDF
    import subprocess
    subprocess.run([
        'pandoc',
        str(output_path),
        '-o', str(output_path.with_suffix('.pdf')),
        '--pdf-engine=wkhtmltopdf',
        '--variable', 'paper-size=a4',
        '--variable', 'margin-top=0mm',
        '--variable', 'margin-bottom=0mm',
        '--variable', 'margin-left=0mm',
        '--variable', 'margin-right=0mm'
    ])
    
    return output_path.with_suffix('.pdf')

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

render_markdown_with_cover(
    'report-templates/markdown-with-cover.md',
    'reports/test-report.md',
    context
)
```

## 🎯 CSS 样式说明

### 封面页样式
```css
.cover-page {
    /* 背景渐变 */
    background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 50%, #ede7f6 100%);
    
    /* A4 尺寸 */
    width: 210mm;
    height: 297mm;
    
    /* 内边距 */
    padding: 30mm 20mm;
    
    /* 分页控制 */
    page-break-after: always;
}
```

### 标题样式
```css
.cover-title {
    /* 藏青色渐变文字 */
    background: linear-gradient(135deg, #1a2332 0%, #233140 50%, #2a3f50 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    
    /* 双层阴影增强质感 */
    text-shadow: 2px 2px 4px rgba(26, 35, 50, 0.3), 
                 0 0 20px rgba(26, 35, 50, 0.15);
}
```

### 信息框样式
```css
.cover-info-box {
    /* 毛玻璃效果 */
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    
    /* 边框和圆角 */
    border: 1px solid rgba(26, 35, 50, 0.2);
    border-radius: 12px;
    
    /* 轻微阴影 */
    box-shadow: 0 2px 8px rgba(26, 35, 50, 0.04);
}
```

## 📊 分页控制

### CSS 分页
```css
/* 封面后强制分页 */
.cover-page {
    page-break-after: always;
}

/* 避免标题和段落分离 */
h1, h2, h3 {
    page-break-after: avoid;
}

/* 避免表格和代码块内部断页 */
table, pre {
    page-break-inside: avoid;
}
```

## 🔧 自定义选项

### 修改封面颜色
```css
/* 更蓝的色调 */
.cover-page {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #e1f5fe 100%);
}

/* 更紫的色调 */
.cover-page {
    background: linear-gradient(135deg, #ede7f6 0%, #e8eaf6 50%, #f3e5f5 100%);
}

/* 更浅的色调 */
.cover-page {
    background: linear-gradient(135deg, #f5f7fa 0%, #f0f4f8 50%, #f9fafb 100%);
}
```

### 修改阴影强度
```css
/* 更轻的阴影 */
.cover-info-box {
    box-shadow: 0 1px 4px rgba(26, 35, 50, 0.02);
}

/* 更重的阴影 */
.cover-info-box {
    box-shadow: 0 4px 12px rgba(26, 35, 50, 0.1);
}
```

## ✅ 验证清单

- [x] HTML 封面在文件开头
- [x] CSS 样式内联在`<style>`标签中
- [x] 使用 `page-break-after: always` 强制分页
- [x] 封面不包含页眉页脚
- [x] Markdown 正文从第二页开始
- [x] 模板变量使用 `{{ }}` 语法
- [x] 支持 Pandoc 直接转换
- [x] 支持 wkhtmltopdf 引擎

## 📝 示例文件

参考文件：`report-templates/markdown-with-cover.md`

## 🚀 快速开始

1. **复制模板**：
   ```bash
   cp report-templates/markdown-with-cover.md reports/my-report.md
   ```

2. **替换变量**：
   使用 Python 脚本或文本编辑器替换所有 `{{ variable }}`

3. **转换为 PDF**：
   ```bash
   pandoc reports/my-report.md -o reports/my-report.pdf \
     --pdf-engine=wkhtmltopdf \
     --variable paper-size=a4
   ```

## 💡 最佳实践

1. **保持简洁**：封面设计不宜过于复杂
2. **信息清晰**：关键信息突出显示
3. **风格统一**：封面与正文风格一致
4. **打印友好**：使用 A4 标准尺寸和合适边距
5. **颜色适配**：确保打印时颜色正常显示

## 📞 技术支持

如有问题，请参考：
- Pandoc 官方文档：https://pandoc.org/
- wkhtmltopdf 文档：https://wkhtmltopdf.org/
