# OpenClaw 集成文档

## 📋 概述

本文档详细说明如何将 `intelligent-test-orchestrator` 集成�?OpenClaw 智能体平台，实现用户通过自然语言调用智能安全测试框架�?
---

## 🏗�?架构设计

### 集成架构�?
```
┌─────────────────────────────────────────�?�?  用户                                   �?�?  - 输入自然语言指令                    �?�?  - 例如�?帮我测试 example.com"        �?└──────────────┬──────────────────────────�?               �?               �?自然语言
               �?┌─────────────────────────────────────────�?�?  OpenClaw 智能�?                       �?�?  - 意图识别                            �?�?  - 参数提取                            �?�?  - 技能匹�?                           �?└──────────────┬──────────────────────────�?               �?               �?结构化调�?               �?┌─────────────────────────────────────────�?�?intelligent-test-orchestrator           �?�?- manifest.json (技能元数据)            �?�?- main.py (调用入口)                    �?�?- core/ (编排核心)                      �?└──────────────┬──────────────────────────�?               �?               �?协调调用
               �?┌─────────────────────────────────────────�?�?Phase 1-4 工具�?                        �?�?- Phase-1: 资产收集                     �?�?- Phase-1: 智能编排                     �?�?- Phase-2: 漏洞检�?                    �?�?- Phase-3: 漏洞利用                     �?�?- Phase-4: 报告生成                     �?└─────────────────────────────────────────�?```

---

## 📦 组件说明

### 1. manifest.json - OpenClaw 技能元数据

**位置**: `intelligent-test-orchestrator/manifest.json`

**作用**: �?OpenClaw 注册技能，定义接口、触发词、依赖项

**关键字段**:
```json
{
  "name": "intelligent-test-orchestrator",
  "interface": {
    "function": {
      "name": "execute_intelligent_test",
      "parameters": {...}
    }
  },
  "triggers": ["智能测试", "安全测试", "漏洞扫描"],
  "dependencies": [...]
}
```

### 2. main.py - OpenClaw 调用入口

**位置**: `intelligent-test-orchestrator/main.py`

**作用**: 接收 OpenClaw 调用，执行测试流程，返回结果

**核心�?*:
- `OpenClawHandler`: 处理器类
- `execute_intelligent_test()`: 主接口方�?
### 3. core/ - 编排核心

**位置**: `intelligent-test-orchestrator/core/`

**作用**: 实现智能编排逻辑（Task 27 �?phase-1 迁移�?
**核心模块**:
- `orchestrator.py`: 统一编排�?- `risk_profiler.py`: 风险画像
- `dynamic_planner.py`: 动态规�?- `tool_selector.py`: 工具选择

---

## 🔌 集成步骤

### 步骤 1: 创建�?Skill 目录

```bash
# Windows PowerShell
New-Item -Path "intelligent-test-orchestrator" -ItemType Directory -Force
New-Item -Path "intelligent-test-orchestrator\core" -ItemType Directory -Force
New-Item -Path "intelligent-test-orchestrator\adapters" -ItemType Directory -Force
New-Item -Path "intelligent-test-orchestrator\data" -ItemType Directory -Force
```

### 步骤 2: 创建 manifest.json

创建 `manifest.json` 文件，定�?OpenClaw 接口�?
```json
{
  "name": "intelligent-test-orchestrator",
  "version": "1.0.0",
  "description": "智能安全测试编排�?,
  "interface": {
    "type": "function",
    "function": {
      "name": "execute_intelligent_test",
      "parameters": {
        "type": "object",
        "properties": {
          "target": {
            "type": "string",
            "description": "测试目标 (URL/IP/域名)"
          },
          "test_mode": {
            "type": "string",
            "enum": ["full", "light", "custom"]
          }
        },
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

### 步骤 3: 实现 main.py 入口

创建 `main.py` 文件，实�?OpenClaw 调用接口�?
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import sys

class OpenClawHandler:
    async def execute_intelligent_test(
        self,
        target: str,
        test_mode: str = "full",
        time_limit: int = 120,
        report_format: str = "html"
    ) -> dict:
        """OpenClaw 调用接口"""
        # 实现测试逻辑
        pass

async def main():
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read())
    
    handler = OpenClawHandler()
    result = await handler.execute_intelligent_test(**input_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
```

