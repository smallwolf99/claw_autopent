# 服务器测试快速指南

## 🚀 快速解决（3 步）

### 步骤 1: 使用独立版本（已修复路径问题）

我已经创建了一个**完全独立**的测试脚本，不需要修改 Python 路径：

```bash
# 在服务器上运行
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase0_real_standalone.py
```

**特点：**
- ✅ 自动查找项目根目录
- ✅ 可以在任何位置运行
- ✅ 不依赖 Python 路径设置

---

### 步骤 2: 上传新版本到服务器

#### 方法 A: 使用 SCP 命令（推荐）

在**本地**运行：

```bash
# Windows PowerShell 或 Linux/Mac
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 上传独立版本
scp test/test_phase0_real_standalone.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/
```

---

#### 方法 B: 使用部署脚本

```bash
# 赋予执行权限
chmod +x deploy_test.sh

# 运行部署
./deploy_test.sh
```

---

#### 方法 C: 手动复制（如果无法 SCP）

1. **复制文件内容**
   - 打开 `test/test_phase0_real_standalone.py`
   - 复制全部内容

2. **SSH 登录服务器**
   ```bash
   ssh ubuntu@119.45.255.144
   ```

3. **创建文件**
   ```bash
   cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test
   nano test_phase0_real_standalone.py
   ```

4. **粘贴内容并保存**
   - 按 `Ctrl+O` 保存
   - 按 `Ctrl+X` 退出

---

### 步骤 3: 在服务器上运行测试

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 进入项目目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行独立版本测试
python3 test/test_phase0_real_standalone.py
```

---

## ✅ 预期输出

```
✅ 项目根目录：/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
✅ 成功导入 Phase0Adapter
======================================================================
  Phase-0 资产收集 - 真实工具调用测试
======================================================================

🎯 测试目标：http://example.com
----------------------------------------------------------------------
📡 开始资产收集...

2026-04-21 14:00:00 - Phase-0 资产收集适配器初始化完成（真实工具调用）
2026-04-21 14:00:00 - 调用 Nmap: http://example.com
2026-04-21 14:00:00 - 执行命令：nmap -sV -sC -T4 --open -oX - http://example.com

📊 测试结果:
  • 发现资产数：3
  • 耗时：45.23 秒 (0.75 分钟)

✅ 验证结果:
  ✅ WhatWeb: 检测到真实技术栈
  ✅ Nmap: 检测到真实端口

⏱️  时间分析:
  ✅ 时间正常：45.23 秒 (0.75 分钟)
     符合真实工具扫描的特征
```

---

## 🔧 如果还是报错

### 错误 1: 仍然报 ModuleNotFoundError

**症状：**
```
ModuleNotFoundError: No module named 'adapters'
```

**解决：**

```bash
# 1. 检查文件是否存在
ls -la /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 2. 检查 Python 路径
python3 -c "import sys; print('\n'.join(sys.path))"

# 3. 手动设置 PYTHONPATH
export PYTHONPATH=/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator:$PYTHONPATH

# 4. 再次运行测试
python3 test/test_phase0_real_standalone.py
```

---

### 错误 2: 文件不存在

**症状：**
```
python3: can't open file 'test/test_phase0_real_standalone.py'
```

**解决：**

```bash
# 1. 检查文件列表
ls -la test/

# 2. 如果文件不存在，重新上传
# 在本地运行：
scp test/test_phase0_real_standalone.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/
```

---

### 错误 3: 权限问题

**症状：**
```
Permission denied
```

**解决：**

```bash
# 赋予执行权限
chmod +x test/test_phase0_real_standalone.py

# 运行
python3 test/test_phase0_real_standalone.py
```

---

## 📊 测试对比

| 版本 | 文件名 | 特点 | 推荐度 |
|------|--------|------|--------|
| **独立版本** | `test_phase0_real_standalone.py` | 自动查找路径，任何位置可运行 | ⭐⭐⭐⭐⭐ |
| **修复版本** | `test_phase0_real.py` | 需要从根目录运行 | ⭐⭐⭐⭐ |
| **原始版本** | （旧版本） | 会报错 | ❌ |

---

## 🎯 快速命令参考

### 本地（Windows）

```bash
# 上传文件
scp test/test_phase0_real_standalone.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/

# 或者使用部署脚本
./deploy_test.sh
```

---

### 服务器（Ubuntu）

```bash
# 进入项目目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行独立版本测试
python3 test/test_phase0_real_standalone.py

# 检查工具依赖
python3 test/check_dependencies.py

# 查看 Python 路径
python3 -c "import sys; print('\n'.join(sys.path))"
```

---

## 📚 相关文档

- 📖 [`test/README.md`](test/README.md) - 测试套件说明
- 📖 [`test/FAQ.md`](test/FAQ.md) - 常见问题解答
- 📖 [`test/PATH_FIX.md`](test/PATH_FIX.md) - 路径修复说明
- 📖 [`deploy_test.sh`](deploy_test.sh) - 部署脚本

---

## 🆘 需要帮助？

如果以上方法都无法解决：

```bash
# 1. 收集诊断信息
ssh ubuntu@119.45.255.144

# 2. 检查目录结构
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
ls -la

# 3. 检查 adapters 目录
ls -la adapters/

# 4. 检查测试目录
ls -la test/

# 5. 运行诊断命令
python3 -c "
import sys
from pathlib import Path
print('当前目录:', Path.cwd())
print('Python 路径:')
for p in sys.path:
    print('  ', p)
print()
print('检查 adapters 目录:', (Path.cwd() / 'adapters').exists())
print('检查 test 目录:', (Path.cwd() / 'test').exists())
"

# 6. 保存输出
python3 test/test_phase0_real_standalone.py 2>&1 | tee test_output.log
```

---

**立即运行测试！** 🚀

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase0_real_standalone.py
```
