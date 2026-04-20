# Intelligent Test Orchestrator

智能安全测试编排器 - OpenClaw 主 Skill

## 📋 简介

`intelligent-test-orchestrator` 是一个智能体驱动的安全测试编排器，作为 OpenClaw 的统一入口，自动协调 Phase 0-4 的工具链，实现从资产收集到报告生成的**全自动安全测试流程**。

## 🎯 核心特性

- ✅ **全自动执行**: 一键启动，自动完成 5 个测试阶段
- ✅ **智能编排**: 基于风险画像动态规划测试路径
- ✅ **简洁反馈**: 每个阶段一行进度，避免信息过载
- ✅ **多格式报告**: 支持 HTML/Markdown/PDF/JSON 报告
- ✅ **灵活配置**: 支持完整/快速/自定义三种测试模式

## 🚀 快速开始

### 通过 OpenClaw 调用

```bash
# 命令行调用
python main.py '{"target": "http://example.com", "test_mode": "full"}'

# 或通过 stdin
echo '{"target": "http://example.com"}' | python main.py
```

### 通过 OpenClaw 智能体

用户输入自然语言：
```
"帮我测试一下 http://zero.webappsecurity.com，做完整的安全测试"
```

OpenClaw 会自动：
1. 识别意图：安全测试
2. 提取参数：target="http://zero.webappsecurity.com", test_mode="full"
3. 调用此 Skill 的 `execute_intelligent_test` 接口

## 📊 接口定义

### execute_intelligent_test

执行智能安全测试全流程

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `target` | string | ✅ 是 | - | 测试目标 (URL/IP/域名) |
| `test_mode` | string | ❌ 否 | "full" | 测试模式：full/light/custom |
| `time_limit` | integer | ❌ 否 | 120 | 时间限制（分钟） |
| `report_format` | string | ❌ 否 | "html" | 报告格式：html/markdown/pdf/json |
| `severity_filter` | array | ❌ 否 | 全部 | 漏洞严重程度过滤 |
| `custom_options` | object | ❌ 否 | {} | 自定义选项 |

#### 测试模式

- **full**: 完整流程 - 执行所有阶段，检测所有级别漏洞
- **light**: 快速扫描 - 仅检测高危和严重漏洞，跳过部分阶段
- **custom**: 自定义 - 通过 `custom_options` 精细控制

#### 返回结果

```json
{
  "success": true,
  "summary": "✅ 测试完成，发现 12 个漏洞（已验证 8 个），风险评分 7.5/100",
  "data": {
    "target": "http://example.com",
    "assets_found": 5,
    "vulnerabilities_found": 12,
    "verified_vulns": 8,
    "risk_score": 7.5,
    "report_path": "/path/to/report.html",
    "report_url": "file:///path/to/report.html",
    "execution_time": 1234.56,
    "start_time": "2026-04-20T10:00:00Z",
    "end_time": "2026-04-20T10:20:34Z"
  }
}
```

## 📁 目录结构

```
intelligent-test-orchestrator/
├── manifest.json          # OpenClaw 元数据
├── SKILL.md              # 技能文档（本文件）
├── main.py               # OpenClaw 调用入口 ⭐
├── core/                 # 编排核心
│   ├── orchestrator.py   # 统一编排器
│   ├── risk_profiler.py  # 风险画像
│   ├── dynamic_planner.py# 动态规划
│   ├── tool_selector.py  # 工具选择
│   └── optimizer.py      # 性能优化
├── adapters/             # 工具适配器
│   ├── phase0_adapter.py # Phase-0 适配
│   ├── phase2_adapter.py # Phase-2 适配
│   └── result_parser.py  # 结果解析
└── data/                 # 数据文件
    ├── tool_rules.yml    # 工具选择规则
    └── cve_mapping.json  # CVE 映射
```

## 🔄 执行流程

### 5 个测试阶段

```
🎯 阶段 1/5: 资产收集中...
   ↓
🧠 阶段 2/5: 风险画像生成中...
   ↓
🔍 阶段 3/5: 漏洞检测中...
   ↓
🔬 阶段 4/5: 漏洞验证中...
   ↓
📄 阶段 5/5: 报告生成中...
```

### 详细流程

1. **Phase-0: 资产收集**
   - WhatWeb: 技术栈识别
   - Nmap: 端口和服务扫描
   - Httpx: Web 探测
   - Subfinder: 子域名发现
   - Katana: 爬虫抓取

