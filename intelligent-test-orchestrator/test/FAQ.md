# 常见问题解答

## ❓ 常见错误及解决方案

---

### 问题 1: `ModuleNotFoundError: No module named 'adapters'`

**症状：**
```bash
$ python test/test_phase0_real.py
Traceback (most recent call last):
  File "test/test_phase0_real.py", line 17, in <module>
    from adapters.phase0_adapter_real import Phase0Adapter
ModuleNotFoundError: No module named 'adapters'
```

**原因：**
Python 路径没有正确设置，无法找到 `adapters` 模块。

**解决方案：**

#### 方法 1: 从项目根目录运行（推荐）

```bash
# ✅ 正确：在项目根目录运行
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python test/test_phase0_real.py

# ❌ 错误：不要进入 test 目录
cd test
python test_phase0_real.py  # 会报错！
```

---

#### 方法 2: 设置 PYTHONPATH

```bash
# 设置 PYTHONPATH 环境变量
export PYTHONPATH=/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator:$PYTHONPATH

# 然后可以运行
python test/test_phase0_real.py
```

---

#### 方法 3: 使用绝对路径运行

```bash
python /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/test_phase0_real.py
```

---

### 问题 2: 工具未找到

**症状：**
```bash
❌ nmap 调用失败：[Errno 2] No such file or directory: 'nmap'
```

**原因：**
系统未安装所需的工具。

**解决方案：**

```bash
# 1. 检查工具依赖
python test/check_dependencies.py

# 2. 根据提示安装缺失的工具

# 安装 Nmap
sudo apt install nmap

# 安装 WhatWeb
sudo apt install whatweb

# 安装 Httpx (Go)
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# 安装 Subfinder (Go)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# 安装 Nuclei (Go)
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# 安装 Afrog (Go)
go install github.com/zan8in/afrog/v2@latest

# 安装 Nikto
sudo apt install nikto

# 安装 SQLMap
git clone https://github.com/sqlmapproject/sqlmap.git

# 安装 ZAP-CLI
pip3 install zap-cli
```

---

### 问题 3: 权限不足

**症状：**
```bash
❌ Nmap 调用失败：permission denied
```

**原因：**
某些 Nmap 扫描需要 root 权限。

**解决方案：**

```bash
# 方法 1: 使用 sudo 运行
sudo python test/test_phase0_real.py

# 方法 2: 使用普通扫描模式（代码中已默认使用 -sT）
# 不需要 root 权限
```

---

### 问题 4: 测试超时

**症状：**
```bash
⚠️  Command timed out
```

**原因：**
网络延迟或目标不可达。

**解决方案：**

```bash
# 1. 测试目标是否可达
ping example.com

# 2. 更换测试目标
# 编辑 test/test_phase0_real.py，修改 test_targets 列表

# 3. 使用本地或内网目标
python test/test_phase0_real.py  # 使用内网 IP
```

---

### 问题 5: 编码错误

**症状：**
```bash
UnicodeEncodeError: 'gbk' codec can't encode character
```

**原因：**
Windows 系统默认编码问题。

**解决方案：**

```bash
# Windows PowerShell 设置 UTF-8
$env:PYTHONIOENCODING="utf-8"
python test/test_phase0_real.py

# 或者在 Linux/Mac 上
export PYTHONIOENCODING="utf-8"
python test/test_phase0_real.py
```

---

### 问题 6: 时间过短（模拟数据）

**症状：**
```bash
⏱️  时间分析:
  ⚠️  警告：耗时过短 (0.35 秒)，可能是模拟数据
     预期：Nmap 扫描至少需要 1-3 分钟
```

**原因：**
使用的是模拟版本的适配器，而非真实工具调用版本。

**解决方案：**

```bash
# 确认使用的是 phase0_adapter_real.py
# 检查代码中的导入

# 查看当前使用的适配器
grep "from adapters" test/test_phase0_real.py

# 应该显示：
# from adapters.phase0_adapter_real import Phase0Adapter
```

---

## 🎯 快速诊断流程

### 步骤 1: 检查运行位置

```bash
# 确认在项目根目录
pwd

# 应该显示：
# /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
```

---

### 步骤 2: 检查工具依赖

```bash
python test/check_dependencies.py
```

---

### 步骤 3: 运行简单测试

```bash
# 先运行基础测试
python test/test_basic.py

# 再运行真实工具测试
python test/test_phase0_real.py
```

---

### 步骤 4: 查看详细错误

```bash
# 保存完整输出
python test/test_phase0_real.py 2>&1 | tee test_output.log

# 查看错误信息
grep -A 10 "Error\|Exception" test_output.log
```

---

## 📚 相关文档

- 📖 [README.md](README.md) - 测试套件说明
- 📖 [TEST_PHASE0_README.md](TEST_PHASE0_README.md) - Phase-0 测试详细说明
- 📖 [PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md) - Phase-0 详细指南
- 📖 [REAL_TOOL_FIX_GUIDE.md](REAL_TOOL_FIX_GUIDE.md) - 真实工具修复指南

---

## 🆘 需要更多帮助？

如果以上方案都无法解决问题：

1. **收集诊断信息**
   ```bash
   # 系统信息
   uname -a
   
   # Python 版本
   python --version
   
   # 工具版本
   nmap --version
   whatweb --version
   
   # 完整测试输出
   python test/test_phase0_real.py 2>&1 | tee full_output.log
   ```

2. **查看日志**
   ```bash
   # 查看 OpenClaw 日志
   pm2 logs openclaw
   
   # 查看测试输出
   cat full_output.log
   ```

3. **提供以下信息**
   - 操作系统及版本
   - Python 版本
   - 已安装的工具及版本
   - 完整的错误输出
   - 运行的命令

---

**祝你测试顺利！** 🎉
