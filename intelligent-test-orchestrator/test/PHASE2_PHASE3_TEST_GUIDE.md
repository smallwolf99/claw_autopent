# Phase-2 & Phase-3 真实工具测试指南

## 📋 测试目标

验证 Phase-2 漏洞检测适配器和 Phase-3 漏洞验证器是否正确调用真实工具。

---

## 🚀 快速开始

### 前提条件

确保以下工具已安装：

```bash
# 检查工具
which nuclei afrog nikto zap-cli sqlmap

# 安装缺失的工具
sudo apt install nikto
pip3 install zap-cli

# Go 工具安装
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/zan8in/afrog/v2@latest
git clone https://github.com/sqlmapproject/sqlmap.git
```

---

### 运行测试

```bash
# 从项目根目录运行
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行 Phase-2 & Phase-3 测试
python3 test/test_phase2_phase3_real.py
```

---

## ✅ 预期输出

### Phase-2 测试

```
======================================================================
  Phase-2 漏洞检测 - 真实工具测试
======================================================================

✅ 项目根目录：/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

🎯 测试目标：http://example.com
📡 开始漏洞检测...

2026-04-21 15:00:00 - Phase-2 漏洞检测适配器初始化完成（真实工具调用）
2026-04-21 15:00:00 - 调用 Nuclei: http://example.com
2026-04-21 15:00:00 - 执行命令：nuclei -u http://example.com -json -silent -timeout 10
...

📊 测试结果:
  • 发现漏洞数：5-20
  • 耗时：120.45 秒 (2.01 分钟)

📋 漏洞详情:

  [1] XSS Vulnerability
      严重程度：MEDIUM
      检测工具：nuclei
      置信度：90%
      描述：Cross-site scripting vulnerability found...

  [2] SQL Injection
      严重程度：HIGH
      检测工具：sqlmap
      置信度：95%
      ...

✅ 验证结果:
  ✅ 使用的工具：nuclei, sqlmap, nikto
  ✅ 检测到 15 个漏洞

⏱️  时间分析:
  ✅ 时间合理：120.45 秒
```

---

### Phase-3 测试

```
======================================================================
  Phase-3 漏洞验证 - 真实工具测试
======================================================================

🔍 开始验证 15 个漏洞...

2026-04-21 15:02:00 - Phase-3 漏洞验证器初始化完成（真实工具调用）
2026-04-21 15:02:00 - 验证漏洞：XSS Vulnerability (类型：xss)
...

📊 验证结果:
  • 验证漏洞数：15
  • 已确认：12
  • 误报：3
  • 耗时：45.67 秒

📋 验证详情:

  [1] ✅ XSS Vulnerability
      严重程度：MEDIUM
      置信度：85%
      利用链：4 步

  [2] ❌ SQL Injection
      严重程度：HIGH
      置信度：30%
      误报原因：SQLMap 未能复现漏洞

✅ 验证总结:
  • 验证通过率：12/15 (80.0%)
  ✅ 成功验证 12 个真实漏洞
  ⚠️  3 个漏洞可能是误报
```

---

## 📊 测试指标

### Phase-2 漏洞检测

| 指标 | 预期值 | 说明 |
|------|--------|------|
| **耗时** | 1-10 分钟 | 取决于目标数量 |
| **漏洞数** | 5-50 个 | 取决于目标安全性 |
| **工具调用** | 3-5 个 | Nuclei, Nikto, SQLMap 等 |
| **置信度** | >0.7 | 平均置信度 |

---

### Phase-3 漏洞验证

| 指标 | 预期值 | 说明 |
|------|--------|------|
| **耗时** | 30 秒 -5 分钟 | 取决于漏洞数量 |
| **验证通过率** | 60-90% | 真实漏洞比例 |
| **误报率** | 10-40% | 正常范围 |
| **置信度提升** | +10-20% | 验证后置信度提高 |

---

## 🔍 结果分析

### 成功标志

#### Phase-2

- ✅ 耗时 > 60 秒（真实扫描需要时间）
- ✅ 检测到多个漏洞（>3 个）
- ✅ 使用多个工具（Nuclei, Nikto, SQLMap 等）
- ✅ 漏洞有详细描述和证据
- ✅ 置信度 > 0.7

---

#### Phase-3

- ✅ 验证通过率 > 50%
- ✅ 误报有明确原因
- ✅ 已验证漏洞有利用链
- ✅ 置信度合理（0.3-0.95）

---

### 失败标志

#### Phase-2

- ❌ 耗时 < 10 秒（太快，可能未真实调用）
- ❌ 没有检测到任何漏洞
- ❌ 工具调用失败日志
- ❌ 漏洞信息不完整

**可能原因：**
1. 工具未安装
2. 网络连接问题
3. 目标不可达
4. 工具配置问题

---

#### Phase-3

- ❌ 验证通过率 < 20%
- ❌ 所有漏洞都被标记为误报
- ❌ 验证过程没有调用工具

**可能原因：**
1. 验证规则过于严格
2. 工具调用失败
3. 漏洞证据不足

---

## 🛠️ 故障排查

### 问题 1: 工具未找到

**症状：**
```
❌ Nuclei 调用失败：[Errno 2] No such file or directory
```

**解决：**
```bash
# 检查工具安装
which nuclei afrog nikto zap-cli sqlmap

# 安装缺失的工具
sudo apt update
sudo apt install nikto

# Go 工具
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/zan8in/afrog/v2@latest

# SQLMap
git clone https://github.com/sqlmapproject/sqlmap.git
export PATH=$PATH:/path/to/sqlmap

# ZAP-CLI
pip3 install zap-cli
```

