# 智能测试编排器 - 运行指南

## 🚀 快速开始

### 方式 1：使用启动脚本（推荐）⭐

**Windows 批处理：**
```bash
.\run.bat '{"target": "http://example.com"}'
```

**PowerShell 脚本：**
```powershell
.\run.ps1 '{"target": "http://example.com"}'
```

### 方式 2：直接 Python 调用

```bash
python main.py '{"target": "http://example.com"}'
```

### 方式 3：JSON 文件输入

```bash
Get-Content test_input.json | python main.py
```

---

## 📋 测试模式

### 1. 完整模式（Full）
```json
{
  "target": "http://zero.webappsecurity.com",
  "test_mode": "full",
  "time_limit": 120,
  "report_format": "html"
}
```

### 2. 快速模式（Light）
```json
{
  "target": "http://example.com",
  "test_mode": "light",
  "time_limit": 30,
  "report_format": "markdown"
}
```

### 3. 自定义模式（Custom）
```json
{
  "target": "192.168.1.100",
  "test_mode": "custom",
  "time_limit": 60,
  "report_format": "json",
  "custom_options": {
    "skip_verification": true,
    "concurrent_tools": 5
  }
}
```

---

## 🧪 测试工具

### OpenClaw 模拟测试
```bash
python test_openclaw_simulate.py
```

**选项：**
1. 演示模式 - 自动执行完整流程
2. 交互模式 - 手动输入测试目标

### 自动化测试
```bash
python test_basic.py
```

运行 5 个自动化测试用例。

---

## 🔧 编码问题解决方案

### 问题描述
Windows PowerShell 默认使用 GBK 编码，导致中文输出乱码。

### 解决方案

#### 方案 A：使用启动脚本（推荐）
- `run.bat` - Windows 批处理版本
- `run.ps1` - PowerShell 版本

两个脚本都会自动设置 UTF-8 编码。

#### 方案 B：手动设置编码
```powershell
# 设置控制台编码
chcp 65001

# 设置环境变量
$env:PYTHONIOENCODING = "utf-8"

# 运行
python main.py '{"target": "http://example.com"}'
```

#### 方案 C：使用管道输入
```bash
Get-Content test_input.json | python main.py
```

---

## 📊 输出示例

### 进度反馈
```
🎯 开始智能安全测试
🔧 目标：http://example.com
🛠️  模式：full
⏱️  时间限制：120 分钟

📦 阶段 1/5: 资产收集中...
✅ 发现 3 个资产

🧠 阶段 2/5: 风险画像生成中...
⚠️  风险评分：7.5/100

🔍 阶段 3/5: 漏洞检测中...
🐛 发现 2 个漏洞

🔬 阶段 4/5: 漏洞验证中...
✔️  已验证 1 个漏洞

📄 阶段 5/5: 报告生成中...
📊 报告已生成：reports/report_20260420_235706.markdown
```

### 返回结果
```json
{
  "success": true,
  "summary": "✅ 测试完成，发现 2 个漏洞（已验证 1 个），风险评分 7.5/100，耗时 0 分 1 秒",
  "data": {
    "target": "http://example.com",
    "assets_found": 3,
    "vulnerabilities_found": 2,
    "verified_vulns": 1,
    "risk_score": 7.5,
    "report_path": "reports/report_20260420_235706.markdown",
    "report_url": "file://reports/report_20260420_235706.markdown",
    "execution_time": 1.85,
    "start_time": "2026-04-20T23:57:04.390296",
    "end_time": "2026-04-20T23:57:06.242262"
  },
  "actions": [
    {
      "label": "查看完整报告",
      "type": "open_file",
      "path": "reports/report_20260420_235706.markdown"
    },
    {
      "label": "导出 PDF",
      "type": "export_pdf",
      "path": "reports/report_20260420_235706.markdown"
    }
  ]
}
```

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口文件 |
| `run.bat` | Windows 启动脚本（UTF-8） |
| `run.ps1` | PowerShell 启动脚本（UTF-8） |
| `test_input.json` | 测试输入模板（完整模式） |
| `test_light.json` | 测试输入模板（快速模式） |
| `test_custom.json` | 测试输入模板（自定义模式） |
| `test_error.json` | 测试输入模板（错误处理） |
| `test_openclaw_simulate.py` | OpenClaw 模拟测试 |
| `test_basic.py` | 自动化测试 |

---

## ⚠️ 常见问题

### Q1: 中文显示乱码
**A:** 使用 `run.bat` 或 `run.ps1` 启动脚本，它们会自动设置 UTF-8 编码。

### Q2: JSON 解析错误
**A:** PowerShell 引号处理问题，建议使用 JSON 文件输入：
```bash
Get-Content test_input.json | python main.py
```

### Q3: 找不到 Python 命令
**A:** 确保已安装 Python 3.8+，并添加到系统 PATH。

---

## 🎯 最佳实践

1. **使用启动脚本** - 避免编码问题
2. **JSON 文件输入** - 避免引号问题
3. **先快速模式测试** - 验证功能后再用完整模式
4. **查看日志输出** - 了解执行进度

---

## 📞 技术支持

如有问题，请查看：
- `SKILL.md` - 技能文档
- `docs/openclaw-integration.md` - OpenClaw 集成文档
- `COMPLETION_SUMMARY.md` - 完成总结报告
