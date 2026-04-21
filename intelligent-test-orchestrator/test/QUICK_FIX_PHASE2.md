# Phase-2 工具快速修复

## 🚨 错误确认

根据你的错误日志，发现以下问题：

1. ❌ **Nikto JSON 解析失败** → Nikto 可能未安装或版本过旧
2. ❌ **Nuclei 执行失败** → Nuclei 未安装
3. ❌ **ZAP-CLI 连接拒绝** → ZAP 代理服务未启动

---

## 🔧 快速修复（推荐）

### 步骤 1: 上传修复脚本到服务器

```bash
# 从本地上传
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp test/fix_phase2_tools.sh ubuntu@119.45.255.144:/home/ubuntu/
scp test/FIX_PHASE2_ERRORS.md ubuntu@119.45.255.144:/home/ubuntu/
```

---

### 步骤 2: SSH 登录服务器并运行修复

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 进入目录
cd /home/ubuntu

# 赋予执行权限
chmod +x fix_phase2_tools.sh

# 运行修复脚本（需要 sudo）
sudo ./fix_phase2_tools.sh
```

**脚本会自动：**
- ✅ 安装 Nikto
- ✅ 安装 Nuclei（包括 Go 环境）
- ✅ 安装 Afrog
- ✅ 安装 ZAP-CLI
- ✅ 启动 ZAP 代理服务
- ✅ 测试所有工具

---

### 步骤 3: 验证修复

```bash
# 检查所有工具
which nikto nuclei afrog zap-cli

# 测试 Nikto
nikto -h http://demo.testfire.net -timeout 10

# 测试 Nuclei
nuclei -u http://demo.testfire.net -json -silent -timeout 10

# 测试 ZAP-CLI
zap-cli status
```

---

### 步骤 4: 重新运行测试

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

python3 test/test_phase2_phase3_real.py
```

---

## 📋 手动修复（如果脚本失败）

### 1. 安装 Nikto

```bash
sudo apt update
sudo apt install -y nikto
```

---

### 2. 安装 Nuclei

```bash
# 安装 Go（如果没有）
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
export PATH=$PATH:$HOME/go/bin

# 安装 Nuclei
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# 初始化模板
nuclei -ut
```

---

### 3. 安装 Afrog

```bash
go install github.com/zan8in/afrog/v2@latest
```

---

### 4. 安装 ZAP-CLI 并启动

```bash
# 安装 ZAP-CLI
pip3 install zap-cli

# 启动 ZAP（需要 Java）
zap-cli start

# 检查状态
zap-cli status
```

**如果 ZAP 启动失败，使用 Docker：**

```bash
# 安装 Docker（如果没有）
sudo apt install -y docker.io

# 启动 ZAP Docker 容器
docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh

# 设置 ZAP-CLI 端口
zap-cli settings set port 8090
```

---

## ✅ 验证标准

所有工具安装成功后，应该看到：

```bash
$ which nikto nuclei afrog zap-cli
/usr/bin/nikto
/home/ubuntu/go/bin/nuclei
/home/ubuntu/go/bin/afrog
/usr/local/bin/zap-cli

$ nikto -Version
nikto v2.5.0

$ nuclei -version
3.0.0

$ afrog -version
afrog v2.0.0

$ zap-cli status
ZAP is running

$ zap-cli quick-scan -s http://demo.testfire.net
[========================================] 100%
```

---

## 🐛 常见问题

### Q1: Go 安装失败？

**A:** 使用预编译二进制：

```bash
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
unzip nuclei_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
```

---

### Q2: ZAP-CLI 无法连接？

**A:** 检查 ZAP 是否运行：

```bash
# 检查进程
ps aux | grep zap

# 检查端口
netstat -tlnp | grep 8080
netstat -tlnp | grep 8090

# 重启 ZAP
zap-cli shutdown
zap-cli start
```

---

### Q3: Nikto 输出不是 JSON？

**A:** 版本过旧，需要更新：

```bash
# 卸载旧版本
sudo apt remove nikto

# 安装新版本
git clone https://github.com/sullo/nikto.git
cd nikto/program
perl nikto.pl -Version
```

---

## 📊 预期结果

修复完成后运行测试：

```bash
python3 test/test_phase2_phase3_real.py
```

**预期输出：**

```
======================================================================
  Phase-2 漏洞检测 - 真实工具测试
======================================================================

🎯 测试目标：http://demo.testfire.net
📡 开始漏洞检测...

2026-04-21 17:00:00 - 调用 Nuclei: http://demo.testfire.net
2026-04-21 17:00:05 - Nuclei 发现 8 个漏洞
2026-04-21 17:00:05 - 调用 Nikto: http://demo.testfire.net
2026-04-21 17:00:30 - Nikto 发现 5 个漏洞
2026-04-21 17:00:30 - 调用 ZAP-CLI: http://demo.testfire.net
...

📊 测试结果:
  • 发现漏洞数：15
  • 耗时：180.45 秒

✅ 验证结果:
  ✅ 使用的工具：nuclei, nikto, zap
  ✅ 检测到 15 个漏洞
```

---

## 📚 相关文档

- 📖 [`FIX_PHASE2_ERRORS.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\FIX_PHASE2_ERRORS.md) - 详细错误分析
- 📖 [`TESTFIRE_TARGET_GUIDE.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\TESTFIRE_TARGET_GUIDE.md) - 靶场测试说明
- 📖 [`PHASE2_PHASE3_TEST_GUIDE.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\PHASE2_PHASE3_TEST_GUIDE.md) - 测试指南

---

**立即执行修复！** 🚀

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu
sudo ./fix_phase2_tools.sh
```
