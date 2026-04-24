# DVWA 报告模板 - PDF 打印优化指南

## ✅ 已完成的打印优化

### 1. **页面设置**
```css
@page {
    size: A4;           /* A4 纸张大小 */
    margin: 2.5cm;      /* 页边距 */
}
```

### 2. **分页控制**

#### 封面页
- ✅ 封面单独一页
- ✅ 使用 `page-break-after: always`

#### 章节标题
- ✅ 避免在标题后断页：`page-break-after: avoid`
- ✅ 主要章节使用 `page-break-before` 控制

#### 内容块
- ✅ 表格：避免在中间断页
- ✅ 列表项：避免在中间断页
- ✅ 代码块：避免在中间断页
- ✅ 段落：使用 orphans/widows 控制

### 3. **打印专用样式**

#### 移除背景色
```css
@media print {
    body {
        background: white;
    }
    .container {
        box-shadow: none;
    }
}
```

#### 确保颜色打印
```css
* {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
```

#### 表格优化
```css
thead {
    display: table-header-group;  /* 跨页时重复表头 */
}
tfoot {
    display: table-footer-group;  /* 跨页时重复表尾 */
}
```

#### 链接显示
```css
a[href]:after {
    content: " (" attr(href) ")";
}
```

### 4. **页眉页脚**

#### 页眉
```
DVWA 综合安全测试报告 - 机密文件
```

#### 页脚
```
第 X 页 / 共 Y 页
```

### 5. **分页控制类**

可在 HTML 中添加以下类来控制分页：

```html
<!-- 在新页开始 -->
<h2 class="page-break-before">章节标题</h2>

<!-- 在新页结束 -->
<hr class="page-break-after" />

<!-- 避免内部断页 -->
<ul class="page-break-inside-avoid">
    <li>内容</li>
</ul>

<table class="page-break-inside-avoid">
    <!-- 表格内容 -->
</table>
```

## 📋 打印建议

### 浏览器打印设置

1. **Chrome/Edge**
   - 打开方式：Ctrl+P
   - 目标打印机：另存为 PDF
   - 纸张大小：A4
   - 边距：默认
   - ✅ 勾选"背景图形"

2. **Firefox**
   - 打开方式：Ctrl+P
   - 打印到：Microsoft Print to PDF
   - 纸张大小：A4
   - ✅ 勾选"打印背景"

3. **Safari**
   - 文件 > 导出为 PDF
   - 纸张大小：A4
   - ✅ 勾选"打印背景"

### 打印质量优化

1. **颜色模式**
   - 使用彩色打印（确保风险等级颜色正确显示）
   - 或高质量黑白（灰度）打印

2. **分辨率**
   - 建议 300 DPI 或更高

3. **双面打印**
   - 建议双面打印，节省纸张

## 📊 页面布局

### 典型报告结构

```
页码 1: 封面页
  - 报告标题
  - 基本信息
  - 保密声明

页码 2-3: 报告信息与执行摘要
  - 目标系统信息
  - 风险评级矩阵
  - 关键发现

页码 4: 测试概述
  - 测试范围
  - 测试方法

页码 5+: 核心漏洞发现
  - 每个漏洞独立展示
  - 包含 PoC 和修复建议

最后页：结论与建议
```

## 🔧 自定义分页

### 强制分页
```html
<div class="page-break-before">
    <!-- 内容将从新页开始 -->
</div>
```

### 避免分页
```html
<div class="page-break-inside-avoid">
    <!-- 内容不会被分页打断 -->
</div>
```

### 章节后分页
```html
<h2>章节标题</h2>
<!-- 内容 -->
<hr class="page-break-after" />
```

## 📝 注意事项

1. **PDF 生成工具**
   - 推荐使用浏览器内置的"另存为 PDF"
   - 或使用专业工具（如 wkhtmltopdf、PrinceXML）

2. **跨浏览器兼容性**
   - 已测试 Chrome、Edge、Firefox
   - Safari 需要额外测试

3. **打印预览**
   - 打印前务必预览
   - 检查分页位置是否合理
   - 确保没有内容被截断

4. **文件大小**
   - 优化图片大小
   - 避免过大的内联样式

## 🎯 打印效果

### 封面页
- 独立一页
- 包含所有关键信息
- 专业的版式设计

### 正文页
- 清晰的章节划分
- 合理的行间距
- 表格完整显示
- 代码块不被截断

### 页眉页脚
- 每页显示报告标题
- 自动页码计数
- 专业的页脚信息

## 📖 使用示例

### 打印完整报告

1. 在浏览器中打开 HTML 文件
2. 按 Ctrl+P（或 Cmd+P）
3. 选择"另存为 PDF"
4. 设置纸张为 A4
5. 勾选"背景图形"
6. 点击"保存"

### 仅打印特定章节

1. 在打印设置中选择"自定义范围"
2. 输入页码范围（如：1-5）
3. 点击"打印"

## 🛠️ 故障排除

### 问题 1：背景色不显示
**解决**：勾选"背景图形"选项

### 问题 2：表格被截断
**解决**：表格已添加 `page-break-inside: avoid`

### 问题 3：页码不连续
**解决**：检查是否有元素使用了 `page-break-after: always`

### 问题 4：内容超出页面
**解决**：调整页边距或缩小字体

---

**最后更新**: 2026-04-22  
**版本**: 1.0
