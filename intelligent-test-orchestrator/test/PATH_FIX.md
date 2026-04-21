# 路径问题修复说明

## 🐛 问题描述

在服务器上运行 `test_phase0_real.py` 时报错：

```bash
$ python test/test_phase0_real.py
ModuleNotFoundError: No module named 'adapters'
```

---

## 🔍 原因分析

测试脚本在 `test/` 子目录中，默认只会在当前目录查找模块。

**目录结构：**
```
intelligent-test-orchestrator/
├── adapters/
│   └── phase0_adapter_real.py
└── test/
    └── test_phase0_real.py
```

**原始代码：**
```python
# ❌ 错误：只添加 test 目录到路径
sys.path.insert(0, str(Path(__file__).parent))
# 结果：只能找到 test/ 目录，找不到 adapters/
```

---

## ✅ 修复方案

### 修改 test/test_phase0_real.py

**修复后代码：**
```python
# ✅ 正确：添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# 结果：可以找到 intelligent-test-orchestrator/adapters/
```

**解释：**
- `Path(__file__)` = test/test_phase0_real.py
- `Path(__file__).parent` = test/
- `Path(__file__).parent.parent` = 项目根目录
- 添加项目根目录到 Python 路径后，就能找到 `adapters/` 模块了

---

## 🚀 运行方法

### 方法 1: 从项目根目录运行（推荐）

```bash
# 1. 进入项目根目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 2. 运行测试
python test/test_phase0_real.py
```

---

### 方法 2: 使用绝对路径

```bash
python /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/test_phase0_real.py
```

---

### 方法 3: 设置 PYTHONPATH

```bash
# 设置环境变量
export PYTHONPATH=/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator:$PYTHONPATH

# 然后运行
python test/test_phase0_real.py
```

---

## 📋 其他测试脚本的运行方法

所有测试脚本都应该从**项目根目录**运行：

```bash
# ✅ 正确
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

python test/check_dependencies.py
python test/test_phase0_real.py
python test/test_basic.py
python test/test_e2e.py

# ❌ 错误（会报错）
cd test
python test_phase0_real.py  # ModuleNotFoundError
```

---

## 📚 相关文档

- 📖 [FAQ.md](FAQ.md) - 常见问题解答
- 📖 [TEST_PHASE0_README.md](TEST_PHASE0_README.md) - Phase-0 测试详细说明
- 📖 [README.md](README.md) - 测试套件说明

---

## ✅ 已修复的文件

- ✅ `test/test_phase0_real.py` - 已修复路径问题
- ✅ `test/README.md` - 已添加运行说明
- ✅ `test/FAQ.md` - 新增常见问题解答
- ✅ `test/TEST_PHASE0_README.md` - 新增 Phase-0 详细说明

---

## 🎯 下一步

1. **在服务器上测试**

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python test/test_phase0_real.py
```

2. **预期输出**

```
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

3. **如果还有问题**

查看 [FAQ.md](FAQ.md) 获取帮助。

---

**修复完成！** 🎉

现在可以在服务器上运行测试了。
