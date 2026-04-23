# 部署后代码同步指南

**问题**: 代码已修改但服务器仍报错  
**时间**: 2026-04-23  
**状态**: ✅ 需要重新加载 Python 模块

---

## 📋 问题分析

### 现象
```
2026-04-23 11:13:41 - Phase2Adapter - INFO - 漏洞检测完成：发现 0 个漏洞
❌ 错误：'Phase2Adapter' object has no attribute 'normalize_vulnerabilities'
```

### 根本原因

Python 模块已缓存，需要重新加载：
1. ✅ 代码已修改并保存到本地
2. ✅ 代码已部署到服务器
3. ❌ **Python 进程仍在使用旧的字节码缓存**

---

## 🔧 解决方案

### 方案 1: 清除 Python 缓存（推荐）

```bash
# SSH 到服务器
ssh ubuntu@你的服务器 IP

# 进入目录
cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator

# 清除所有 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 验证缓存已清除
ls -la adapters/__pycache__/ 2>/dev/null || echo "✅ 缓存已清除"
```

### 方案 2: 重启 OpenClaw（如果使用了 OpenClaw）

```bash
# 停止 OpenClaw
docker stop openclaw  # 或 kill <PID>

# 重新启动
docker start openclaw  # 或重新启动进程
```

### 方案 3: 重新部署代码

```bash
# 在本地 PowerShell
cd d:\TRAE\advanced-pentester-v1.2

# 重新部署到服务器
.\deploy_to_server.ps1 -TargetDirectory "advanced-pentester-v2"
```

---

## 🚀 完整测试流程

### 步骤 1: 清除缓存
```bash
cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator

# 清除缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

echo "✅ Python 缓存已清除"
```

### 步骤 2: 验证代码版本
```bash
# 检查 normalize_vulnerabilities 方法是否存在
grep -n "def normalize_vulnerabilities" adapters/phase2_adapter_real.py

# 应该输出类似：
# 462:    def normalize_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
```

### 步骤 3: 测试方法
```bash
# 设置路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 快速测试
python3 -c "
from adapters.phase2_adapter_real import Phase2Adapter
adapter = Phase2Adapter()
print('✅ normalize_vulnerabilities 方法存在')
print('✅ 方法位置:', adapter.normalize_vulnerabilities)
"
```

### 步骤 4: 运行集成测试
```bash
# 运行完整测试
python3 test/test_integration_fixed.py

# 或运行特定测试
python3 test/test_integration.py
```

---

## 📊 验证清单

在服务器上执行以下命令：

```bash
# 1. 检查代码文件
echo "=== 检查代码文件 ==="
grep -n "def normalize_vulnerabilities" adapters/phase2_adapter_real.py

# 2. 清除缓存
echo -e "\n=== 清除 Python 缓存 ==="
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
echo "✅ 缓存已清除"

# 3. 验证方法存在
echo -e "\n=== 验证方法存在 ==="
python3 -c "
from adapters.phase2_adapter_real import Phase2Adapter
adapter = Phase2Adapter()
has_method = hasattr(adapter, 'normalize_vulnerabilities')
print(f'✅ normalize_vulnerabilities: {\"存在\" if has_method else \"不存在\"}')
"

# 4. 测试标准化功能
echo -e "\n=== 测试标准化功能 ==="
python3 -c "
from adapters.phase2_adapter_real import Phase2Adapter
adapter = Phase2Adapter()

test_vulns = [
    {'id': 'TEST-001', 'name': 'Test Vuln', 'severity': 'HIGH', 'tool': 'zap'}
]

normalized = adapter.normalize_vulnerabilities(test_vulns)
print(f'✅ 标准化成功：{len(normalized)} 个漏洞')
print(f'   漏洞名称：{normalized[0][\"name\"]}')
print(f'   严重程度：{normalized[0][\"severity\"]}')
"
```

**预期输出**:
```
=== 检查代码文件 ===
462:    def normalize_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

=== 清除 Python 缓存 ===
✅ 缓存已清除

=== 验证方法存在 ===
✅ normalize_vulnerabilities: 存在

=== 测试标准化功能 ===
✅ 标准化成功：1 个漏洞
   漏洞名称：Test Vuln
   严重程度：high
```

---

## 🎯 常见部署问题

### 问题 1: 代码未同步

**症状**: 服务器代码与本地不一致

**解决**:
```bash
# 在服务器上检查文件修改时间
ls -lh adapters/phase2_adapter_real.py

# 检查文件内容
head -n 500 adapters/phase2_adapter_real.py | tail -n 50
```

### 问题 2: 缓存未清除

**症状**: 代码已更新但仍使用旧版本

**解决**:
```bash
# 强制清除所有缓存
find ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator \
  -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator \
  -name "*.pyc" -delete

# 验证
find . -type d -name __pycache__ | wc -l  # 应该输出 0
```

### 问题 3: Python 路径错误

**症状**: 导入错误的模块

**解决**:
```bash
# 检查 Python 路径
python3 -c "import sys; print('\n'.join(sys.path))"

# 设置正确的路径
export PYTHONPATH="$HOME/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator:$PYTHONPATH"

# 验证
python3 -c "
import adapters.phase2_adapter_real
print('模块路径:', adapters.phase2_adapter_real.__file__)
"
```

---

## 📁 相关文件

### 本地文件
- ✅ [`adapters/phase2_adapter_real.py`](../adapters/phase2_adapter_real.py) - 已修复
- ✅ [`MISSING_METHOD_FIX.md`](../MISSING_METHOD_FIX.md) - 修复报告
- ✅ [`ZAP_SCAN_FIX_GUIDE.md`](../ZAP_SCAN_FIX_GUIDE.md) - ZAP 修复指南

### 服务器文件
- 📍 `~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator/adapters/phase2_adapter_real.py`
- 📍 `~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator/test/`

---

## 🎉 总结

**修复步骤**:

1. **清除 Python 缓存** (必须！)
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

2. **验证代码已更新**
   ```bash
   grep -n "def normalize_vulnerabilities" adapters/phase2_adapter_real.py
   ```

3. **测试方法存在**
   ```bash
   python3 -c "from adapters.phase2_adapter_real import Phase2Adapter; print('✅ OK')"
   ```

4. **重新运行测试**
   ```bash
   python3 test/test_integration_fixed.py
   ```

**完成这些步骤后，错误应该消失了！** 🚀

---

**指南完成时间**: 2026-04-23
