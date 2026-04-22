# 阶段 3 优化代码 - 部署清单

**部署日期**: 2026-04-22  
**部署目标**: 服务器 OpenClaw 环境  
**部署类型**: 增量更新（仅优化模块）

---

## 📦 需要部署的文件

### 核心模块（8 个文件）

| 文件 | 路径 | 说明 | 必须 |
|------|------|------|------|
| `cache.py` | `utils/cache.py` | 缓存系统 | ✅ |
| `performance_monitor.py` | `utils/performance_monitor.py` | 性能监控 | ✅ |
| `health_checker.py` | `utils/health_checker.py` | 健康检查 | ✅ |
| `memory_optimizer.py` | `utils/memory_optimizer.py` | 内存优化 | ✅ |
| `logger.py` | `utils/logger.py` | 日志系统 | ✅ |
| `base_tool_adapter.py` | `adapters/base_tool_adapter.py` | 基类适配器 | ✅ |
| `config_optimized.py` | `core/config_optimized.py` | 优化配置 | ✅ |
| `config_validation.py` | `core/config_validation.py` | 配置验证 | ✅ |

### 依赖检查

| 依赖 | 版本 | 检查命令 | 必须 |
|------|------|----------|------|
| `psutil` | >=5.9.0 | `pip3 show psutil` | ✅ |
| `pydantic` | >=2.0.0 | `pip3 show pydantic` | ✅ |
| `redis` | >=4.0.0 | `pip3 show redis` | ❌ (可选) |

---

## 🚀 部署步骤

### 步骤 1: 服务器连接

```bash
# SSH 连接
ssh ubuntu@your-server-ip
```

### 步骤 2: 依赖检查

```bash
# 检查 Python 版本
python3 --version  # 应该 >= 3.8

# 检查必需依赖
pip3 show psutil
pip3 show pydantic

# 如果缺少，安装依赖
pip3 install psutil pydantic
```

### 步骤 3: 备份现有代码

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 创建备份目录
mkdir -p backup_$(date +%Y%m%d_%H%M%S)

