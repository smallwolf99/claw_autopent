# ZAP 无法启动 - 完整诊断

## 🚨 错误信息

```
requests.exceptions.ProxyError: HTTPConnectionPool(host='127.0.0.1', port=8090): 
Max retries exceeded with url: http://demo.testfire.net/  
(Caused by ProxyError('Cannot connect to proxy.', 
NewConnectionError('<urllib3.connection.HTTPConnection object>: 
Failed to establish a new connection: [Errno 111] Connection refused')))
```

**问题：** ZAP 代理服务没有在 8090 端口运行

---

## 🔍 诊断步骤

### 步骤 1: 检查 ZAP 是否运行

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 检查进程
ps aux | grep -i "zap.*jar\|zap.*daemon" | grep -v grep

# 检查端口
netstat -tlnp | grep 8090
# 或
ss -tlnp | grep 8090
```

**如果没有输出，说明 ZAP 没有运行。**

---

### 步骤 2: 检查 ZAP 文件

```bash
# 检查 ZAP JAR 文件
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/

# 查找所有 zap jar 文件
find /home/ubuntu -name "zap*.jar" 2>/dev/null
```

---

### 步骤 3: 检查 Java

```bash
# 检查 Java 版本
java -version

# 如果没有 Java
sudo apt update
sudo apt install -y openjdk-11-jdk
```

---

## ✅ 解决方案

### 方法 1: 使用简单启动脚本（推荐）

#### 上传脚本

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp test\start_zap_simple.sh ubuntu@119.45.255.144:/home/ubuntu/
```

#### 运行脚本

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 运行
cd /home/ubuntu
chmod +x start_zap_simple.sh
./start_zap_simple.sh
```

**预期输出：**
```
==========================================
  ZAP 服务启动脚本
==========================================

[-] 检查 ZAP 是否运行...
✅ ZAP 文件存在：/home/ubuntu/tools/zap/ZAP_2.17.0/zap-2.17.0.jar

[-] 启动 ZAP...
    PID: 12345

[-] 等待 ZAP 启动 (最多 30 秒)...

✅ ZAP 启动成功!

==========================================
  ZAP 服务信息
==========================================
  PID: 12345
  端口：8090
  路径：/home/ubuntu/tools/zap/ZAP_2.17.0
```

---

### 方法 2: 手动启动（最直接）

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 进入 ZAP 目录
cd /home/ubuntu/tools/zap/ZAP_2.17.0

# 启动 ZAP
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 等待 15 秒
sleep 15

# 验证
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8090
```

---

### 方法 3: 前台启动看错误（调试用）

如果后台启动失败，尝试前台启动看详细错误：

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 进入目录
cd /home/ubuntu/tools/zap/ZAP_2.17.0

# 前台启动（会看到实时日志）
java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090

# 按 Ctrl+C 停止
```

---

## 🐛 常见问题

### 问题 1: JAR 文件名不对

**检查实际文件名：**

```bash
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/
```

**可能的文件名：**
- `zap-2.17.0.jar`
- `ZAP_2.17.0.jar`
- `zap.jar`

**修改启动命令：**

```bash
# 根据实际文件名调整
nohup java -Xmx512m -jar 实际文件名.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &
```

---

### 问题 2: Java 版本不兼容

**检查 Java 版本：**

```bash
java -version
```

**ZAP 2.17.0 需要 Java 11+：**

```bash
# 安装 Java 11
sudo apt update
sudo apt install -y openjdk-11-jdk
```

---

### 问题 3: 内存不足

**减少内存分配：**

```bash
nohup java -Xmx256m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &
```

---

### 问题 4: 端口被占用

**检查并释放端口：**

```bash
# 检查端口
netstat -tlnp | grep 8090

# 杀掉占用进程
sudo fuser -k 8090/tcp

# 或使用不同端口
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8091 > /tmp/zap.log 2>&1 &
```

---

## 📊 验证 ZAP 运行

### 检查清单

```bash
# 1. 检查进程
ps aux | grep -i "zap.*jar" | grep -v grep

# 应该看到类似：
# ubuntu   12345  5.0  2.0  1234567  89012  ?  Sl   20:00   0:10  java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090

# 2. 检查端口
netstat -tlnp | grep 8090

# 应该看到类似：
# tcp   0   0.0.0.0:8090   0.0.0.0:*   LISTEN   12345/java

# 3. 测试 zap-cli
zap-cli -p 8090 status

# 应该看到：
# ZAP is running

# 4. 测试扫描
zap-cli -p 8090 quick-scan -s http://demo.testfire.net
```

---

## 🔧 Phase-2 适配器配置

如果 ZAP 使用非标准端口，修改 [`phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)：

```python
async def _call_zap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
    """调用 ZAP-CLI 进行 Web 应用扫描"""
    logger.info(f"调用 ZAP-CLI: {target}")
    
    try:
        # 使用 -p 参数指定端口
        cmd = f"zap-cli -p 8090 quick-scan -s {target}"
        # ... 其余代码
```

---

## 🎯 完整启动流程

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 检查 ZAP 文件
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/

# 3. 启动 ZAP
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &

# 4. 等待
sleep 15

# 5. 验证
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8090
zap-cli -p 8090 status

# 6. 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 📝 快速参考

### 启动命令（复制粘贴）

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &
sleep 15
ps aux | grep -i zap | grep -v grep
netstat -tlnp | grep 8090
zap-cli -p 8090 status
```

### 测试命令

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 🆘 如果还是失败

### 收集信息

```bash
# 1. 进程信息
ps aux | grep -i zap

# 2. 端口信息
netstat -tlnp | grep -i java

# 3. ZAP 日志
cat /tmp/zap.log

# 4. Java 版本
java -version

# 5. 文件列表
ls -la /home/ubuntu/tools/zap/ZAP_2.17.0/
```

### 提供这些信息以获取帮助

---

**立即执行启动 ZAP！** 🚀

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu/tools/zap/ZAP_2.17.0
nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8090 > /tmp/zap.log 2>&1 &
sleep 15
zap-cli -p 8090 status
```
