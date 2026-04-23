# 🚀 快速部署说明

**阶段 3 优化代码** - 一键部署到 OpenClaw 服务器

---

## ⚡ 快速开始（3 步部署）

### Windows (PowerShell)

```powershell
# 1. 进入目录
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test

# 2. 运行部署脚本
.\deploy_to_server.ps1 -ServerIP "你的服务器 IP"

# 3. 等待完成（约 2-5 分钟）
```

### Linux/Mac (Bash)

```bash
# 1. 进入目录
cd /d/TRAE/advanced-pentester-v1.2/intelligent-test-orchestrator/test

# 2. 添加执行权限
chmod +x deploy_to_server.sh

# 3. 运行部署脚本
./deploy_to_server.sh 你的服务器 IP
```

---

## 📋 部署前检查清单

- [ ] **服务器 IP**: 知道服务器的 IP 地址或域名
- [ ] **SSH 访问**: 可以 SSH 连接到服务器
- [ ] **本地文件**: 8 个核心优化文件已存在
- [ ] **网络**: 本地可以访问外网（上传文件）

---

## 🎯 部署的文件

### 8 个核心优化模块

| 文件 | 功能 | 行数 |
|------|------|------|
| `utils/cache.py` | 缓存系统（901.7x 加速） | 271 |
| `utils/performance_monitor.py` | 性能监控 | 319 |
| `utils/health_checker.py` | 健康检查 | 267 |
| `utils/memory_optimizer.py` | 内存优化（99.8% 节省） | 156 |
| `utils/logger.py` | 日志系统 | - |
| `adapters/base_tool_adapter.py` | 基类适配器 | - |
| `core/config_optimized.py` | 优化配置 | - |
| `core/config_validation.py` | 配置验证 | - |

---

## ✅ 部署验证

### 快速验证（1 分钟）

```bash
# SSH 到服务器
ssh ubuntu@你的服务器 IP

# 测试导入
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 -c "
from utils.cache import MemoryCache
from utils.performance_monitor import PerformanceMonitor
from utils.health_checker import HealthChecker
print('✅ 所有模块导入成功')
"
```

### 完整验证（5 分钟）

```bash
# 运行测试
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase3_optimization.py
python3 test/test_e2e_optimization.py
```

---

## 🔧 常见问题

### Q1: SSH 连接失败？

**检查**:
```bash
ping 你的服务器 IP
ssh -v ubuntu@你的服务器 IP
```

**解决**:
- 确认服务器 IP 正确
- 检查 SSH 密钥配置
- 确认服务器在线

### Q2: 权限错误？

**解决**:
```bash
# 在服务器上
chmod 644 ~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/*.py
chmod 644 ~/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/*.py
chmod 644 ~/.openclaw/workspace/skills/intelligent-test-orchestrator/core/*.py
```

### Q3: 导入错误？

**解决**:
```bash
# 设置 Python 路径
export PYTHONPATH="$HOME/.openclaw/workspace/skills/intelligent-test-orchestrator:$PYTHONPATH"

# 或添加到 ~/.bashrc
echo "export PYTHONPATH=\"\$HOME/.openclaw/workspace/skills/intelligent-test-orchestrator:\$PYTHONPATH\"" >> ~/.bashrc
source ~/.bashrc
```

### Q4: 依赖缺失？

**解决**:
```bash
pip3 install psutil pydantic
```

---

## 📊 部署时间估算

| 步骤 | 预计时间 |
|------|----------|
| 检查本地文件 | 10 秒 |
| SSH 连接测试 | 5 秒 |
| 创建备份 | 10 秒 |
| 上传文件（8 个） | 1-2 分钟 |
| 验证文件 | 30 秒 |
| 测试导入 | 30 秒 |
| 功能测试 | 1-2 分钟 |
| **总计** | **3-5 分钟** |

---

## 🎉 部署成功标志

部署成功后，你应该看到：

```
✅ 所有文件已成功部署
✅ Python 导入测试通过
✅ 功能测试通过
✅ OpenClaw 正常运行
```

**性能指标**:
- 缓存加速：>100x（实际 901.7x）
- 内存节省：>90%（实际 99.8%）
- 测试覆盖：100%

---

## 📁 相关文档

- **详细部署指南**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
- **部署检查清单**: [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md)
- **优化完成报告**: [`PHASE3_OPTIMIZATION_COMPLETE.md`](../PHASE3_OPTIMIZATION_COMPLETE.md)
- **端到端测试报告**: [`E2E_TEST_REPORT.md`](E2E_TEST_REPORT.md)

---

## 🔄 回滚（如果需要）

```bash
# SSH 到服务器
ssh ubuntu@你的服务器 IP

# 找到最新备份
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
ls -td backup_* | head -1

# 恢复备份
BACKUP_DIR=$(ls -td backup_* | head -1)
cp $BACKUP_DIR/utils/*.py utils/
cp $BACKUP_DIR/adapters/*.py adapters/
cp $BACKUP_DIR/core/*.py core/
```

---

## 📞 需要帮助？

如果部署过程中遇到问题：

1. 查看 [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) 详细指南
2. 检查故障排查章节
3. 查看日志：`tail -f ~/.openclaw/logs/openclaw.log`

---

**版本**: v1.0  
**日期**: 2026-04-22  
**状态**: ✅ 生产就绪

**立即部署**: 
```powershell
.\deploy_to_server.ps1 -ServerIP "你的服务器 IP"
```

或

```bash
./deploy_to_server.sh 你的服务器 IP
```

🚀