# 备份关键文件
cp utils/*.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp adapters/*.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp core/*.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
```

### 步骤 4: 上传新代码

#### 方法 A: 使用 SCP（推荐）

```bash
# 从本地上传
# 在本地执行，不在服务器

# 上传 utils 目录
scp utils/cache.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/performance_monitor.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/health_checker.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/memory_optimizer.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
scp utils/logger.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/

# 上传 adapters 目录
scp adapters/base_tool_adapter.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/

# 上传 core 目录
scp core/config_optimized.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/core/
scp core/config_validation.py ubuntu@your-server-ip:~/.openclaw/workspace/skills/intelligent-test-orchestrator/core/
```

#### 方法 B: 使用 Git（如果已配置）

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 拉取最新代码
git pull origin main

# 或者切换到特定分支
git checkout phase3-optimization
```

#### 方法 C: 手动复制（备选）

```bash
# 在服务器上创建临时目录
mkdir -p /tmp/optimization_files

# 通过任何方式上传文件到 /tmp/optimization_files
# (FTP、SFTP、或者直接粘贴)

# 然后复制到目标位置
cp /tmp/optimization_files/cache.py ~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
cp /tmp/optimization_files/performance_monitor.py ~/.openclaw/workspace/skills/intelligent-test-orchestrator/utils/
# ... 其他文件
```

### 步骤 5: 验证文件完整性

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 检查文件是否存在
ls -lh utils/cache.py
ls -lh utils/performance_monitor.py
ls -lh utils/health_checker.py
ls -lh utils/memory_optimizer.py
ls -lh adapters/base_tool_adapter.py
ls -lh core/config_optimized.py
ls -lh core/config_validation.py

# 检查文件大小（应该与本地一致）
wc -l utils/*.py adapters/*.py core/*.py
```

### 步骤 6: 测试导入

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 测试 Python 导入
python3 -c "from utils.cache import MemoryCache; print('✅ 缓存系统导入成功')"
python3 -c "from utils.performance_monitor import PerformanceMonitor; print('✅ 性能监控导入成功')"
python3 -c "from utils.health_checker import HealthChecker; print('✅ 健康检查导入成功')"
python3 -c "from utils.memory_optimizer import VulnerabilityStream; print('✅ 内存优化导入成功')"
python3 -c "from adapters.base_tool_adapter import BaseToolAdapter; print('✅ 基类适配器导入成功')"
```

### 步骤 7: 运行快速测试

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行简单测试
python3 -c "
from utils.cache import MemoryCache
cache = MemoryCache()
cache.set('test', 'value')
assert cache.get('test') == 'value'
print('✅ 缓存功能测试通过')
"

# 测试性能监控
python3 -c "
from utils.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
report = monitor.get_report()
print('✅ 性能监控测试通过')
"
```

### 步骤 8: 重启 OpenClaw（如果需要）

```bash
# 检查 OpenClaw 进程
ps aux | grep openclaw

# 如果需要重启，先停止
# (找到进程 ID 并 kill)
kill <pid>

# 重新启动 OpenClaw
cd ~/.openclaw
./start.sh  # 或者使用实际的启动命令
```

---

## ✅ 验证清单

### 基础验证

- [ ] 所有 8 个文件已上传
- [ ] 文件大小与本地一致
- [ ] Python 导入无错误
- [ ] 依赖包已安装

### 功能验证

- [ ] 缓存系统工作正常
- [ ] 性能监控工作正常
- [ ] 健康检查工作正常
- [ ] 内存优化工作正常

### 集成验证

- [ ] OpenClaw 能正常加载
- [ ] 智能编排功能正常
- [ ] 进度反馈正常显示
- [ ] 无异常日志

---

## 🔧 故障排查

### 问题 1: 导入错误

```bash
# 错误：ModuleNotFoundError
# 解决：检查 Python 路径
export PYTHONPATH=~/.openclaw/workspace/skills/intelligent-test-orchestrator:$PYTHONPATH
```

### 问题 2: 依赖缺失

```bash
# 错误：No module named 'psutil'
# 解决：安装依赖
pip3 install psutil pydantic
```

### 问题 3: 文件权限

```bash
# 错误：Permission denied
# 解决：修正权限
chmod 644 utils/*.py adapters/*.py core/*.py
chown ubuntu:ubuntu utils/*.py adapters/*.py core/*.py
```

### 问题 4: OpenClaw 未加载新代码

```bash
# 解决：清除 Python 缓存
find ~/.openclaw/workspace/skills/intelligent-test-orchestrator -name "*.pyc" -delete
find ~/.openclaw/workspace/skills/intelligent-test-orchestrator -name "__pycache__" -type d -exec rm -rf {} +

# 重启 OpenClaw
```

---

## 📊 部署后验证

### 本地测试（部署前）

```bash
# 在本地运行测试
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
python test\test_phase3_optimization.py
python test\test_e2e_optimization.py
```

### 服务器测试（部署后）

```bash
# 在服务器上运行测试
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase3_optimization.py
python3 test/test_e2e_optimization.py
```

### 性能对比

记录部署前后的性能指标：

| 指标 | 部署前 | 部署后 | 目标 |
|------|--------|--------|------|
| 缓存加速比 | - | ? | >100x |
| 内存占用 | ? | ? | <500MB |
| 全流程时间 | ? | ? | <30 分钟 |

---

## 📝 回滚方案

如果部署后出现问题，执行回滚：

```bash
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 找到最新的备份
ls -lt backup_* | head -1

# 恢复备份
cp backup_*/utils/*.py utils/
cp backup_*/adapters/*.py adapters/
cp backup_*/core/*.py core/

# 重启 OpenClaw
```

---

## 🎯 成功标准

部署成功的标志：

- ✅ 所有文件正确上传
- ✅ Python 导入无错误
- ✅ 功能测试全部通过
- ✅ OpenClaw 正常运行
- ✅ 智能编排功能正常
- ✅ 性能指标达标

---

**部署负责人**: ___________  
**部署时间**: ___________  
**验证人**: ___________  
**部署状态**: ⏳ 待开始 / ✅ 成功 / ❌ 失败
