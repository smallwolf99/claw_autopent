# Nuclei 返回码 2 - 错误诊断与修复

## 🚨 错误信息

```
adapters.phase2_adapter_real - WARNING - Nuclei 返回码非 0: 2
```

---

## 🔍 Nuclei 返回码含义

| 返回码 | 含义 |
|--------|------|
| **0** | 成功执行 |
| **1** | 执行错误 |
| **2** | **参数错误/配置问题** |
| **3** | 发现漏洞 |

**返回码 2 表示：命令参数有问题或 Nuclei 配置不正确**

---

## 🐛 可能的原因

### 原因 1: Nuclei 模板未更新

Nuclei 首次运行需要下载模板，如果网络问题可能导致模板下载失败。

**检查：**
```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 检查模板
nuclei -ut

# 查看模板数量
nuclei -silent -u http://demo.testfire.net | wc -l
```

---

### 原因 2: 命令参数问题

当前使用的命令：
```bash
nuclei -u http://demo.testfire.net -json -silent -timeout 10
```

**可能的问题：**
- `-json` 参数格式可能需要 `-jsonl`（新版 Nuclei）
- `-timeout 10` 可能太短

---

### 原因 3: Nuclei 版本问题

旧版本 Nuclei 可能不支持某些参数。

**检查：**
```bash
# 查看版本
nuclei -version

# 查看帮助
nuclei -h | grep -i json
```

---

### 原因 4: 目标 URL 无法访问

如果目标 URL 无法访问，Nuclei 可能返回错误。

**检查：**
```bash
# 测试目标
curl -I http://demo.testfire.net

# 使用 wget
wget --spider http://demo.testfire.net
```

---

## ✅ 解决方案

### 方案 1: 更新 Nuclei 模板（推荐）

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 更新模板
nuclei -ut

# 测试运行
nuclei -u http://demo.testfire.net -jsonl -timeout 10 | head -5
```

---

### 方案 2: 修改命令参数

修改 [`phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)：

```python
async def _call_nuclei(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
    """调用 Nuclei 进行模板化漏洞扫描"""
    logger.info(f"调用 Nuclei: {target}")
    
    try:
        # 真实调用 Nuclei
        # -u: 目标 URL
        # -jsonl: JSON Lines 输出（新版 Nuclei）
        # -silent: 静默模式
        # -timeout: 超时时间（秒）
        # -rate-limit: 每秒请求数限制
        cmd = f"nuclei -u {target} -jsonl -silent -timeout 10 -rate-limit 10"
        logger.info(f"执行命令：{cmd}")
        
        # ... 其余代码不变
```

**修改说明：**
- `-json` → `-jsonl`（新版 Nuclei 使用 JSONL 格式）
- 添加 `-rate-limit 10` 避免请求过快

---

### 方案 3: 增加超时时间

```python
# 修改超时时间
cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 5"
```

---

### 方案 4: 使用特定模板

如果默认模板有问题，可以指定模板：

```python
# 只使用 Web 漏洞模板
cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -tags web"
```

---

## 🔧 完整诊断流程

### 步骤 1: SSH 登录并检查

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 1. 检查 Nuclei 版本
nuclei -version

# 2. 更新模板
nuclei -ut

# 3. 测试运行（手动）
nuclei -u http://demo.testfire.net -jsonl -timeout 10 | head -10

# 4. 查看错误
nuclei -u http://demo.testfire.net -timeout 10 2>&1 | head -20
```

---

### 步骤 2: 修改代码

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 编辑 phase2_adapter_real.py
# 修改第 119 行：
# 从：cmd = f"nuclei -u {target} -json -silent -timeout 10"
# 改为：cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 5"
```

---

### 步骤 3: 重新上传并测试

```bash
# 上传修改后的文件
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# SSH 登录
ssh ubuntu@119.45.255.144

# 重启 OpenClaw
sudo systemctl restart openclaw

# 测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 📊 快速修复命令

```bash
# 1. SSH 登录
ssh ubuntu@119.45.255.144

# 2. 更新 Nuclei 模板
nuclei -ut

# 3. 测试运行
nuclei -u http://demo.testfire.net -jsonl -timeout 30 | head -5

# 4. 如果成功，修改代码并重新上传
```

---

## 🎯 推荐的代码修改

### 修改 1: 使用 JSONL 格式

```python
# 第 119 行
cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 5"
```

### 修改 2: 改进错误处理

```python
# 第 137-142 行
if process.returncode != 0:
    logger.warning(f"Nuclei 返回码非 0: {process.returncode}")
    if error_output:
        logger.warning(f"Nuclei 错误：{error_output[:500]}")
    # 继续尝试解析输出（可能有部分结果）
    # 如果返回码是 2，记录详细信息
    if process.returncode == 2:
        logger.error(f"Nuclei 参数错误，命令：{cmd}")
```

### 修改 3: 添加版本检查

```python
# 在 _call_nuclei 方法开头添加
import subprocess
try:
    result = subprocess.run(['nuclei', '-version'], capture_output=True, text=True, timeout=5)
    logger.info(f"Nuclei 版本：{result.stdout.strip()}")
except Exception as e:
    logger.warning(f"无法获取 Nuclei 版本：{e}")
```

---

## 📝 测试命令

### 手动测试 Nuclei

```bash
# 基础测试
nuclei -u http://demo.testfire.net -timeout 10

# JSONL 输出
nuclei -u http://demo.testfire.net -jsonl -timeout 10 | head -5

# 详细模式
nuclei -u http://demo.testfire.net -v

# 只运行特定模板
nuclei -u http://demo.testfire.net -tags xss,sqli -timeout 10
```

---

## 🆘 如果还是失败

### 收集信息

```bash
# 1. Nuclei 版本
nuclei -version

# 2. 模板数量
nuclei -ut
ls -la ~/nuclei-templates/ | wc -l

# 3. 测试运行
nuclei -u http://demo.testfire.net -v 2>&1 | head -50

# 4. 系统信息
uname -a
free -h
```

---

## ✅ 成功标志

```bash
# 成功运行应该看到：
nuclei -u http://demo.testfire.net -jsonl -timeout 30

# 输出类似：
{"template":"cves/2021/CVE-2021-1234.yaml","info":{"name":"Example Vulnerability","severity":"high"},"host":"http://demo.testfire.net","matched-at":"http://demo.testfire.net/login","type":"http","request":"GET /login HTTP/1.1"}
```

---

**立即执行更新和测试！** 🚀

```bash
ssh ubuntu@119.45.255.144
nuclei -ut
nuclei -u http://demo.testfire.net -jsonl -timeout 30 | head -5
```
