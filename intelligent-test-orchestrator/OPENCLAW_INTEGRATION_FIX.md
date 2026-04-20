# OpenClaw 集成问题排查指南

## 问题描述

**现象:** 飞书没有反馈进度，但 OpenClaw 日志显示在调用工具

**可能原因:**
1. ✅ OpenClaw 正确调用了 Skill
2. ❌ 但输出没有正确回传到飞书
3. ❌ 返回值格式可能不兼容

---

## 🔧 解决方案

### 方案 1: 使用兼容版本（推荐）⭐

我已经创建了一个**兼容版本**：`main_openclaw_compatible.py`

**特点:**
- ✅ 同时使用 `print()` 和 `logger` 输出
- ✅ 添加多个返回值字段（`message`、`text`、`summary`）
- ✅ 输出 JSON 格式的最终结果
- ✅ 完整的错误追踪

**部署步骤:**

```bash
# SSH 到服务器
ssh ubuntu@119.45.255.144

# 备份原文件
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
cp main.py main.py.backup

# 使用兼容版本
cp main_openclaw_compatible.py main.py

# 或者直接使用新文件
mv main_openclaw_compatible.py main.py
```

**或者从本地上传:**

```powershell
# Windows PowerShell
scp main_openclaw_compatible.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/main.py
```

---

### 方案 2: 检查 OpenClaw 配置

**查看 OpenClaw 配置文件:**

```bash
ssh ubuntu@119.45.255.144
cat /home/ubuntu/.openclaw/config.yaml
```

**确认配置:**
```yaml
skills:
  - name: intelligent-test-orchestrator
    path: /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
    entry_point: main:OpenClawHandler.execute_intelligent_test
    # 或者
    module: main
    function: OpenClawHandler.execute_intelligent_test
    triggers:
      - "安全测试"
      - "渗透测试"
      - "漏洞扫描"
      - "帮我测试"
```

**检查返回格式配置:**
```yaml
# 某些 OpenClaw 版本需要配置返回格式
response_format:
  type: "json"  # 或 "text"
  include_output: true
  include_logs: true
```

---

### 方案 3: 查看 OpenClaw 日志

**实时查看日志:**

```bash
ssh ubuntu@119.45.255.144
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

**查找关键信息:**

1. **Skill 加载:**
   ```
   Loaded skill: intelligent-test-orchestrator
   ```

2. **触发词匹配:**
   ```
   Matched trigger: 帮我测试
   Calling function: execute_intelligent_test
   ```

3. **函数调用:**
   ```
   Calling intelligent-test-orchestrator.execute_intelligent_test
   Parameters: {"target": "http://...", "test_mode": "full"}
   ```

4. **输出内容:**
   ```
   stdout: 🚀 开始智能安全测试
   stdout: 🎯 目标：http://...
   ```

5. **返回值:**
   ```
   Return value: {"success": true, "summary": "..."}
   ```

6. **错误信息:**
   ```
   ERROR: Exception in execute_intelligent_test
   Traceback: ...
   ```

---

### 方案 4: 测试返回值格式

**创建测试脚本:**

```bash
ssh ubuntu@119.45.255.144
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
```

**创建 `test_return.py`:**

```python
#!/usr/bin/env python3
import json

