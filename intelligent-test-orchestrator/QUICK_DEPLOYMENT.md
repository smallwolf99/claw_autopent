# 快速部署指南

## 🚀 5 分钟快速部署到 OpenClaw

### 前提条件

- ✅ OpenClaw 测试服务器访问权限
- ✅ Python 3.8+ 环境
- ✅ 基础命令行操作能力

---

### 方案一：模拟模式（推荐首次部署）

**特点:** 
- ⚡ 快速（5 分钟）
- 📦 无需安装额外工具
- ✅ 验证 OpenClaw 集成
- 🔍 使用模拟数据

#### 步骤 1: 上传代码

```bash
# 方法 A: 使用 SCP
scp -r intelligent-test-orchestrator/ user@your-openclaw-server:/path/to/skills/

# 方法 B: 使用 Git
cd /path/to/skills
git clone <your-repo-url> intelligent-test-orchestrator
```

#### 步骤 2: 安装基础依赖

```bash
cd /path/to/skills/intelligent-test-orchestrator
pip install -r requirements.txt
```

#### 步骤 3: 注册到 OpenClaw

编辑 OpenClaw 配置文件（通常是 `config.yaml` 或 `skills.json`）:

```yaml
skills:
  - name: intelligent-test-orchestrator
    path: /path/to/skills/intelligent-test-orchestrator
    entry_point: main:OpenClawHandler.execute_intelligent_test
    triggers:
      - "安全测试"
      - "渗透测试"
      - "漏洞扫描"
      - "帮我测试"
      - "security test"
      - "pentest"
```

#### 步骤 4: 重启 OpenClaw

```bash
# 根据 OpenClaw 部署方式选择
systemctl restart openclaw
# 或
docker restart openclaw
# 或
python -m openclaw restart
```

#### 步骤 5: 测试

在 OpenClaw 中输入：
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

✅ 测试完成！
```

---

### 方案二：完整部署（生产环境）

**特点:**
- 🔧 使用真实工具
- 📊 真实测试结果
- ⏱️ 需要 20-30 分钟
- 📦 需要安装多个工具

#### 步骤 1-4: 同方案一

#### 步骤 5: 安装安全测试工具

**安装 Nuclei:**
```bash
# 需要 Go 环境
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

**安装 Nmap:**
```bash
# Windows: 下载安装包
# Linux:
sudo apt-get update
sudo apt-get install -y nmap
```

**安装 Httpx:**
```bash
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

**安装 WhatWeb:**
```bash
# 需要 Ruby
gem install whatweb
```

**安装 Subfinder:**
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

**安装 Afrog:**
```bash
# 从 GitHub 下载
wget https://github.com/zan8in/afrog/releases/latest/download/afrog-linux-amd64
chmod +x afrog-linux-amd64
sudo mv afrog-linux-amd64 /usr/local/bin/afrog
```

**安装 Nikto:**
```bash
# Perl 环境
cpan Nikto
# 或
git clone https://github.com/sullo/nikto.git
cd nikto/program
chmod +x nikto.pl
sudo ln -s $(pwd)/nikto.pl /usr/local/bin/nikto
```

#### 步骤 6: 验证工具安装

```bash
nuclei -version
nmap --version
httpx -version
whatweb --version
subfinder -version
afrog -version
nikto -Version
```

#### 步骤 7: 配置工具路径（如需要）

如果工具不在 PATH 中，编辑 `adapters/` 下的对应文件，指定完整路径：

```python
# adapters/phase0_adapter.py
cmd = f"/usr/local/bin/nmap -sV {target}"
```

#### 步骤 8: 测试真实扫描

```bash
python main.py '{"target": "http://testphp.vulnweb.com", "test_mode": "light"}'
```

---

## 📋 部署验证

### 快速验证脚本

创建 `verify_deployment.sh`:

```bash
#!/bin/bash

echo "=== OpenClaw 智能测试编排器部署验证 ==="
echo ""

# 1. Python 版本
echo "1. 检查 Python 版本..."
python --version

# 2. 依赖检查
echo ""
echo "2. 检查依赖安装..."
pip list | grep -E "(aiohttp|pyyaml|jsonschema|pandas)"

# 3. 文件完整性
echo ""
echo "3. 检查文件完整性..."
ls -la main.py manifest.json SKILL.md

# 4. 目录结构
echo ""
echo "4. 检查目录结构..."
ls -d core/ adapters/

# 5. 快速测试
echo ""
echo "5. 运行快速测试..."
python test_simple.py

echo ""
echo "=== 验证完成 ==="
```

运行：
```bash
chmod +x verify_deployment.sh
./verify_deployment.sh
```

---

## 🔧 常见问题解决

### 问题 1: OpenClaw 无法识别 Skill

**症状:** 触发词无响应

**解决:**
1. 检查 manifest.json 格式
2. 确认触发词配置正确
3. 重启 OpenClaw 服务
4. 查看 OpenClaw 日志

### 问题 2: 导入错误

**症状:** `ModuleNotFoundError`

**解决:**
```bash
pip install -r requirements.txt --upgrade
```

### 问题 3: 权限错误

**症状:** `PermissionError`

**解决:**
```bash
chmod -R 755 /path/to/intelligent-test-orchestrator
```

### 问题 4: 报告无法生成

**症状:** 报告文件未创建

**解决:**
1. 检查输出目录权限
2. 确认磁盘空间
3. 查看错误日志

---

## 📊 部署检查清单

部署完成后，确认以下项目：

- [ ] ✅ 代码已上传到服务器
- [ ] ✅ 依赖已安装
- [ ] ✅ OpenClaw 配置已更新
- [ ] ✅ OpenClaw 服务已重启
- [ ] ✅ 触发词测试通过
- [ ] ✅ 报告生成正常
- [ ] ✅ 日志输出正常
- [ ] ✅ 权限设置正确

---

## 📞 获取帮助

### 日志位置

```bash
# OpenClaw 日志
tail -f /var/log/openclaw.log

# 应用日志
tail -f intelligent-test-orchestrator/*.log
```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py '{"target": "http://test.com"}'
```

---

## 🎯 部署后建议

### 监控

1. **性能监控**
   - CPU 使用率
   - 内存占用
   - 执行时间

2. **错误监控**
   - 失败率
   - 异常类型
   - 用户反馈

3. **使用统计**
   - 调用次数
   - 平均执行时间
   - 报告生成数量

### 优化

1. **性能优化**
   - 调整并发数
   - 优化工具参数
   - 添加缓存

2. **用户体验**
   - 优化进度反馈
   - 改进报告格式
   - 提供更多示例

---

**部署准备就绪！** 🚀

**下一步:** 选择部署方案，开始部署到 OpenClaw 测试服务器！
