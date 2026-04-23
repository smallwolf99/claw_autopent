# OpenClaw 集成指南

**版本**: v1.0  
**日期**: 2026-04-22  
**目的**: �?intelligent-test-orchestrator 集成�?OpenClaw，支持自然语言调用

---

## 📋 集成步骤

### 步骤 1: 确认 Skill 结构

```
intelligent-test-orchestrator/
├── manifest.json          �?OpenClaw 元数�?├── main.py                �?调用入口
├── SKILL.md               �?技能文�?├── core/                  �?核心编排
├── adapters/              �?工具适配
└── test/                  �?测试套件
```

### 步骤 2: 配置 OpenClaw 技能注�?
�?OpenClaw 的技能配置中添加�?
```json
{
  "skills": [
    {
      "name": "intelligent-test-orchestrator",
      "path": "./intelligent-test-orchestrator",
      "enabled": true,
      "priority": 1
    }
  ]
}
```

### 步骤 3: 验证 manifest.json

关键配置检查：

```json
{
  "name": "intelligent-test-orchestrator",
  "interface": {
    "function": {
      "name": "execute_intelligent_test",
      "parameters": {
        "required": ["target"]
      }
    }
  },
  "triggers": [
    "智能测试",
    "安全测试",
    "漏洞扫描",
    "渗透测�?
  ]
}
```

---

## 🎯 用户调用方式

### 方式 1: 自然语言调用（推荐）

用户输入自然语言，OpenClaw 自动解析�?
#### 示例 1: 完整测试

**用户输入**:
```
帮我测试一�?http://zero.webappsecurity.com，做完整的安全测�?```

**OpenClaw 解析**:
- 意图：安全测�?- 目标：http://zero.webappsecurity.com
- 模式：full（完整）

**自动调用**:
```python
execute_intelligent_test(
    target="http://zero.webappsecurity.com",
    test_mode="full"
)
```

#### 示例 2: 快速扫�?
**用户输入**:
```
快速扫�?example.com 的安全漏�?```

**OpenClaw 解析**:
- 意图：漏洞扫�?- 目标：example.com
- 模式：light（快速）

**自动调用**:
```python
execute_intelligent_test(
    target="example.com",
    test_mode="light"
)
```

#### 示例 3: 指定时间

**用户输入**:
```
�?192.168.1.100 进行渗透测试，时间限制 60 分钟
```

**OpenClaw 解析**:
- 意图：渗透测�?- 目标�?92.168.1.100
- 时间�?0 分钟

**自动调用**:
```python
execute_intelligent_test(
    target="192.168.1.100",
    time_limit=60
)
```

#### 示例 4: 指定报告格式

**用户输入**:
```
帮我做安全测试，生成 PDF 报告，目�?http://demo.testfire.net
```

**OpenClaw 解析**:
- 意图：安全测�?- 目标：http://demo.testfire.net
- 报告：PDF

**自动调用**:
```python
execute_intelligent_test(
    target="http://demo.testfire.net",
    report_format="pdf"
)
```

---

### 方式 2: 命令行调�?
直接通过命令行测试：

```bash
# 完整测试
python main.py '{"target": "http://zero.webappsecurity.com", "test_mode": "full"}'

# 快速扫�?python main.py '{"target": "example.com", "test_mode": "light"}'

# 自定义配�?python main.py '{"target": "192.168.1.100", "time_limit": 60, "report_format": "pdf"}'
```

---

### 方式 3: API 调用

通过 HTTP API 调用（如�?OpenClaw 提供）：

```bash
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "intelligent-test-orchestrator",
    "function": "execute_intelligent_test",
    "params": {
      "target": "http://zero.webappsecurity.com",
      "test_mode": "full"
    }
  }'
```

---

## 📊 触发词配�?
### 中文触发�?
```python
triggers = [
    "智能测试",
    "自动化渗�?,
    "安全测试",
    "漏洞扫描",
    "渗透测�?,
    "一键测�?,
    "全面测试",
    "帮我测试",
    "扫描漏洞",
    "评估风险",
    "检测漏�?,
    "安全检�?,
    "风险评估"
]
```

