# 测试快速指南

## 🚀 快速开始（3 步）

### 步骤 1: 检查工具依赖

```bash
cd test
python check_dependencies.py
```

---

### 步骤 2: 测试真实工具调用

```bash
python test_phase0_real.py
```

**预期：** 30 秒 -3 分钟完成真实扫描

---

### 步骤 3: 查看详细文档

```bash
# Phase-0 详细测试指南
cat PHASE0_TEST_GUIDE.md

# 真实工具修复指南
cat REAL_TOOL_FIX_GUIDE.md

# 测试套件说明
cat README.md
```

---

## 📁 目录结构

```
test/
├── README.md                      # 测试套件说明（本文档）
├── PHASE0_TEST_GUIDE.md          # Phase-0 详细测试指南
├── REAL_TOOL_FIX_GUIDE.md        # 真实工具修复指南
├── SERVER_TEST_GUIDE.md          # 服务器测试指南
├── DEPLOYMENT_FIX_GUIDE.md       # 部署问题修复指南
│
├── check_dependencies.py         # 工具依赖检查
├── test_phase0_real.py           # Phase-0 真实工具测试
├── test_score_modes.py           # 风险评分模式对比
│
├── test_sqlmap_integration.py    # SQLMap 集成测试
├── test_zap_integration.py       # ZAP-CLI 集成测试
│
├── test_simple.py                # 简化版快速测试
├── test_e2e.py                   # 端到端完整测试
│
└── ... (其他测试脚本)
```

---

## 🎯 常用测试命令

### 快速验证（<30 秒）

```bash
cd test

# 1. 检查依赖
python check_dependencies.py

# 2. 基础功能测试
python test_basic.py

# 3. 评分模式测试
python test_score_modes.py
```

---

### 真实工具测试（1-3 分钟）

```bash
cd test

# 测试 Phase-0 真实工具调用
python test_phase0_real.py
```

---

### 完整测试（5-15 分钟）

```bash
cd test

# 端到端测试
python test_e2e.py

# 或者简化版
python test_simple.py
```

---

## 📊 测试对比

| 测试脚本 | 用途 | 预期时间 | 说明 |
|---------|------|---------|------|
| **check_dependencies.py** | 检查工具 | <1 秒 | 必做 |
| **test_phase0_real.py** | 真实工具 | 30 秒 -3 分 | ⭐ 推荐 |
| **test_score_modes.py** | 评分模式 | 5 秒 | 了解评分系统 |
| **test_sqlmap_integration.py** | SQLMap | 5-30 秒 | 工具集成 |
| **test_zap_integration.py** | ZAP-CLI | 5-30 秒 | 工具集成 |
| **test_simple.py** | 快速流程 | 1-2 分 | 简化版 |
| **test_e2e.py** | 完整流程 | 5-15 分 | 完整测试 |

---

## 🔍 如何判断测试成功？

### Phase-0 真实工具测试

**成功标志：**
- ✅ 耗时 > 10 秒（真实扫描需要时间）
- ✅ 检测到真实技术栈（如 Nginx 1.18.0）
- ✅ 端口数 > 2 个（不是固定的 80,443）
- ✅ 日志显示"执行命令：nmap ..."

**失败标志：**
- ❌ 耗时 < 1 秒（太快，是模拟数据）
- ❌ 只有 2 个固定端口
- ❌ 技术栈为空或过于简单

---

### 评分模式测试

**成功标志：**
- ✅ 显示两种模式的对比
- ✅ 默认是安全模式（分数越低越安全）
- ✅ 等级划分正确

---

## 🐛 常见问题

### Q1: 工具未找到怎么办？

**A:** 运行依赖检查，根据提示安装：

```bash
python check_dependencies.py
```

输出会显示每个工具的安装命令。

---

### Q2: 测试超时怎么办？

**A:** 可能是网络问题或目标不可达，尝试：

```bash
# 更换测试目标（编辑 test_phase0_real.py）
# 或者使用本地目标测试
python test_phase0_real.py  # 默认使用 example.com
```

---

### Q3: 编码错误怎么办？

**A:** Windows 设置 UTF-8：

```bash
$env:PYTHONIOENCODING="utf-8"
python test_phase0_real.py
```

---

## 📚 详细文档索引

| 文档 | 用途 | 阅读时机 |
|------|------|---------|
| **[README.md](README.md)** | 测试套件总览 | 首次使用 |
| **[PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md)** | Phase-0 详细指南 | 测试 Phase-0 |
| **[REAL_TOOL_FIX_GUIDE.md](REAL_TOOL_FIX_GUIDE.md)** | 真实工具修复 | 遇到问题 |
| **[SERVER_TEST_GUIDE.md](SERVER_TEST_GUIDE.md)** | 服务器测试 | 部署到服务器 |
| **[DEPLOYMENT_FIX_GUIDE.md](DEPLOYMENT_FIX_GUIDE.md)** | 部署问题修复 | 部署失败 |

---

## 🎯 推荐测试流程

### 新手流程

```bash
cd test

# 1. 检查依赖
python check_dependencies.py

# 2. 阅读详细指南
cat PHASE0_TEST_GUIDE.md

# 3. 测试 Phase-0
python test_phase0_real.py

# 4. 查看评分模式
python test_score_modes.py
```

---

### 开发者流程

```bash
cd test

# 1. 快速验证
python check_dependencies.py
python test_basic.py

# 2. 测试修改的功能
python test_<your_feature>.py

# 3. 完整测试
python test_e2e.py
```

---

### 部署前流程

```bash
cd test

# 1. 检查所有工具
python check_dependencies.py

# 2. 测试所有集成
python test_sqlmap_integration.py
python test_zap_integration.py
python test_phase0_real.py

# 3. 运行完整流程
python test_simple.py
```

---

## 📞 需要帮助？

1. **查看详细指南**
   - [PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md)
   - [README.md](README.md)

2. **收集诊断信息**
   ```bash
   python check_dependencies.py
   python test_phase0_real.py 2>&1 | tee test_output.log
   ```

3. **查看错误日志**
   ```bash
   grep -A 5 "Error\|Exception" test_output.log
   ```

---

**开始测试吧！** 🚀

```bash
cd test
python check_dependencies.py
python test_phase0_real.py
```
