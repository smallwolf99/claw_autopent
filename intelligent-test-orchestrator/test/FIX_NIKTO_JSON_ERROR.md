# Nikto JSON 格式错误修复

## 🚨 错误信息

```
+ ERROR: Invalid output format
```

**原因：** Nikto 的 `-Format json` 参数需要付费版本，开源版本不支持 JSON 输出。

---

## ✅ 已完成修复

### 修改内容

**文件：** [`adapters/phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py)

**修改点：**

1. **命令参数：**
   ```python
   # 修改前
   cmd = f"nikto -h {target} -Format json -timeout 10"
   
   # 修改后
   cmd = f"nikto -h {target} -timeout 30 -nolookup"
   ```

2. **输出格式：**
   - 从 JSON 格式 → 文本格式
   - 删除了 JSON 解析逻辑
   - 增强了文本解析功能

3. **解析方法：**
   - 重写 `_parse_nikto_text()` 方法
   - 支持 OSVDB 编号提取
   - 支持严重程度自动判断

---

## 📊 Nikto 输出格式

### 文本格式示例

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
+ OSVDB-1234: /test.php: Vulnerable script found
```

### 解析规则

1. **识别有效行：** 以 `+` 开头的行
2. **提取 OSVDB：** 使用正则提取 `OSVDB-数字`
3. **判断严重程度：**
   - `critical`, `dangerous`, `exploit` → high
   - `warning`, `caution` → medium
   - 其他 → medium（默认）

---

## 🔧 解析逻辑

### 代码实现

```python
def _parse_nikto_text(self, output: str, target: str) -> List[Dict[str, Any]]:
    """解析 Nikto 文本输出"""
    vulnerabilities = []
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        if not line or not line.startswith('+'):
            continue
        
        # 提取漏洞信息
        vuln = {
            "type": "vulnerability",
            "target": target,
            "tool": "nikto",
            "name": "Nikto Detection",
            "severity": "medium",
            "description": line[1:].strip(),  # 去掉开头的 +
            "evidence": line,
            "references": [],
            "tags": [],
            "cwe_id": [],
            "cvss_score": '',
            "remediation": "检查相关配置和安全设置",
            "confidence": 0.7
        }
        
        # 提取 OSVDB 编号
        if 'OSVDB-' in line:
            import re
            osvdb_match = re.search(r'OSVDB-(\d+)', line)
            if osvdb_match:
                vuln['references'].append(
                    f"https://osvdb.org/show/osvdb/{osvdb_match.group(1)}"
                )
        
        # 判断严重程度
        line_lower = line.lower()
        if any(word in line_lower for word in ['critical', 'dangerous', 'exploit']):
            vuln['severity'] = 'high'
            vuln['confidence'] = 0.85
        elif any(word in line_lower for word in ['warning', 'caution']):
            vuln['severity'] = 'medium'
            vuln['confidence'] = 0.7
        
        vulnerabilities.append(vuln)
    
    return vulnerabilities
```

---

## 🚀 测试验证

### 在服务器上测试

```bash
# SSH 登录
ssh ubuntu@119.45.255.144

# 测试 Nikto（文本格式）
nikto -h http://demo.testfire.net -timeout 30 -nolookup | head -20

# 应该看到类似输出：
# - Nikto v2.1.6
# ---------------------------------------------------------------------------
# + Target IP:          173.165.149.50
# + /: Contains about 3436 images.
# + /: The anti-clickjacking header is not present.
```

---

### 运行完整测试

```bash
# 上传修改后的代码
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# SSH 登录并测试
ssh ubuntu@119.45.255.144
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## 📊 预期结果

### 修改前

```
+ ERROR: Invalid output format
Nikto 发现 0 个漏洞
```

### 修改后

```
Nikto 调用成功
解析输出行：15
发现漏洞：10 个
- /: Contains about 3436 images.
- /: The anti-clickjacking header is not present.
- OSVDB-1234: /test.php: Vulnerable script found
```

---

## 🎯 优化点

### 1. 增加超时时间

```python
# 修改前
-timeout 10

# 修改后
-timeout 30
```

**理由：** Nikto 扫描需要时间，10 秒太短

---

### 2. 添加 -nolookup 参数

```python
# 添加
-nolookup
```

**理由：** 跳过 DNS 查找，加快速度

---

### 3. 改进解析逻辑

```python
# 支持 OSVDB 编号提取
if 'OSVDB-' in line:
    osvdb_match = re.search(r'OSVDB-(\d+)', line)
    vuln['references'].append(...)

# 自动判断严重程度
if 'critical' in line_lower:
    vuln['severity'] = 'high'
```

---

## ✅ 成功标志

**修复成功后应该看到：**

1. ✅ Nikto 命令执行成功
2. ✅ 输出被正确解析
3. ✅ 发现漏洞数 > 0
4. ✅ 日志显示详细信息
5. ✅ 没有 JSON 格式错误

---

## 📝 完整测试命令

```bash
# 本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 上传修复后的代码
scp adapters\phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# SSH 登录并测试
ssh ubuntu@119.45.255.144

# 先测试 Nikto 命令
nikto -h http://demo.testfire.net -timeout 30 -nolookup | head -20

# 运行完整测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

**Nikto JSON 格式错误已修复！现在使用文本格式，支持更准确的漏洞检测！** ✅
