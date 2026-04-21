# Phase-0 真实工具调用测试

## 📋 用途

验证 Phase-0 资产收集适配器是否正确调用真实工具（Nmap、WhatWeb 等），而非使用模拟数据。

---

## 🚀 运行方法

### 方法 1: 从项目根目录运行（推荐）

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行测试
python test/test_phase0_real.py
```

---

### 方法 2: 直接从 test 目录运行

```bash
cd test

# 运行测试
python test_phase0_real.py
```

---

### 方法 3: 使用绝对路径

```bash
python /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/test_phase0_real.py
```

---

## ✅ 预期输出

### 成功标志

```
======================================================================
  Phase-0 资产收集 - 真实工具调用测试
======================================================================

🎯 测试目标：http://example.com
----------------------------------------------------------------------
📡 开始资产收集...

2026-04-21 14:00:00 - Phase-0 资产收集适配器初始化完成（真实工具调用）
2026-04-21 14:00:00 - 开始资产收集：http://example.com
2026-04-21 14:00:00 - 调用 Nmap: http://example.com
2026-04-21 14:00:00 - 执行命令：nmap -sV -sC -T4 --open -oX - http://example.com

📊 测试结果:
  • 发现资产数：3
  • 耗时：45.23 秒 (0.75 分钟)

📋 资产详情:

  [1] WEB
      URL: http://example.com
      状态码：200
      标题：Example Domain
      技术栈:
        - Nginx 1.18.0
        - PHP 7.4.3

  [2] PORT
      主机：example.com
      开放端口 (3 个):
        - 80/tcp http nginx 1.18.0
        - 443/tcp https nginx 1.18.0

✅ 验证结果:
  ✅ WhatWeb: 检测到真实技术栈
  ✅ Nmap: 检测到真实端口

⏱️  时间分析:
  ✅ 时间正常：45.23 秒 (0.75 分钟)
     符合真实工具扫描的特征
```

---

### 失败标志

#### 错误 1: ModuleNotFoundError

```
Traceback (most recent call last):
  File "test/test_phase0_real.py", line 17, in <module>
    from adapters.phase0_adapter_real import Phase0Adapter
ModuleNotFoundError: No module named 'adapters'
```

**解决：** 从项目根目录运行，而不是从 test 目录运行：

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python test/test_phase0_real.py
```

---

#### 错误 2: 工具未找到

```
❌ nmap 调用失败：[Errno 2] No such file or directory: 'nmap'
```

**解决：** 安装缺失的工具

```bash
# 检查工具依赖
python test/check_dependencies.py

# 根据提示安装缺失的工具
sudo apt install nmap
sudo apt install whatweb
```

---

#### 错误 3: 时间过短（模拟数据）

```
⏱️  时间分析:
  ⚠️  警告：耗时过短 (0.35 秒)，可能是模拟数据
     预期：Nmap 扫描至少需要 1-3 分钟
```

**解决：** 确认使用的是 `phase0_adapter_real.py` 而不是 `phase0_adapter.py`

---

## 📊 测试对比

| 指标 | 模拟模式 | 真实模式 | 如何区分 |
|------|---------|---------|----------|
| **总耗时** | 1-2 秒 | 30 秒 -3 分钟 | **最明显！** |
| **Nmap 扫描** | 0.3 秒 | 10 秒 -2 分钟 | 看日志 |
| **端口数量** | 2 个（80,443） | 实际扫描结果 | 数端口 |
| **技术栈** | 通用/简单 | 具体版本 | 看详情 |
| **子域名** | 3 个（固定） | 实际收集 | 数数量 |

---

## 🔧 故障排查

### 问题 1: 导入错误

**症状：** `ModuleNotFoundError: No module named 'adapters'`

**原因：** 从 test 目录直接运行，Python 路径不正确

**解决：**

```bash
# 错误方式
cd test
python test_phase0_real.py

# 正确方式
cd ..  # 回到项目根目录
python test/test_phase0_real.py
```

---

### 问题 2: 工具未安装

**症状：** `[Errno 2] No such file or directory`

**解决：**

```bash
# 检查工具
python test/check_dependencies.py

# 安装 Nmap
sudo apt install nmap

# 安装 WhatWeb
sudo apt install whatweb

# 或者使用 Go 安装其他工具
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

---

### 问题 3: 权限不足

**症状：** `permission denied`

**解决：**

```bash
# 使用普通扫描（代码中已使用 -sT 而不是 -sS）
# 或者使用 sudo
sudo python test/test_phase0_real.py
```

---

### 问题 4: 网络超时

**症状：** `Command timed out`

**解决：**

```bash
# 测试目标是否可达
ping example.com

# 更换测试目标（编辑 test_phase0_real.py）
# 或者使用内网目标
```

---

## 📚 相关文档

- 📖 [README.md](README.md) - 测试套件完整说明
- 📖 [PHASE0_TEST_GUIDE.md](PHASE0_TEST_GUIDE.md) - Phase-0 详细测试指南
- 📖 [REAL_TOOL_FIX_GUIDE.md](REAL_TOOL_FIX_GUIDE.md) - 真实工具修复指南
- 📖 [../adapters/phase0_adapter_real.py](../adapters/phase0_adapter_real.py) - Phase-0 源码

---

## 🎯 下一步

测试通过后：

1. **确认结果**
   - ✅ 时间合理（>10 秒）
   - ✅ 数据真实（详细、具体）
   - ✅ 日志正常（有命令执行）

2. **部署到服务器**
   ```bash
   # 如果已在服务器，跳过此步
   
   # 上传真实版本
   scp adapters/phase0_adapter_real.py ubuntu@server:/path/to/intelligent-test-orchestrator/adapters/
   
   # 重启 OpenClaw
   pm2 restart openclaw
   ```

3. **继续实现 Phase-2**
   - 等待 Phase-0 验证通过
   - 创建 Phase-2 真实版本

---

**祝你测试顺利！** 🎉
