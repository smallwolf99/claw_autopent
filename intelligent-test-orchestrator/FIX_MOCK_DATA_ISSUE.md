# 模拟数据问题诊断与解决

## 🐛 问题确认

**症状：**
```
⚠️  警告：数据看起来像模拟数据
   - 端口数 <= 2
   - 技术栈为空或过于简单
```

**根本原因：**
服务器上使用的仍然是 **`phase0_adapter.py`（模拟版本）**，而不是 **`phase0_adapter_real.py`（真实版本）**。

---

## 🔍 验证方法

### 方法 1: 检查服务器上的文件

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 检查 adapters 目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
ls -la phase0*.py
```

**预期输出：**
```
-rw-r--r-- 1 ubuntu ubuntu 12345 Apr 20 10:00 phase0_adapter.py          # 模拟版本
-rw-r--r-- 1 ubuntu ubuntu 23456 Apr 21 10:00 phase0_adapter_real.py      # 真实版本（如果已上传）
```

**如果只有 `phase0_adapter.py`，说明真实版本还没上传！**

---

### 方法 2: 检查导入的模块

```bash
# 在服务器上运行
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

try:
    from adapters.phase0_adapter_real import Phase0Adapter
    print('✅ 成功导入 phase0_adapter_real')
    print(f'   文件路径：{Phase0Adapter.__module__}')
except ImportError as e:
    print(f'❌ 导入失败：{e}')
    print('   服务器上可能没有 phase0_adapter_real.py 文件')

try:
    from adapters.phase0_adapter import Phase0Adapter
    print('✅ 成功导入 phase0_adapter（模拟版本）')
except ImportError as e:
    print(f'❌ 导入失败：{e}')
"
```

---

## ✅ 解决方案

### 方案 1: 上传真实版本到服务器（推荐）

#### 步骤 1: 上传 phase0_adapter_real.py

**从本地运行（Windows PowerShell）：**

```bash
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 上传真实版本
scp adapters/phase0_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
```

#### 步骤 2: SSH 登录服务器验证

```bash
ssh ubuntu@119.45.255.144

# 检查文件是否存在
ls -la /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase0*.py

# 应该看到两个文件：
# - phase0_adapter.py（旧的模拟版本）
# - phase0_adapter_real.py（新的真实版本）
```

#### 步骤 3: 运行测试

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行测试（会导入 phase0_adapter_real.py）
python3 test/test_phase0_real_standalone.py
```

---

### 方案 2: 直接修改模拟版本为真实版本

如果不想上传新文件，可以直接修改 `phase0_adapter.py`：

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 备份旧版本
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
cp phase0_adapter.py phase0_adapter_mock.py.backup

# 编辑文件（或者使用本地文件覆盖）
# 方法 A: 使用 nano 编辑
nano phase0_adapter.py

# 方法 B: 从本地上传覆盖
# 在本地运行：
scp adapters/phase0_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase0_adapter.py
```

---

### 方案 3: 使用调试版本诊断

```bash
# 上传调试版本
scp test/test_phase0_debug.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/

# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 运行调试版本
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase0_debug.py
```

**调试版本会显示：**
- 每个工具的实际调用命令
- 工具的原始输出
- 解析后的数据
- 详细的诊断信息

---

## 📊 对比两个版本

### phase0_adapter.py（模拟版本）

```python
# ❌ 模拟代码
async def _call_nmap(self, target: str):
    await asyncio.sleep(0.3)  # 假装在扫描
    return [{
        "type": "port",
        "host": target,
        "ports": [
            {"port": 80, "protocol": "tcp", "service": "http"},
            {"port": 443, "protocol": "tcp", "service": "https"}
        ]
    }]
```

**特征：**
- ⏱️ 耗时极短（0.3 秒）
- 📊 固定返回 2 个端口（80, 443）
- 🔧 没有真实调用工具

---

### phase0_adapter_real.py（真实版本）

```python
# ✅ 真实代码
async def _call_nmap(self, target: str):
    cmd = f"nmap -sV -sC -T4 --open -oX - {target}"
    process = await asyncio.create_subprocess_shell(cmd, ...)
    stdout, _ = await process.communicate()
    ports = self._parse_nmap_xml(stdout.decode())
    return [{
        "type": "port",
        "host": target,
        "ports": ports  # 真实扫描结果
    }]
