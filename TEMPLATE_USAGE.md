# HTML 报告模板使用说明

## 📋 模板特性

### ✅ 已实现功能

1. **专业封面页**
   - 渐变紫色背景
   - 毛玻璃效果信息框
   - 中英双语标题
   - 机密声明

2. **智能分页**
   - 封面单独一页
   - 章节标题后不断页
   - 表格、代码块不被截断
   - 信息框完整显示

3. **自动页码**
   - 打印时自动计算总页数
   - 显示"第 X 页 / 共 Y 页"
   - 页眉显示报告标题

4. **A4 打印优化**
   - 精确的页面尺寸（210mm × 297mm）
   - 合理的页边距（上下 20mm，左右 15mm）
   - 页眉页脚高度仅 15mm
   - 内容自动换行，防止溢出

5. **专业样式**
   - 风险等级颜色标识
   - 信息框/警告框/危险框
   - 表格跨页显示表头
   - 代码自动换行

## 🎨 样式说明

### 页面尺寸
```
封面页：210mm × 297mm (A4)
正文页：210mm × 297mm (A4)
页边距：上 20mm, 下 20mm, 左 15mm, 右 15mm
页眉高：15mm
页脚高：15mm
```

### 颜色方案
| 元素 | 颜色代码 | 说明 |
|------|---------|------|
| 严重 (Critical) | #dc3545 | 红色 |
| 高危 (High) | #fd7e14 | 橙色 |
| 中危 (Medium) | #ffc107 | 黄色 |
| 低危 (Low) | #28a745 | 绿色 |
| 信息 (Info) | #17a2b8 | 蓝色 |
| 标题 | #2c3e50 | 深蓝灰 |
| 副标题 | #7f8c8d | 灰色 |

### 字体设置
- 主字体：Segoe UI
- 代码字体：Consolas / Courier New
- 正文字号：1em (约 16px)
- 代码字号：0.85em

## 📝 使用方法

### 1. 替换模板变量

模板中使用 `{{变量名}}` 作为占位符，需要替换为实际内容：

```html
<!-- 封面页 -->
{{报告标题}} → DVWA 综合安全测试报告
{{目标系统名称}} → DVWA (Damn Vulnerable Web Application)
{{测试时间}} → 2026-04-22 10:25 - 12:45
{{测试人员}} → 安小易 008 (高级安全渗透测试专家)
{{报告版本}} → v1.0
{{风险等级}} → 🔴 极度危险

<!-- 报告正文 -->
{{报告副标题}} → Comprehensive Security Assessment
{{执行摘要内容}} → 本次测试共发现...
{{整体安全态势描述}} → 系统存在多个严重漏洞...
```

### 2. 添加漏洞详情

复制以下模板，添加多个漏洞：

```html
<h2>3.X 漏洞名称：{{漏洞名称}}</h2>
<table>
    <tr>
        <th style="width: 25%;">漏洞地址</th>
        <td>{{漏洞 URL}}</td>
    </tr>
    <tr>
        <th>风险等级</th>
        <td><span class="critical">🔴 严重</span></td>
    </tr>
    <tr>
        <th>发现时间</th>
        <td>{{发现时间}}</td>
    </tr>
    <tr>
        <th>PoC 验证</th>
        <td><code>{{PoC 代码}}</code></td>
    </tr>
</table>

<div class="warning-box">
    <strong>⚠️ 安全影响：</strong>
    <p style="margin-top: 10px;">{{影响描述}}</p>
</div>

<div class="info-box">
    <strong>💡 修复建议：</strong>
    <p style="margin-top: 10px;">{{修复建议}}</p>
</div>
```

### 3. 使用风险等级类名

```html
<span class="critical">🔴 严重</span>
<span class="high">🟠 高危</span>
<span class="medium">🟡 中危</span>
<span class="low">🟢 低危</span>
<span class="info">🔵 信息</span>
```

### 4. 使用信息框

```html
<!-- 信息框 -->
<div class="info-box">
    <strong>📌 重要信息：</strong>
    <p style="margin-top: 10px;">内容...</p>
</div>

<!-- 警告框 -->
<div class="warning-box">
    <strong>⚠️ 注意事项：</strong>
    <p style="margin-top: 10px;">内容...</p>
</div>

<!-- 危险框 -->
<div class="danger-box">
    <strong>🔴 紧急警告：</strong>
    <p style="margin-top: 10px;">内容...</p>
</div>
```

