# 服务器端手动测试指南

## 📋 测试目标

在 OpenClaw 服务器（119.45.255.144）上手动测试智能编排功能，验证：
1. ✅ 代码部署是否成功
2. ✅ SQLMap 和 ZAP 是否集成
3. ✅ 完整测试流程是否正常
4. ✅ OpenClaw 调用是否生效

---

## ⚙️ OpenClaw 端口配置

**重要：** 如果你的 OpenClaw 不在默认端口（18789）运行，需要先设置环境变量。

### 检查 OpenClaw 运行端口

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 方法 1: 检查端口占用
netstat -tlnp | grep -E "(9000|18789)"

# 方法 2: 测试端口连通性
curl http://localhost:9000/health
curl http://localhost:18789/health

# 方法 3: 查看 PM2 配置
pm2 describe openclaw | grep -i port
```

### 设置端口环境变量

**如果 OpenClaw 运行在 9000 端口：**

```bash
# 临时设置（当前会话有效）
export OPENCLAW_PORT=9000

# 永久设置（添加到 ~/.bashrc）
echo "export OPENCLAW_PORT=9000" >> ~/.bashrc
source ~/.bashrc
```

**如果 OpenClaw 运行在其他端口：**

```bash
# 替换 9000 为你的端口号
export OPENCLAW_PORT=YOUR_PORT
```

---

## 🚀 快速测试（推荐）

### 方法 1：使用自动化测试脚本

**步骤 1: 上传测试脚本**

```bash
# 在本地执行
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
scp test_on_server.sh ubuntu@119.45.255.144:/home/ubuntu/
```

**步骤 2: SSH 登录服务器并执行**

```bash
ssh ubuntu@119.45.255.144

# 添加执行权限
chmod +x /home/ubuntu/test_on_server.sh

# 运行测试
sudo /home/ubuntu/test_on_server.sh
```

**预期输出：**
```
==========================================
  智能编排功能 - 服务器端测试
==========================================

📋 步骤 1/6: 检查技能文件完整性
✅ manifest.json
✅ main.py
✅ SKILL.md
✅ adapters/phase2_adapter.py
✅ core/risk_profiler.py

🔧 步骤 2/6: 检查工具集成情况
检查 SQLMap 集成:
  ✅ SQLMap 已集成
  36:            'sqlmap': self._call_sqlmap,
  97:            tools.append('sqlmap')

检查 ZAP 集成:
  ✅ ZAP 已集成
  35:            'zap': self._call_zap,

📦 步骤 3/6: 检查 Python 依赖
✅ 依赖安装完成

🧪 步骤 4/6: 运行单元测试
  ✅ SQLMap 测试通过
  ✅ ZAP 测试通过

🎯 步骤 5/6: 运行完整流程测试
✅ 完整流程测试通过

📊 测试结果摘要:
  vulnerabilities_found: 24
  verified_vulns: 24
  risk_score: 16.63

🤖 步骤 6/6: 测试 OpenClaw 调用
✅ OpenClaw 正在运行

==========================================
  测试总结
==========================================
通过测试：5/5
🎉 所有测试通过！智能编排功能正常！
```

---

### 方法 2：手动逐步测试

如果你想更细致地检查每个环节：

#### 步骤 1: 登录服务器并检查文件

```bash
ssh ubuntu@119.45.255.144

# 进入技能目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查目录结构
ls -la
ls -la adapters/
ls -la core/
```

#### 步骤 2: 验证 SQLMap 和 ZAP 集成

```bash
# 检查 SQLMap
echo "=== SQLMap 集成检查 ==="
grep -n "sqlmap" adapters/phase2_adapter.py

# 应该看到：
# 36:            'sqlmap': self._call_sqlmap,  # 新增 SQLMap
# 97:            tools.append('sqlmap')  # SQLMap 专项检测 SQL 注入
# 300:    async def _call_sqlmap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:

# 检查 ZAP
echo "=== ZAP 集成检查 ==="
grep -n "zap" adapters/phase2_adapter.py

