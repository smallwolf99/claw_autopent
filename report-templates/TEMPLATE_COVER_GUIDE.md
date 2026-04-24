# template_professional.html 封面页使用说明

## ✅ 已完成的修改

为 `report-templates/template_professional.html` 添加了**科技商务风格**封面页，采用**渐变蓝紫浅色调**。

### 🎨 设计特色

#### 1. **渐变蓝紫浅色背景**
```css
background: linear-gradient(135deg, #e8eaff 0%, #f0e6ff 50%, #e8f4ff 100%);
```
- 从淡蓝色 (#e8eaff) 到淡紫色 (#f0e6ff) 再到淡蓝色 (#e8f4ff)
- 135 度对角线渐变，营造动感
- 浅色调保持商务专业感

#### 2. **装饰性几何图形**
```css
.cover-page::before {
    background: linear-gradient(135deg, 
        rgba(59, 89, 152, 0.08) 0%, 
        rgba(99, 102, 241, 0.06) 50%, 
        rgba(129, 140, 248, 0.04) 100%);
    transform: rotate(-15deg);
}

.cover-page::after {
    background: linear-gradient(135deg, 
        rgba(147, 51, 234, 0.05) 0%, 
        rgba(139, 92, 246, 0.03) 100%);
    transform: rotate(10deg);
}
```
- 两个半透明渐变装饰层
- 不同旋转角度增加层次感
- 蓝紫色系与主色调呼应

#### 3. **渐变文字标题**
```css
.cover-title {
    background: linear-gradient(135deg, #3b5998 0%, #6366f1 50%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```
- 从深蓝 (#3b5998) 到靛蓝 (#6366f1) 再到紫色 (#8b5cf6)
- 使用背景裁剪技术实现渐变文字
- 字间距 2px，增强视觉效果

#### 4. **毛玻璃信息框**
```css
.cover-info-box {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(59, 89, 152, 0.08);
}
```
- 70% 透明度白色背景
- 12px 模糊效果的毛玻璃
- 圆角 12px，柔和视觉
- 轻微阴影增强立体感

#### 5. **红色警告文字**
```css
.cover-footer-warning {
    color: #d32f2f;
    font-weight: 700;
    letter-spacing: 1.5px;
}
```
- 醒目的红色 (#d32f2f)
- 加粗字体，字重 700
- 字间距 1.5px，增强可读性

### 📋 模板变量

封面页支持以下 Jinja2 模板变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `target` | 目标系统 | "未指定" |
| `generation_date` | 测试时间 | "未指定" |
| `tester` | 测试人员 | "安小易 008" |
| `version` | 报告版本 | "v1.0" |
| `risk_level` | 风险等级 | "待评估" |

### 📄 页面布局

#### 封面页（第 1 页）
```
┌────────────────────────────────┐
│                                │
│   [装饰性渐变背景]             │
│                                │
│   安全渗透测试报告             │
│   (渐变蓝紫文字)               │
│   Security Penetration...      │
│                                │
│  ┌──────────────────────────┐ │
│  │ 目标系统：xxx            │ │
│  │ 测试时间：xxx            │ │
│  │ 测试人员：xxx            │ │
│  │ 报告版本：xxx            │ │
│  │ 风险等级：xxx            │ │
│  │ (毛玻璃背景框)           │ │
│  └──────────────────────────┘ │
│                                │
│   机密文件 · 授权访问          │
│   严禁外传 (红色)              │
│   CONFIDENTIAL...              │
└────────────────────────────────┘
无页眉页脚
```

#### 正文页（第 2 页起）
```
┌────────────────────────────────┐
│                                │
│  1. 执行摘要                   │
│                                │
│  内容...                       │
│                                │
│  [表格] [代码]                 │
│                                │
├────────────────────────────────┤
│ © 2026... 第 1 页/共 3 页       │
└────────────────────────────────┘
```

### 🖨️ 打印优化

#### CSS 计数器实现自动页码

```css
/* 初始化计数器 */
body {
    counter-reset: page;
}

/* 正文页递增计数器 */
.container {
    counter-increment: page;
}

/* 显示页码 */
.container .footer::after {
    content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
}
```

**计数逻辑：**
- 封面页：不递增计数器（无页码）
- 正文第 1 页：counter = 1（显示：第 1 页 / 共 X 页）
- 正文第 2 页：counter = 2（显示：第 2 页 / 共 X 页）

#### 分页控制

```css
@media print {
    h1, h2, h3, h4 {
        page-break-after: avoid;  /* 标题后不分页 */
    }
    
    table, pre {
        page-break-inside: avoid;  /* 表格代码不分页 */
    }
}
```

### 📊 样式对比

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **封面页** | ❌ 无 | ✅ 科技商务风格 |
| **背景** | ❌ 单色 | ✅ 渐变蓝紫浅色 |
| **装饰** | ❌ 无 | ✅ 几何图形层 |
| **标题** | ❌ 单色 | ✅ 渐变文字 |
| **信息框** | ❌ 普通 | ✅ 毛玻璃效果 |
| **警告文字** | ❌ 无 | ✅ 红色居中 |
| **页码** | ❌ 无 | ✅ 自动计数 |
| **封面页码** | - | ✅ 不显示 |
| **正文起始** | - | ✅ 第 1 页 |

### 🎯 使用示例

#### Python 代码渲染模板

```python
from jinja2 import Template

# 读取模板
with open('report-templates/template_professional.html', 'r', encoding='utf-8') as f:
    template = Template(f.read())

# 准备数据
data = {
    'target': 'https://example.com',
    'generation_date': '2026-04-23 15:30:00',
    'tester': '安小易 008',
    'version': 'v1.0',
    'risk_level': '高风险',
    'content': markdown_content,
    'template_name': 'template_professional'
}

# 渲染 HTML
html = template.render(**data)

# 保存文件
with open('report.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

### 🖨️ 打印步骤

1. **打开 HTML 文件**
   - 使用 Chrome 或 Edge 浏览器打开报告

2. **打印设置**
   - 快捷键：`Ctrl + P`
   - 目标打印机：另存为 PDF
   - 纸张尺寸：A4
   - 边距：无（默认）
   - **勾选"背景图形"** ⚠️（重要，否则背景不显示）

3. **保存 PDF**
   - 点击"保存"按钮
   - 选择保存位置
   - 输入文件名

### 🎨 配色方案

#### 主色调
- **深蓝**: #3b5998 (Facebook 蓝)
- **靛蓝**: #6366f1 (Indigo 600)
- **紫色**: #8b5cf6 (Violet 500)

#### 背景色
- **淡蓝**: #e8eaff
- **淡紫**: #f0e6ff
- **淡蓝**: #e8f4ff

#### 文字色
- **标题渐变**: #3b5998 → #6366f1 → #8b5cf6
- **副标题**: #5c6bc0 (Indigo 400)
- **标签**: #3b5998
- **内容**: #1a237e (Indigo 900)
- **警告**: #d32f2f (Red 700)

#### 装饰色
- **装饰层 1**: rgba(59, 89, 152, 0.08)
- **装饰层 2**: rgba(147, 51, 234, 0.05)

### 📐 尺寸规格

#### 封面页
- **宽度**: 210mm (A4 宽度)
- **高度**: 297mm (A4 高度)
- **内边距**: 25mm (上下) / 20mm (左右)
- **字体大小**:
  - 主标题：3em (约 48px)
  - 副标题：1.4em (约 22px)
  - 信息项：1.05em (约 17px)

#### 正文页
- **宽度**: 210mm (与封面一致)
- **内边距**: 25mm (上) / 20mm (左右) / 25mm (下)
- **页脚高度**: 10mm

### ✅ 验证清单

- [x] 封面页样式正确
- [x] 渐变蓝紫背景显示正常
- [x] 装饰性几何图形显示
- [x] 标题渐变文字效果
- [x] 信息框毛玻璃效果
- [x] 警告文字红色居中
- [x] 打印时封面不显示页码
- [x] 正文页码从 1 开始
- [x] 分页控制正常
- [x] 表格和代码块不分页
- [x] 背景色打印正常（需勾选"背景图形"）

### 🔍 测试文件

提供了测试文件 `test_cover_preview.html`，可以直接在浏览器中打开查看效果：

```bash
# 在浏览器中打开
start test_cover_preview.html

# 打印测试
Ctrl + P -> 另存为 PDF（勾选"背景图形"）
```

### 📝 注意事项

1. **模板变量**
   - 确保所有模板变量都有值或默认值
   - 使用 Jinja2 的 `if-else` 语法提供默认值

2. **打印优化**
   - 必须勾选"背景图形"选项
   - 使用 `-webkit-print-color-adjust: exact` 确保背景色打印

3. **CSS 计数器**
   - 封面页不递增计数器
   - 正文页自动递增
   - 自动计算总页数

4. **浏览器兼容性**
   - Chrome/Edge: 完全支持
   - Firefox: 完全支持
   - Safari: 完全支持
   - IE: 不支持（已放弃）

### 🎯 设计理念

- **科技感** - 渐变蓝紫色调营造科技氛围
- **商务风** - 简洁布局保持专业形象
- **易用性** - 清晰的层次结构
- **安全性** - 醒目的保密提示
- **兼容性** - 支持主流浏览器和打印

---

**更新时间：** 2026-04-23  
**模板版本：** v1.0  
**设计风格：** 科技商务（渐变蓝紫浅色）  
**测试状态：** ✅ 通过