def test_return():
    """测试返回值格式"""
    result = {
        "success": True,
        "message": "测试成功",
        "text": "这是返回的文本",
        "summary": "这是摘要信息",
        "output": "这是输出内容",
        "data": {
            "test": "value"
        }
    }
    
    print("返回值:", json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == "__main__":
    test_return()
```

**运行测试:**
```bash
python3 test_return.py
```

**检查 OpenClaw 如何解析:**
```bash
tail -f /home/ubuntu/.openclaw/logs/openclaw.log | grep -A 10 "test_return"
```

---

### 方案 5: 简化输出测试

**创建简化版本 `main_simple.py`:**

```python
#!/usr/bin/env python3
import asyncio

class OpenClawHandler:
    async def execute_intelligent_test(self, target: str, **kwargs):
        """简化测试版本"""
        print(f"🚀 开始测试：{target}")
        
        # 简单返回
        return {
            "success": True,
            "message": f"测试完成：{target}",
            "text": f"✅ 已测试 {target}",
            "data": {
                "target": target,
                "status": "completed"
            }
        }

async def main():
    handler = OpenClawHandler()
    result = await handler.execute_intelligent_test("http://test.com")
    print("返回:", result)
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

**测试:**
```bash
# 备份原文件
cp main.py main.py.full

# 使用简化版本
cp main_simple.py main.py

# 重启 OpenClaw
systemctl restart openclaw

# 在飞书测试
# 输入：帮我测试 http://test.com
```

---

## 📋 排查步骤清单

### 步骤 1: 确认 Skill 加载

```bash
ssh ubuntu@119.45.255.144
grep "Loaded skill" /home/ubuntu/.openclaw/logs/openclaw.log
```

**预期:**
```
Loaded skill: intelligent-test-orchestrator
```

### 步骤 2: 确认触发词匹配

```bash
grep "trigger" /home/ubuntu/.openclaw/logs/openclaw.log | tail -20
```

**预期:**
```
Matched trigger: 帮我测试
```

### 步骤 3: 确认函数调用

```bash
grep "execute_intelligent_test" /home/ubuntu/.openclaw/logs/openclaw.log | tail -20
```

**预期:**
```
Calling function: execute_intelligent_test
```

### 步骤 4: 查看标准输出

```bash
grep "stdout" /home/ubuntu/.openclaw/logs/openclaw.log | tail -30
```

**预期:**
```
stdout: 🚀 开始智能安全测试
stdout: 🎯 目标：http://...
```

### 步骤 5: 查看返回值

```bash
grep "Return value" /home/ubuntu/.openclaw/logs/openclaw.log | tail -10
```

**预期:**
```
Return value: {"success": true, "summary": "..."}
```

### 步骤 6: 查看飞书响应

```bash
grep "feishu" /home/ubuntu/.openclaw/logs/openclaw.log | tail -20
# 或
grep "lark" /home/ubuntu/.openclaw/logs/openclaw.log | tail -20
```

**预期:**
```
Sending message to feishu: {...}
Message sent successfully
```

---

## 🔍 常见问题

### 问题 1: 有日志无输出

**症状:** OpenClaw 日志显示调用，但飞书无响应

**可能原因:**
- OpenClaw 没有捕获 stdout
- 返回值格式不正确
- 飞书 API 调用失败

**解决:**
```bash
# 查看详细日志
tail -f /home/ubuntu/.openclaw/logs/openclaw.log

# 检查 OpenClaw 配置
cat /home/ubuntu/.openclaw/config.yaml
```

### 问题 2: 返回值未解析

**症状:** 函数执行成功，但飞书显示空白

**可能原因:**
- OpenClaw 期望特定字段名
- JSON 格式不正确
- 编码问题

**解决:**
使用兼容版本，包含多个字段：
```python
return {
    "success": True,
    "message": "...",  # OpenClaw 常用
    "text": "...",     # 某些版本使用
    "summary": "...",  # 通用字段
    "output": "..."    # 备用字段
}
```

### 问题 3: 输出被截断

**症状:** 只显示部分输出

**可能原因:**
- 输出缓冲区限制
- 日志级别设置
- 飞书消息长度限制

**解决:**
```python
# 使用 flush=True
print("消息", flush=True)

# 分段输出
for line in lines:
    print(line, flush=True)
```

---

## 🎯 推荐排查流程

1. **使用兼容版本** - 上传 `main_openclaw_compatible.py`
2. **查看日志** - 确认调用和输出
3. **简化测试** - 使用最简版本验证
4. **检查配置** - 确认 OpenClaw 配置正确
5. **查看飞书日志** - 确认消息发送

---

## 📞 需要帮助

如果以上方法都无效，请提供：

1. **OpenClaw 日志片段** (调用前后的完整日志)
   ```bash
   ssh ubuntu@119.45.255.144
   tail -100 /home/ubuntu/.openclaw/logs/openclaw.log
   ```

2. **OpenClaw 配置文件**
   ```bash
   cat /home/ubuntu/.openclaw/config.yaml
   ```

3. **测试结果**
   ```bash
   cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
   python3 test_simple.py
   ```

4. **飞书截图** - 显示输入和输出（或缺少输出）

---

**下一步:** 先使用兼容版本测试，然后查看日志确认问题！🔍
