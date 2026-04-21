# Phase-2 工具错误修复指南

## 🐛 错误分析

根据你提供的错误日志，有三个主要问题：

---

### 问题 1: Nikto JSON 解析失败

```
2026-04-21 16:06:06,931 - adapters.phase2_adapter_real - ERROR - 解析 Nikto JSON 失败
2026-04-21 16:06:06,932 - adapters.phase2_adapter_real - INFO - Nikto 发现 0 个漏洞
```

**原因：**
- Nikto 可能没有安装
- 或者 Nikto 输出格式不是 JSON（可能是文本格式）
- Nikto 版本过旧，不支持 `-Format json` 参数

**验证方法：**
```bash
# 检查 Nikto 是否安装
which nikto

# 检查 Nikto 版本
nikto -Version

# 测试 Nikto 输出
nikto -h http://demo.testfire.net -Format json -timeout 10 | head -20
```

**解决方案：**

#### 方案 A: 安装/更新 Nikto

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nikto

# 或从源码安装（最新版本）
git clone https://github.com/sullo/nikto.git
cd nikto/program
perl nikto.pl -Version
```

---

#### 方案 B: 修改代码支持文本输出

如果 Nikto 版本过旧，修改 [`phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py#L268-L299)：

```python
async def _call_nikto(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
    """调用 Nikto 进行 Web 漏洞扫描"""
    logger.info(f"调用 Nikto: {target}")
    
    try:
        # 尝试使用 JSON 格式（新版本）
        cmd = f"nikto -h {target} -Format json -timeout 10"
        logger.info(f"执行命令：{cmd}")
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=600
        )
        
        output = stdout.decode()
        
        # 如果 JSON 解析失败，尝试文本解析
        vulnerabilities = []
        try:
            data = json.loads(output)
            vulns = data.get('vulnerabilities', [])
            for vuln in vulns:
                normalized = self._normalize_nikto_vuln(vuln, target)
                if normalized:
                    vulnerabilities.append(normalized)
        except json.JSONDecodeError:
            # 文本格式解析
            logger.info("Nikto 输出为文本格式，尝试解析...")
            vulnerabilities = self._parse_nikto_text(output, target)
        
        logger.info(f"Nikto 发现 {len(vulnerabilities)} 个漏洞")
        return vulnerabilities
```

---

### 问题 2: Nuclei 执行失败

```
2026-04-21 16:06:06,977 - adapters.phase2_adapter_real - WARNING - Nuclei 执行失败：
```

**原因：**
- Nuclei 未安装
- Nuclei 不在 PATH 中
- Nuclei 模板未初始化

**验证方法：**
```bash
# 检查 Nuclei 是否安装
which nuclei

# 检查版本
nuclei -version

# 测试运行
nuclei -u http://demo.testfire.net -json -silent -timeout 10
```

**解决方案：**

#### 安装 Nuclei

```bash
# 方法 1: 使用 Go（推荐）
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# 方法 2: 下载二进制文件
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
unzip nuclei_linux_amd64.zip
sudo mv nuclei /usr/local/bin/

# 初始化模板
nuclei -ut
```

---

### 问题 3: ZAP-CLI 连接拒绝

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**原因：**
- ZAP 代理服务未启动
- ZAP 未监听默认端口（8080 或 8090）

**验证方法：**
```bash
# 检查 ZAP 是否运行
ps aux | grep zap

# 检查端口
netstat -tlnp | grep 8080
netstat -tlnp | grep 8090

# 测试 ZAP-CLI
zap-cli status
```

**解决方案：**

#### 启动 ZAP 代理服务

```bash
# 方法 1: 启动 ZAP 守护进程
zap-cli start

# 检查状态
zap-cli status

# 如果失败，查看日志
zap-cli logs

# 方法 2: 手动启动 OWASP ZAP
# 下载并安装 OWASP ZAP
# https://www.zaproxy.org/download/

# 启动 ZAP（GUI 模式）
./zap.sh

# 或在后台启动
java -jar zap.jar -daemon -port 8090
```

---

#### 配置 ZAP-CLI 端口

如果 ZAP 运行在非标准端口：

```bash
# 设置 API 密钥（如果需要）
zap-cli settings set api-key your-api-key

# 设置端口
zap-cli settings set port 8090

# 验证连接
zap-cli status
```

---

## 🔧 一键修复脚本

创建修复脚本：

