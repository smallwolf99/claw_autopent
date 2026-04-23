# 部署指南 - 阶段 3 优化代码

**版本**: v1.0  
**日期**: 2026-04-22  
**目标**: 将阶段 3 优化代码部署到 OpenClaw 服务器

---

## 📋 部署前准备

### 1. 确认服务器信息

你需要以下信息：
- **服务器 IP 地址**: 例如 `192.168.1.100` 或域名
- **SSH 用户名**: 通常是 `ubuntu`
- **SSH 密钥**: 已配置免密登录，或准备密码

### 2. 检查本地文件

确保以下文件存在：

```
d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\
├── utils\
│   ├── cache.py              ✅ 缓存系统
│   ├── performance_monitor.py ✅ 性能监控
│   ├── health_checker.py      ✅ 健康检查
│   ├── memory_optimizer.py    ✅ 内存优化
│   └── logger.py              ✅ 日志系统
├── adapters\
│   └── base_tool_adapter.py   ✅ 基类适配器
└── core\
    ├── config_optimized.py    ✅ 优化配置
    └── config_validation.py   ✅ 配置验证
```

### 3. 安装 SCP/SSH 工具

**Windows (PowerShell)**:
- 已内置 SSH 和 SCP（Windows 10+）
- 或者安装 Git Bash

**Linux/Mac**:
- 已内置 SSH 和 SCP

---

## 🚀 部署方法

### 方法 1: 使用 PowerShell 脚本（推荐 - Windows）

#### 步骤

1. **打开 PowerShell**
   ```powershell
   cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\test
   ```

2. **运行部署脚本**
   ```powershell
   .\deploy_to_server.ps1 -ServerIP "your-server-ip"
   ```
   
   示例：
   ```powershell
   .\deploy_to_server.ps1 -ServerIP "192.168.1.100"
   .\deploy_to_server.ps1 -ServerIP "demo.testfire.net" -ServerUser "ubuntu"
   ```

3. **等待完成**
   - 脚本会自动检查、备份、上传、验证
   - 大约需要 2-5 分钟

---

### 方法 2: 使用 Bash 脚本（推荐 - Linux/Mac）

#### 步骤

1. **打开终端**
   ```bash
   cd d:/TRAE/advanced-pentester-v1.2/intelligent-test-orchestrator/test
   ```

2. **添加执行权限**
   ```bash
   chmod +x deploy_to_server.sh
   ```

3. **运行部署脚本**
   ```bash
   ./deploy_to_server.sh your-server-ip
   ```
   
   示例：
   ```bash
   ./deploy_to_server.sh 192.168.1.100
   ./deploy_to_server.sh demo.testfire.net
   ```

---

### 方法 3: 手动部署（备选）

如果脚本无法使用，可以手动部署：

#### 步骤 1: SSH 连接服务器

```bash
ssh ubuntu@your-server-ip
```

#### 步骤 2: 创建备份

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
mkdir -p backup_$(date +%Y%m%d_%H%M%S)/{utils,adapters,core}
cp utils/*.py backup_*/utils/ 2>/dev/null || true
cp adapters/*.py backup_*/adapters/ 2>/dev/null || true
cp core/*.py backup_*/core/ 2>/dev/null || true
```

#### 步骤 3: 上传文件（从本地）

在**本地**执行（新开终端窗口）：

```bash
cd d:/TRAE/advanced-pentester-v1.2/intelligent-test-orchestrator

# 上传 utils 文件
scp utils/cache.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/performance_monitor.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/health_checker.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/memory_optimizer.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/logger.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/

# 上传 adapters 文件
scp adapters/base_tool_adapter.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 上传 core 文件
scp core/config_optimized.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/core/
scp core/config_validation.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/core/
```

#### 步骤 4: 验证文件

在**服务器**执行：

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查文件
ls -lh utils/*.py adapters/*.py core/*.py

# 测试导入
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 -c "from utils.cache import MemoryCache; print('✅ 成功')"
python3 -c "from utils.performance_monitor import PerformanceMonitor; print('✅ 成功')"
python3 -c "from utils.health_checker import HealthChecker; print('✅ 成功')"
```

---

## ✅ 部署后验证

### 1. 检查文件

```bash
# SSH 到服务器
ssh ubuntu@your-server-ip

# 进入目录
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查文件是否存在
ls -lh utils/cache.py
ls -lh utils/performance_monitor.py
ls -lh utils/health_checker.py
ls -lh utils/memory_optimizer.py
```

### 2. 测试导入

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"