---

### 问题 2: 权限不足

**症状：**
```
❌ SQLMap 调用失败：permission denied
```

**解决：**
```bash
# 赋予执行权限
chmod +x /path/to/sqlmap/sqlmap.py

# 或使用 sudo
sudo python3 test/test_phase2_phase3_real.py
```

---

### 问题 3: 网络超时

**症状：**
```
⚠️  Nuclei 扫描超时：http://example.com
```

**解决：**
```bash
# 测试目标是否可达
curl http://example.com

# 更换测试目标（编辑测试脚本）
nano test/test_phase2_phase3_real.py
# 修改 test_assets 列表
```

---

### 问题 4: ZAP-CLI 配置问题

**症状：**
```
❌ ZAP-CLI 调用失败
```

**解决：**
```bash
# 启动 ZAP 代理
zap-cli start
zap-cli quick-scan --help

# 配置 ZAP
zap-cli settings set api-key your-api-key
```

---

## 📚 工具说明

### Phase-2 集成工具

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| **Nuclei** | 模板化漏洞扫描 | `go install nuclei` |
| **Afrog** | PoC 验证扫描 | `go install afrog` |
| **Nikto** | Web 漏洞扫描 | `apt install nikto` |
| **ZAP-CLI** | OWASP ZAP 命令行 | `pip3 install zap-cli` |
| **SQLMap** | SQL 注入检测 | `git clone sqlmap` |

---

### Phase-3 验证方法

| 漏洞类型 | 验证方法 | 工具 |
|---------|---------|------|
| **SQL 注入** | SQLMap 复现 | SQLMap |
| **XSS** | Payload 检测 | 正则匹配 |
| **路径遍历** | 特征匹配 | 正则匹配 |
| **命令注入** | 特征匹配 | 正则匹配 |
| **SSRF** | 特征匹配 | 正则匹配 |

---

## 🎯 测试最佳实践

### 1. 选择合适的测试目标

```python
# 推荐测试目标
test_assets = [
    {"type": "web", "url": "http://example.com"},  # 安全的公共测试目标
    {"type": "web", "url": "http://testphp.vulnweb.com"},  # 漏洞测试站点
]

# ❌ 避免测试生产环境
# ❌ 避免未授权测试
```

---

### 2. 控制测试范围

```bash
# 限制并发数量
# 编辑 phase2_adapter_real.py，修改并发参数

# 设置超时时间
# 代码中已默认设置合理超时
```

---

### 3. 保存测试记录

```bash
# 保存测试输出
python3 test/test_phase2_phase3_real.py 2>&1 | tee test_output.log

# 分析结果
grep -E "✅|❌|⚠️" test_output.log
```

---

## 📊 性能基准

### 不同规模目标的预期时间

| 目标数量 | Phase-2 耗时 | Phase-3 耗时 | 总耗时 |
|---------|------------|------------|--------|
| **1 个 Web** | 1-3 分钟 | 30-60 秒 | 2-4 分钟 |
| **5 个 Web** | 5-15 分钟 | 2-5 分钟 | 7-20 分钟 |
| **10 个 Web** | 10-30 分钟 | 5-10 分钟 | 15-40 分钟 |

---

## 🔧 配置选项

### 自定义测试策略

```python
# 在测试脚本中指定工具
test_strategy = {
    'tools': ['nuclei', 'nikto'],  # 只使用特定工具
    'timeout': 300,  # 超时时间
    'severity_filter': ['high', 'critical']  # 只检测高危漏洞
}

vulnerabilities = await adapter.detect(assets, test_strategy)
```

---

### 调整验证规则

```python
# 在 phase3_validator_real.py 中
self.verification_rules = {
    'critical': {'min_tools': 2, 'require_exploit': True},
    'high': {'min_tools': 2, 'require_exploit': False},
    'medium': {'min_tools': 1, 'require_exploit': False},
    'low': {'min_tools': 1, 'require_exploit': False}
}
```

---

## 📝 部署到服务器

### 上传文件

```bash
# 从本地上传
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 上传适配器
scp adapters/phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
scp adapters/phase3_validator_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 上传测试脚本
scp test/test_phase2_phase3_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/
```

---

### 在服务器测试

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 进入目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行测试
python3 test/test_phase2_phase3_real.py
```

---

## 📚 相关文档

- 📖 [`test/README.md`](test/README.md) - 测试套件说明
- 📖 [`test/FAQ.md`](test/FAQ.md) - 常见问题解答
- 📖 [`FIX_MOCK_DATA_ISSUE.md`](FIX_MOCK_DATA_ISSUE.md) - 模拟数据问题解决
- 📖 [`SERVER_QUICK_TEST.md`](SERVER_QUICK_TEST.md) - 服务器测试指南

---

## 🆘 需要帮助？

如果测试遇到问题：

1. **检查工具安装**
   ```bash
   which nuclei afrog nikto zap-cli sqlmap
   ```

2. **查看详细日志**
   ```bash
   python3 test/test_phase2_phase3_real.py 2>&1 | tee debug.log
   ```

3. **分析错误**
   ```bash
   grep -A 5 "Error\|Exception" debug.log
   ```

4. **提供信息**
   - 操作系统及版本
   - Python 版本
   - 已安装的工具及版本
   - 完整的错误输出

---

**祝你测试顺利！** 🎉

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```
