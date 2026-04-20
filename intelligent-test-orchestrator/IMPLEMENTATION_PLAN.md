# 🎯 轻量级智能测试编排 Skill 实施方案

**版本**: v1.0  
**创建时间**: 2026-04-20  
**最后更新**: 2026-04-20  
**状态**: ✅ 已批准，准备实施  

---

## 📋 目录

- [项目概述](#项目概述)
- [核心功能定位](#核心功能定位)
- [技术架构设计](#技术架构设计)
- [OpenClaw 集成](#openclaw-集成)
- [实施路线图](#实施路线图)
- [任务清单](#任务清单)
- [交付物清单](#交付物清单)
- [技术决策](#技术决策)
- [风险管理](#风险管理)
- [成功指标](#成功指标)

---

## 项目概述

### 项目目标
构建一个**轻量级智能测试编排 Skill**，整合 Phase 0-4 的工具链，实现从资产收集到报告生成的**全自动安全测试流程**。

### 核心设计理念
- ✅ **轻量级**: 核心代码 ~500 行，5-6 个核心文件
- ✅ **智能化**: 基于规则的多步推理，自动规划攻击路径
- ✅ **全自动**: 一键执行，无需手工干预
- ✅ **可扩展**: 插件式架构，易于添加新工具和新规则

### 开发策略
- ✅ **分阶段实施**: MVP → 功能增强 → 优化完善 → OpenClaw 集成
- ✅ **复用优先**: 优化调整现有 PRD 代码，非推倒重来
- ✅ **独立模块**: Phase-3 独立为漏洞利用验证模块
- ✅ **多格式报告**: 支持 HTML/Markdown/PDF
- ✅ **OpenClaw 集成**: 创建独立主 Skill，支持智能体调用

---

## 核心功能定位

### 五大核心功能

| 功能 | 对应 Phase | 状态 | 说明 |
|------|-----------|------|------|
| **资产收集** | Phase-0 | ✅ 已有 | 调用现有 WhatWeb/Nmap/Httpx 等工具 |
| **智能编排** | Phase-1 | ⚠️ 优化 | 核心大脑，风险画像 + 路径规划 + 工具选择 |
| **漏洞检测** | Phase-2 | ✅ 已有 | 调用现有 Nuclei/Afrog/Nikto 等工具 |
| **漏洞利用** | Phase-3 | ❌ 新增 | 独立模块，漏洞验证 + 利用链生成 |
| **报告生成** | Phase-4 | ❌ 新增 | HTML/Markdown/PDF多格式支持 |

### 完整工作流

```
┌─────────────┐
│  目标输入   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Phase-0: 资产收集   │ ← 已有
│ - WhatWeb 技术识别  │
│ - Nmap 端口扫描     │
│ - Httpx Web 探测    │
│ - Subfinder 子域名  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Phase-1: 智能编排   │ ← 核心大脑（优化）
│ - 风险画像          │
│ - 路径规划          │
│ - 工具选择          │
│ - 任务调度          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Phase-2: 漏洞检测   │ ← 已有
│ - Nuclei 模板扫描   │
│ - Afrog PoC 验证    │
│ - Nikto Web 扫描    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Phase-3: 漏洞利用   │ ← 新增
│ - 漏洞验证          │
│ - 利用链生成        │
│ - 手工验证辅助      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Phase-4: 报告生成   │ ← 新增
│ - HTML 报告         │
│ - Markdown 报告     │
│ - PDF 报告          │
│ - JSON 原始数据     │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  完整报告   │
└─────────────┘
```

---

## 技术架构设计

### 整体架构

```
┌─────────────────────────────────────────────────┐
│          统一入口：SecurityTestOrchestrator     │
│  - execute_full_test()  # 完整流程             │
│  - execute_phase(phase) # 单阶段执行            │
└───────────────────┬─────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐      ┌───▼───┐      ┌───▼───┐
│Phase-0│      │Phase-1│      │Phase-2│
│资产收集│ ←──→ │智能编排│ ──→ │漏洞检测│
└───────┘      └───────┘      └───────┘
   ↑              │               │
   │              │               ▼
   │              │         ┌───▼───┐
   │              │         │Phase-3│
   │              │         │漏洞利用│
   │              │         └───────┘
   │              │               │
   │              ▼               ▼
   │         ┌───────────────────────┐
   │         │      Phase-4          │
   └──────── │     报告生成          │
             └───────────────────────┘
```

### Phase-1 核心架构（优化后）

```
Phase-1: 智能编排（优化调整现有代码）
├── core/
│   ├── orchestrator.py          # ⭐ 统一入口，协调所有阶段
│   ├── risk_profiler.py         # ✅ 风险画像（简化版）
│   ├── dynamic_planner.py       # ✅ 动态规划（简化为启发式）
│   ├── tool_selector.py         # ⭐ 工具选择器（基于规则）
│   ├── optimizer.py             # ⭐ 性能优化（异步 + 缓存）
│   └── learning_optimizer.py    # ⭐ 学习优化（简化版，v2.0）
│
├── adapters/
│   ├── phase0_adapter.py        # ⭐ Phase-0 工具调用适配
│   ├── phase2_adapter.py        # ⭐ Phase-2 工具调用适配
│   └── result_parser.py         # ⭐ 结果解析标准化
│
└── data/
    ├── tool_rules.yml           # ⭐ 工具选择规则库
    ├── cve_mapping.json         # ✅ CVE→工具映射
    └── attack_patterns.json     # ⭐ 攻击模式库
```

**图例**: ✅ 已有（优化） | ⭐ 新增

### 核心算法设计

#### 1. 风险评分算法（保留现有精华）

```python
# 多维度加权风险评估
总风险分 = 技术栈风险×0.4 + 暴露面风险×0.3 + 业务风险×0.2 + 配置风险×0.1

# 风险等级划分
0-20:   🟢 安全
20-40:  🟡 低风险
40-60:  🟠 中风险
60-80:  🟣 高风险
80-100: 🔴 危急
```

#### 2. 漏洞路径规划（新增核心）

```python
# 基于规则的启发式路径规划
def plan_attack_path(assets):
    # 1. 匹配攻击模式
    patterns = match_attack_patterns(assets)
    
    # 2. 生成测试路径
    path = []
    for pattern in patterns:
        # 基于规则选择工具
        tools = select_tools(pattern)
        # 基于优先级排序
        tools = sort_by_priority(tools)
        # 基于依赖关系排序
        tools = sort_by_dependency(tools)
        path.extend(tools)
    
    return path
```

#### 3. 工具选择规则（增强现有）

```yaml
# 规则示例
- IF: 识别到"Tomcat" + CVE-2020-5407
  THEN: 
    工具：nuclei(CVE 模板) → afrog(验证) → 手工验证
    优先级：CRITICAL
    预计时间：15 分钟
    
- IF: 识别到"jQuery<1.9" 
  THEN: 
    工具：afrog(jQuery 规则) → 检查 XSS
    优先级：MEDIUM
    预计时间：10 分钟
```

---

## OpenClaw 集成

### 集成策略

创建**独立主 Skill**：`intelligent-test-orchestrator`，作为 OpenClaw 智能体的统一调用入口。

---

### 架构设计

```
┌─────────────────────────────────────────┐
│   OpenClaw 智能体                        │
│   - 理解用户意图                        │
│   - 提取测试参数                        │
│   - 匹配触发词                          │
└──────────────┬──────────────────────────┘
               │
               │ 调用
               ▼
┌─────────────────────────────────────────┐
│ intelligent-test-orchestrator (主 Skill)│
│ - manifest.json (OpenClaw 元数据)       │
│ - main.py (调用入口) ⭐                  │
│ - core/ (编排核心)                      │
│ - adapters/ (工具适配)                  │
└──────────────┬──────────────────────────┘
               │
               │ 协调调用
               ▼
┌─────────────────────────────────────────┐
│ Phase 0-4 工具链                         │
│ - Phase-0: 资产收集                     │
│ - Phase-1: 智能编排                     │
│ - Phase-2: 漏洞检测                     │
│ - Phase-3: 漏洞利用                     │
│ - Phase-4: 报告生成                     │
└─────────────────────────────────────────┘
```

---

### 主 Skill 结构

```
intelligent-test-orchestrator/          # ⭐ 新增：独立主 Skill
├── manifest.json                       # OpenClaw 技能元数据
├── SKILL.md                            # 技能文档
├── main.py                             # OpenClaw 调用入口 ⭐
├── core/                               # 编排核心（从 phase-1 迁移）
│   ├── orchestrator.py                # 统一编排器
│   ├── risk_profiler.py               # 风险画像
│   ├── dynamic_planner.py             # 动态规划
│   ├── tool_selector.py               # 工具选择
│   └── optimizer.py                   # 性能优化
├── adapters/                           # 工具适配器
│   ├── phase0_adapter.py              # Phase-0 适配
│   ├── phase2_adapter.py              # Phase-2 适配
│   └── result_parser.py               # 结果解析
└── data/
    ├── tool_rules.yml                 # 工具选择规则
    └── cve_mapping.json               # CVE 映射
```

---

### OpenClaw 接口设计

#### 1. manifest.json

```json
{
  "name": "intelligent-test-orchestrator",
  "version": "1.0.0",
  "description": "智能安全测试编排器 - 全自动资产收集、漏洞检测、利用验证、报告生成",
  "author": "安小易 008",
  "category": "penetration-testing",
  "subcategory": "orchestration",
  
  "interface": {
    "type": "function",
    "function": {
      "name": "execute_intelligent_test",
      "description": "执行智能安全测试全流程",
      "parameters": {
        "type": "object",
        "properties": {
          "target": {
            "type": "string",
            "description": "测试目标 (URL/IP/域名)"
          },
          "test_mode": {
            "type": "string",
            "enum": ["full", "light", "custom"],
            "description": "测试模式：full=完整流程，light=快速扫描，custom=自定义"
          },
          "time_limit": {
            "type": "integer",
            "description": "时间限制（分钟）"
          },
          "report_format": {
            "type": "string",
            "enum": ["html", "markdown", "pdf", "json"],
            "description": "报告格式"
          }
        },
        "required": ["target"]
      }
    }
  },
  
  "triggers": [
    "智能测试",
    "自动化渗透",
    "安全测试",
    "漏洞扫描",
    "渗透测试",
    "一键测试"
  ],
  
  "dependencies": [
    "phase-0-asset-collection/whatweb-skill",
    "phase-0-asset-collection/nmap-scanner",
    "phase-2-vulnerability-scan/nuclei-scanner",
    "phase-2-vulnerability-scan/afrog"
  ]
}
```

#### 2. main.py（OpenClaw 入口）

```python
#!/usr/bin/env python3
"""
智能测试编排器 - OpenClaw 主入口
"""

import asyncio
import json
import sys
from core.orchestrator import SecurityTestOrchestrator

class OpenClawHandler:
    """OpenClaw 接口处理器"""
    
    def __init__(self):
        self.orchestrator = SecurityTestOrchestrator()
    
    async def execute_intelligent_test(
        self,
        target: str,
        test_mode: str = "full",
        time_limit: int = 120,
        report_format: str = "html"
    ) -> dict:
        """
        OpenClaw 调用接口 - 执行智能安全测试
        
        简洁进度反馈:
        - 每个阶段一行输出
        - 使用 emoji 标识状态
        - 关键数据突出显示
        """
        try:
            # 阶段 1: 资产收集
            print("🎯 阶段 1/5: 资产收集中...")
            assets = await self.orchestrator.collect_assets(target)
            print(f"✅ 发现 {len(assets)} 个资产")
            
            # 阶段 2: 风险画像
            print("🧠 阶段 2/5: 风险画像生成中...")
            risk_report = self.orchestrator.assess_risk(assets)
            print(f"⚠️  风险评分：{risk_report.overall_score}/100")
            
            # 阶段 3: 漏洞检测
            print("🔍 阶段 3/5: 漏洞检测中...")
            vulns = await self.orchestrator.detect_vulnerabilities(assets)
            print(f"🐛 发现 {len(vulns)} 个漏洞")
            
            # 阶段 4: 漏洞验证
            print("🔬 阶段 4/5: 漏洞验证中...")
            verified = await self.orchestrator.verify_vulnerabilities(vulns)
            print(f"✔️  已验证 {len(verified)} 个漏洞")
            
            # 阶段 5: 报告生成
            print("📄 阶段 5/5: 报告生成中...")
            report_path = await self.orchestrator.generate_report(
                assets=assets,
                vulns=vulns,
                verified=verified,
                format=report_format
            )
            print(f"📊 报告已生成：{report_path}")
            
            # 返回结果
            return {
                "success": True,
                "summary": f"✅ 测试完成，发现 {len(vulns)} 个漏洞（已验证 {len(verified)} 个），风险评分 {risk_report.overall_score}/100",
                "data": {
                    "target": target,
                    "assets_found": len(assets),
                    "vulnerabilities_found": len(vulns),
                    "verified_vulns": len(verified),
                    "risk_score": risk_report.overall_score,
                    "report_path": str(report_path),
                    "report_url": f"file://{report_path}"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"测试失败：{str(e)}"
            }

# OpenClaw 调用入口
async def main():
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read())
    
    handler = OpenClawHandler()
    result = await handler.execute_intelligent_test(
        target=input_data.get("target"),
        test_mode=input_data.get("test_mode", "full"),
        time_limit=input_data.get("time_limit", 120),
        report_format=input_data.get("report_format", "html")
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 调用流程示例

#### 用户输入
```
"帮我测试一下 http://zero.webappsecurity.com，做完整的安全测试"
```

#### OpenClaw 处理
1. **意图识别**: 安全测试/渗透测试
2. **参数提取**: 
   - target: "http://zero.webappsecurity.com"
   - test_mode: "full" (从"完整"推断)
3. **技能匹配**: 触发词"安全测试" → intelligent-test-orchestrator
4. **调用执行**: `execute_intelligent_test(target, test_mode="full")`

#### 执行过程（简洁反馈）
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

#### 返回结果
```json
{
  "success": true,
  "summary": "✅ 测试完成，发现 12 个漏洞（已验证 8 个），风险评分 7.5/100",
  "data": {
    "target": "http://zero.webappsecurity.com",
    "assets_found": 5,
    "vulnerabilities_found": 12,
    "verified_vulns": 8,
    "risk_score": 7.5,
    "report_path": "/path/to/report.html",
    "report_url": "file:///path/to/report.html"
  }
}
```

---

### OpenClaw 配置要点

#### 1. 触发词设计（已批准）
```json
{
  "triggers": [
    "智能测试",
    "自动化渗透",
    "安全测试",
    "漏洞扫描",
    "渗透测试",
    "一键测试"
  ]
}
```

#### 2. 进度反馈（简洁方式）
- ✅ 每个阶段一行输出
- ✅ 使用 emoji 标识状态
- ✅ 只显示关键数据
- ✅ 避免过多技术细节

#### 3. 结果展示
- ✅ 结构化 JSON 数据
- ✅ 包含摘要信息
- ✅ 提供报告访问链接
- ✅ 支持后续操作（查看/导出）

---

### 部署步骤

1. **创建主 Skill 目录**
   ```bash
   mkdir intelligent-test-orchestrator
   ```

2. **复制核心代码**
   ```bash
   # 从 phase-1 迁移核心代码
   cp -r phase-1-strategy-planning/core intelligent-test-orchestrator/
   cp -r phase-1-strategy-planning/adapters intelligent-test-orchestrator/
   ```

3. **创建 OpenClaw 接口文件**
   - manifest.json
   - main.py
   - SKILL.md

4. **注册到 OpenClaw**
   ```bash
   # OpenClaw 会自动扫描技能目录
   # 或在配置中手动添加
   ```

5. **测试调用**
   ```bash
   # 命令行测试
   python main.py '{"target": "http://example.com", "test_mode": "full"}'
   ```

---

### 与现有代码的关系

```
intelligent-test-orchestrator/    # ⭐ 新增：OpenClaw 主入口
  ├── core/                       # 从 phase-1 迁移
  └── adapters/                   # 新增：工具适配

phase-1-strategy-planning/        # 保留：核心库
  ├── core/                       # 与 orchestrator 共享
  └── scripts/                    # 原有代码（向后兼容）

关系：
- intelligent-test-orchestrator 是 OpenClaw 的统一入口
- phase-1 提供核心算法和编排逻辑
- 两者共享 core/ 目录的代码
- 通过 adapters/ 调用 Phase 0-4 工具
```

---

## 实施路线图

### Phase 1：MVP（最小可行产品）- 3 天

**目标**: 打通完整流程，验证核心架构

**时间**: 第 1-3 天

**任务**:
- [x] Task 1: Phase-1 代码分析和优化方案设计
- [ ] Task 2: Phase-1 核心代码简化（10+ 文件 → 5-6 个核心文件）
- [ ] Task 3: 实现统一入口 SecurityTestOrchestrator
- [ ] Task 4: 实现 Phase-0 资产收集适配器
- [ ] Task 5: 实现 Phase-2 漏洞检测适配器
- [ ] Task 6: 实现结果解析标准化模块
- [ ] Task 7: MVP 端到端测试和验证

**交付物**:
- ✅ 优化后的 Phase-1 核心代码（5-6 个文件）
- ✅ 统一入口 `SecurityTestOrchestrator`
- ✅ Phase-0/2 适配器
- ✅ 基础 JSON 报告输出
- ✅ MVP 演示脚本

**验收标准**:
- ✅ 能够自动完成资产收集 → 漏洞检测全流程
- ✅ 生成包含资产、风险评分、漏洞列表的 JSON 报告
- ✅ 核心流程无阻塞，错误处理完善

---

### Phase 2：功能增强 - 3 天

**目标**: 实现 Phase-3 利用验证模块和 Phase-4 报告生成

**时间**: 第 4-6 天

**任务**:
- [ ] Task 8: Phase-3 漏洞利用模块 - 漏洞验证器
- [ ] Task 9: Phase-3 漏洞利用模块 - 利用链生成
- [ ] Task 10: Phase-3 漏洞利用模块 - 验证规则库
- [ ] Task 11: Phase-4 报告生成 - HTML 报告模板和渲染
- [ ] Task 12: Phase-4 报告生成 - Markdown 报告模板
- [ ] Task 13: Phase-4 报告生成 - PDF 转换功能
- [ ] Task 14: Phase-4 报告生成 - 报告样式美化

**交付物**:
- ✅ Phase-3 完整漏洞利用模块
- ✅ Phase-4 报告生成模块（HTML/Markdown/PDF）
- ✅ 漏洞验证和利用链生成机制
- ✅ 专业美观的报告模板

**验收标准**:
- ✅ 高危漏洞验证率 100%
- ✅ 利用链可执行
- ✅ 报告格式完整，内容专业
- ✅ PDF 生成正常，样式美观

---

### Phase 3：优化完善 - 2-3 天

**目标**: 性能优化、学习机制、完整测试

**时间**: 第 7-9 天

**任务**:
- [ ] Task 15: 性能优化 - 异步并发执行
- [ ] Task 16: 性能优化 - 缓存机制实现
- [ ] Task 17: 简化版学习优化机制
- [ ] Task 18: 工具选择规则库优化
- [ ] Task 19: 端到端测试用例编写
- [ ] Task 20: 性能基准测试
- [ ] Task 21: 用户文档和使用指南
- [ ] Task 22: API 参考文档
- [ ] Task 23: 示例代码和演示脚本

**交付物**:
- ✅ 性能优化（异步并发 + 缓存）
- ✅ 简化版学习优化机制
- ✅ 完整的测试用例和基准测试
- ✅ 用户文档和 API 参考
- ✅ 示例代码和演示脚本

**验收标准**:
- ✅ 单个目标全流程 <30 分钟
- ✅ 内存占用 <500MB
- ✅ 并发执行 5+ 工具无阻塞
- ✅ 文档完整，示例清晰

---

### Phase 4：OpenClaw 集成 - 1 天

**目标**: 实现 OpenClaw 智能体调用接口

**时间**: 第 10 天

**任务**:
- [x] Task 24: 创建 intelligent-test-orchestrator 主 Skill 目录 ✅
- [x] Task 25: 编写 manifest.json（OpenClaw 元数据） ✅
- [x] Task 26: 实现 main.py（OpenClaw 调用入口） ✅
- [ ] Task 27: 从 phase-1 迁移核心代码到主 Skill ⏳
- [x] Task 28: 实现简洁进度反馈机制 ✅
- [x] Task 29: 配置触发词和参数映射 ✅
- [x] Task 30: 测试 OpenClaw 调用流程 ✅
- [x] Task 31: 编写 OpenClaw 集成文档 ✅

**交付物**:
- ✅ intelligent-test-orchestrator Skill（完整可调用）
- ✅ manifest.json（OpenClaw 元数据配置）
- ✅ main.py（OpenClaw 调用入口）
- ✅ 简洁进度反馈（5 个阶段，每阶段一行）
- ✅ OpenClaw 调用文档
- ✅ 演示视频/截图

**验收标准**:
- ✅ OpenClaw 能正确识别触发词
- ✅ 能够解析用户自然语言输入
- ✅ 正确提取测试参数（target、test_mode 等）
- ✅ 完整执行 5 个阶段并反馈进度
- ✅ 返回结构化结果（JSON 格式）
- ✅ 报告可正常访问（file:// 链接）

---

## 任务清单

### 高优先级任务（7 个）

| ID | 任务 | 阶段 | 预计时间 | 状态 |
|----|------|------|----------|------|
| 1 | Phase-1 代码分析和优化方案设计 | Phase 1 | 2 小时 | ⏳ 待开始 |
| 2 | Phase-1 核心代码简化（10+ 文件 → 5-6 个核心文件） | Phase 1 | 1 天 | ⏳ 待开始 |
| 3 | 实现统一入口 SecurityTestOrchestrator | Phase 1 | 1 天 | ⏳ 待开始 |
| 7 | MVP 端到端测试和验证 | Phase 1 | 0.5 天 | ⏳ 待开始 |
| 8 | Phase-3 漏洞利用模块 - 漏洞验证器 | Phase 2 | 1 天 | ⏳ 待开始 |
| 11 | Phase-4 报告生成 - HTML 报告模板和渲染 | Phase 2 | 1 天 | ⏳ 待开始 |
| 19 | 端到端测试用例编写 | Phase 3 | 0.5 天 | ⏳ 待开始 |

### 中优先级任务（10 个）

| ID | 任务 | 阶段 | 预计时间 | 状态 |
|----|------|------|----------|------|
| 4 | 实现 Phase-0 资产收集适配器 | Phase 1 | 0.5 天 | ⏳ 待开始 |
| 5 | 实现 Phase-2 漏洞检测适配器 | Phase 1 | 0.5 天 | ⏳ 待开始 |
| 6 | 实现结果解析标准化模块 | Phase 1 | 0.5 天 | ⏳ 待开始 |
| 9 | Phase-3 漏洞利用模块 - 利用链生成 | Phase 2 | 0.5 天 | ⏳ 待开始 |
| 10 | Phase-3 漏洞利用模块 - 验证规则库 | Phase 2 | 0.5 天 | ⏳ 待开始 |
| 12 | Phase-4 报告生成 - Markdown 报告模板 | Phase 2 | 0.5 天 | ⏳ 待开始 |
| 15 | 性能优化 - 异步并发执行 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 18 | 工具选择规则库优化 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 20 | 性能基准测试 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 21 | 用户文档和使用指南 | Phase 3 | 0.5 天 | ⏳ 待开始 |

### 中优先级任务（续）

| ID | 任务 | 阶段 | 预计时间 | 状态 |
|----|------|------|----------|------|
| 24 | 创建 intelligent-test-orchestrator 主 Skill | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 25 | 编写 manifest.json（OpenClaw 元数据） | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 26 | 实现 main.py（OpenClaw 调用入口） | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 27 | 从 phase-1 迁移核心代码 | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 28 | 实现简洁进度反馈机制 | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 29 | 配置触发词和参数映射 | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 30 | 测试 OpenClaw 调用流程 | Phase 4 | 0.5 天 | ⏳ 待开始 |
| 31 | 编写 OpenClaw 集成文档 | Phase 4 | 0.5 天 | ⏳ 待开始 |

### 低优先级任务（6 个）

| ID | 任务 | 阶段 | 预计时间 | 状态 |
|----|------|------|----------|------|
| 13 | Phase-4 报告生成 - PDF 转换功能 | Phase 2 | 0.5 天 | ⏳ 待开始 |
| 14 | Phase-4 报告生成 - 报告样式美化 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 16 | 性能优化 - 缓存机制实现 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 17 | 简化版学习优化机制 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 22 | API 参考文档 | Phase 3 | 0.5 天 | ⏳ 待开始 |
| 23 | 示例代码和演示脚本 | Phase 3 | 0.5 天 | ⏳ 待开始 |

---

## 交付物清单

### 代码结构

```
advanced-pentester-v1.2/
├── intelligent-test-orchestrator/  # ⭐ 新增：OpenClaw 主 Skill
│   ├── manifest.json               # OpenClaw 元数据 ⭐
│   ├── SKILL.md                    # 技能文档 ⭐
│   ├── main.py                     # OpenClaw 调用入口 ⭐
│   ├── core/                       # 编排核心（从 phase-1 迁移）
│   │   ├── orchestrator.py         # 统一编排器
│   │   ├── risk_profiler.py        # 风险画像
│   │   ├── dynamic_planner.py      # 动态规划
│   │   ├── tool_selector.py        # 工具选择
│   │   └── optimizer.py            # 性能优化
│   ├── adapters/                   # 工具适配器
│   │   ├── phase0_adapter.py       # Phase-0 适配
│   │   ├── phase2_adapter.py       # Phase-2 适配
│   │   └── result_parser.py        # 结果解析
│   └── data/
│       ├── tool_rules.yml          # 工具选择规则
│       └── cve_mapping.json        # CVE 映射
│
├── phase-0-asset-collection/       # 资产收集（已有）
│   ├── whatweb-skill/
│   ├── nmap-scanner/
│   ├── httpx-skill/
│   ├── subfinder/
│   └── katana/
│
├── phase-1-strategy-planning/      # 智能编排（核心库）⭐
│   ├── core/                       # 与 orchestrator 共享
│   │   └── ...                     # 核心算法
│   └── scripts/                    # 原有代码（保留）
│
├── phase-2-vulnerability-scan/     # 漏洞检测（已有）
│   ├── nuclei-scanner/
│   ├── afrog/
│   └── nikto/
│
├── phase-3-exploitation/           # 漏洞利用（新增）⭐
│   ├── core/
│   │   ├── validator.py            # 验证器
│   │   ├── exploit_chain.py        # 利用链生成
│   │   └── verification_rules.yml  # 验证规则
│   └── exploits/
│       └── ...                     # 利用脚本
│
├── phase-4-reporting/              # 报告生成（新增）⭐
│   ├── core/
│   │   ├── report_generator.py     # 报告生成器
│   │   └── pdf_converter.py        # PDF 转换
│   ├── templates/
│   │   ├── executive.html          # 高管摘要
│   │   ├── technical.md            # 技术报告
│   │   └── full_report.html        # 完整报告
│   └── styles/
│       └── report.css              # 样式文件
│
└── examples/
    ├── example_1_basic.py          # 基础示例
    └── example_2_advanced.py       # 高级示例
```

### 核心功能模块

- ✅ **intelligent-test-orchestrator**: OpenClaw 主 Skill（统一入口）⭐
- ✅ **Phase-1 智能编排**: 风险画像 + 路径规划 + 工具选择 + 任务调度
- ✅ **Phase-3 漏洞利用**: 漏洞验证 + 利用链生成 + 验证规则
- ✅ **Phase-4 报告生成**: HTML + Markdown + PDF + JSON

### 文档

- ✅ 实施方案文档（本文档）
- ✅ OpenClaw 集成文档 ⭐
- ✅ 用户文档和使用指南
- ✅ API 参考文档
- ✅ 示例代码和演示脚本

---

## 技术决策

### 1. 异步执行模型

```python
# 使用 asyncio 实现并发
import asyncio

async def execute_full_test(self, target):
    # 并行执行资产收集
    tasks = [
        self.call_whatweb(target),
        self.call_nmap(target),
        self.call_httpx(target)
    ]
    results = await asyncio.gather(*tasks)
    
    # 串行执行漏洞检测（避免过载）
    for task in test_plan:
        await self.execute_task(task)
```

**理由**: 
- 提高执行效率
- 避免阻塞
- Python 原生支持

---

### 2. 工具调用模式

```python
# 统一工具调用接口
class ToolAdapter:
    async def execute(self, tool_name, params):
        # 1. 构建命令
        cmd = self.build_command(tool_name, params)
        
        # 2. 执行命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # 3. 解析结果
        return self.parse_result(tool_name, stdout)
```

**理由**:
- 统一接口，易于扩展
- 错误处理完善
- 支持异步执行

---

### 3. 报告生成技术栈

```python
# HTML 报告：Jinja2 模板
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('full_report.html')
html = template.render(data)

# Markdown 报告：直接字符串模板
markdown = render_markdown_template(data)

# PDF 报告：weasyprint 或 pdfkit
from weasyprint import HTML
pdf = HTML(string=html).write_pdf()
```

**依赖**:
```txt
jinja2>=3.0.0
weasyprint>=59.0  # 或 pdfkit>=2.0.0
markdown>=3.4.0
```

**理由**:
- Jinja2 成熟稳定
- weasyprint 支持 CSS 样式
- 轻量级，无复杂依赖

---

### 4. 代码简化策略

**保留精华（20%）**:
- ✅ `risk_profiler.py` 的风险评分算法
- ✅ `priority_engine.py` 的优先级排序逻辑
- ✅ `test_scheduler.py` 的任务调度框架
- ✅ `rule_engine.py` 的规则匹配机制

**简化或移除（80%）**:
- ❌ MDP 动态规划 → 改用启发式规则
- ❌ 学习优化机制 → v2.0 再考虑
- ❌ 未知技术处理 → 使用默认策略
- ❌ 复杂的数据结构 → 简化为 dict/list

**理由**:
- 保持核心功能
- 降低复杂度
- 提高可维护性

---

## 风险管理

### 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| Phase-1 代码复杂度高 | 🟡 中 | 🔴 高 | 先简化再优化，保留核心 20% |
| 工具调用失败处理 | 🔴 高 | 🟡 中 | 完善的错误处理和重试机制 |
| PDF 生成依赖复杂 | 🟡 中 | 🟢 低 | 优先保证 HTML，PDF 作为可选 |
| 验证模块误报率高 | 🟡 中 | 🟡 中 | 保守策略，宁可漏报不误报 |
| 性能不达标 | 🟢 低 | 🟡 中 | 异步并发 + 缓存优化 |

### 应对措施

#### 1. Phase-1 代码复杂度

**问题**: 现有代码 279KB，10+ 文件，复杂度高

**应对**:
- 第 1 步：深入阅读所有核心文件，识别精华部分
- 第 2 步：设计简化后的架构（5-6 个核心文件）
- 第 3 步：逐步迁移精华逻辑，丢弃复杂部分
- 第 4 步：单元测试验证功能正确性

---

#### 2. 工具调用失败

**问题**: 外部工具（Nmap/Nuclei/Afrog）可能安装失败或执行出错

**应对**:
```python
# 完善的错误处理
async def execute_with_retry(self, tool_name, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await self.adapter.execute(tool_name, params)
            return result
        except ToolNotFoundError:
            logger.error(f"工具{tool_name}未找到，尝试自动安装")
            await self.auto_install(tool_name)
        except ExecutionError as e:
            logger.warning(f"执行失败（尝试{attempt+1}/{max_retries}）: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

---

#### 3. 验证模块误报

**问题**: 漏洞验证可能产生误报或漏报

**应对**:
- **保守策略**: 宁可漏报，不误报（特别是高危漏洞）
- **交叉验证**: 使用不同工具交叉验证同一漏洞
- **置信度评分**: 为每个验证结果提供置信度（0-1）
- **手工验证辅助**: 提供手工验证的步骤和工具

---

## 成功指标

### 功能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 全自动完成度 | 100% | 5 个阶段全部自动执行 |
| 报告格式支持 | 3 种 | HTML/Markdown/PDF |
| Phase-3 验证准确率 | >80% | 已验证漏洞/总漏洞 |
| 规则库覆盖率 | 主流 CVE + 常见漏洞 | 统计规则库覆盖范围 |

### 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 单目标全流程时间 | <30 分钟 | 中等规模目标 |
| 内存占用 | <500MB | 峰值内存使用 |
| 并发工具数 | 5+ | 同时执行的工具数 |
| 错误恢复率 | >95% | 成功恢复的错误/总错误 |

### 用户体验指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 一键执行 | ✅ 支持 | 无需手工干预 |
| 进度可见 | ✅ 实时显示 | 控制台/日志输出 |
| 错误定位 | ✅ 清晰可定位 | 错误信息包含行号/工具 |
| 报告专业性 | ✅ 美观专业 | 用户反馈 |

---

## 下一步行动

### 立即开始

**Task 1: Phase-1 代码分析和优化方案设计**

**工作内容**:
1. 深入阅读现有 Phase-1 核心代码（10+ 个文件）
2. 识别哪些是核心精华（保留）
3. 识别哪些可以简化或移除
4. 设计优化后的代码结构
5. 输出详细的优化方案文档

**预计时间**: 2 小时

**输出**:
- 现有代码分析报告
- 优化后的架构设计
- 文件迁移计划

---

### 依赖关系

```
Task 1 (代码分析)
  ↓
Task 2 (代码简化)
  ↓
Task 3 (统一入口)
  ↓
Task 4/5/6 (适配器)
  ↓
Task 7 (MVP 验证)
  ↓
Task 8/9/10 (Phase-3)
  ↓
Task 11/12/13/14 (Phase-4)
  ↓
Task 15-23 (优化完善)
```

---

## 附录

### 附录 A：现有 Phase-1 文件清单

```
phase-1-strategy-planning/scripts/
├── intelligent_test_engine.py      # 279KB 主程序
├── demo_full_intelligent_engine.py # 演示脚本
├── risk_profiler.py                # ✅ 保留：风险画像
├── dynamic_planner.py              # ✅ 保留（简化）：动态规划
├── priority_engine.py              # ✅ 保留：优先级排序
├── resource_optimizer.py           # ⚠️ 简化：资源优化
├── test_scheduler.py               # ✅ 保留（简化）：任务调度
├── unknown_tech_handler.py         # ❌ 移除：未知技术处理
├── feature_extractor.py            # ❌ 移除：特征提取
├── learning_optimizer.py           # ⚠️ 简化：学习优化
├── pattern_learner.py              # ❌ 移除：模式学习
├── rule_optimizer.py               # ❌ 移除：规则优化
├── knowledge_evolver.py            # ❌ 移除：知识进化
├── asset_normalizer.py             # ✅ 保留：资产标准化
├── rule_engine.py                  # ✅ 保留（增强）：规则引擎
└── test_strategist.py              # ⚠️ 合并：策略生成
```

### 附录 B：核心 API 设计

```python
# 统一入口 API
class SecurityTestOrchestrator:
    async def execute_full_test(
        self,
        target: str,
        options: dict = None
    ) -> TestResult:
        """执行完整安全测试流程"""
        pass
    
    async def execute_phase(
        self,
        phase: str,
        target: str,
        options: dict = None
    ) -> Any:
        """执行单个阶段"""
        pass

# 结果数据结构
@dataclass
class TestResult:
    assets: List[Asset]
    risk_report: RiskReport
    vulnerabilities: List[Vulnerability]
    verified_vulns: List[VerifiedVulnerability]
    report_url: str
```

### 附录 C：工具选择规则示例

```yaml
# tool_rules.yml 示例
rules:
  - id: tomcat_cve_detection
    name: Tomcat CVE 检测
    condition:
      technologies:
        - name: "Tomcat"
          version: "<9.0.0"
    actions:
      - tool: nuclei
        templates:
          - cve-2020-5407
          - cve-2021-22991
        priority: critical
        estimated_time: 15
      
      - tool: afrog
        poc_filter: "tomcat"
        priority: high
        estimated_time: 10
    
    dependencies:
      - "nmap_port_scan"
    
    conflicts: []
  
  - id: jquery_xss_detection
    name: jQuery XSS 检测
    condition:
      technologies:
        - name: "jQuery"
          version: "<1.9.0"
    actions:
      - tool: afrog
        poc_filter: "jquery,xss"
        priority: medium
        estimated_time: 10
    
    dependencies:
      - "whatweb_scan"
    
    conflicts: []
```

---

## 修订历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-04-20 | 安小易 008 | 初始版本，基于最终讨论方案 |
| v1.1 | 2026-04-20 | 安小易 008 | 调整目录结构：Phase-0 资产收集，Phase-1 智能编排，Phase-2 漏洞检测，Phase-3 漏洞利用，Phase-4 报告生成 |
| v1.2 | 2026-04-20 | 安小易 008 | 增加 OpenClaw 集成章节：创建独立主 Skill、manifest.json、main.py 入口、简洁进度反馈 | |

---

**文档状态**: ✅ 已批准，准备实施  
**下一步**: 开始 Task 1 - Phase-1 代码分析和优化方案设计