python3 -c "
from utils.cache import MemoryCache
from utils.performance_monitor import PerformanceMonitor
from utils.health_checker import HealthChecker
from utils.memory_optimizer import VulnerabilityStream
print('✅ 所有模块导入成功')
"
```

### 3. 运行测试

```bash
# 运行单元测试
python3 test/test_phase3_optimization.py

# 运行端到端测试
python3 test/test_e2e_optimization.py
```

### 4. 验证 OpenClaw 集成

1. **重启 OpenClaw**（如果需要）:
   ```bash
   # 找到进程
   ps aux | grep openclaw
   
   # 重启
   # (根据实际安装方式重启)
   ```

2. **测试智能编排**:
   - 在 OpenClaw 中调用智能测试编排技能
   - 观察进度反馈是否正常
   - 检查日志是否有错误

---

## 🔧 故障排查

### 问题 1: SSH 连接失败

**症状**: `ssh: connect to host port 22: Connection timed out`

**解决**:
1. 检查服务器 IP 是否正确
2. 检查服务器是否在线：`ping your-server-ip`
3. 检查 SSH 配置：`ssh -v ubuntu@your-server-ip`
4. 配置 SSH 密钥（如果需要）

### 问题 2: SCP 上传失败

**症状**: `scp: Permission denied`

**解决**:
1. 检查用户名是否正确
2. 检查 SSH 密钥权限：`chmod 600 ~/.ssh/id_rsa`
3. 使用密码认证：`scp -o PreferredAuthentications=password`

### 问题 3: Python 导入错误

**症状**: `ModuleNotFoundError: No module named 'utils.cache'`

**解决**:
```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
export PYTHONPATH="$PWD:$PYTHONPATH"

# 或者添加到 ~/.bashrc
echo "export PYTHONPATH=\"$HOME/.openclaw/workspace/skills/intelligent-test-orchestrator:\$PYTHONPATH\"" >> ~/.bashrc
source ~/.bashrc
```

### 问题 4: 依赖缺失

**症状**: `No module named 'psutil'`

**解决**:
```bash
pip3 install psutil pydantic
```

### 问题 5: OpenClaw 未加载新代码

**症状**: 调用技能仍使用旧代码

**解决**:
1. 清理 Python 缓存：
   ```bash
   find ~/.openclaw/workspace/skills/intelligent-test-orchestrator -name "*.pyc" -delete
   find ~/.openclaw/workspace/skills/intelligent-test-orchestrator -name "__pycache__" -type d -exec rm -rf {} +
   ```

2. 重启 OpenClaw

---

## 🔄 回滚方案

如果部署后出现问题，可以快速回滚：

```bash
# SSH 到服务器
ssh ubuntu@your-server-ip

# 进入目录
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 找到最新备份
ls -lt backup_* | head -1

# 恢复备份
BACKUP_DIR=$(ls -td backup_* | head -1)
cp $BACKUP_DIR/utils/*.py utils/
cp $BACKUP_DIR/adapters/*.py adapters/
cp $BACKUP_DIR/core/*.py core/

# 重启 OpenClaw
```

---

## 📊 部署检查清单

部署前确认：

- [ ] 服务器 IP 地址已知
- [ ] SSH 连接正常
- [ ] 本地文件完整（8 个核心文件）
- [ ] 已安装 SCP/SSH 工具

部署中确认：

- [ ] 备份已创建
- [ ] 所有文件上传成功
- [ ] 文件验证通过
- [ ] Python 导入测试通过
- [ ] 功能测试通过

部署后确认：

- [ ] OpenClaw 正常运行
- [ ] 智能编排功能正常
- [ ] 进度反馈正常显示
- [ ] 无异常日志

---

## 📝 部署记录

**部署日期**: ___________  
**部署人**: ___________  
**服务器 IP**: ___________  
**部署版本**: Phase 3 Optimization  
**备份位置**: `backup_YYYYMMDD_HHMMSS`  

**验证结果**:
- [ ] 文件检查 ✅
- [ ] 导入测试 ✅
- [ ] 功能测试 ✅
- [ ] OpenClaw 集成 ✅

**备注**:
_________________________________
_________________________________

---

## 🎯 成功标准

部署成功的标志：

✅ 所有 8 个核心文件正确上传  
✅ Python 导入无错误  
✅ 功能测试全部通过  
✅ OpenClaw 正常运行  
✅ 智能编排功能正常  
✅ 性能指标达标（缓存加速 >100x）

---

**文档版本**: v1.0  
**最后更新**: 2026-04-22  
**维护者**: 开发团队