### 步骤 4: 注册�?OpenClaw

#### 方式 A: 自动扫描（推荐）

OpenClaw 会自动扫描技能目录：

```bash
# 将技能目录放�?OpenClaw �?skills 文件�?cp -r intelligent-test-orchestrator /path/to/openclaw/skills/
```

#### 方式 B: 手动配置

�?OpenClaw 配置文件中添加：

```yaml
skills:
  - name: intelligent-test-orchestrator
    path: /path/to/intelligent-test-orchestrator
    entry: main.py
```

### 步骤 5: 测试调用

#### 命令行测�?
```bash
# 方式 1: 命令行参�?python main.py '{"target": "http://example.com", "test_mode": "full"}'

# 方式 2: stdin 输入
echo '{"target": "http://example.com"}' | python main.py

# 方式 3: 文件输入
Get-Content test_input.json | python main.py
```

#### OpenClaw 测试

�?OpenClaw 中输入自然语言�?
```
"帮我测试一�?http://zero.webappsecurity.com，做完整的安全测�?
```

---

## 📊 调用流程详解

### 1. 用户输入 �?OpenClaw 理解

**用户输入示例**:
```
"帮我测试一�?http://zero.webappsecurity.com，做完整的安全测�?
```

**OpenClaw 处理**:
- **意图识别**: 安全测试/渗透测�?- **实体提取**: 
  - target: "http://zero.webappsecurity.com"
  - test_mode: "full" (�?完整�?推断)
- **技能匹�?*: 触发�?安全测试" �?intelligent-test-orchestrator

### 2. OpenClaw �?Skill 调用

OpenClaw 调用 Skill 接口�?
```python
execute_intelligent_test(
    target="http://zero.webappsecurity.com",
    test_mode="full",
    time_limit=120,
    report_format="html"
)
```

### 3. Skill 执行 �?进度反馈

Skill 执行 5 个阶段，每阶段输出一行进度：

```
🚀 开始智能安全测�?🎯 目标：http://zero.webappsecurity.com
📊 模式：full
⏱️  时间限制�?20 分钟

🎯 阶段 1/5: 资产收集�?..
�?发现 5 个资�?
🧠 阶段 2/5: 风险画像生成�?..
⚠️  风险评分�?.5/100

🔍 阶段 3/5: 漏洞检测中...
🐛 发现 12 个漏�?
🔬 阶段 4/5: 漏洞验证�?..
✔️  已验�?8 个漏�?
📄 阶段 5/5: 报告生成�?..
📊 报告已生成：/path/to/report.html
```

### 4. 返回结果 �?OpenClaw 展示

