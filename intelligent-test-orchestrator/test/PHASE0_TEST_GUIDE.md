# Phase-0 真实工具测试指南

## 📋 测试目标

验证 Phase-0 资产收集适配器是否正确调用真实工具，而非使用模拟数据。

---

## 🚀 快速测试（3 步）

### 步骤 1: 检查工具依赖

```bash
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 检查所需工具是否已安装
python check_dependencies.py
```

**预期输出：**

```
======================================================================
  智能编排器 - 工具依赖检查
======================================================================

======================================================================
  Phase-0 资产收集 工具依赖检查
======================================================================

✅ nmap            端口扫描和网络发现
   版本：Nmap version 7.94 ( https://nmap.org )

✅ whatweb         Web 技术识别
   版本：WhatWeb 0.5.5

❌ httpx           HTTP 探测工具
   安装：go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

❌ subfinder       子域名收集
   安装：go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

----------------------------------------------------------------------
总计：2/4 个工具已安装
⚠️  缺少 2 个工具，请安装后再使用
```

**如果工具未安装：**

```bash
# Windows 安装 Nmap
# 下载：https://nmap.org/download.html

# Windows 安装 WhatWeb (需要 Ruby)
gem install whatweb

# 或者先只测试已安装的工具
```

---

### 步骤 2: 运行 Phase-0 测试

```bash
# 运行真实工具测试
python test_phase0_real.py
```

**预期输出（成功）：**

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
2026-04-21 14:00:30 - 调用 WhatWeb: http://example.com
...

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
        - 22/tcp ssh OpenSSH 8.2

✅ 验证结果:
  ✅ WhatWeb: 检测到真实技术栈
  ✅ Nmap: 检测到真实端口

⏱️  时间分析:
  ✅ 时间正常：45.23 秒 (0.75 分钟)
     符合真实工具扫描的特征

======================================================================
  测试总结
======================================================================

✅ 测试完成！
```

**预期输出（失败 - 模拟数据）：**

```
📊 测试结果:
  • 发现资产数：2
  • 耗时：0.35 秒 (0.01 分钟)

⚠️  警告：耗时过短 (0.35 秒)，可能是模拟数据
     预期：Nmap 扫描至少需要 1-3 分钟
```

---

### 步骤 3: 分析结果

#### ✅ 成功标志

1. **时间合理**
   - 总耗时 > 10 秒
   - Nmap 扫描 > 5 秒
   - WhatWeb > 2 秒

2. **数据真实**
   - 检测到真实技术栈（Nginx, Apache 等）
   - 端口数 > 2 个
   - 有具体的版本信息

3. **日志正常**
   - 显示"执行命令：nmap ..."
   - 显示工具输出解析过程

#### ❌ 失败标志

1. **时间过短**
   - 总耗时 < 1 秒
   - 每个工具都是 0.3-0.5 秒

2. **数据简单**
   - 只有 2 个端口（80, 443）
   - 技术栈为空或过于通用

3. **无命令执行日志**
   - 没有"执行命令"的输出
   - 直接返回结果

---

## 🔧 常见问题排查

### 问题 1: 工具未安装

**症状：**
```
❌ nmap 调用失败：[Errno 2] No such file or directory: 'nmap'
```

**解决：**
```bash
# Windows
# 下载 Nmap: https://nmap.org/download.html
# 安装后添加到 PATH

# Linux/Mac
sudo apt install nmap
sudo apt install whatweb

# 或者使用 Go 安装
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
```

---

### 问题 2: 权限不足

**症状：**
```
❌ Nmap 调用失败：permission denied
```

**解决：**
```bash
# 使用普通扫描（不需要 root）
# 代码中已使用 -sT 而不是 -sS

# 或者使用 sudo
sudo python test_phase0_real.py
```

---

### 问题 3: 网络超时

**症状：**
```
⚠️  Nmap 执行失败：Command timed out
```

**解决：**
```python
# 在代码中增加超时时间
process = await asyncio.wait_for(
    asyncio.create_subprocess_shell(cmd),
    timeout=300  # 改为 5 分钟
)
```

---

### 问题 4: 目标不可达

**症状：**
```
⚠️  未发现任何资产
```

**解决：**
```bash
# 测试目标是否可达
ping example.com

# 更换测试目标
python test_phase0_real.py  # 脚本中有多个测试目标
```

---

## 📊 性能基准

### 不同目标的预期扫描时间

| 目标类型 | 预期时间 | 说明 |
|---------|---------|------|
| **本地目标** (localhost) | 5-15 秒 | 无网络延迟 |
| **内网目标** | 30 秒 -2 分钟 | 内网速度快 |
| **公网小网站** | 1-3 分钟 | 标准扫描 |
| **公网大网站** | 3-10 分钟 | 多端口、多服务 |
| **WAF 保护目标** | 5-20 分钟 | 可能被限流 |

---

## 🎯 对比测试：模拟 vs 真实

### 运行模拟版本

```bash
# 临时修改导入
python -c "
from adapters.phase0_adapter import Phase0Adapter  # 模拟版本
import asyncio

async def test():
    adapter = Phase0Adapter()
    assets = await adapter.collect('http://example.com')
    print(f'模拟模式：{len(assets)} 个资产')

asyncio.run(test())
"
```

**预期：** 1-2 秒完成

---

### 运行真实版本

```bash
python test_phase0_real.py
```

**预期：** 30 秒 -3 分钟完成

---

### 结果对比

| 指标 | 模拟模式 | 真实模式 | 差距 |
|------|---------|---------|------|
| **时间** | 1-2 秒 | 30-180 秒 | **30-90 倍** |
| **端口数** | 2 个（固定） | 实际扫描 | **真实** |
| **技术栈** | 简单/通用 | 详细具体 | **真实** |
| **子域名** | 3 个（固定） | 实际收集 | **真实** |

---

## 🚀 下一步

### Phase-0 测试通过后

1. **确认结果**
   - ✅ 时间合理（>10 秒）
   - ✅ 数据真实（详细、具体）
   - ✅ 日志正常（有命令执行）

2. **部署到服务器**
   ```bash
   # 上传真实版本
   scp adapters/phase0_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
   
   # SSH 登录
   ssh ubuntu@119.45.255.144
   
   # 备份旧版本
   cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
   cp phase0_adapter.py phase0_adapter_mock.py
   cp phase0_adapter_real.py phase0_adapter.py
   
   # 重启 OpenClaw
   pm2 restart openclaw
   ```

3. **继续实现 Phase-2**
   - 等待 Phase-0 验证通过
   - 我再帮你创建 Phase-2 真实版本

---

## 📞 获取帮助

### 如果测试失败

请提供以下信息：

1. **工具检查结果**
   ```bash
   python check_dependencies.py
   ```

2. **测试输出**
   ```bash
   python test_phase0_real.py 2>&1 | tee test_output.log
   ```

3. **系统信息**
   ```bash
   # Windows
   systeminfo
   
   # Linux
   uname -a
   ```

---

## 📚 相关文档

- 📖 [REAL_TOOL_FIX_GUIDE.md](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\REAL_TOOL_FIX_GUIDE.md) - 完整修复指南
- 📖 [phase0_adapter_real.py](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase0_adapter_real.py) - Phase-0 真实版本源码
- 🧪 [test_phase0_real.py](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test_phase0_real.py) - 测试脚本
- 🔧 [check_dependencies.py](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\check_dependencies.py) - 依赖检查脚本

---

**祝你测试顺利！** 🎉

如果 Phase-0 测试通过，告诉我，我会继续帮你实现 Phase-2 和 Phase-3 的真实版本！