```bash
#!/bin/bash
# fix_phase2_tools.sh

echo "=========================================="
echo "  Phase-2 工具修复脚本"
echo "=========================================="

# 检查 Nikto
echo ""
echo "[-] 检查 Nikto..."
if ! command -v nikto &> /dev/null; then
    echo "❌ Nikto 未安装，正在安装..."
    sudo apt update
    sudo apt install -y nikto
else
    echo "✅ Nikto 已安装"
    nikto -Version
fi

# 检查 Nuclei
echo ""
echo "[-] 检查 Nuclei..."
if ! command -v nuclei &> /dev/null; then
    echo "❌ Nuclei 未安装，正在安装..."
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    # 初始化模板
    nuclei -ut
else
    echo "✅ Nuclei 已安装"
    nuclei -version
fi

# 检查 ZAP-CLI
echo ""
echo "[-] 检查 ZAP-CLI..."
if ! command -v zap-cli &> /dev/null; then
    echo "❌ ZAP-CLI 未安装，正在安装..."
    pip3 install zap-cli
else
    echo "✅ ZAP-CLI 已安装"
fi

# 启动 ZAP
echo ""
echo "[-] 启动 ZAP 代理服务..."
zap-cli start
sleep 5

# 检查状态
echo ""
echo "[-] 检查 ZAP 状态..."
zap-cli status

# 测试工具
echo ""
echo "=========================================="
echo "  测试工具"
echo "=========================================="

echo ""
echo "[-] 测试 Nikto..."
timeout 30 nikto -h http://demo.testfire.net -Format json 2>&1 | head -5

echo ""
echo "[-] 测试 Nuclei..."
timeout 30 nuclei -u http://demo.testfire.net -json -silent 2>&1 | head -5

echo ""
echo "[-] 测试 ZAP-CLI..."
zap-cli status

echo ""
echo "=========================================="
echo "  修复完成！"
echo "=========================================="
```

---

## 📊 工具依赖清单

### 必需工具

| 工具 | 最低版本 | 安装方式 | 用途 |
|------|---------|---------|------|
| **Nikto** | 2.1.6 | `apt install nikto` | Web 漏洞扫描 |
| **Nuclei** | 3.0+ | `go install nuclei` | 模板化扫描 |
| **ZAP-CLI** | 0.2.0+ | `pip3 install zap-cli` | ZAP 命令行 |
| **OWASP ZAP** | 2.14+ | 官网下载 | Web 应用扫描 |
| **SQLMap** | 1.7+ | `git clone` | SQL 注入检测 |
| **Afrog** | 2.0+ | `go install` | PoC 验证 |

---

## 🚀 完整安装流程

### 在 Ubuntu 服务器上

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
sudo apt install -y git curl wget perl python3-pip

# 3. 安装 Nikto
sudo apt install -y nikto

# 4. 安装 Nuclei（需要 Go）
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -ut  # 初始化模板

# 5. 安装 ZAP-CLI
pip3 install zap-cli

# 6. 安装 SQLMap
git clone https://github.com/sqlmapproject/sqlmap.git
echo 'export PATH=$PATH:/path/to/sqlmap' >> ~/.bashrc
source ~/.bashrc

# 7. 安装 Afrog
go install github.com/zan8in/afrog/v2@latest

# 8. 启动 ZAP
zap-cli start

# 9. 验证所有工具
which nikto nuclei zap-cli sqlmap afrog
```

---

## 🔍 调试技巧

### 1. 单独测试每个工具

```bash
# 测试 Nikto
nikto -h http://demo.testfire.net -timeout 10

# 测试 Nuclei
nuclei -u http://demo.testfire.net -json -silent -timeout 10

# 测试 ZAP-CLI
zap-cli quick-scan -s http://demo.testfire.net

# 测试 SQLMap
sqlmap --batch --level=1 --risk=1 -u "http://demo.testfire.net" --dbs

# 测试 Afrog
afrog -u http://demo.testfire.net -json
```

---

### 2. 查看详细日志

修改 `phase2_adapter_real.py`，增加日志级别：

```python
# 在文件开头
logging.basicConfig(level=logging.DEBUG)
```

---

### 3. 检查工具输出

```python
# 在工具调用后添加调试输出
logger.info(f"Nikto stdout: {stdout.decode()[:500]}")
logger.info(f"Nikto stderr: {stderr.decode()[:500]}")
```

---

## 📝 常见问题 FAQ

### Q1: Nikto 输出不是 JSON 格式？

**A:** 旧版本 Nikto 不支持 JSON 输出，需要：
1. 更新到最新版本
2. 或修改代码支持文本解析

---

### Q2: Nuclei 模板加载失败？

**A:** 需要初始化模板：
```bash
nuclei -ut
```

---

### Q3: ZAP-CLI 一直连接失败？

**A:** 
1. 确保 ZAP 已启动：`zap-cli start`
2. 检查端口：`netstat -tlnp | grep 8080`
3. 设置正确的端口：`zap-cli settings set port 8090`

---

### Q4: 工具安装成功但调用失败？

**A:** 
1. 检查 PATH 环境变量
2. 使用绝对路径测试
3. 检查权限：`chmod +x /path/to/tool`

---

## ✅ 验证修复

运行测试验证：

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行测试
python3 test/test_phase2_phase3_real.py
```

**预期输出：**
```
✅ 所有工具调用成功
📊 发现 10+ 个漏洞
⏱️  耗时 5-15 分钟
```

---

## 📚 相关文档

- 📖 [`test/TESTFIRE_TARGET_GUIDE.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\TESTFIRE_TARGET_GUIDE.md) - 靶场测试说明
- 📖 [`test/PHASE2_PHASE3_TEST_GUIDE.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\PHASE2_PHASE3_TEST_GUIDE.md) - Phase-2&3 测试指南
- 📖 [`test/FAQ.md`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\FAQ.md) - 常见问题

---

**修复完成后再次运行测试！** 🚀

```bash
python3 test/test_phase2_phase3_real.py
```