Skill 返回结构�?JSON�?
```json
{
  "success": true,
  "summary": "�?测试完成，发�?12 个漏洞（已验�?8 个），风险评�?7.5/100",
  "data": {
    "target": "http://zero.webappsecurity.com",
    "assets_found": 5,
    "vulnerabilities_found": 12,
    "verified_vulns": 8,
    "risk_score": 7.5,
    "report_path": "/path/to/report.html",
    "report_url": "file:///path/to/report.html"
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

OpenClaw 解析并展示结果�?
---

## ⚙️ 配置选项

### manifest.json 配置

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | �?| 技能名�?|
| `version` | string | �?| 版本�?|
| `description` | string | �?| 技能描�?|
| `interface` | object | �?| 接口定义 |
| `triggers` | array | �?| 触发词列�?|
| `dependencies` | array | �?| 依赖技�?|
| `permissions` | array | �?| 权限列表 |

### 调用参数配置

| 参数 | 类型 | 默认�?| 说明 |
|------|------|--------|------|
| `target` | string | - | 测试目标（必需�?|
| `test_mode` | string | "full" | 测试模式 |
| `time_limit` | integer | 120 | 时间限制（分钟） |
| `report_format` | string | "html" | 报告格式 |
| `severity_filter` | array | 全部 | 漏洞过滤 |
| `custom_options` | object | {} | 自定义选项 |

---

## 🧪 测试验证

### 测试用例

#### 1. 基本调用测试

```bash
python main.py '{"target": "http://example.com", "test_mode": "full"}'
```

**预期输出**:
- �?success: true
- �?包含 summary �?data 字段
- �?进度反馈正常显示

#### 2. 快速模式测�?
```bash
python main.py '{"target": "http://example.com", "test_mode": "light"}'
```

**预期**: 仅检测高危漏洞，执行时间较短

#### 3. 自定义模式测�?
```bash
python main.py '{"target": "http://example.com", "test_mode": "custom", "custom_options": {"skip_verification": true}}'
```

**预期**: 跳过漏洞验证阶段

#### 4. 错误处理测试

```bash
python main.py '{"test_mode": "full"}'
```

**预期**: 
- �?success: false
- �?包含错误信息（缺�?target�?
---

## 🐛 故障排除

### 常见问题

#### Q1: OpenClaw 无法识别技�?
**原因**: manifest.json 配置错误或路径不正确

**解决**:
1. 检�?manifest.json 语法
2. 确认技能目录在 OpenClaw 扫描路径�?3. 重启 OpenClaw

#### Q2: 调用时返回编码错�?
**原因**: Windows 默认编码�?GBK，与 UTF-8 冲突

**解决**:
�?main.py 开头添加：
```python
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

#### Q3: 进度反馈显示乱码

**原因**: 终端不支�?UTF-8 emoji

**解决**:
- 方式 1: 使用支持 UTF-8 的终端（�?VSCode 终端�?- 方式 2: 移除进度输出中的 emoji

#### Q4: 依赖技能未找到

**原因**: manifest.json 中声明的依赖未安�?
**解决**:
```bash
# 安装依赖技�?cp -r phase-1-asset-collection/whatweb-skill /path/to/openclaw/skills/
cp -r phase-1-asset-collection/nmap-scanner /path/to/openclaw/skills/
```

---

## 📚 最佳实�?
### 1. 触发词设�?
- �?覆盖常见场景（智能测试、安全测试、漏洞扫描）
- �?包含中英文触发词
- �?避免过于宽泛的触发词

### 2. 进度反馈

- �?每个阶段一行输�?- �?使用 emoji 增强可读�?- �?显示关键数据（资产数、漏洞数�?- �?避免过多技术细�?
### 3. 错误处理

- �?返回结构化错误信�?- �?包含错误类型和时间戳
- �?提供友好的错误提�?
### 4. 性能优化

- �?设置合理的时间限�?- �?支持并发执行工具
- �?提供快速模式（light�?
---

## 📊 监控和日�?
### 日志记录

建议�?production 环境中添加日志：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### 性能监控

监控关键指标�?- 执行时间
- 资产发现数量
- 漏洞检测数�?- 内存占用

---

## 🔐 安全注意事项

### 1. 权限控制

- 仅允许授权用户调�?- 限制测试目标范围（内�?授权目标�?- 记录所有测试活�?
### 2. 速率限制

- 限制并发测试数量
- 避免对目标造成过大负载
- 设置合理的超时时�?
### 3. 数据保护

- 加密存储测试报告
- 定期清理敏感数据
- 遵守隐私保护法规

---

## 📖 相关文档

- [SKILL.md](../SKILL.md) - 技能使用文�?- [manifest.json](../manifest.json) - 技能元数据
- [main.py](../main.py) - 调用入口源码
- [IMPLEMENTATION_PLAN.md](../../phase-1-strategy-planning/IMPLEMENTATION_PLAN.md) - 实施方案

---

## 🎯 下一�?
完成基础集成后，可以继续�?
1. **Task 27**: �?phase-1 迁移核心代码
2. **实现真实工具调用**: 集成 Phase-1 �?Phase-2 工具
3. **优化性能**: 实现并发执行和缓存机�?4. **完善报告**: 实现 HTML/Markdown/PDF 报告生成

---

**版本**: 1.0.0  
**创建时间**: 2026-04-20  
**最后更�?*: 2026-04-20