### 英文触发�?
```python
triggers = [
    "security test",
    "penetration test",
    "vulnerability scan",
    "automated test",
    "full test",
    "security assessment",
    "pentest",
    "vuln scan"
]
```

---

## 🔧 参数映射规则

### 目标提取

| 用户输入 | 提取的目�?|
|---------|-----------|
| "测试 http://example.com" | http://example.com |
| "扫描 example.com" | example.com |
| "�?192.168.1.1 进行测试" | 192.168.1.1 |
| "target is demo.testfire.net" | demo.testfire.net |

### 模式识别

| 用户输入关键�?| 测试模式 |
|---------------|---------|
| "完整"�?全面"�?full" | full |
| "快�?�?简�?�?light" | light |
| "自定�?�?custom" | custom |

### 报告格式识别

| 用户输入关键�?| 报告格式 |
|---------------|---------|
| "HTML"�?网页" | html |
| "Markdown"�?MD" | markdown |
| "PDF" | pdf |
| "JSON"�?原始数据" | json |

---

## 📝 执行流程

### 1. 用户输入

```
帮我测试 http://demo.testfire.net，做全面的安全检�?```

### 2. OpenClaw 解析

```python
{
    "intent": "security_test",
    "target": "http://demo.testfire.net",
    "test_mode": "full",  # �?全面"推断
    "report_format": "html"  # 默认
}
```

### 3. 调用 Skill

```python
handler = OpenClawHandler()
result = await handler.execute_intelligent_test(
    target="http://demo.testfire.net",
    test_mode="full",
    time_limit=120,
    report_format="html"
)
```

### 4. 执行阶段

```
阶段 0: 资产收集 (2-5 分钟)
  �?WhatWeb: Web 技术识�?  �?Nmap: 端口扫描
  �?Httpx: Web 探测
  �?Subfinder: 子域名枚�?
阶段 2: 漏洞检�?(5-15 分钟)
  �?Nuclei: 模板化扫�?  �?Afrog: PoC 验证
  �?Nikto: Web 漏洞
  �?ZAP-CLI: 全栈扫描
  �?SQLMap: SQL 注入

阶段 3: 漏洞验证 (2-5 分钟)
  �?交叉验证
  �?误报过滤
  �?利用链生�?
阶段 4: 报告生成 (1-2 分钟)
  �?风险评分
  �?漏洞统计
  �?修复建议
  �?报告输出
```

### 5. 返回结果

```json
{
    "success": true,
    "summary": "完成全面安全测试，发�?15 个漏洞，风险评分 16.63/100",
    "data": {
        "target": "http://demo.testfire.net",
        "assets_found": 6,
        "vulnerabilities_found": 15,
        "verified_vulns": 5,
        "risk_score": 16.63,
        "report_path": "./reports/demo.testfire.net_20260422.html",
        "report_url": "file:///reports/demo.testfire.net_20260422.html",
        "execution_time": 1245.67,
        "start_time": "2026-04-22 10:00:00",
        "end_time": "2026-04-22 10:20:45"
    }
}
```

---

## 🎨 进度反馈

### 简洁模式（每阶段一行）

```
[阶段 0/4] 资产收集�?.. 发现 6 个资�?�?[阶段 2/4] 漏洞检测中... 发现 15 个漏�?�?[阶段 3/4] 漏洞验证�?.. 确认 5 个真实漏�?�?[阶段 4/4] 报告生成�?.. 已保存到 reports/ �?```

### 详细模式（实时日志）

```
2026-04-22 10:00:00 - 开始智能安全测�?2026-04-22 10:00:01 - Phase 1: 启动资产收集
2026-04-22 10:00:05 - WhatWeb: 识别�?Flask + Nginx
2026-04-22 10:00:10 - Nmap: 发现 5 个开放端�?2026-04-22 10:05:00 - Phase 1 完成，发�?6 个资�?2026-04-22 10:05:01 - Phase 2: 启动漏洞检�?2026-04-22 10:05:05 - Nuclei: 开始扫�?...
```

