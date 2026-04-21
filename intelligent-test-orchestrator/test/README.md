# 智能编排器 - 测试套件

本目录包含所有测试相关的脚本和文档。

---

## 📁 文件结构

### 测试脚本

#### Phase 测试
- **`test_phase0_real.py`** - Phase-0 真实工具调用测试
- **`check_dependencies.py`** - 工具依赖检查脚本

#### 集成测试
- **`test_sqlmap_integration.py`** - SQLMap 集成测试
- **`test_zap_integration.py`** - ZAP-CLI 集成测试
- **`test_score_modes.py`** - 风险评分模式对比测试

#### 端到端测试
- **`test_e2e.py`** - 端到端完整流程测试
- **`test_simple.py`** - 简化版快速测试
- **`test_task27.py`** - Task 27 专项测试
- **`test_task28_e2e.py`** - Task 28 端到端测试

#### 功能测试
- **`test_basic.py`** - 基础功能测试
- **`test_pdf_generation.py`** - PDF 报告生成测试
- **`test_encoding.py`** - 编码问题测试

#### OpenClaw 测试
- **`test_openclaw_simulate.py`** - OpenClaw 调用模拟测试

---

### 文档指南

#### 测试指南
- **`PHASE0_TEST_GUIDE.md`** - Phase-0 真实工具测试指南
- **`SERVER_TEST_GUIDE.md`** - 服务器端手动测试指南
- **`DEPLOYMENT_FIX_GUIDE.md`** - 部署问题诊断与修复指南
- **`REAL_TOOL_FIX_GUIDE.md`** - 真实工具调用修复指南
- **`RUN_GUIDE.md`** - 运行指南

#### 其他文档
- **`README.md`** - 项目主文档（在上级目录）
- **`RISK_SCORE_CONFIG.md`** - 风险评分配置指南（在上级目录）

---

## 🚀 快速开始

### 1. 检查工具依赖

```bash
# 从项目根目录运行
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查依赖
python test/check_dependencies.py
```

**重要：** 所有测试脚本都应该从**项目根目录**运行，而不是从 `test` 目录运行！

```bash
# ✅ 正确：从根目录运行
python test/test_phase0_real.py

# ❌ 错误：从 test 目录运行（会报 ModuleNotFoundError）
cd test
python test_phase0_real.py
```

**输出示例：**
```
======================================================================
  智能编排器 - 工具依赖检查
======================================================================

======================================================================
  Phase-0 资产收集 工具依赖检查
======================================================================

✅ nmap            端口扫描和网络发现
   版本：Nmap version 7.94

✅ whatweb         Web 技术识别
   版本：WhatWeb 0.5.5

❌ httpx           HTTP 探测工具
   安装：go install -v ...
```

---

### 2. 测试 Phase-0 真实工具调用

```bash
python test_phase0_real.py
```

**预期：**
- ⏱️ 耗时：30 秒 -3 分钟（真实扫描）
- 📊 发现：真实的端口、技术栈、子域名
- ✅ 验证：确认调用的是真实工具，不是模拟数据

---

### 3. 测试风险评分模式

```bash
python test_score_modes.py
```

**输出示例：**
```
======================================================================
  风险评分模式对比测试
======================================================================

⚠️  威胁模式（分数越高越危险）
----------------------------------------------------------------------
分数         等级              描述
----------------------------------------------------------------------
12.5       🟢 安全            非常安全的目标
35.8       🟡 低风险           低风险目标

🔒 安全模式（分数越低越安全，默认）
----------------------------------------------------------------------
分数         等级              描述
----------------------------------------------------------------------
12.5       🔴 危急            非常安全的目标
35.8       🟣 高风险           低风险目标
```

---

### 4. 运行集成测试

```bash
# SQLMap 集成测试
python test_sqlmap_integration.py

# ZAP-CLI 集成测试
python test_zap_integration.py
```

---

### 5. 端到端测试

```bash
# 简化版快速测试
python test_simple.py

# 完整流程测试
python test_e2e.py
```

---

## 📋 测试分类

### 按测试类型

| 类型 | 脚本 | 用途 | 耗时 |
|------|------|------|------|
| **依赖检查** | `check_dependencies.py` | 检查工具是否安装 | <1 秒 |
| **单元测试** | `test_*.py` | 测试特定功能 | 1-10 秒 |
| **集成测试** | `test_*_integration.py` | 测试工具集成 | 5-30 秒 |
| **真实工具** | `test_phase0_real.py` | 测试真实工具调用 | 30 秒 -3 分钟 |
| **端到端** | `test_e2e.py`, `test_simple.py` | 测试完整流程 | 1-10 分钟 |

---

### 按测试阶段

