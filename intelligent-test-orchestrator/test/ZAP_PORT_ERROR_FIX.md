# ZAP 端口错误 - 8090 vs 8080

## 🚨 问题分析

错误日志显示：
```
HTTPConnectionPool(host='127.0.0.1', port=8090): Max retries exceeded
```

**问题：** 有代码在尝试连接 8090 端口，但 ZAP 实际运行在 8080 端口

---

## 🔍 可能的原因

### 原因 1: zap-cli 内部配置使用 8090

zap-cli 可能有默认端口配置，需要使用 `-p 8080` 参数。

**检查：**
```bash
# 查看 zap-cli 帮助
zap-cli --help | grep -i port

# 测试连接
zap-cli -p 8080 status
zap-cli -p 8090 status
```

---

### 原因 2: 服务器上运行的是旧代码

**可能：** OpenClaw 加载的还是旧版本的代码（使用 8090 端口）

**解决：**
```bash
# 1. 检查 OpenClaw 加载的代码版本
ls -la /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase2_adapter_real.py

# 2. 查看文件内容中的端口配置
grep -n "8080\|8090" /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase2_adapter_real.py

# 3. 如果文件还是旧的，需要重新上传
```

---

### 原因 3: 其他服务在使用 8090

**检查：**
```bash
# 查看 8090 端口
netstat -tlnp | grep 8090

# 查看是什么进程
ps aux | grep 8090
```

---

## ✅ 解决方案

### 方案 1: 诊断服务器配置（推荐）

#### 步骤 1: 上传诊断脚本

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp test\check_zap_config.py ubuntu@119.45.255.144:/home/ubuntu/
```

#### 步骤 2: SSH 登录并运行

```bash
ssh ubuntu@119.45.255.144

# 运行诊断
cd /home/ubuntu
python3 check_zap_config.py
```

---

### 方案 2: 检查并更新服务器代码

#### 步骤 1: 检查服务器上的代码

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 检查文件
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
grep -n "8080\|8090" phase2_adapter_real.py
```

**预期输出：**
```
401:            cmd = f"zap-cli -p 8080 quick-scan -s all -f json -o /tmp/zap_report_{hash(target)}.json {target}"
```

**如果不是，说明代码是旧的，需要重新上传。**

---

#### 步骤 2: 重新上传最新代码

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 上传适配器
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 重启 OpenClaw
ssh ubuntu@119.45.255.144
sudo systemctl restart openclaw
```

---

### 方案 3: 修改 ZAP 端口为 8090（备选）

如果不想改代码，可以把 ZAP 改成 8090 端口：

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 杀掉当前 ZAP
ps aux | grep -i "zap.*jar" | grep -v grep
sudo fuser -k 8080/tcp

# 启动 ZAP (8090 端口)
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &
sleep 15

# 验证
zap-cli -p 8090 status
```

---

## 📊 完整诊断流程

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 检查 ZAP 进程
ps aux | grep -i "zap.*jar.*daemon" | grep -v grep

# 3. 检查端口
netstat -tlnp | grep -E "8080|8090"

# 4. 检查代码
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
grep -n "zap-cli" phase2_adapter_real.py

# 5. 测试连接
zap-cli -p 8080 status
zap-cli -p 8090 status

# 6. 运行诊断脚本
cd /home/ubuntu
python3 check_zap_config.py
```

---

## 🎯 快速修复

### 如果 ZAP 在 8080 端口运行

```bash
# 确保代码使用 8080 端口
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters
grep "zap-cli" phase2_adapter_real.py

# 应该看到：
# cmd = f"zap-cli -p 8080 quick-scan -s all -f json -o /tmp/zap_report_{hash(target)}.json {target}"

# 测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

### 如果想统一使用 8090 端口

**修改本地代码：**

1. 修改 [`phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)

```python
# 第 401 行
cmd = f"zap-cli -p 8090 quick-scan -s all -f json -o /tmp/zap_report_{hash(target)}.json {target}"
```

2. 修改 [`start_zap_simple.sh`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\start_zap_simple.sh)

```bash
# 第 11 行
ZAP_PORT=8090
```

3. 重新上传并重启 OpenClaw

```bash
# 本地 PowerShell
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
ssh ubuntu@119.45.255.144
sudo systemctl restart openclaw
```

---

## 📝 建议

**推荐使用 8080 端口**，因为：

1. ✅ 代码已经修改为使用 8080
2. ✅ 避免与其他服务冲突
3. ✅ 8080 是常见的 HTTP 代理端口

---

## 🔧 立即执行

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 运行诊断
cd /home/ubuntu
python3 check_zap_config.py

# 3. 根据诊断结果修复
# - 如果 ZAP 在 8080 运行，确保代码使用 -p 8080
# - 如果代码是旧的，重新上传最新代码
```

---

**关键：确保 ZAP 运行端口和代码配置端口一致！** ✅
