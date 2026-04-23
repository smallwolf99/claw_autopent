# ZAP 扫描失败修复指南

**问题**: ZAP 扫描返回码为 1，报告文件不存在  
**时间**: 2026-04-23  
**状态**: ✅ 已改进错误处理和诊断

---

## 📋 问题现象

### 错误日志
```
2026-04-23 10:03:05,313 - Phase2Adapter - WARNING - 命令返回码非 0: 1, 错误：无
2026-04-23 10:03:05 - Phase2Adapter - WARNING - ZAP 报告文件不存在：/tmp/zap_report_xxx.json
```

### 可能原因

1. **ZAP 服务未运行** - ZAP daemon 未启动或崩溃
2. **目标无法访问** - 网络问题或目标拒绝连接
3. **ZAP 配置问题** - 端口不对、权限问题等
4. **扫描超时** - 目标响应太慢或被防火墙拦截
5. **磁盘空间不足** - /tmp 目录写满

---

## 🔧 已实施的改进

### 1. 增强错误日志

**修改前**:
```python
self.logger.warning(f"ZAP 报告文件不存在：{report_file}")
self.logger.debug(f"stdout: {stdout[:500]}")
```

**修改后**:
```python
self.logger.error(f"ZAP 报告文件不存在：{report_file}")
self.logger.error(f"可能原因:")
self.logger.error(f"  1. ZAP 扫描失败或被中断")
self.logger.error(f"  2. 目标无法访问：{target}")
self.logger.error(f"  3. ZAP 配置问题")
self.logger.debug(f"stdout: {stdout[:1000]}")  # 更详细的输出
```

### 2. 添加重试机制

```python
# 使用 call_tool_with_retry 增加重试机制
return await self.call_tool_with_retry(
    cmd=cmd,
    timeout=900,
    parse_func=parse_output,
    max_retries=2,      # 最多重试 2 次
    retry_delay=5       # 重试间隔 5 秒
)
```

### 3. 创建诊断工具

新增 [`test/diagnose_zap_scan.py`](../test/diagnose_zap_scan.py) - 完整的 ZAP 诊断工具

**功能**:
- ✅ 检查 zap-cli 路径
- ✅ 检查 ZAP 服务状态
- ✅ 检查 8080 端口监听
- ✅ 测试目标可达性
- ✅ 执行测试扫描
- ✅ 提供详细修复建议

---

## 🚀 诊断步骤

### 方法 1: 使用诊断工具（推荐）

```bash
# SSH 到服务器
ssh ubuntu@你的服务器 IP

# 进入目录
cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator

# 设置路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 运行诊断工具
python3 test/diagnose_zap_scan.py http://demo.testfire.net
```

**预期输出**:
```
============================================================
ZAP 扫描失败诊断工具
============================================================
目标：http://demo.testfire.net

============================================================
步骤 0: 检查 zap-cli 路径
============================================================
执行：which zap-cli
✅ zap-cli 路径：/home/ubuntu/.local/bin/zap-cli
✅ 文件可执行
✅ 命令正常：Usage: zap-cli [OPTIONS] COMMAND [ARGS]...

============================================================
步骤 1: 检查 ZAP 服务状态
============================================================
执行：zap-cli -p 8080 status
✅ ZAP 服务运行正常

============================================================
步骤 2: 检查 8080 端口监听
============================================================
执行：ss -tlnp | grep :8080
✅ 端口 8080 正在监听:
   tcp  0  0 0.0.0.0:8080  0.0.0.0:*  LISTEN  1234/java

============================================================
步骤 3: 测试目标可达性 (http://demo.testfire.net)
============================================================
执行：curl -I --connect-timeout 10 http://demo.testfire.net
✅ 目标可访问
   HTTP/1.1 200 OK
   Content-Type: text/html
   ...

============================================================
步骤 4: 测试 ZAP 快速扫描
============================================================
执行命令：zap-cli -p 8080 quick-scan -s all -f json -o /tmp/zap_test_report_xxx.json http://demo.testfire.net
返回码：0
✅ ZAP 扫描成功
✅ 报告生成成功，发现 15 个警报
   1. SQL Injection
   2. Cross-Site Scripting (Reflected)
   3. External Redirect
...

============================================================
诊断总结
============================================================
✅ zap-cli 路径: 正常
✅ ZAP 服务运行: 正常
✅ 8080 端口监听: 正常
✅ 目标可访问: 正常
✅ ZAP 扫描测试: 正常

============================================================
✅ 所有检查通过，ZAP 配置正常
============================================================
```

### 方法 2: 手动诊断

#### 步骤 1: 检查 ZAP 状态
```bash
zap-cli -p 8080 status
```

**正常输出**: `ZAP is running`

**错误处理**:
```bash
# 如果失败，启动 ZAP
zap-cli start

# 或指定端口
zap-cli -p 8080 start
```