### 5. 控制分页

```html
<!-- 强制在新页开始 -->
<h1 class="page-break-before">新章节</h1>

<!-- 强制在新页结束 -->
<div class="page-break-after">内容</div>

<!-- 避免内部断页 -->
<div class="page-break-inside-avoid">
    <table>...</table>
</div>
```

## 🖨️ 打印步骤

### 方法 1：浏览器打印
1. 在浏览器中打开 `report_template.html`
2. 按 `Ctrl+P` (或 `Cmd+P`)
3. 选择"另存为 PDF"
4. 设置：
   - 纸张大小：A4
   - 边距：无（模板已设置）
   - 缩放：100%
   - ✅ 勾选"背景图形"
5. 预览检查
6. 保存 PDF

### 方法 2：程序生成
使用 Python 自动化生成：

```python
from jinja2 import Template

# 读取模板
with open('report_template.html', 'r', encoding='utf-8') as f:
    template = Template(f.read())

# 准备数据
data = {
    '报告标题': 'DVWA 综合安全测试报告',
    '目标系统名称': 'DVWA',
    '测试时间': '2026-04-22',
    # ... 其他变量
}

# 生成报告
html = template.render(**data)

# 保存
with open('output.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

## 📊 页面布局

```
┌─────────────────────────────────┐
│  封面页 (第 1 页)                │
│  - 渐变背景                     │
│  - 报告标题                     │
│  - 信息框                       │
│  - 保密声明                     │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  正文页 (第 2 页起)              │
│  ┌─────────────────────────┐   │
│  │ 页眉 (15mm)             │   │
│  ├─────────────────────────┤   │
│  │                         │   │
│  │  报告内容               │   │
│  │  - 标题                 │   │
│  │  - 表格                 │   │
│  │  - 代码                 │   │
│  │  - 信息框               │   │
│  │                         │   │
│  ├─────────────────────────┤   │
│  │ 页脚 (15mm)             │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

## ✅ 打印检查清单

打印前请确认：

- [ ] 所有 `{{变量}}` 已替换为实际内容
- [ ] 封面页信息完整
- [ ] 风险等级颜色正确
- [ ] 表格内容自动换行
- [ ] 代码块没有溢出
- [ ] 分页位置合理
- [ ] 没有内容被截断
- [ ] 页码正确显示

## 🎯 最佳实践

### 1. 内容组织
- 每个主要章节使用 `page-break-before`
- 表格前后留足空间（20px margin）
- 长代码块使用 `<pre><code>` 标签
- 重要信息使用信息框突出

### 2. 表格设计
```html
<table>
    <thead>
        <tr>
            <th style="width: 20%;">列 1</th>
            <th style="width: 30%;">列 2</th>
            <th style="width: 50%;">列 3</th>
        </tr>
    </thead>
    <tbody>
        <!-- 内容 -->
    </tbody>
</table>
```

### 3. 代码展示
```html
<h3>代码示例：</h3>
<pre><code>GET /vulnerabilities/sqli/?id=1' UNION SELECT user,password FROM users-- HTTP/1.1
Host: example.com
Cookie: PHPSESSID=abc123</code></pre>
```

### 4. 漏洞描述结构
```
1. 漏洞名称（h2）
2. 基本信息表格
3. 安全影响（警告框）
4. 修复建议（信息框）
5. 利用代码（代码块）
```

## 📁 文件说明

1. `report_template.html` - 报告模板文件
2. `print_test.html` - 打印测试页面
3. `DVWA_report_templates.html` - DVWA 专用报告
4. `TEMPLATE_USAGE.md` - 本文档

## 🛠️ 自定义样式

如需修改样式，编辑 `<style>` 部分：

```css
/* 修改封面背景 */
.cover-page {
    background: linear-gradient(135deg, #你的颜色 0%, #你的颜色 100%);
}

/* 修改页眉高度 */
.page-header {
    height: 12mm;  /* 更小 */
}

/* 修改页边距 */
@media print {
    .a4-page {
        padding: 25mm 20mm;  /* 更大边距 */
    }
}
```

---

**最后更新**: 2026-04-22  
**版本**: 1.0  
**适用**: A4 纸打印
