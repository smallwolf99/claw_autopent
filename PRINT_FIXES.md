# PDF 打印优化解决方案

## 🔧 已修复的问题

### 问题 1：内容超出 A4 纸张
**原因：**
- `max-width: 1000px` 太宽
- `padding: 40px` 占用过多空间
- 表格和代码没有宽度限制

**解决方案：**
```css
body {
    max-width: 210mm;  /* A4 宽度 */
    padding: 15px;      /* 减小 padding */
}

.container {
    padding: 20px;      /* 减小 padding */
    max-width: 100%;
}

table {
    table-layout: fixed;  /* 固定表格布局 */
    width: 100% !important;
}

pre, code {
    max-width: 100%;
    word-wrap: break-word;
    white-space: pre-wrap;
}
```

### 问题 2：表格被截断
**解决方案：**
- 使用 `table-layout: fixed` 固定表格布局
- 单元格自动换行：`word-wrap: break-word`
- 减小字体：`font-size: 0.9em`
- 减小 padding：`padding: 10px 12px`

### 问题 3：代码溢出
**解决方案：**
- 代码自动换行：`white-space: pre-wrap`
- 限制最大宽度：`max-width: 100%`
- 减小字体：`font-size: 0.85em`
- 减小 padding：`padding: 12px`

### 问题 4：格式错乱
**解决方案：**
```css
@media print {
    body {
        width: 210mm;     /* 固定宽度 */
        max-width: 210mm;
    }
    
    .container {
        width: 100%;      /* 占满可用宽度 */
        max-width: 100%;
    }
    
    * {
        max-width: 100%;  /* 所有元素不超出 */
    }
}
```

## 📐 页面尺寸设置

### A4 纸张规格
- **宽度**: 210mm (21cm)
- **高度**: 297mm (29.7cm)
- **页边距**: 2cm (上下左右)
- **可用宽度**: 约 170mm

### CSS 设置
```css
@page {
    size: A4;
    margin: 2cm;
}
```

## 🎯 打印优化要点

### 1. 宽度控制
```css
/* 屏幕显示 */
body {
    max-width: 210mm;
}

/* 打印时 */
@media print {
    body {
        width: 210mm;
        max-width: 210mm;
    }
}
```

### 2. 表格优化
```css
table {
    table-layout: fixed;        /* 固定布局 */
    width: 100% !important;     /* 占满宽度 */
    font-size: 0.9em;          /* 减小字体 */
}

th, td {
    word-wrap: break-word;     /* 自动换行 */
    padding: 10px 12px;        /* 减小 padding */
}
```

### 3. 代码优化
```css
pre, code {
    white-space: pre-wrap;     /* 自动换行 */
    word-wrap: break-word;     /* 单词内换行 */
    max-width: 100%;           /* 限制宽度 */
    font-size: 0.85em;         /* 减小字体 */
}
```

### 4. 分页控制
```css
/* 避免在元素内部断页 */
h1, h2, h3 {
    page-break-after: avoid;
}

table, pre, ul {
    page-break-inside: avoid;
}

/* 强制分页 */
.cover-page {
    page-break-after: always;
}
```

## 📋 打印步骤

### 方法 1：使用测试页面
1. 打开 `print_test.html`
2. 点击 "🖨️ 打印为 PDF" 按钮
3. 选择"另存为 PDF"
4. 检查预览效果
5. 保存 PDF

### 方法 2：直接打印报告
1. 打开 `DVWA_report_templates.html`
2. 按 `Ctrl+P` (或 `Cmd+P`)
3. 设置：
   - **目标打印机**: 另存为 PDF
   - **纸张大小**: A4
   - **边距**: 默认
   - **缩放**: 100%
   - ✅ **勾选"背景图形"**
4. 预览检查
5. 保存 PDF

## ✅ 检查清单

打印前请检查：

- [ ] 内容没有超出页面边界
- [ ] 左右边距合适（不贴边）
- [ ] 上下边距合适
- [ ] 表格完整显示，没有被截断
- [ ] 表格内容自动换行
- [ ] 代码块自动换行
- [ ] 代码没有被截断
- [ ] 标题后没有立即分页
- [ ] 列表项没有被分页打断
- [ ] 颜色正常显示（特别是风险等级）
- [ ] 页码正确显示

## 🛠️ 常见问题解决

### 问题：表格还是超出页面
**解决：**
```css
table {
    table-layout: fixed;
    width: 100% !important;
}

td {
    word-wrap: break-word;
    overflow-wrap: break-word;
}
```

### 问题：代码还是溢出
**解决：**
```css
pre {
    max-width: 100%;
    overflow-x: auto;
}

code {
    white-space: pre-wrap;
    word-break: break-all;
}
```

### 问题：内容被截断
**解决：**
1. 检查是否有固定宽度：`width: xxx px`
2. 改为百分比或自动：`width: 100%` 或 `width: auto`
3. 添加：`max-width: 100%`

### 问题：打印时背景色不显示
**解决：**
- Chrome/Edge: 勾选"背景图形"
- Firefox: 勾选"打印背景"
- 添加 CSS: `print-color-adjust: exact`

## 📊 优化效果对比

### 优化前 ❌
- 内容超出 A4 纸
- 表格被截断
- 代码溢出
- 格式错乱

### 优化后 ✅
- 完美适配 A4
- 表格自动换行
- 代码不溢出
- 格式整齐

## 🎨 打印质量建议

### 颜色模式
- **彩色打印**: 推荐，风险等级颜色清晰
- **黑白打印**: 使用灰度模式，确保对比度

### 分辨率
- 建议：300 DPI 或更高
- 最低：150 DPI

### 纸张
- 推荐：80g A4 打印纸
- 双面打印：节省纸张

## 📁 相关文件

1. `DVWA_report_templates.html` - 优化的报告模板
2. `print_test.html` - 打印测试页面
3. `PRINT_OPTIMIZATION_GUIDE.md` - 打印优化指南
4. `PRINT_FIXES.md` - 本文档

---

**最后更新**: 2026-04-22  
**版本**: 2.0 (修复溢出问题)
