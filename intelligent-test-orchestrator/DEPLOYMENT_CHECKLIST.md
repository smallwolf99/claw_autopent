# OpenClaw 部署准备检查清单

## 📋 部署前检查

### ✅ 代码准备（已完成）

| 项目 | 状态 | 说明 |
|------|------|------|
| **核心代码** | ✅ 完成 | main.py 已实现 |
| **manifest.json** | ✅ 完成 | OpenClaw 元数据配置 |
| **SKILL.md** | ✅ 完成 | 技能文档 |
| **core 模块** | ✅ 完成 | 风险画像、测试策略、规则引擎 |
| **adapters 模块** | ✅ 完成 | Phase-0/2/3/4 适配器 |
| **requirements.txt** | ✅ 完成 | 依赖清单 |

---

### ✅ 功能验证（已完成）

| 测试项 | 状态 | 说明 |
|--------|------|------|
| **单元测试** | ✅ 通过 | 所有模块测试通过 |
| **端到端测试** | ✅ 通过 | 完整流程测试成功 |
| **PDF 生成** | ✅ 完成 | 代码实现，待安装 weasyprint |
| **报告生成** | ✅ 通过 | HTML/Markdown/JSON正常 |
| **错误处理** | ✅ 通过 | 异常处理完善 |

---

### ⚠️ 待准备事项（部署前需要）

#### 1. OpenClaw 服务器环境

**需要确认:**
- [ ] OpenClaw 服务器地址
- [ ] 部署方式（Docker/直接部署）
- [ ] 访问权限和认证
- [ ] 服务器 Python 版本（需要 3.8+）

#### 2. 依赖安装

**服务器需要安装:**
```bash
# 基础依赖
pip install -r requirements.txt

# 可选：PDF 生成
pip install weasyprint>=57.0

# 可选：真实工具调用
# Nuclei, Nmap, WhatWeb, Httpx, Subfinder, Afrog, Nikto
```

#### 3. 工具安装（如需真实执行）

**Phase-0 工具:**
- [ ] WhatWeb
- [ ] Nmap
- [ ] Httpx
- [ ] Subfinder

**Phase-2 工具:**
- [ ] Nuclei
- [ ] Afrog
- [ ] Nikto

**Phase-3 工具:**
- [ ] 漏洞验证工具（代码中已预留）

#### 4. 配置文件

**需要配置:**
- [ ] 工具路径配置（如不在 PATH 中）
- [ ] 输出目录权限
- [ ] 日志目录
- [ ] 临时文件目录

---

## 🚀 部署步骤

### 方案 A: 完整部署（推荐）

**步骤 1: 准备服务器环境**
```bash
# 1. 确认 Python 版本
python --version  # 需要 3.8+

# 2. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

**步骤 2: 安装工具（可选，如需真实执行）**
```bash
# 安装 Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# 安装 Nmap
# Windows: 下载安装包安装
# Linux: sudo apt-get install nmap

# 安装 WhatWeb
gem install whatweb

# 其他工具参考各自官方文档
```

**步骤 3: 部署代码**
```bash
# 复制整个目录到服务器
scp -r intelligent-test-orchestrator/ user@server:/path/to/openclaw/skills/

# 或使用 git
git clone <repository-url> /path/to/openclaw/skills/intelligent-test-orchestrator
```

**步骤 4: 配置 OpenClaw**
```bash
# 在 OpenClaw 配置中注册 Skill
# 编辑 openclaw/config.yaml 或类似文件
skills:
  - name: intelligent-test-orchestrator
    path: /path/to/intelligent-test-orchestrator
    entry: main.execute_intelligent_test
    triggers:
      - "安全测试"
      - "渗透测试"
      - "漏洞扫描"
      - "帮我测试"
```

**步骤 5: 测试部署**
```bash
# 测试调用
cd /path/to/intelligent-test-orchestrator
python main.py '{"target": "http://test.example.com", "test_mode": "light"}'
```

---

### 方案 B: 模拟模式部署（快速验证）

**说明:** 使用模拟数据，不依赖真实工具，适合快速验证 OpenClaw 集成

**步骤 1: 部署代码**
```bash
# 复制代码到服务器
scp -r intelligent-test-orchestrator/ user@server:/path/to/openclaw/skills/
```

**步骤 2: 安装基础依赖**
```bash
pip install -r requirements.txt
# 不需要安装 weasyprint 和真实工具
```

**步骤 3: 配置 OpenClaw**
```yaml
skills:
  - name: intelligent-test-orchestrator
    path: /path/to/intelligent-test-orchestrator
    entry: main.execute_intelligent_test
