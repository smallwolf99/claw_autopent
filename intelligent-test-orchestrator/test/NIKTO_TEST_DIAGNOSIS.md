# Nikto 测试诊断

## 📋 测试命令

```bash
nikto -h http://demo.testfire.net -timeout 30 -nolookup | head -20
```

---

## 🔍 可能的结果

### 情况 1: 正常输出

```
- Nikto v2.1.6
---------------------------------------------------------------------------
+ Target IP:          173.165.149.50
+ Target Hostname:    demo.testfire.net
+ Target Port:        80
+ Start Time:         2026-04-22 12:00:00
---------------------------------------------------------------------------
+ /: Contains about 3436 images.
+ /: The anti-clickjacking header is not present.
+ /admin.php: PHP admin page found.
```

**说明：** Nikto 工作正常 ✅

---

### 情况 2: 没有输出

**可能原因：**
- 网络问题
- 目标无法访问
- Nikto 被防火墙阻止

**诊断命令：**
```bash
# 测试网络连接
curl -I http://demo.testfire.net

# 测试 DNS 解析
ping -c 3 demo.testfire.net

# 不使用 -nolookup 测试
nikto -h http://demo.testfire.net -timeout 30 | head -20
```

---

### 情况 3: 错误信息

**常见错误：**

#### 错误 1: 无法解析主机
```
ERROR: Unable to resolve host name
```
**解决：** DNS 问题，检查 `/etc/resolv.conf`

#### 错误 2: 无法连接
```
ERROR: Unable to connect to target
```
**解决：** 网络问题或目标不可达

#### 错误 3: 超时
```
ERROR: Timeout
```
**解决：** 增加超时时间

---

## 🔧 完整诊断脚本

```bash
#!/bin/bash

echo "=========================================="
echo "  Nikto 诊断测试"
echo "=========================================="
echo ""

TARGET="http://demo.testfire.net"

# 1. 测试网络连接
echo "[-] 测试网络连接..."
curl -I -m 10 $TARGET 2>&1 | head -5
echo ""

# 2. 测试 DNS
echo "[-] 测试 DNS 解析..."
ping -c 3 demo.testfire.net 2>&1 | head -5
echo ""

# 3. 测试 Nikto（基础）
echo "[-] 测试 Nikto（基础模式）..."
timeout 60 nikto -h $TARGET -timeout 30 2>&1 | head -30
echo ""

# 4. 测试 Nikto（快速）
echo "[-] 测试 Nikto（快速模式，不 DNS 查找）..."
timeout 60 nikto -h $TARGET -timeout 30 -nolookup 2>&1 | head -30
echo ""

# 5. 检查 Nikto 版本
echo "[-] Nikto 版本..."
nikto -Version 2>&1
echo ""

echo "=========================================="
echo "  诊断完成"
echo "=========================================="
```

---

## 📊 使用诊断脚本

### 创建脚本

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 创建诊断脚本
cat > /home/ubuntu/nikto_diagnose.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "  Nikto 诊断测试"
echo "=========================================="
echo ""

TARGET="http://demo.testfire.net"

# 1. 测试网络连接
echo "[-] 测试网络连接..."
curl -I -m 10 $TARGET 2>&1 | head -5
echo ""

# 2. 测试 DNS
echo "[-] 测试 DNS 解析..."
ping -c 3 demo.testfire.net 2>&1 | head -5
echo ""

# 3. 测试 Nikto（基础）
echo "[-] 测试 Nikto（基础模式）..."
timeout 60 nikto -h $TARGET -timeout 30 2>&1 | head -30
echo ""

# 4. 测试 Nikto（快速）
echo "[-] 测试 Nikto（快速模式）..."
timeout 60 nikto -h $TARGET -timeout 30 -nolookup 2>&1 | head -30
echo ""

# 5. 检查 Nikto 版本
echo "[-] Nikto 版本..."
nikto -Version 2>&1
echo ""

echo "=========================================="
echo "  诊断完成"
echo "=========================================="
EOF

chmod +x /home/ubuntu/nikto_diagnose.sh
```

---

### 运行诊断

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 运行诊断
./nikto_diagnose.sh
```

---

## 🎯 快速验证

### 最简单的测试

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 测试目标可达性
curl -I http://demo.testfire.net

# 应该看到：
# HTTP/1.1 200 OK
# Content-Type: text/html
```

---

### 如果 curl 成功但 Nikto 失败

**可能原因：**
- Nikto 配置问题
- Nikto 版本太旧
- Nikto 插件缺失

**解决：**
```bash
# 重新安装 Nikto
sudo apt remove -y nikto
sudo apt update
sudo apt install -y nikto

# 或使用 Git 安装最新版
cd /opt
sudo git clone https://github.com/sullo/nikto.git
ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto
```

---

### 如果 curl 也失败

**可能原因：**
- 网络问题
- 防火墙阻止
- 目标不可达

**解决：**
```bash
# 检查网络
ping -c 3 8.8.8.8
ping -c 3 demo.testfire.net

# 检查防火墙
sudo ufw status

# 检查路由
traceroute demo.testfire.net
```

---

## 📝 请提供输出

**请执行以下命令并提供输出：**

```bash
# 1. 测试网络
curl -I http://demo.testfire.net

# 2. 测试 Nikto
nikto -h http://demo.testfire.net -timeout 30 -nolookup | head -30

# 3. 检查版本
nikto -Version
```

**把这些输出发给我，我可以帮你诊断具体问题！** 🔍
