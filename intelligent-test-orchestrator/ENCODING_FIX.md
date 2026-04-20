# 编码问题修复指南

## 📋 问题描述

在 Windows PowerShell 环境中运行智能测试编排器时，会出现中文乱码问题。这是因为：
- Python 默认使用 UTF-8 编码
- Windows PowerShell 默认使用 GBK 编码（代码页 936）
- 两者不匹配导致中文显示为乱码

## ✅ 解决方案

### 方案 1：使用 UTF-8 启动脚本（推荐）⭐

#### Windows 批处理版本
```bash
.\run.bat '{"target": "http://example.com"}'
```

**run.bat 内容：**
```batch
@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
python "%~dp0main.py" %*
```

#### PowerShell 版本
```powershell
.\run.ps1 '{"target": "http://example.com"}'
```

**run.ps1 内容：**
```powershell
#!/usr/bin/env pwsh
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
python "$scriptPath\main.py" $args
```

### 方案 2：手动设置编码

```powershell
# 设置控制台代码页为 UTF-8
chcp 65001

# 设置环境变量
$env:PYTHONIOENCODING = "utf-8"

# 运行程序
python main.py '{"target": "http://example.com"}'
```

### 方案 3：使用 JSON 文件输入（避免引号问题）

```powershell
# 创建 UTF-8 编码的 JSON 文件（无 BOM）
[System.IO.File]::WriteAllText("test.json", '{
  "target": "http://example.com",
  "test_mode": "full"
}', (New-Object System.Text.UTF8Encoding $false))

# 使用管道输入
python main.py < test.json
```

## 🔧 已修复的文件

### main.py
```python
# 设置标准输出编码为 UTF-8（Windows 兼容性）
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
```

### test_openclaw_simulate.py
```python
# 设置标准输出编码为 UTF-8（Windows 兼容性）
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# subprocess 调用时传递环境
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
result = subprocess.run(
    [sys.executable, "-X", "utf8", str(main_py), json.dumps(params, ensure_ascii=False)],
    capture_output=True,
    text=True,
    encoding='utf-8',
    env=env
)
```

## 📊 测试验证

### 测试 1：演示模式
```bash
python test_openclaw_simulate.py
# 选择 1（演示模式）
```

**预期结果：**
- 中文正常显示
- Emoji 正常显示
- 进度反馈清晰可见

### 测试 2：JSON 文件输入
```bash
Get-Content test_input.json | python main.py
```

**注意：** Get-Content 可能会添加 BOM，建议使用：
```bash
python main.py '{"target": "http://example.com"}'
```

### 测试 3：启动脚本
```bash
.\run.bat '{"target": "http://example.com"}'
```

**预期结果：**
- 中文正常显示
- 无乱码

## ⚠️ 常见问题

### Q1: 还是看到乱码怎么办？

**A:** 检查以下几点：
1. 确认使用了 `run.bat` 或 `run.ps1` 启动脚本
2. 确认控制台支持 UTF-8（运行 `chcp 65001`）
3. 尝试重启终端

### Q2: JSON 解析错误 "Unexpected UTF-8 BOM"

**A:** 文件有 BOM 标记，解决方法：
```powershell
# 使用无 BOM 的 UTF-8 编码保存
[System.IO.File]::WriteAllText("test.json", $content, (New-Object System.Text.UTF8Encoding $false))
```

### Q3: PowerShell 引号问题

**A:** PowerShell 对引号处理特殊，建议：
1. 使用 JSON 文件输入
2. 使用启动脚本
3. 使用双引号包裹 JSON

## 🎯 最佳实践

1. **始终使用启动脚本** - `run.bat` 或 `run.ps1`
2. **使用 JSON 文件** - 避免命令行引号问题
3. **设置 UTF-8 环境** - 确保编码一致
4. **避免 Get-Content** - 使用其他方式读取文件

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `run.bat` | Windows 批处理启动脚本 |
| `run.ps1` | PowerShell 启动脚本 |
| `main.py` | 主入口（已修复编码） |
| `test_openclaw_simulate.py` | 测试脚本（已修复编码） |
| `RUN_GUIDE.md` | 完整运行指南 |

## ✅ 修复验证清单

- [x] main.py 添加 UTF-8 编码设置
- [x] test_openclaw_simulate.py 添加 UTF-8 编码设置
- [x] 创建 run.bat 启动脚本
- [x] 创建 run.ps1 启动脚本
- [x] 创建 RUN_GUIDE.md 文档
- [x] 创建编码修复指南（本文档）

## 🎉 总结

通过以上修复，智能测试编排器现在可以：
- ✅ 在 Windows PowerShell 中正常显示中文
- ✅ 支持 UTF-8 编码输入输出
- ✅ 兼容 OpenClaw 调用
- ✅ 支持多种运行方式

**推荐使用 `run.bat` 或 `run.ps1` 启动程序，可获得最佳中文显示效果！**
