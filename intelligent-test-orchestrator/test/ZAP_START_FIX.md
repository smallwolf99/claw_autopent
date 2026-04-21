# ZAP 启动问题修复

## 🐛 问题分析

### 错误 1: ZAP 路径错误
```
[ERROR] ZAP was not found in the path "/zap"
```

**原因：** zap-cli 默认在 `/zap` 路径查找 ZAP，但实际路径是 `/home/ubuntu/tools/zap/ZAP_2.17.0/`

---

### 错误 2: settings 命令不存在
```
Error: No such command "settings"
```

**原因：** zap-cli 版本过旧，不支持 `settings` 命令

---

## ✅ 解决方案

### 方法 1: 使用新启动脚本（推荐）

#### 步骤 1: 上传修复脚本

```bash
# 在本地 PowerShell 执行
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp test\start_zap_fixed.sh ubuntu@119.45.255.144:/home/ubuntu/
```

#### 步骤 2: SSH 登录并运行

```bash
ssh ubuntu@119.45.255.144

cd /home/ubuntu
chmod +x start_zap_fixed.sh
./start_zap_fixed.sh
```

**预期输出：**
```
==========================================
  启动 ZAP 代理服务
==========================================

[-] ZAP 路径：/home/ubuntu/tools/zap/ZAP_2.17.0
[-] ZAP JAR: /home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar

[-] 检查 ZAP 状态...
[-] 启动 ZAP...
    端口：8090
    日志：/tmp/zap.log
    PID: 12345

[-] 等待 ZAP 启动...
✅ ZAP 启动成功

==========================================
  ZAP 服务信息
==========================================
  端口：8090
  PID: 12345
  路径：/home/ubuntu/tools/zap/ZAP_2.17.0

使用命令:
  zap-cli -p 8090 status
  zap-cli -p 8090 quick-scan http://demo.testfire.net
```

---

### 方法 2: 手动启动（简单直接）

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 直接进入 ZAP 目录
cd /home/ubuntu/tools/zap/ZAP_2.17.0

# 启动 ZAP（后台运行）
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 等待 10 秒
sleep 10

# 检查是否启动成功
ps aux | grep -i zap | grep -v grep

# 检查端口
netstat -tlnp | grep 8090
```

**验证：**
```bash
# 使用 -p 参数指定端口
zap-cli -p 8090 status
```

---

### 方法 3: 设置环境变量（永久方案）

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 编辑 ~/.bashrc
nano ~/.bashrc

# 添加以下内容到文件末尾
export ZAP_PATH=/home/ubuntu/tools/zap/ZAP_2.17.0
export PATH=$PATH:$ZAP_PATH

# 保存并退出（Ctrl+O, Enter, Ctrl+X）

# 使环境变量生效
source ~/.bashrc

# 启动 ZAP
cd $ZAP_PATH
java -jar zap-2.17.0.jar -daemon -port 8090 &

# 等待
sleep 10

# 验证
zap-cli status
```

---

## 🔧 配置 Phase-2 适配器

修改 [`phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)，指定 ZAP 端口：

```python
async def _call_zap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
    """调用 ZAP-CLI 进行 Web 应用扫描"""
    logger.info(f"调用 ZAP-CLI: {target}")
    
    try:
        # 使用 -p 参数指定端口
        cmd = f"zap-cli -p 8090 quick-scan -s {target}"
        logger.info(f"执行命令：{cmd}")
        
        # ... 其余代码不变
```

---

## 📊 验证 ZAP 运行

### 检查进程

```bash
ps aux | grep -i "zap.*jar\|zap.*daemon" | grep -v grep
```

**应该看到：**
```
ubuntu   12345  5.0  2.0  1234567  89012  ?  Sl   19:00   0:10  java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090
```

---

### 检查端口

```bash
netstat -tlnp | grep 8090
# 或
ss -tlnp | grep 8090
```

**应该看到：**
```
tcp   0   0.0.0.0:8090   0.0.0.0:*   LISTEN   12345/java
```

---

### 测试 zap-cli

```bash
# 使用 -p 参数指定端口
zap-cli -p 8090 status

# 或设置别名
alias zap='zap-cli -p 8090'
zap status
```

**应该看到：**
```
ZAP is running
```

---

## 🧪 测试 ZAP 扫描

### 快速扫描测试

```bash
# 使用 -p 参数
zap-cli -p 8090 quick-scan http://demo.testfire.net

# 或
zap-cli -p 8090 quick-scan -s http://demo.testfire.net
```

**预期输出：**
```
[INFO] Spidering target...
[INFO] Active scanning target...
[========================================] 100%
[INFO] Found 3 issues
```

---

### 运行完整测试

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**预期输出：**
```
2026-04-21 20:00:00 - 调用 ZAP-CLI: http://demo.testfire.net
2026-04-21 20:00:30 - ZAP-CLI 发现 3 个漏洞 ✅
```

---

## 🛠️ 常见问题

### Q1: Java 内存不足？

**A:** 减少内存分配：

```bash
java -Xmx256m -jar zap-2.17.0.jar -daemon -port 8090
```

---

### Q2: 端口被占用？

**A:** 使用不同端口：

```bash
java -jar zap-2.17.0.jar -daemon -port 8091
zap-cli -p 8091 status
```

---

### Q3: ZAP 启动后立即退出？

**A:** 查看日志：

```bash
cat /tmp/zap.log
```

**常见错误：**
- Java 版本不兼容 → 使用 Java 11
- 端口冲突 → 更换端口
- 内存不足 → 减少 `-Xmx` 参数

---

### Q4: zap-cli 版本过旧？

**A:** 更新 zap-cli：

```bash
pip3 install --upgrade zap-cli
```

---

## 📝 完整启动流程

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 进入 ZAP 目录
cd /home/ubuntu/tools/zap/ZAP_2.17.0

# 3. 启动 ZAP
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 4. 等待启动
sleep 10

# 5. 验证
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8090

# 6. 测试 zap-cli
zap-cli -p 8090 status

# 7. 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 🎯 立即执行

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 启动 ZAP（简单方法）
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 3. 等待
sleep 10

# 4. 验证
ps aux | grep -i zap | grep -v grep
zap-cli -p 8090 status

# 5. 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**完成！ZAP 现在应该能正常工作了！** 🎉
