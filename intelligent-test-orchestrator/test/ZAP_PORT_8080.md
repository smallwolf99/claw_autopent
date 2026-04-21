# ZAP 端口配置更新

## ✅ 端口已更新

ZAP 在服务器上运行的端口已从 **8090** 改为 **8080**

---

## 🔧 已修改的文件

### 1. Phase-2 适配器

**文件：** [`adapters/phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)

**修改内容：**
```python
# 之前
cmd = f"zap-cli quick-scan -s {target}"

# 现在
cmd = f"zap-cli -p 8080 quick-scan -s {target}"
```

---

### 2. ZAP 启动脚本

**文件：** [`test/start_zap_simple.sh`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\start_zap_simple.sh)

**修改内容：**
```bash
# 之前
ZAP_PORT=8090

# 现在
ZAP_PORT=8080
```

---

## 🚀 使用指南

### 启动 ZAP（8080 端口）

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 进入 ZAP 目录
cd /home/ubuntu/tools/zap/ZAP_2.17.0

# 启动 ZAP（8080 端口）
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080 > /tmp/zap.log 2>&1 &

# 等待
sleep 15

# 验证
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8080
zap-cli -p 8080 status
```

**预期输出：**
```
ubuntu   12345  5.0  2.0  1234567  89012  ?  Sl   21:00   0:10  java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080
tcp   0   0.0.0.0:8080   0.0.0.0:*   LISTEN   12345/java
ZAP is running
```

---

### 运行测试

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**Phase-2 适配器会自动使用 8080 端口调用 ZAP-CLI**

---

## 📊 验证命令

### 检查 ZAP 运行

```bash
# 检查进程
ps aux | grep -i "zap.*jar.*daemon" | grep -v grep

# 检查端口
netstat -tlnp | grep 8080

# 测试 zap-cli
zap-cli -p 8080 status

# 快速扫描测试
zap-cli -p 8080 quick-scan -s http://demo.testfire.net
```

---

## 🔧 手动使用 ZAP-CLI

所有 zap-cli 命令都需要加 `-p 8080` 参数：

```bash
# ✅ 正确
zap-cli -p 8080 status
zap-cli -p 8080 quick-scan http://demo.testfire.net
zap-cli -p 8080 spider http://demo.testfire.net
zap-cli -p 8080 active-scan http://demo.testfire.net

# ❌ 错误（会使用默认端口 8080，可能导致连接失败）
zap-cli status
```

---

## 📝 完整测试流程

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 启动 ZAP（8080 端口）
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080 > /tmp/zap.log 2>&1 &
sleep 15

# 3. 验证
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8080
zap-cli -p 8080 status

# 4. 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 🎯 快速参考

### 端口信息

| 服务 | 端口 | 说明 |
|------|------|------|
| **ZAP 代理** | 8080 | OWASP ZAP 代理服务 |
| **OpenClaw** | 9000 | OpenClaw 服务（根据实际配置） |

---

### 常用命令

```bash
# 启动 ZAP
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080 > /tmp/zap.log 2>&1 &

# 检查状态
zap-cli -p 8080 status

# 快速扫描
zap-cli -p 8080 quick-scan -s http://demo.testfire.net

# 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## ✅ 配置完成

**所有文件已更新为使用 8080 端口**

现在执行以下命令即可：

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 启动 ZAP（如果还没启动）
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080 > /tmp/zap.log 2>&1 &
sleep 15

# 验证并测试
zap-cli -p 8080 status
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**完成！ZAP 现在使用 8080 端口运行！** 🎉