# 应该看到：
# 35:            'zap': self._call_zap,
# 96:            tools.append('zap')  # ZAP 专注于 Web 应用扫描
# 203:    async def _call_zap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
```

#### 步骤 3: 运行集成测试

```bash
# 测试 SQLMap
echo "=== 运行 SQLMap 集成测试 ==="
python3 test_sqlmap_integration.py

# 预期输出：
# ======================================================================
#   SQLMap 集成测试
# ======================================================================
# ✅ SQLMap 已集成到工具列表
#   • 可用工具：['nuclei', 'afrog', 'nikto', 'zap', 'sqlmap']
# 🎉 SQLMap 集成成功！

# 测试 ZAP
echo "=== 运行 ZAP 集成测试 ==="
python3 test_zap_integration.py

# 预期输出：
# ======================================================================
#   ZAP-CLI 集成测试
# ======================================================================
# ✅ ZAP-CLI 已集成到工具列表
#   • 可用工具：['nuclei', 'afrog', 'nikto', 'zap', 'sqlmap']
# 🎉 ZAP-CLI 集成成功！
```

#### 步骤 4: 运行完整流程测试

```bash
# 运行简单测试（使用模拟数据）
echo "=== 运行完整流程测试 ==="
python3 test_simple.py

# 预期输出（关键部分）：
# 📊 摘要：✅ 测试完成，发现 24 个漏洞（已验证 24 个），风险评分 16.63/100，耗时 0 分 12 秒
# 
# 📁 数据:
#   • target: http://demo-test.example.com
#   • assets_found: 6
#   • vulnerabilities_found: 24
#   • verified_vulns: 24
#   • risk_score: 16.63
#   • report_path: .../pentest_report_*.html
```

#### 步骤 5: 检查 OpenClaw 状态

```bash
# 检查 OpenClaw 是否运行
pm2 list | grep openclaw

# 查看日志
tail -100 /home/ubuntu/.openclaw/logs/openclaw.log | grep -i "intelligent-test"

# 实时查看日志（另开一个终端测试）
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

---

## 🎯 飞书集成测试

### 在飞书中测试技能调用

**步骤 1: 确保 OpenClaw 正在运行**

```bash
pm2 status
# 应该看到 openclaw 状态为 online
```

**步骤 2: 在飞书中发送消息**

```
帮我测试 http://demo.test.com
```

或者更详细的指令：

```
对 http://test.example.com 进行完整的安全测试，包括资产收集、漏洞检测、漏洞验证和报告生成
```

**步骤 3: 观察飞书响应**

预期响应应该包含：
- ✅ 资产收集结果（子域名、端口、技术栈等）
- ✅ 风险评分（0-100 分）
- ✅ 漏洞列表（包含 SQLMap 和 ZAP 发现的漏洞）
- ✅ 报告生成链接

**步骤 4: 查看服务器日志**

在飞书发送测试请求后，立即在服务器上查看：

```bash
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

**关键日志信息（新版本）：**
```
Phase-2 漏洞检测适配器初始化完成（集成 ZAP-CLI + SQLMap）
调用 SQLMap: http://demo.test.com
调用 ZAP-CLI: http://demo.test.com
```

如果看到这些日志，说明新版本已生效！

---

## 📊 测试结果验证

### 验证点 1: 工具数量

**旧版本（3 个工具）:**
```
可用工具：['nuclei', 'afrog', 'nikto']
```

**新版本（5 个工具）:**
```
可用工具：['nuclei', 'afrog', 'nikto', 'zap', 'sqlmap']
```

### 验证点 2: SQLMap 漏洞特征

SQLMap 发现的漏洞应该包含特有字段：

```json
{
  "id": "SQLMAP-001",
  "name": "SQL Injection - Boolean-based Blind",
  "severity": "high",
  "tool": "sqlmap",
  "verified": true,
  "sqlmap_type": "boolean-based blind",
  "sqlmap_payload": "id=1' AND 1234=1234",
  "sqlmap_dbms": "MySQL",
  "sqlmap_confidence": 95
}
```

### 验证点 3: ZAP 漏洞特征

ZAP 发现的漏洞应该包含特有字段：

```json
{
  "id": "ZAP-001",
  "name": "SQL Injection",
  "severity": "high",
  "tool": "zap",
  "zap_risk": "High",
  "zap_confidence": "Medium",
  "zap_solution": "使用参数化查询或预编译语句"
}
```

### 验证点 4: 漏洞总数

**旧版本:** 约 10 个漏洞（只有 Nuclei, Afrog, Nikto）

**新版本:** 约 24 个漏洞（增加 SQLMap 和 ZAP 的检测）

---

## 🐛 常见问题排查

### 问题 1: 找不到 SQLMap/ZAP 集成

**症状：** `grep -n "sqlmap" adapters/phase2_adapter.py` 无输出

**解决：**
```bash
# 重新上传代码
cd d:\TRAE\advanced-pentester-v1.2
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/

