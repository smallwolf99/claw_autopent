# 部署问题诊断与修复指南

## 🔍 问题现象

部署新版本后，OpenClaw 仍然使用旧版本的测试流程，新集成的 ZAP 和 SQLMap 没有生效。

---

## 📋 诊断步骤

### 1. 确认服务器上的代码版本

SSH 登录服务器后执行：

```bash
ssh ubuntu@119.45.255.144

# 进入技能目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查 phase2_adapter.py 是否包含 SQLMap
grep -n "sqlmap" adapters/phase2_adapter.py

# 应该看到以下输出：
# 36:            'sqlmap': self._call_sqlmap,  # 新增 SQLMap
# 97:            tools.append('sqlmap')  # SQLMap 专项检测 SQL 注入
# 300:    async def _call_sqlmap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
```

**如果没有输出**，说明代码没有更新成功。

---

### 2. 检查 OpenClaw 日志

```bash
# 查看 OpenClaw 日志
tail -100 /home/ubuntu/.openclaw/logs/openclaw.log | grep -i "intelligent-test"

# 或者实时查看
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

然后在飞书中触发技能，观察日志输出。

**关键信息：**
- 技能调用路径
- 是否有错误信息
- 加载的代码版本

---

### 3. 检查技能注册信息

```bash
# 查看 OpenClaw 的技能列表
cd /home/ubuntu/.openclaw
ls -la workspace/skills/

# 检查技能配置文件
cat workspace/skills/intelligent-test-orchestrator/manifest.json | grep name
```

---

## 🔧 修复方案

### 方案 1：完全重新部署（推荐）

```bash
# 1. 删除服务器上的旧版本
ssh ubuntu@119.45.255.144
rm -rf /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 2. 从本地重新上传
cd d:\TRAE\advanced-pentester-v1.2
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/

# 3. 验证上传成功
ssh ubuntu@119.45.255.144 "ls -la /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/"

# 4. 检查新版本
ssh ubuntu@119.45.255.144 "grep -n 'sqlmap' /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase2_adapter.py"

# 5. 安装依赖
ssh ubuntu@119.45.255.144 "cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator && pip3 install -r requirements.txt"

# 6. 重启 OpenClaw（如果有必要）
ssh ubuntu@119.45.255.144 "pm2 restart openclaw"
# 或者
ssh ubuntu@119.45.255.144 "systemctl restart openclaw"
```

---

### 方案 2：增量更新

如果只想更新特定文件：

```bash
# 只上传 phase2_adapter.py
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
scp adapters/phase2_adapter.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 上传测试脚本
scp test_zap_integration.py test_sqlmap_integration.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/

# 验证
ssh ubuntu@119.45.255.144 "grep -n 'sqlmap' /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/phase2_adapter.py"
```

---

### 方案 3：清除 OpenClaw 缓存

OpenClaw 可能缓存了技能信息：

```bash
# 1. 停止 OpenClaw
ssh ubuntu@119.45.255.144 "pm2 stop openclaw"
# 或
ssh ubuntu@119.45.255.144 "systemctl stop openclaw"

# 2. 清除缓存
ssh ubuntu@119.45.255.144 "rm -rf /home/ubuntu/.openclaw/cache/"
ssh ubuntu@119.45.255.144 "rm -rf /home/ubuntu/.openclaw/.cache/"

# 3. 重新启动
ssh ubuntu@119.45.255.144 "pm2 start openclaw"
# 或
ssh ubuntu@119.45.255.144 "systemctl start openclaw"

# 4. 等待 1-2 分钟让 OpenClaw 重新加载技能
```

---

## ✅ 验证步骤

### 1. 验证代码已更新

```bash
ssh ubuntu@119.45.255.144 << 'EOF'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查 SQLMap 集成
echo "=== 检查 SQLMap 集成 ==="
grep -n "sqlmap" adapters/phase2_adapter.py | head -5

# 检查 ZAP 集成
echo "=== 检查 ZAP 集成 ==="
grep -n "zap" adapters/phase2_adapter.py | head -5

# 检查工具列表
echo "=== 检查工具注册 ==="
grep -A 6 "self.tools = {" adapters/phase2_adapter.py

# 运行测试
echo "=== 运行 SQLMap 测试 ==="
python3 test_sqlmap_integration.py | head -20
EOF
```

---

### 2. 验证 OpenClaw 调用新版本

在飞书中发送：

```
帮我测试 http://demo.test.com
```

然后立即查看日志：

```bash
ssh ubuntu@119.45.255.144 "tail -f /home/ubuntu/.openclaw/logs/openclaw.log"
```

**关键日志信息：**
- `Phase-2 漏洞检测适配器初始化完成（集成 ZAP-CLI + SQLMap）`
- `调用 SQLMap: http://demo.test.com`
- `调用 ZAP-CLI: http://demo.test.com`

如果看到这些日志，说明新版本已生效。

---

### 3. 对比测试结果

**旧版本（只有 3 个工具）:**
```
可用工具：['nuclei', 'afrog', 'nikto']
```

**新版本（5 个工具）:**
```
可用工具：['nuclei', 'afrog', 'nikto', 'zap', 'sqlmap']
```

在飞书的测试结果中，应该能看到：
- SQLMap 发现的 SQL 注入漏洞（带 `sqlmap_type`, `sqlmap_payload` 等字段）
- ZAP 发现的 Web 漏洞（带 `zap_risk`, `zap_confidence` 等字段）

