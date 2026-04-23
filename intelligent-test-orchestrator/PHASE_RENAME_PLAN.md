# Phase 命名统一修改计划

**修改时间**: 2026-04-22  
**修改范围**: 整个项目文档和代码注释  
**原则**: 只修改文档和注释，不修改代码类名和文件名

---

## 📋 修改原则

### ✅ 需要修改的内容

1. **文档中的 Phase 描述** - Phase-0 → Phase-1
2. **代码注释** - Phase-0 → Phase-1
3. **日志输出** - Phase 0 → Phase 1
4. **测试用例名称** - Phase 0 → Phase 1
5. **目录结构说明** - phase-0-asset-collection → phase-1-asset-collection

### ❌ 不修改的内容

1. **Python 类名** - `Phase0Adapter` 保持不变
2. **Python 文件名** - `phase0_adapter.py` 保持不变
3. **导入语句** - `from adapters.phase0_adapter import Phase0Adapter` 保持不变
4. **配置类名** - `Phase0Config` 保持不变

**原因**: 代码内部实现，修改成本高且不影响功能

---

## 🔍 需要修改的文件清单

### 核心文档（高优先级）

| 文件 | 修改数量 | 优先级 |
|------|---------|--------|
| `IMPLEMENTATION_PLAN.md` | ~15 处 | 🔴 高 |
| `OPENCLAW_INTEGRATION.md` | ~5 处 | 🔴 高 |
| `README.md` | 待检查 | 🔴 高 |
| `SKILL.md` | 待检查 | 🔴 高 |

### 测试文档（中优先级）

| 文件 | 修改数量 | 优先级 |
|------|---------|--------|
| `test/test_integration_fixed.py` | ~5 处 | 🟡 中 |
| `test/test_integration.py` | ~5 处 | 🟡 中 |
| `test/INTEGRATION_TEST_GUIDE.md` | ~8 处 | 🟡 中 |
| `test/SERVER_TEST.md` | ~2 处 | 🟡 中 |
| `test/E2E_TEST_REPORT.md` | ~2 处 | 🟡 中 |

### 部署文档（低优先级）

| 文件 | 修改数量 | 优先级 |
|------|---------|--------|
| `deploy_to_server.ps1` | ~6 处 | 🟢 低 |
| `DEPLOY_OPTIMIZED_CODE.md` | ~10 处 | 🟢 低 |

### 代码文件（仅注释）

| 文件 | 修改数量 | 优先级 |
|------|---------|--------|
| `adapters/phase0_adapter_real.py` | 注释 | 🟡 中 |
| `core/config_optimized.py` | 注释 | 🟡 中 |
| `core/config_validation.py` | 注释 | 🟡 中 |

---

## 📝 修改示例

### 文档修改

**修改前**:
```markdown
## Phase-0: 资产收集

Phase-0 负责收集目标资产信息...
```

**修改后**:
```markdown
## Phase-1: 资产收集

Phase-1 负责收集目标资产信息...
```

### 代码注释修改

**修改前**:
```python
class Phase0Adapter(BaseToolAdapter):
    """Phase-0 资产收集适配器"""
```

**修改后**:
```python
class Phase0Adapter(BaseToolAdapter):
    """Phase-1 资产收集适配器（类名保持不变）"""
```

### 测试用例修改

**修改前**:
```python
async def test_phase0_asset_collection(target: str):
    """测试 Phase 0: 资产收集"""
    result = IntegrationTestResult("Phase 0: 资产收集")
```

**修改后**:
```python
async def test_phase1_asset_collection(target: str):
    """测试 Phase 1: 资产收集"""
    result = IntegrationTestResult("Phase 1: 资产收集")
```

---

## 🚀 执行计划

### 阶段 1: 核心文档（立即执行）

1. ✅ `IMPLEMENTATION_PLAN.md` - 所有 Phase-0 描述
2. ✅ `OPENCLAW_INTEGRATION.md` - 集成文档
3. ⏳ `README.md` - 项目说明
4. ⏳ `SKILL.md` - Skill 文档

### 阶段 2: 测试文件（随后执行）

1. ⏳ `test/test_integration_fixed.py` - 测试函数名
2. ⏳ `test/test_integration.py` - 测试函数名
3. ⏳ `test/INTEGRATION_TEST_GUIDE.md` - 测试指南
4. ⏳ 其他测试文档

### 阶段 3: 代码注释（可选执行）

1. ⏳ `adapters/phase0_adapter_real.py` - 类注释
2. ⏳ `core/*.py` - 配置类注释

---

## ⚠️ 注意事项

### 不影响功能

- 所有修改都是文档和注释层面
- 不影响代码执行逻辑
- 不影响 API 接口

### 向后兼容

- 类名保持 `Phase0Adapter`
- 文件名保持 `phase0_adapter.py`
- 导入语句不变

### 版本控制

- 建议在修改前创建备份
- 使用 Git 记录修改历史
- 便于回滚和审查

---

## ✅ 验证步骤

修改完成后，运行以下命令验证：

```bash
# 检查是否还有 Phase-0 的引用（仅文档历史）
grep -r "Phase-0" . --include="*.md"

# 检查 Phase-1 是否正确应用
grep -r "Phase-1" . --include="*.md" | head -20

# 验证代码文件（类名应该保持 Phase0）
grep -r "class Phase0Adapter" . --include="*.py"
```

---

## 📊 修改统计

预计修改：
- 📄 文档文件：~15 个
- 💻 代码文件：~5 个（仅注释）
- 📝 总修改行数：~100 行
- ⏱️ 预计时间：30 分钟

---

**报告生成时间**: 2026-04-22  
**状态**: 准备执行
