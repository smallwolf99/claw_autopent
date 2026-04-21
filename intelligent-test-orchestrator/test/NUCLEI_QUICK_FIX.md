# Nuclei 返回码 2 - 快速修复

## ✅ 已完成修改

### 修改内容

**文件：** [`adapters/phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)

**修改点：**

1. **输出格式：** `-json` → `-jsonl`（兼容新版 Nuclei）
2. **超时时间：** `10 秒` → `30 秒`
3. **添加限流：** `-rate-limit 5`（避免请求过快）
4. **总超时：** `5 分钟` → `10 分钟`
5. **错误日志：** 增强返回码 2 的错误记录

---

## 🚀 立即执行

### 步骤 1: 上传修改后的文件

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
```

---

### 步骤 2: SSH 登录并更新 Nuclei 模板

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 更新 Nuclei 模板（重要！）
nuclei -ut
```

---

### 步骤 3: 测试 Nuclei

```bash
# 手动测试
nuclei -u http://demo.testfire.net -jsonl -timeout 30 -rate-limit 5 | head -10

# 如果看到 JSON 输出，说明成功
```

**预期输出：**
```json
{"template":"http/cves/2021/CVE-2021-1234.yaml","info":{"name":"Example Vulnerability","severity":"high"},"host":"http://demo.testfire.net","matched-at":"http://demo.testfire.net/login"}
```

---

### 步骤 4: 重启 OpenClaw 并测试

```bash
# 重启 OpenClaw
sudo systemctl restart openclaw

# 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 📊 验证命令

### 检查 Nuclei

```bash
# 版本
nuclei -version

# 模板数量
ls -la ~/nuclei-templates/ | head -5

# 测试运行
nuclei -u http://demo.testfire.net -v | head -20
```

---

### 检查代码

```bash
# 确认代码已更新
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
grep "nuclei -u" phase2_adapter_real.py

# 应该看到：
# cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 5"
```

---

## 🐛 如果还是失败

### 收集错误信息

```bash
# 1. 手动运行 Nuclei
nuclei -u http://demo.testfire.net -timeout 30 2>&1 | head -50

# 2. 检查模板
nuclei -ut

# 3. 查看日志
tail -100 /tmp/zap.log
journalctl -u openclaw -n 50
```

---

## ✅ 成功标志

```
✅ Nuclei 返回码为 0
✅ 输出 JSONL 格式的漏洞信息
✅ 没有参数错误
```

---

## 📝 完整命令（复制粘贴）

```bash
# 本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# SSH 登录
ssh ubuntu@119.45.255.144

# 更新模板
nuclei -ut

# 测试
nuclei -u http://demo.testfire.net -jsonl -timeout 30 -rate-limit 5 | head -10

# 重启 OpenClaw
sudo systemctl restart openclaw

# 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

**执行完这些命令，Nuclei 应该能正常工作了！** 🎉