---

## 📋 配置选项

### 测试模式

| 模式 | 说明 | 适用场景 | 预计时间 |
|------|------|---------|---------|
| **full** | 完整流程 | 新目标全面评�?| 20-30 分钟 |
| **light** | 快速扫�?| 日常巡检 | 5-10 分钟 |
| **custom** | 自定�?| 特定需�?| 可配�?|

### 报告格式

| 格式 | 说明 | 适用场景 |
|------|------|---------|
| **html** | 网页报告 | 可视化展�?|
| **markdown** | Markdown 文档 | 版本控制 |
| **pdf** | PDF 文档 | 正式报告 |
| **json** | 原始数据 | 程序处理 |

### 严重性过�?
```python
severity_filter = ["critical", "high"]  # 仅高�?severity_filter = ["critical", "high", "medium"]  # 中高
severity_filter = ["critical", "high", "medium", "low", "info"]  # 全部
```

---

## 🔍 故障排查

### 问题 1: Skill 未识�?
**现象**: OpenClaw 无法识别 intelligent-test-orchestrator

**解决**:
```bash
# 检�?manifest.json 是否存在
ls manifest.json

# 验证 JSON 格式
python -m json.tool manifest.json

# 重启 OpenClaw
openclaw restart
```

### 问题 2: 触发词不生效

**现象**: 输入触发词后无响�?
**解决**:
```bash
# 检查触发词配置
cat manifest.json | grep triggers

# 添加更多触发�?"triggers": ["测试", "扫描", "检�?, ...]
```

### 问题 3: 参数解析错误

**现象**: 目标提取失败

**解决**:
```python
# 检查参数映射规�?# 确保 URL 格式正确
target = "http://example.com"  # 推荐
target = "example.com"  # 也可接受
```

---

## 📊 性能优化

### 并发控制

```python
# manifest.json 配置
"custom_options": {
    "concurrent_tools": 3  # 同时运行 3 个工�?}
```

### 时间限制

```python
# 防止超时
"time_limit": 120  # 120 分钟
```

### 缓存优化

```python
# 启用缓存
"enable_caching": true  # 重复测试加�?```

---

## 📁 相关文件

- **manifest.json**: [`manifest.json`](manifest.json) - OpenClaw 元数�?- **main.py**: [`main.py`](main.py) - 调用入口
- **SKILL.md**: [`SKILL.md`](SKILL.md) - 技能文�?- **INTEGRATION_TEST_GUIDE.md**: [`INTEGRATION_TEST_GUIDE.md`](INTEGRATION_TEST_GUIDE.md) - 集成测试指南

---

## 🎯 快速开�?
### 1. 本地测试

```bash
# 测试 Skill
python main.py '{"target": "http://demo.testfire.net", "test_mode": "full"}'
```

### 2. 部署�?OpenClaw

```bash
# 复制 Skill �?OpenClaw 目录
cp -r intelligent-test-orchestrator ~/.openclaw/skills/

# 重启 OpenClaw
openclaw restart
```

### 3. 验证集成

```bash
# 检查技能列�?openclaw skills list

# 应该看到 intelligent-test-orchestrator
```

### 4. 开始使�?
**用户输入**:
```
帮我测试 http://demo.testfire.net
```

**预期输出**:
```
�?已启动智能安全测�?[阶段 0/4] 资产收集�?..
[阶段 2/4] 漏洞检测中...
[阶段 3/4] 漏洞验证�?..
[阶段 4/4] 报告生成�?..
�?测试完成！发�?15 个漏�?📄 报告：file:///reports/demo.testfire.net.html
```

---

## 📞 需要帮助？

如果遇到任何问题�?
1. 检�?manifest.json 配置
2. 验证 main.py 调用
3. 查看 OpenClaw 日志
4. 运行集成测试

**立即开始集�?*:

```bash
# 部署 Skill
cp -r intelligent-test-orchestrator ~/.openclaw/skills/

# 重启 OpenClaw
openclaw restart

# 验证
openclaw skills list
```

🚀