# 验证
ssh ubuntu@119.45.255.144 "grep -n 'sqlmap' /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase2_adapter.py"
```

### 问题 2: Python 依赖缺失

**症状：** `ModuleNotFoundError: No module named 'xxx'`

**解决：**
```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
pip3 install -r requirements.txt --user
```

### 问题 3: 测试脚本报编码错误

**症状：** `UnicodeEncodeError: 'gbk' codec can't encode character`

**解决：**
```bash
# 设置 UTF-8 编码
export PYTHONIOENCODING=utf-8
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# 或者修改测试脚本头部
sed -i '1s/^/# -*- coding: utf-8 -*-\n/' test_sqlmap_integration.py
```

### 问题 4: OpenClaw 不响应

**症状：** 飞书发送消息后无响应

**解决：**
```bash
# 检查 OpenClaw 状态
pm2 list

# 重启 OpenClaw
pm2 restart openclaw

# 查看日志
pm2 logs openclaw --lines 100
```

### 问题 5: 技能未被识别

**症状：** 飞书提示"未找到此技能"

**解决：**
```bash
# 检查技能目录
ls -la /home/ubuntu/.openclaw/workspace/skills/

# 检查 manifest.json
cat /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/manifest.json

# 重启 OpenClaw（强制重新加载技能）
pm2 restart openclaw
```

---

## 📈 性能基准测试

### 测试不同目标的性能

**测试 1: 小型目标（快速测试）**

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

cat > /tmp/test_small.json << 'EOF'
{
    "target": "http://small-test.example.com",
    "test_mode": "light",
    "time_limit": 60
}
EOF

time python3 main.py /tmp/test_small.json
```

**预期：**
- 执行时间：~5-10 秒
- 发现漏洞：~5-10 个
- 风险评分：正常计算

**测试 2: 完整目标（全面测试）**

```bash
cat > /tmp/test_full.json << 'EOF'
{
    "target": "http://full-test.example.com",
    "test_mode": "full",
    "time_limit": 300
}
EOF

time python3 main.py /tmp/test_full.json
```

**预期：**
- 执行时间：~30-60 秒（模拟模式）
- 发现漏洞：~20-30 个
- 包含 SQLMap 和 ZAP 的漏洞

---

## 🎓 最佳实践

### 1. 定期测试

建议每周执行一次完整测试：

```bash
# 添加到 crontab
crontab -e

# 每周日上午 10 点自动测试
0 10 * * 0 /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test_on_server.sh >> /var/log/intelligent-test-weekly.log 2>&1
```

### 2. 监控日志

设置日志监控告警：

```bash
# 监控错误日志
tail -f /home/ubuntu/.openclaw/logs/openclaw.log | grep -i "error\|exception"
```

### 3. 性能优化

如果发现测试速度变慢：

```bash
# 清理临时文件
rm -rf /tmp/intelligent-test-*
rm -rf adapters/reports/*

# 重启 OpenClaw
pm2 restart openclaw
```

---

## 📞 获取帮助

如果测试过程中遇到问题：

1. **查看测试日志：** `/tmp/intelligent-test-*.log`
2. **查看 OpenClaw 日志：** `tail -100 /home/ubuntu/.openclaw/logs/openclaw.log`
3. **检查技能文件：** `ls -la /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/`

记录以下信息以便排查：
- 错误日志内容
- 测试步骤
- 预期结果 vs 实际结果

---

**祝你测试顺利！** 🎉