| 阶段 | 脚本 | 测试内容 |
|------|------|---------|
| **Phase-0** | `test_phase0_real.py` | 资产收集（Nmap, WhatWeb 等） |
| **Phase-1** | `test_score_modes.py` | 风险画像评估 |
| **Phase-2** | `test_sqlmap_integration.py`, `test_zap_integration.py` | 漏洞检测工具 |
| **完整流程** | `test_simple.py`, `test_e2e.py` | 从资产收集到报告生成 |

---

## 🎯 测试场景

### 场景 1: 开发环境快速验证

```bash
# 1. 检查依赖
python check_dependencies.py

# 2. 运行快速测试
python test_basic.py

# 3. 测试评分模式
python test_score_modes.py
```

**总耗时：** <30 秒

---

### 场景 2: 验证真实工具调用

```bash
# 1. 确保工具已安装
python check_dependencies.py

# 2. 测试 Phase-0 真实调用
python test_phase0_real.py
```

**总耗时：** 1-3 分钟

---

### 场景 3: 完整功能验证

```bash
# 运行端到端测试
python test_e2e.py
```

**总耗时：** 5-15 分钟

---

### 场景 4: 部署前验证

```bash
# 1. 检查依赖
python check_dependencies.py

# 2. 测试所有集成功能
python test_sqlmap_integration.py
python test_zap_integration.py
python test_phase0_real.py

# 3. 运行完整流程
python test_simple.py
```

**总耗时：** 5-10 分钟

---

## 🐛 故障排查

### 问题 1: 工具未找到

**症状：**
```
❌ nmap 调用失败：[Errno 2] No such file or directory
```

**解决：**
```bash
# 检查工具安装
python check_dependencies.py

# 根据提示安装缺失的工具
```

---

### 问题 2: 测试超时

**症状：**
```
⚠️  测试超时，已终止
```

**解决：**
```bash
# 增加超时时间（编辑测试脚本）
# 或者使用更小的测试目标
python test_phase0_real.py  # 默认使用 example.com
```

---

### 问题 3: 编码错误

**症状：**
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**解决：**
```bash
# Windows PowerShell 设置 UTF-8
$env:PYTHONIOENCODING="utf-8"
python test_phase0_real.py
```

---

## 📊 测试报告

每次测试后，查看输出日志：

```bash
# 保存测试输出
python test_phase0_real.py 2>&1 | tee test_output.log

# 查看关键信息
grep -E "✅|❌|⚠️" test_output.log
```

---

## 🔧 维护指南

### 添加新测试

1. **创建测试文件**
   ```bash
   # 命名规范：test_<功能>.py
   touch test_new_feature.py
   ```

2. **编写测试用例**
   ```python
   #!/usr/bin/env python3
   # -*- coding: utf-8 -*-
   """
   新功能测试
   """
   
   import asyncio
   import sys
   from pathlib import Path
   
   sys.path.insert(0, str(Path(__file__).parent.parent))
   
   async def test_new_feature():
       """测试新功能"""
       print("=" * 70)
       print("  新功能测试")
       print("=" * 70)
       
       # 测试代码...
       
   if __name__ == '__main__':
       asyncio.run(test_new_feature())
   ```

3. **添加到文档**
   - 在本 README 中添加测试说明
   - 更新相关指南文档

---

### 更新现有测试

定期检查和更新测试脚本：

```bash
# 检查测试脚本最后修改时间
dir test_*.py | Select-Object Name, LastWriteTime
```

---

## 📚 相关文档

- 📖 [PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md) - Phase-0 详细测试指南
- 📖 [REAL_TOOL_FIX_GUIDE.md](REAL_TOOL_FIX_GUIDE.md) - 真实工具修复指南
- 📖 [SERVER_TEST_GUIDE.md](SERVER_TEST_GUIDE.md) - 服务器测试指南
- 📖 [DEPLOYMENT_FIX_GUIDE.md](DEPLOYMENT_FIX_GUIDE.md) - 部署问题修复
- 📖 [../RISK_SCORE_CONFIG.md](../RISK_SCORE_CONFIG.md) - 风险评分配置

---

## 🎓 最佳实践

### 1. 定期运行测试

```bash
# 每天开发前
python check_dependencies.py
python test_basic.py

# 每周完整测试
python test_e2e.py
```

### 2. 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 保存测试记录

```bash
# 创建测试记录目录
mkdir test\logs

# 保存测试输出
python test_phase0_real.py > test\logs\phase0_$(Get-Date -Format "yyyyMMdd_HHmmss").log 2>&1
```

---

## 📞 获取帮助

如果测试遇到问题：

1. **查看详细指南**
   - [PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md)
   - [REAL_TOOL_FIX_GUIDE.md](REAL_TOOL_FIX_GUIDE.md)

2. **收集诊断信息**
   ```bash
   python check_dependencies.py
   python test_phase0_real.py 2>&1 | tee test_output.log
   ```

3. **查看错误日志**
   ```bash
   grep -A 5 "Error\|Exception\|Failed" test_output.log
   ```

---

**祝你测试顺利！** 🎉
