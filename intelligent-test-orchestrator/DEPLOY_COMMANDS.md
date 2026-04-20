# 部署命令清单 - OpenClaw 服务器

## 📦 服务器信息

- **IP 地址:** 119.45.255.144
- **用户名:** ubuntu
- **部署路径:** /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

---

## 🚀 快速部署（推荐）

### Windows PowerShell

```powershell
# 在项目根目录执行
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
.\deploy_to_openclaw.ps1
```

### Linux/Mac Bash

```bash
# 在项目根目录执行
cd /path/to/intelligent-test-orchestrator
chmod +x deploy_to_openclaw.sh
./deploy_to_openclaw.sh
```

---

## 📋 手动部署步骤

### 步骤 1: 上传代码

**Windows PowerShell:**
```powershell
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
```

**Linux/Mac:**
```bash
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
```

### 步骤 2: SSH 连接并安装依赖

```bash
ssh ubuntu@119.45.255.144
```

连接后执行：

```bash
# 进入部署目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 安装依赖
pip3 install -r requirements.txt
```

### 步骤 3: 验证文件

```bash
# 检查文件完整性
ls -la manifest.json main.py SKILL.md

# 检查目录结构
ls -d core/ adapters/
```

### 步骤 4: 测试运行

```bash
# 运行简单测试
python3 test_simple.py
```

### 步骤 5: 退出 SSH

```bash
exit
```

---

## ✅ 验证部署成功

### 方法 1: 飞书测试

在飞书中输入：
```
帮我测试 http://demo.test.com
```

**预期输出:**
```
🚀 开始智能安全测试
🎯 目标：http://demo.test.com
📊 模式：full

🎯 阶段 1/5: 资产收集中...
✅ 发现 6 个资产

🧠 阶段 2/5: 风险画像生成中...
⚠️  风险评分：16.63/100

🔍 阶段 3/5: 漏洞检测中...
🐛 发现 10 个漏洞

🔬 阶段 4/5: 漏洞验证中...
✔️  已验证 10 个漏洞

📄 阶段 5/5: 报告生成中...
📊 报告已生成：/path/to/report.html

✅ 测试完成，发现 10 个漏洞（已验证 10 个），风险评分 16.63/100
```

### 方法 2: 查看日志

```bash
# SSH 连接到服务器
ssh ubuntu@119.45.255.144

# 查看 OpenClaw 日志
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

查看是否有：
- ✅ Skill 加载成功
- ✅ 触发词匹配
- ✅ 函数调用记录

### 方法 3: 直接调用测试

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 main.py '{"target": "http://test.example.com", "test_mode": "full"}'
```

---

## 🔧 故障排查

### 问题 1: SCP 上传失败

**错误信息:**
```
Permission denied (publickey).
```

**解决方案:**
```bash
# 检查 SSH 密钥
ssh ubuntu@119.45.255.144

# 如果无法连接，需要配置 SSH 密钥或使用密码
ssh-copy-id ubuntu@119.45.255.144
```

### 问题 2: pip3 安装失败

**错误信息:**
```
Command 'pip3' not found
```

**解决方案:**
```bash
# 安装 pip
ssh ubuntu@119.45.255.144
sudo apt-get update
sudo apt-get install -y python3-pip

# 或使用 python -m pip
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 -m pip install -r requirements.txt
```

### 问题 3: 依赖冲突

**错误信息:**
```
ERROR: Cannot install X and Y because they require different versions
```

**解决方案:**
```bash
# 升级 pip
pip3 install --upgrade pip

# 使用 --no-cache-dir
pip3 install --no-cache-dir -r requirements.txt
```

### 问题 4: OpenClaw 未识别 Skill

**检查清单:**
1. ✅ 确认目录在 `/home/ubuntu/.openclaw/workspace/skills/` 下
2. ✅ 确认 `manifest.json` 存在且格式正确
3. ✅ 确认 `main.py` 存在
4. ✅ 重启 OpenClaw

**重启 OpenClaw:**
```bash
ssh ubuntu@119.45.255.144
# 根据安装方式选择
systemctl restart openclaw
# 或
docker restart openclaw
# 或
pm2 restart openclaw
```

---

## 📊 部署检查清单

部署完成后，请确认：

- [ ] ✅ 代码已上传到服务器
- [ ] ✅ 依赖安装成功（pip3 install -r requirements.txt）
- [ ] ✅ 文件结构完整（manifest.json, main.py, core/, adapters/）
- [ ] ✅ 测试运行成功（python3 test_simple.py）
- [ ] ✅ 飞书测试成功（帮我测试 http://demo.test.com）
- [ ] ✅ 日志正常（无错误信息）

---

## 🎯 常用命令

### SSH 连接
```bash
ssh ubuntu@119.45.255.144
```

### 上传文件
```bash
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
```

### 查看日志
```bash
ssh ubuntu@119.45.255.144 'tail -f /home/ubuntu/.openclaw/logs/openclaw.log'
```

### 远程执行
```bash
ssh ubuntu@119.45.255.144 'cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator && python3 test_simple.py'
```

### 重启 OpenClaw
```bash
ssh ubuntu@119.45.255.144 'systemctl restart openclaw'
```

---

## 📞 获取帮助

### 查看 OpenClaw 状态
```bash
ssh ubuntu@119.45.255.144
systemctl status openclaw
```

### 查看 Skill 列表
```bash
ssh ubuntu@119.45.255.144
ls -la /home/ubuntu/.openclaw/workspace/skills/
```

### 查看已加载的 Skills
```bash
ssh ubuntu@119.45.255.144
cat /home/ubuntu/.openclaw/logs/openclaw.log | grep "Loaded skill"
```

---

**部署准备就绪！** 🚀

**下一步:** 选择自动或手动方式部署到 OpenClaw 服务器！
