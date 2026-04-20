# Intelligent Test Orchestrator

智能安全测试编排器 - OpenClaw 主 Skill

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

## 📊 执行效果

```
🚀 开始智能安全测试
🎯 目标：http://zero.webappsecurity.com
📊 模式：full
⏱️  时间限制：120 分钟

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

## 📁 目录结构

```
intelligent-test-orchestrator/
├── manifest.json          # OpenClaw 元数据
├── SKILL.md              # 技能文档
├── README.md             # 本文件
├── main.py               # OpenClaw 调用入口 ⭐
├── requirements.txt      # Python 依赖
├── test_input.json       # 测试输入示例
├── test_basic.py         # 测试脚本
├── core/                 # 编排核心（TODO: 迁移）
├── adapters/             # 工具适配器（TODO: 实现）
├── data/                 # 数据文件（TODO: 创建）
├── docs/                 # 文档
│   └── openclaw-integration.md
└── reports/              # 生成的报告
    └── report_*.html
```

## 🎯 核心功能

- ✅ **全自动执行**: 一键启动，自动完成 5 个测试阶段
- ✅ **智能编排**: 基于风险画像动态规划测试路径
- ✅ **简洁反馈**: 每个阶段一行进度，避免信息过载
- ✅ **多格式报告**: 支持 HTML/Markdown/PDF/JSON 报告
- ✅ **灵活配置**: 支持完整/快速/自定义三种测试模式

## 📋 测试模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **full** | 完整流程 - 执行所有阶段，检测所有级别漏洞 | 全面安全评估 |
| **light** | 快速扫描 - 仅检测高危和严重漏洞 | 快速风险评估 |
| **custom** | 自定义 - 通过 custom_options 精细控制 | 特定需求测试 |

## 🔌 接口参数

### execute_intelligent_test

```json
{
  "target": "http://example.com",        // 必需：测试目标
  "test_mode": "full",                   // 可选：测试模式 (full/light/custom)
  "time_limit": 120,                     // 可选：时间限制（分钟）
  "report_format": "html",               // 可选：报告格式 (html/markdown/pdf/json)
  "severity_filter": ["critical", "high", "medium", "low", "info"],  // 可选：漏洞过滤
  "custom_options": {}                   // 可选：自定义选项
}
```

### custom_options 选项

| 选项 | 类型 | 说明 |
|------|------|------|
| `skip_asset_collection` | boolean | 跳过资产收集（如果已有资产信息） |
| `skip_verification` | boolean | 跳过漏洞验证 |
| `concurrent_tools` | integer | 并发执行的工具数量（默认：3） |

## 📊 返回结果

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
  },
  "actions": [
    {
      "label": "查看完整报告",
      "type": "open_file",
      "path": "/path/to/report.html"
    }
  ]
}
```

## 🔄 执行流程

### 5 个测试阶段

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

## 🛠️ 安装

### 依赖安装

```bash
pip install -r requirements.txt
```

### OpenClaw 集成

1. 将本目录复制到 OpenClaw 的 skills 目录：
```bash
cp -r intelligent-test-orchestrator /path/to/openclaw/skills/
```

2. 重启 OpenClaw

3. 验证技能已注册：
```bash
openclaw skills list
```

## 🧪 测试

### 运行测试脚本

```bash
python test_basic.py
```

### 手动测试

```bash
# 测试完整流程
Get-Content test_input.json | python main.py

# 测试快速模式
python main.py '{"target": "http://example.com", "test_mode": "light"}'

# 测试自定义模式
python main.py '{"target": "http://example.com", "test_mode": "custom", "custom_options": {"skip_verification": true}}'
```

## 📚 文档

- [SKILL.md](SKILL.md) - 详细技能文档
- [docs/openclaw-integration.md](docs/openclaw-integration.md) - OpenClaw 集成指南
- [IMPLEMENTATION_PLAN.md](../phase-1-strategy-planning/IMPLEMENTATION_PLAN.md) - 实施方案

## 🎯 当前状态

### ✅ 已完成

- [x] 创建主 Skill 目录结构
- [x] 编写 manifest.json（OpenClaw 元数据）
- [x] 实现 main.py（OpenClaw 调用入口）
- [x] 实现简洁进度反馈机制
- [x] 配置触发词和参数映射
- [x] 测试 OpenClaw 调用流程（使用模拟数据）
- [x] 编写 OpenClaw 集成文档

### ⏳ 待完成

- [ ] 从 phase-1 迁移核心代码
- [ ] 实现 Phase-0 资产收集适配器
- [ ] 实现 Phase-2 漏洞检测适配器
- [ ] 实现漏洞验证模块
- [ ] 实现报告生成模块
- [ ] 端到端测试（使用真实工具）

## 🐛 故障排除

### 常见问题

**Q: 调用时返回编码错误**

A: 在 Windows 上运行时，添加 UTF-8 编码设置：
```python
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

**Q: OpenClaw 无法识别技能**

A: 检查：
1. manifest.json 是否在正确位置
2. 技能目录是否在 OpenClaw 扫描路径中
3. 重启 OpenClaw

**Q: 进度反馈显示乱码**

A: 使用支持 UTF-8 的终端（如 VSCode 终端）

## 📄 许可证

MIT License

## 👥 支持

- Email: support@example.com
- Issues: https://github.com/advanced-pentester/issues

---

**版本**: 1.0.0  
**创建时间**: 2026-04-20  
**最后更新**: 2026-04-20