---

## 🐛 常见问题

### 问题 1：scp 上传失败

**错误：** `Bad owner or permissions on .ssh/config`

**解决：**
```bash
# 修复 SSH 配置权限
chmod 600 ~/.ssh/config
chmod 700 ~/.ssh

# 或者直接使用密码上传
scp -o StrictHostKeyChecking=no -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
```

---

### 问题 2：OpenClaw 不重新加载

**症状：** 代码已更新，但 OpenClaw 仍使用旧版本

**解决：**
```bash
# 方法 1：重启 OpenClaw
ssh ubuntu@119.45.255.144 "pm2 restart openclaw"

# 方法 2：清除缓存后重启
ssh ubuntu@119.45.255.144 << 'EOF'
cd /home/ubuntu/.openclaw
rm -rf cache/ .cache/
pm2 restart openclaw
EOF

# 方法 3：修改 manifest.json 的版本号，强制重新加载
# 编辑 manifest.json，将 version 从 "1.0.0" 改为 "1.0.1"
```

---

### 问题 3：依赖未安装

**症状：** SQLMap/ZAP 调用失败，提示找不到命令

**解决：**
```bash
ssh ubuntu@119.45.255.144 << 'EOF'
# 安装 SQLMap
sudo apt-get update
sudo apt-get install -y sqlmap

# 安装 ZAP-CLI
pip3 install zap-cli

# 验证安装
which sqlmap
which zap-cli
EOF
```

---

### 问题 4：编码问题导致测试失败

**症状：** `UnicodeEncodeError: 'gbk' codec can't encode character`

**解决：**
```bash
ssh ubuntu@119.45.255.144 << 'EOF'
# 设置 UTF-8 编码
export PYTHONIOENCODING=utf-8
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# 或者在测试脚本开头添加
echo '# -*- coding: utf-8 -*-' | cat - test_zap_integration.py > temp && mv temp test_zap_integration.py
EOF
```

---

## 📊 完整部署验证脚本

创建一个验证脚本 `verify_deployment.sh`：

```bash
#!/bin/bash
# 部署验证脚本

echo "=========================================="
echo "  部署验证"
echo "=========================================="
echo ""

# 1. 检查文件
echo "1️⃣ 检查文件完整性..."
FILES="manifest.json main.py SKILL.md adapters/phase2_adapter.py"
for file in $FILES; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
        exit 1
    fi
done
echo ""

# 2. 检查 SQLMap 集成
echo "2️⃣ 检查 SQLMap 集成..."
if grep -q "sqlmap" adapters/phase2_adapter.py; then
    echo "  ✅ SQLMap 已集成"
    grep -n "sqlmap" adapters/phase2_adapter.py | head -3
else
    echo "  ❌ SQLMap 未集成"
    exit 1
fi
echo ""

# 3. 检查 ZAP 集成
echo "3️⃣ 检查 ZAP 集成..."
if grep -q "zap" adapters/phase2_adapter.py; then
    echo "  ✅ ZAP 已集成"
    grep -n "zap" adapters/phase2_adapter.py | head -3
else
    echo "  ❌ ZAP 未集成"
    exit 1
fi
echo ""

# 4. 运行测试
echo "4️⃣ 运行集成测试..."
python3 test_sqlmap_integration.py > /tmp/sqlmap_test.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ SQLMap 测试通过"
else
    echo "  ❌ SQLMap 测试失败"
    tail -20 /tmp/sqlmap_test.log
    exit 1
fi

python3 test_zap_integration.py > /tmp/zap_test.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ ZAP 测试通过"
else
    echo "  ❌ ZAP 测试失败"
    tail -20 /tmp/zap_test.log
    exit 1
fi
echo ""

# 5. 运行完整流程
echo "5️⃣ 运行完整流程测试..."
python3 test_simple.py > /tmp/full_test.log 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ 完整流程测试通过"
    grep "vulnerabilities_found" /tmp/full_test.log
else
    echo "  ❌ 完整流程测试失败"
    tail -30 /tmp/full_test.log
    exit 1
fi
echo ""

echo "=========================================="
echo "  🎉 所有验证通过！"
echo "=========================================="
```

使用方法：
```bash
chmod +x verify_deployment.sh
./verify_deployment.sh
```

---

## 🎯 快速修复（一键执行）

如果时间紧急，直接执行这个一键修复脚本：

```bash
# 本地执行（Windows PowerShell）
cd d:\TRAE\advanced-pentester-v1.2

# 1. 删除服务器上的旧版本
ssh ubuntu@119.45.255.144 "rm -rf /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator"

# 2. 重新上传
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/

# 3. 验证并重启
ssh ubuntu@119.45.255.144 << 'EOF'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
pip3 install -r requirements.txt
grep -n "sqlmap" adapters/phase2_adapter.py | head -3
pm2 restart openclaw
echo "✅ 部署完成，等待 2 分钟后在飞书测试"
EOF
```

---

## 📞 获取帮助

如果以上方案都无法解决问题，请提供：

1. 服务器上的 `grep -n "sqlmap" adapters/phase2_adapter.py` 输出
2. OpenClaw 日志片段（`tail -100 /home/ubuntu/.openclaw/logs/openclaw.log`）
3. 飞书中的测试结果截图

这样可以更准确地定位问题。