```

**步骤 4: 测试**
```bash
python main.py '{"target": "http://demo.test.com", "test_mode": "full"}'
```

**预期结果:**
- ✅ 返回模拟测试结果
- ✅ 生成 HTML 报告
- ✅ OpenClaw 能正常调用

---

## 📊 部署验证清单

### 基础验证

- [ ] **代码完整性检查**
  ```bash
  ls -la intelligent-test-orchestrator/
  # 应该包含：main.py, manifest.json, SKILL.md, core/, adapters/
  ```

- [ ] **依赖安装检查**
  ```bash
  pip list | grep -E "(aiohttp|pyyaml|jsonschema)"
  ```

- [ ] **Python 版本检查**
  ```bash
  python --version  # 应该 >= 3.8
  ```

- [ ] **文件权限检查**
  ```bash
  chmod +x main.py
  chmod -R 755 intelligent-test-orchestrator/
  ```

### 功能验证

- [ ] **简单测试**
  ```bash
  python test_simple.py
  # 应该返回成功的测试结果
  ```

- [ ] **报告生成测试**
  ```bash
  python test_pdf_generation.py
  # 应该生成 HTML/Markdown/JSON 报告
  ```

- [ ] **OpenClaw 调用测试**
  ```bash
  # 通过 OpenClaw 触发
  # 观察日志和输出
  ```

### 性能验证

- [ ] **内存占用**
  ```bash
  # 运行时监控内存
  # 应该 < 500MB
  ```

- [ ] **执行时间**
  ```bash
  # 记录完整流程时间
  # 模拟模式：< 10 秒
  # 真实工具：根据目标复杂度
  ```

---

## 🔧 故障排查

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'xxx'
```
**解决:** 
```bash
pip install -r requirements.txt
```

#### 2. 编码错误
```
UnicodeDecodeError: 'gbk' codec can't decode...
```
**解决:** 
- 已在代码中设置 UTF-8 编码
- 确保服务器支持 UTF-8

#### 3. 权限错误
```
PermissionError: [Errno 13] Permission denied
```
**解决:**
```bash
chmod 755 intelligent-test-orchestrator/
chmod +x main.py
```

#### 4. 工具未找到
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```
**解决:**
- 安装对应工具
- 或将工具添加到 PATH 环境变量

---

## 📝 部署记录模板

### 部署信息

| 项目 | 值 |
|------|-----|
| **部署日期** | YYYY-MM-DD |
| **部署人员** | - |
| **服务器地址** | - |
| **部署方式** | 完整部署 / 模拟模式 |
| **Python 版本** | 3.x.x |
| **OpenClaw 版本** | - |

### 部署步骤

1. [ ] 环境准备完成
2. [ ] 依赖安装完成
3. [ ] 代码部署完成
4. [ ] 配置完成
5. [ ] 测试通过

### 测试结果

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 基础功能 | ✅ / ❌ | - |
| OpenClaw 集成 | ✅ / ❌ | - |
| 报告生成 | ✅ / ❌ | - |
| 性能测试 | ✅ / ❌ | - |

### 问题记录

- 问题 1: -
  - 解决方案: -

---

## 🎯 下一步建议

### 立即可做

1. **确认 OpenClaw 服务器信息**
   - 服务器地址
   - 部署方式
   - 访问权限

2. **选择部署模式**
   - 模拟模式（快速验证）
   - 完整部署（生产使用）

3. **准备部署脚本**
   - 自动化部署脚本
   - 配置管理

### 部署后

1. **监控运行**
   - 日志监控
   - 性能监控
   - 错误告警

2. **用户培训**
   - 使用说明
   - 最佳实践
   - 故障排查

3. **持续优化**
   - 性能调优
   - 功能增强
   - 工具更新

---

## 📞 联系支持

如遇到部署问题，请提供：
- 服务器环境信息
- Python 版本
- 错误日志
- 复现步骤

---

**部署准备就绪！** 🚀

**当前状态:**
- ✅ 代码准备完成
- ✅ 功能验证通过
- ✅ 文档齐全
- ⏳ 等待服务器环境信息

**建议:** 先使用模拟模式部署到 OpenClaw 测试服务器验证集成，确认无误后再部署完整版本。