```

**特征：**
- ⏱️ 耗时正常（10 秒 -3 分钟）
- 📊 返回真实端口（数量不定）
- 🔧 真实调用工具

---

## 🎯 快速验证

### 上传后运行测试

```bash
# 在服务器上
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行测试
python3 test/test_phase0_real_standalone.py

# 预期输出：
# ✅ 项目根目录：/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
# ✅ 成功导入 Phase0Adapter
# ...
# ✅ 验证结果:
#   ✅ WhatWeb: 检测到真实技术栈
#   ✅ Nmap: 检测到真实端口
# ...
# ⏱️  时间正常：45.23 秒
```

---

## 📝 文件清单

需要上传到服务器的文件：

1. **核心文件**
   - ✅ `adapters/phase0_adapter_real.py` - Phase-0 真实版本

2. **测试文件**
   - ✅ `test/test_phase0_real_standalone.py` - 独立测试脚本
   - ✅ `test/test_phase0_debug.py` - 调试版本（可选）
   - ✅ `test/check_dependencies.py` - 依赖检查（可选）

3. **文档**
   - ✅ `SERVER_QUICK_TEST.md` - 服务器测试指南

---

## 🚀 一键上传脚本

在本地运行：

```bash
#!/bin/bash
# deploy_real_version.sh

SERVER="ubuntu@119.45.255.144"
REMOTE_PATH="/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator"

echo "📦 上传真实版本..."

# 上传核心文件
scp adapters/phase0_adapter_real.py $SERVER:$REMOTE_PATH/adapters/

# 上传测试文件
scp test/test_phase0_real_standalone.py $SERVER:$REMOTE_PATH/test/
scp test/test_phase0_debug.py $SERVER:$REMOTE_PATH/test/

echo "✅ 上传完成！"
echo ""
echo "在服务器上运行:"
echo "  ssh $SERVER"
echo "  cd $REMOTE_PATH"
echo "  python3 test/test_phase0_real_standalone.py"
```

---

## 🆘 故障排查

### 问题 1: 上传后仍然报导入错误

**症状：**
```
ModuleNotFoundError: No module named 'phase0_adapter_real'
```

**解决：**

```bash
# 1. 检查文件是否存在
ls -la adapters/phase0_adapter_real.py

# 2. 检查文件内容
head -20 adapters/phase0_adapter_real.py

# 3. 检查 Python 版本
python3 --version

# 4. 尝试直接导入
python3 -c "from adapters.phase0_adapter_real import Phase0Adapter; print('成功')"
```

---

### 问题 2: 工具执行失败

**症状：**
```
❌ nmap 调用失败：[Errno 2] No such file or directory
```

**解决：**

```bash
# 检查工具是否安装
which nmap whatweb httpx subfinder

# 安装缺失的工具
sudo apt update
sudo apt install nmap whatweb

# Httpx 和 Subfinder 使用 Go 安装
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

---

### 问题 3: 权限不足

**症状：**
```
❌ Nmap 调用失败：permission denied
```

**解决：**

```bash
# 使用 sudo 运行
sudo python3 test/test_phase0_real_standalone.py

# 或者使用普通扫描模式（代码中已默认使用 -sT）
```

---

## 📚 相关文档

- 📖 [`SERVER_QUICK_TEST.md`](SERVER_QUICK_TEST.md) - 服务器快速测试指南
- 📖 [`test/FAQ.md`](test/FAQ.md) - 常见问题解答
- 📖 [`test/TEST_PHASE0_README.md`](test/TEST_PHASE0_README.md) - Phase-0 测试说明

---

## ✅ 成功标志

测试通过后应该看到：

```
📊 测试结果:
  • 发现资产数：3-10
  • 耗时：30 秒 -3 分钟

✅ 验证结果:
  ✅ WhatWeb: 检测到真实技术栈
  ✅ Nmap: 检测到真实端口

⏱️  时间分析:
  ✅ 时间正常：45.23 秒
     符合真实工具扫描的特征
```

---

**立即上传真实版本并测试！** 🚀

```bash
# 本地（Windows）
scp adapters/phase0_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 服务器
ssh ubuntu@119.45.255.144
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase0_real_standalone.py
```