#### 步骤 2: 检查端口监听
```bash
ss -tlnp | grep :8080
# 或
netstat -tlnp | grep :8080
```

**正常输出**: `tcp  0  0 0.0.0.0:8080  LISTEN  1234/java`

#### 步骤 3: 测试目标访问
```bash
curl -I http://demo.testfire.net
```

**正常输出**: `HTTP/1.1 200 OK`

#### 步骤 4: 手动测试 ZAP 扫描
```bash
# 创建测试报告
zap-cli -p 8080 quick-scan -s all -f json -o /tmp/test_zap.json http://demo.testfire.net

# 检查返回码
echo $?  # 应该输出 0

# 检查报告文件
ls -lh /tmp/test_zap.json

# 查看报告内容
cat /tmp/test_zap.json | python3 -m json.tool | head -30
```

---

## 🎯 常见问题解决

### 问题 1: ZAP 服务未运行

**症状**:
```
zap-cli -p 8080 status
Error: Unable to connect to ZAP
```

**解决**:
```bash
# 启动 ZAP
zap-cli start

# 等待启动完成
sleep 5

# 验证状态
zap-cli -p 8080 status
```

### 问题 2: 端口被占用

**症状**:
```
zap-cli start
Error: Port 8080 is already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8080
# 或
netstat -tlnp | grep :8080

# 杀死占用进程
kill -9 <PID>

# 或使用其他端口
zap-cli -p 8090 start
```

### 问题 3: 目标无法访问

**症状**:
```
curl: (7) Failed to connect to demo.testfire.net port 80: Connection refused
```

**解决**:
```bash
# 检查网络
ping demo.testfire.net

# 检查 DNS
nslookup demo.testfire.net

# 检查防火墙
sudo ufw status
```

### 问题 4: 扫描超时

**症状**:
```
命令返回码非 0: 1
ZAP 报告文件不存在
```

**解决**:
```bash
# 增加超时时间
zap-cli -p 8080 quick-scan -s all -t 600 http://demo.testfire.net

# 或减少扫描范围
zap-cli -p 8080 quick-scan -s medium,low http://demo.testfire.net
```

### 问题 5: 磁盘空间不足

**症状**:
```
No space left on device
```

**解决**:
```bash
# 检查磁盘空间
df -h /tmp

# 清理临时文件
rm -rf /tmp/zap_report_*.json
rm -rf /tmp/zap_test_*.json

# 检查大文件
du -sh /tmp/* | sort -h | tail -10
```

---

## 📊 修复前后对比

### 修复前

**日志输出**:
```
WARNING - 命令返回码非 0: 1, 错误：无
WARNING - ZAP 报告文件不存在：/tmp/xxx.json
```

**问题**:
- ❌ 错误信息不明确
- ❌ 没有重试机制
- ❌ 缺乏诊断工具
- ❌ 调试信息不足

### 修复后

**日志输出**:
```
ERROR - ZAP 报告文件不存在：/tmp/xxx.json
ERROR - 可能原因:
ERROR -   1. ZAP 扫描失败或被中断
ERROR -   2. 目标无法访问：http://demo.testfire.net
ERROR -   3. ZAP 配置问题
DEBUG - stdout: [详细输出 1000 字符]
```

**改进**:
- ✅ 详细的错误分析
- ✅ 自动重试机制（2 次）
- ✅ 完整的诊断工具
- ✅ 增强的调试日志（1000 字符）

---

## 📁 更新的文件

### 代码改进
- ✅ [`adapters/phase2_adapter_real.py`](../adapters/phase2_adapter_real.py)
  - 增强错误日志
  - 添加重试机制
  - 扩展调试信息

### 新增工具
- ✅ [`test/diagnose_zap_scan.py`](../test/diagnose_zap_scan.py) - 完整诊断工具

### 新建文档
- ✅ [`ZAP_SCAN_FIX_GUIDE.md`](../ZAP_SCAN_FIX_GUIDE.md) - 本文件

---

## ✅ 验证清单

在服务器上执行以下检查：

```bash
# 1. 检查 ZAP 状态
zap-cli -p 8080 status

# 2. 运行诊断工具
python3 test/diagnose_zap_scan.py

# 3. 测试实际扫描
python3 test/test_integration_fixed.py
```

---

## 🎉 总结

**修复完成！**

- ✅ 增强了错误日志输出
- ✅ 添加了重试机制
- ✅ 创建了完整的诊断工具
- ✅ 提供了详细的修复指南
- ✅ 扩展了调试信息

**现在请按以下步骤操作**:

1. **运行诊断工具**:
   ```bash
   python3 test/diagnose_zap_scan.py
   ```

2. **根据诊断结果修复问题**

3. **重新运行测试**:
   ```bash
   python3 test/test_integration_fixed.py
   ```

**如果仍有问题，请提供诊断工具的完整输出！** 🚀

---

**文档完成时间**: 2026-04-23
