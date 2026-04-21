# 从模拟数据切换到真实工具 - 完整指南

## ✅ 问题已修复

**修改文件：** [`main.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\main.py)

**修改内容：** 第 43-46 行导入语句

```python
# 修改前（模拟数据）
from adapters.phase0_adapter import Phase0Adapter
from adapters.phase2_adapter import Phase2Adapter
from adapters.phase3_validator import Phase3Validator

# 修改后（真实工具）
from adapters.phase0_adapter_real import Phase0Adapter
from adapters.phase2_adapter_real import Phase2Adapter
from adapters.phase3_validator_real import Phase3Validator
```

---

## 🚀 立即部署到服务器

### 步骤 1: 上传修改后的 main.py

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp main.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/
```

---

### 步骤 2: SSH 登录并重启 OpenClaw

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 重启 OpenClaw
sudo systemctl restart openclaw

# 查看状态
sudo systemctl status openclaw
```

---

### 步骤 3: 验证修改

```bash
# 检查文件是否更新
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
grep "from adapters" main.py

# 应该看到：
# from adapters.phase0_adapter_real import Phase0Adapter
# from adapters.phase2_adapter_real import Phase2Adapter
# from adapters.phase3_validator_real import Phase3Validator
```

---

### 步骤 4: 运行测试

```bash
# 运行 Phase-2 和 Phase-3 测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 📊 预期结果对比

### 修改前（模拟模式）

| 指标 | 数值 | 说明 |
|------|------|------|
| **执行时间** | ~12 秒 | 固定时间 |
| **发现资产** | 6 个 | 固定数量 |
| **发现漏洞** | 24 个 | 固定数量 |
| **风险评分** | 16.63/100 | 固定算法 |
| **每次结果** | 完全相同 | 模拟数据 |

---

### 修改后（真实模式）

| 指标 | 预期数值 | 说明 |
|------|---------|------|
| **执行时间** | 2-10 分钟 | 根据网络和工具 |
| **发现资产** | 动态变化 | 根据目标实际情况 |
| **发现漏洞** | 动态变化 | 根据扫描结果 |
| **风险评分** | 动态变化 | 根据实际风险 |
| **每次结果** | 可能不同 | 真实网络扫描 |

---

## 🔍 验证真实工具调用

### 方法 1: 观察执行时间

**真实工具调用应该：**
- Phase-0（资产收集）：30-120 秒
- Phase-2（漏洞检测）：60-300 秒
- Phase-3（漏洞验证）：30-120 秒
- **总计**：2-10 分钟

**如果还是 ~12 秒完成，说明仍在使用模拟数据。**

---

### 方法 2: 查看进程

```bash
# 在另一个终端查看运行的进程
ps aux | grep -E "nuclei|nmap|whatweb|nikto|sqlmap"

# 应该看到真实工具进程在运行
```

---

### 方法 3: 查看日志

```bash
# 查看 OpenClaw 日志
sudo journalctl -u openclaw -f

# 查看工具执行日志
tail -100 /var/log/openclaw.log | grep -i "nuclei\|nmap\|whatweb"

# 应该看到真实命令执行日志
```

---

### 方法 4: 检查结果变化

```bash
# 运行两次测试，比较结果
python3 test/test_phase2_phase3_real.py > test1.txt
python3 test/test_phase2_phase3_real.py > test2.txt

# 比较结果（应该不同）
diff test1.txt test2.txt

# 如果结果不同，说明使用真实工具
```

---

## 🐛 故障排查

### 问题 1: OpenClaw 无法启动

**可能原因：** 导入错误

```bash
# 检查 Python 语法
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 -m py_compile main.py

# 查看错误日志
sudo journalctl -u openclaw -n 50
```

**解决方法：**
```bash
# 检查文件是否存在
ls -la adapters/phase0_adapter_real.py
ls -la adapters/phase2_adapter_real.py
ls -la adapters/phase3_validator_real.py
```

---

### 问题 2: 工具未安装

**可能原因：** 服务器上缺少安全工具

```bash
# 检查工具是否安装
which nuclei nmap whatweb nikto sqlmap

# 如果缺少，安装工具
# Nuclei
curl -o nuclei.tar.gz https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.tar.gz
tar -xzf nuclei.tar.gz
sudo mv nuclei /usr/local/bin/

# Nmap
sudo apt install -y nmap

# WhatWeb
sudo apt install -y whatweb

# Nikto
sudo apt install -y nikto

# SQLMap
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap
ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap
```

---

### 问题 3: 权限问题

**可能原因：** 工具没有执行权限

```bash
# 检查权限
ls -la /usr/local/bin/nuclei
ls -la /usr/local/bin/nmap

# 添加执行权限
chmod +x /usr/local/bin/nuclei
chmod +x /usr/local/bin/nmap
```

---

## 📝 完整测试流程

### 在服务器上

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 确认文件已更新
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
grep "from adapters" main.py

# 3. 重启 OpenClaw
sudo systemctl restart openclaw

# 4. 等待 10 秒
sleep 10

# 5. 查看状态
sudo systemctl status openclaw

# 6. 运行测试
python3 test/test_phase2_phase3_real.py

# 7. 观察执行时间（应该 > 2 分钟）
# 8. 检查结果（应该动态变化）
```

---

## 🎯 成功标志

✅ **修改成功的标志：**

1. ✅ `main.py` 导入真实适配器
2. ✅ OpenClaw 正常启动
3. ✅ 执行时间 > 2 分钟
4. ✅ 看到真实工具进程（nuclei、nmap 等）
5. ✅ 每次测试结果不同
6. ✅ 日志显示真实工具调用

---

## 📊 监控工具执行

### 实时监控

```bash
# 打开新终端监控进程
watch -n 1 'ps aux | grep -E "nuclei|nmap|whatweb|nikto" | grep -v grep'

# 在另一个终端运行测试
python3 test/test_phase2_phase3_real.py
```

---

### 网络监控

```bash
# 监控网络请求
sudo tcpdump -i any -n port 80 or port 443 | head -100

# 或使用 iftop 查看实时流量
sudo iftop -Pn
```

---

## 🎉 完成！

**修改完成后，系统将使用真实工具进行安全测试！**

### 下一步

1. ✅ 运行完整测试验证
2. ✅ 对真实目标进行测试
3. ✅ 查看生成的报告
4. ✅ 分析漏洞结果

---

**立即执行部署命令！** 🚀

```bash
# 本地 PowerShell
scp main.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/

# SSH 登录
ssh ubuntu@119.45.255.144
sudo systemctl restart openclaw
python3 test/test_phase2_phase3_real.py
```

**系统将执行真实的安全测试，不再使用模拟数据！** ✅
