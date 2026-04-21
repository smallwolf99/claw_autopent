# Phase-2 工具调用修复

## 🐛 问题确认

工具都已安装，但调用失败：

```bash
$ which nuclei afrog nikto zap-cli sqlmap
/home/ubuntu/go/bin/nuclei
/home/ubuntu/go/bin/afrog
/usr/bin/nikto
/home/ubuntu/.local/bin/zap-cli
/home/ubuntu/.local/bin/sqlmap
```

**错误日志：**
1. `解析 Nikto JSON 失败` - Nikto 输出格式问题
2. `Nuclei 执行失败` - 空错误（返回码非 0）
3. `ZAP-CLI 连接拒绝` - ZAP 服务未启动

---

## 🔧 修复方案

### 方案 1: 快速修复（推荐）

#### 步骤 1: 上传修复后的代码

```bash
# 从本地上传修复后的 phase2_adapter_real.py
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

scp adapters/phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/
```

#### 步骤 2: 启动 ZAP 服务

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 上传启动脚本
scp test/start_zap.sh ubuntu@119.45.255.144:/home/ubuntu/

# 登录服务器并启动 ZAP
ssh ubuntu@119.45.255.144
cd /home/ubuntu
chmod +x start_zap.sh
./start_zap.sh
```

**如果 ZAP 启动成功，会显示：**
```
✅ ZAP 已经在运行
ZAP is running
```

---

#### 步骤 3: 运行诊断脚本

```bash
# 上传诊断脚本
scp test/diagnose_tools.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/

# 运行诊断
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/diagnose_tools.py
```

**诊断脚本会显示：**
- Nikto 的实际输出和返回码
- Nuclei 的实际输出和返回码
- ZAP-CLI 的运行状态

---

#### 步骤 4: 重新测试

```bash
python3 test/test_phase2_phase3_real.py
```

---

### 方案 2: 手动修复

#### 1. 启动 ZAP 服务

```bash
# 方法 A: 使用 zap-cli
zap-cli start

# 检查状态
zap-cli status

# 如果失败，使用 Docker
docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh

# 设置端口（如果使用非标准端口）
zap-cli settings set port 8090
```

---

#### 2. 更新 Nuclei 模板

```bash
# 更新 Nuclei 模板
nuclei -ut

# 测试 Nuclei
nuclei -u http://demo.testfire.net -json -silent -timeout 10 | head -5
```

---

#### 3. 测试 Nikto

```bash
# 测试 Nikto JSON 输出
nikto -h http://demo.testfire.net -Format json -timeout 10 2>&1 | head -20

# 如果 JSON 格式不支持，使用文本格式
nikto -h http://demo.testfire.net -timeout 10 2>&1 | head -20
```

---

## 📊 代码修复说明

### 修复 1: Nikto JSON 解析

**问题：** Nikto 可能输出文本格式而非 JSON

**修复：** 添加文本解析备用方案

```python
async def _call_nikto(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
    # ...
    try:
        data = json.loads(output)
        # 解析 JSON
    except json.JSONDecodeError:
        # 使用文本解析备用方案
        vulnerabilities = self._parse_nikto_text(output, target)
```

---

### 修复 2: Nuclei 错误处理

**问题：** Nuclei 返回码非 0 时直接返回空列表

**修复：** 继续尝试解析输出，记录详细错误

```python
if process.returncode != 0:
    logger.warning(f"Nuclei 返回码非 0: {process.returncode}")
    if error_output:
        logger.warning(f"Nuclei 错误：{error_output[:300]}")
    # 继续尝试解析输出
```

---

### 修复 3: ZAP 服务检查

**问题：** ZAP 服务未启动

**修复：** 提供启动脚本 `start_zap.sh`

---

## 🔍 诊断工具

### 运行诊断脚本

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/diagnose_tools.py
```

**输出示例：**

```
======================================================================
  Phase-2 工具诊断
======================================================================

----------------------------------------------------------------------
1. 诊断 Nikto
----------------------------------------------------------------------
命令：nikto -h http://demo.testfire.net -Format json -timeout 10

返回码：0
STDOUT (前 500 字符):
{"vulnerabilities": [{"id": "1", "msg": "Server found", ...}

✅ JSON 解析成功
   漏洞数：5

----------------------------------------------------------------------
2. 诊断 Nuclei
----------------------------------------------------------------------
命令：nuclei -u http://demo.testfire.net -json -silent -timeout 10

返回码：0
STDOUT (前 500 字符):
{"template-id": "xss-detected", ...}

✅ Nuclei 执行成功
   有输出内容

----------------------------------------------------------------------
3. 诊断 ZAP-CLI
----------------------------------------------------------------------
检查 ZAP 服务状态...
命令：zap-cli status

返回码：0
STDOUT:
ZAP is running

✅ ZAP 服务正在运行
```

---

## ✅ 验证标准

修复后运行测试应该看到：

```
======================================================================
  Phase-2 漏洞检测 - 真实工具测试
======================================================================

🎯 测试目标：http://demo.testfire.net
📡 开始漏洞检测...

2026-04-21 18:00:00 - 调用 Nuclei: http://demo.testfire.net
2026-04-21 18:00:05 - Nuclei 发现 8 个漏洞 ✅
2026-04-21 18:00:05 - 调用 Nikto: http://demo.testfire.net
2026-04-21 18:00:30 - Nikto 发现 5 个漏洞 ✅
2026-04-21 18:00:30 - 调用 ZAP-CLI: http://demo.testfire.net
2026-04-21 18:01:00 - ZAP-CLI 发现 3 个漏洞 ✅

📊 测试结果:
  • 发现漏洞数：16
  • 耗时：180.45 秒

✅ 验证结果:
  ✅ 使用的工具：nuclei, nikto, zap
  ✅ 检测到 16 个漏洞
```

---

## 🛠️ 常见问题

### Q1: ZAP 启动失败？

**A:** 使用 Docker：

```bash
docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh
zap-cli settings set port 8090
```

---

### Q2: Nuclei 没有输出？

**A:** 更新模板：

```bash
nuclei -ut
```

---

### Q3: Nikto JSON 解析失败？

**A:** 代码已自动降级到文本解析，无需手动干预。

---

## 📚 相关文件

| 文件 | 路径 | 用途 |
|------|------|------|
| **修复后的适配器** | [`adapters/phase2_adapter_real.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter_real.py) | 主要修复代码 |
| **诊断脚本** | [`test/diagnose_tools.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\diagnose_tools.py) | 诊断工具问题 |
| **ZAP 启动脚本** | [`test/start_zap.sh`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test\start_zap.sh) | 启动 ZAP 服务 |

---

## 🚀 立即执行

```bash
# 1. 上传修复后的代码
scp adapters/phase2_adapter_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 2. SSH 登录
ssh ubuntu@119.45.255.144

# 3. 启动 ZAP
cd /home/ubuntu
chmod +x start_zap.sh
./start_zap.sh

# 4. 运行诊断（可选）
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/diagnose_tools.py

# 5. 运行测试
python3 test/test_phase2_phase3_real.py
```

**预期：** 发现 10-25 个漏洞，耗时 5-15 分钟 ✅
