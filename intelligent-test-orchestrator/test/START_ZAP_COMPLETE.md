# 启动 ZAP 服务（完整步骤）

## 🚀 快速启动

### 方法 1: 使用修复后的脚本

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 进入目录
cd /home/ubuntu

# 再次运行启动脚本（已修复）
./start_zap.sh
```

**预期输出：**
```
==========================================
  启动 ZAP 代理服务
==========================================

[-] 检查 ZAP 状态...
[-] 启动 ZAP...
[-] 尝试手动启动 ZAP...
   找到 ZAP (已知路径): /home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar
   正在启动 ZAP...
✅ ZAP 手动启动成功
ZAP is running
```

---

### 方法 2: 手动启动（如果脚本失败）

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 直接启动 ZAP
nohup java -jar /home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 等待启动
sleep 10

# 设置 zap-cli 端口
zap-cli settings set port 8090

# 检查状态
zap-cli status
```

---

### 方法 3: 使用完整路径启动

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 找到准确的 JAR 文件名
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/

# 启动（替换为实际文件名）
cd /home/ubuntu/tools/zap/ZAP_2.17.0/
java -jar zap-2.17.0.jar -daemon -port 8090 &

# 等待
sleep 10

# 配置 zap-cli
zap-cli settings set port 8090
zap-cli status
```

---

## ✅ 验证 ZAP 运行

### 检查进程

```bash
ps aux | grep -i zap | grep -v grep
```

**应该看到类似：**
```
ubuntu   12345  5.0  2.0  1234567  89012  ?  Sl   18:00   0:10  java -jar zap-2.17.0.jar -daemon -port 8090
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
tcp        0      0 0.0.0.0:8090    0.0.0.0:*    LISTEN   12345/java
```

---

### 测试 ZAP-CLI

```bash
zap-cli status
```

**应该看到：**
```
ZAP is running
```

---

## 🔧 故障排查

### 问题 1: Java 未找到

```bash
# 检查 Java
java -version

# 如果未安装
sudo apt update
sudo apt install -y openjdk-11-jdk
```

---

### 问题 2: 端口被占用

```bash
# 检查 8090 端口
netstat -tlnp | grep 8090

# 如果已被占用，杀掉进程
sudo kill -9 <PID>

# 或使用不同端口
java -jar zap-2.17.0.jar -daemon -port 8091
zap-cli settings set port 8091
```

---

### 问题 3: 内存不足

```bash
# 检查内存
free -h

# 如果内存不足，限制 ZAP 内存
java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090
```

---

### 问题 4: ZAP 启动失败

```bash
# 查看日志
cat /tmp/zap.log

# 或直接启动看错误
java -jar /home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar -daemon -port 8090
```

---

## 📝 完整启动流程

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 确认 ZAP 路径
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/

# 3. 启动 ZAP
cd /home/ubuntu/tools/zap/ZAP_2.17.0/
nohup java -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 4. 等待启动
sleep 10

# 5. 配置 zap-cli
zap-cli settings set port 8090

# 6. 验证
zap-cli status

# 7. 测试快速扫描
zap-cli quick-scan -s http://demo.testfire.net
```

---

## 🎯 启动后的测试

ZAP 启动成功后，运行完整测试：

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**预期输出：**
```
2026-04-21 19:00:00 - 调用 ZAP-CLI: http://demo.testfire.net
2026-04-21 19:00:30 - ZAP-CLI 发现 3 个漏洞 ✅
```

---

## 💡 自动化脚本

创建 `~/start_zap.sh`：

```bash
#!/bin/bash
echo "启动 ZAP..."

# 检查是否已在运行
if zap-cli status &> /dev/null; then
    echo "✅ ZAP 已经在运行"
    exit 0
fi

# 启动
nohup java -jar /home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 等待
sleep 10

# 配置
zap-cli settings set port 8090

# 验证
if zap-cli status &> /dev/null; then
    echo "✅ ZAP 启动成功"
    zap-cli status
else
    echo "❌ ZAP 启动失败"
    cat /tmp/zap.log
fi
```

使用：
```bash
chmod +x ~/start_zap.sh
~/start_zap.sh
```

---

**立即执行启动 ZAP！** 🚀

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu
./start_zap.sh
```