2. **Phase-1: 智能编排**
   - 风险画像：计算技术栈风险、暴露风险、业务风险
   - 路径规划：基于规则生成最优测试路径
   - 工具选择：根据资产特征选择最合适的工具
   - 任务调度：并发执行、资源优化

3. **Phase-2: 漏洞检测**
   - Nuclei: 模板化漏洞扫描
   - Afrog: PoC 验证扫描
   - Nikto: Web 漏洞扫描

4. **Phase-3: 漏洞验证**
   - 交叉验证：多工具结果对比
   - 误报过滤：基于规则过滤误报
   - 利用链生成：生成漏洞利用路径

5. **Phase-4: 报告生成**
   - HTML 报告：美观的网页报告
   - Markdown 报告：技术文档
   - PDF 报告：可打印格式
   - JSON 报告：原始数据

## 💡 使用示例

### 示例 1: 完整安全测试

```json
{
  "target": "http://zero.webappsecurity.com",
  "test_mode": "full"
}
```

**输出**:
```
🎯 阶段 1/5: 资产收集中...
✅ 发现 5 个资产

🧠 阶段 2/5: 风险画像生成中...
⚠️  风险评分：7.5/100

🔍 阶段 3/5: 漏洞检测中...
🐛 发现 12 个漏洞

🔬 阶段 4/5: 漏洞验证中...
✔️  已验证 8 个漏洞

📄 阶段 5/5: 报告生成中...
📊 报告已生成：/path/to/report.html
```

### 示例 2: 快速扫描高危漏洞

```json
{
  "target": "example.com",
  "test_mode": "light",
  "severity_filter": ["critical", "high"]
}
```

### 示例 3: 自定义测试并生成 PDF 报告

```json
{
  "target": "192.168.1.100",
  "test_mode": "custom",
  "report_format": "pdf",
  "time_limit": 60,
  "custom_options": {
    "skip_verification": true,
    "concurrent_tools": 3
  }
}
```

## ⚙️ 配置选项

### custom_options 详解

| 选项 | 类型 | 说明 |
|------|------|------|
| `skip_asset_collection` | boolean | 跳过资产收集（如果已有资产信息） |
| `skip_verification` | boolean | 跳过漏洞验证 |
| `concurrent_tools` | integer | 并发执行的工具数量（默认：3） |

## 🔌 依赖项

本 Skill 依赖以下 Phase 工具：

### Phase-0: 资产收集
- whatweb
- nmap
- httpx
- subfinder
- katana

### Phase-2: 漏洞检测
- nuclei
- afrog
- nikto
- zap-cli
- custom-scanner

## 📝 触发词

以下关键词会触发此 Skill：

**中文**:
- 智能测试
- 自动化渗透
- 安全测试
- 漏洞扫描
- 渗透测试
- 一键测试
- 全面测试
- 帮我测试
- 扫描漏洞
- 评估风险

**英文**:
- security test
- penetration test
- vulnerability scan
- automated test

## 🛡️ 权限说明

本 Skill 需要以下权限：

- `network_access`: 访问目标网络
- `file_write`: 写入测试报告和日志
- `process_execution`: 执行外部工具（Nmap、Nuclei 等）

## 📊 性能指标

- **执行时间**: 单个目标完整流程通常 10-30 分钟
- **内存占用**: <500MB
- **并发能力**: 支持同时执行 5+ 工具
- **报告生成**: <5 秒

## 🐛 故障排除

### 常见问题

**Q: 测试超时怎么办？**
A: 增加 `time_limit` 参数，或使用 `light` 模式快速扫描。

**Q: 如何跳过某个阶段？**
A: 使用 `custom_options` 配置，例如 `"skip_verification": true`。

**Q: 报告在哪里？**
A: 返回结果中包含 `report_path` 和 `report_url`，可通过文件浏览器或浏览器访问。

## 📚 相关文档

- [实施方案](../phase-1-strategy-planning/IMPLEMENTATION_PLAN.md)
- [PRD](../phase-1-strategy-planning/PRD.md)
- [OpenClaw 集成文档](./docs/openclaw-integration.md)

## 📄 许可证

MIT License

## 👥 支持

- Email: support@example.com
- Issues: https://github.com/advanced-pentester/issues

---

**版本**: 1.0.0  
**创建时间**: 2026-04-20  
**最后更新**: 2026-04-20
