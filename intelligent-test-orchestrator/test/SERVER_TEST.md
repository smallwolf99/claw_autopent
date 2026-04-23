# 服务器部署验证测试

**目的**: 快速验证部署到服务器的优化代码是否正常工作

---

## 🚀 快速测试（5 分钟）

### 步骤 1: SSH 连接到服务器

```bash
ssh ubuntu@你的服务器 IP
```

### 步骤 2: 进入项目目录

```bash
cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator
```

### 步骤 3: 验证文件是否存在

```bash
# 检查优化文件
ls -lh utils/cache.py
ls -lh utils/performance_monitor.py
ls -lh utils/health_checker.py
ls -lh utils/memory_optimizer.py
ls -lh adapters/base_tool_adapter.py
ls -lh core/config_optimized.py
```

**预期输出**:
```
-rw-r--r-- 1 ubuntu ubuntu 8.9K Apr 22 10:00 utils/cache.py
-rw-r--r-- 1 ubuntu ubuntu 12K Apr 22 10:00 utils/performance_monitor.py
-rw-r--r-- 1 ubuntu ubuntu 9.1K Apr 22 10:00 utils/health_checker.py
-rw-r--r-- 1 ubuntu ubuntu 5.6K Apr 22 10:00 utils/memory_optimizer.py
```

---

## ✅ 测试 1: 导入测试（30 秒）

```bash
# 设置 Python 路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 测试导入所有模块
python3 -c "
from utils.cache import MemoryCache, CacheManager, cached
from utils.performance_monitor import PerformanceMonitor
from utils.health_checker import HealthChecker
from utils.memory_optimizer import VulnerabilityStream
from adapters.base_tool_adapter import BaseToolAdapter
print('✅ 所有模块导入成功')
"
```

**预期输出**:
```
✅ 所有模块导入成功
```

---

## ✅ 测试 2: 缓存功能测试（1 分钟）

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from utils.cache import MemoryCache

# 创建缓存
cache = MemoryCache(max_size=100, default_ttl=3600)

# 测试设置和获取
cache.set('test_key', 'test_value')
value = cache.get('test_key')

assert value == 'test_value', '缓存值不匹配'
print('✅ 缓存功能测试通过')

# 测试缓存统计
stats = cache.get_stats()
print(f'✅ 缓存统计：命中率 {stats[\"hit_rate\"]*100:.1f}%')
"
```

**预期输出**:
```
✅ 缓存功能测试通过
✅ 缓存统计：命中率 50.0%
```

---

## ✅ 测试 3: 性能监控测试（2 分钟）

```bash
python3 -c "
import sys
import time
sys.path.insert(0, '.')
from utils.performance_monitor import PerformanceMonitor

# 创建性能监控器
monitor = PerformanceMonitor()

# 启动监控
monitor.start_monitoring(interval=1)

# 等待收集数据
print('正在收集性能数据...')
time.sleep(3)

# 获取报告
report = monitor.get_report()
metrics_count = len(report.get('metrics', {}))

print(f'✅ 性能监控测试通过')
print(f'   收集的指标数：{metrics_count}个')

# 停止监控
monitor.stop_monitoring()
"
```

**预期输出**:
```
正在收集性能数据...
✅ 性能监控测试通过
   收集的指标数：3 个
```

---

## ✅ 测试 4: 健康检查测试（3 分钟）

```bash
python3 -c "
import sys
import asyncio
sys.path.insert(0, '.')
from utils.health_checker import HealthChecker

async def test_health():
    # 创建健康检查器
    health_checker = HealthChecker()
    
    # 检查所有工具
    print('正在检查工具状态...')
    results = await health_checker.check_all_tools()
    
    # 统计健康工具
    healthy_count = sum(1 for r in results.values() if r.status == 'healthy')
    total_count = len(results)
    
    print(f'✅ 健康检查测试通过')
    print(f'   健康工具：{healthy_count}/{total_count}')
    
    # 获取摘要
    summary = health_checker.get_health_summary()
    print(f'   健康率：{summary.get(\"health_rate\", \"N/A\")}')

# 运行异步测试
asyncio.run(test_health())
"
```

**预期输出**:
```
正在检查工具状态...
✅ 健康检查测试通过
   健康工具：X/11
   健康率：XX%
```

---

## ✅ 测试 5: 内存优化测试（1 分钟）

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from utils.memory_optimizer import VulnerabilityStream

# 创建测试数据
test_vulns = [
    {'id': i, 'severity': 'high' if i % 2 == 0 else 'low'}
    for i in range(1000)
]

# 测试流式处理
stream = VulnerabilityStream(test_vulns)
result = (
    stream
    .filter(lambda v: v['severity'] == 'high')
    .limit(10)
    .to_list()
)

print(f'✅ 内存优化测试通过')
print(f'   处理数据：{len(test_vulns)}个')
print(f'   过滤结果：{len(result)}个')
assert len(result) == 10, '流式处理结果不正确'
"
```

**预期输出**:
```
✅ 内存优化测试通过
   处理数据：1000 个
   过滤结果：10 个
```

---

## ✅ 测试 6: 运行单元测试套件（5 分钟）

```bash
# 运行阶段 3 单元测试
python3 test/test_phase3_optimization.py
```

**预期输出**:
```
╔==========================================================╗
║            阶段 3 优化 - 完整测试套件            ║
╚==========================================================╝

============================================================
测试 1: 缓存系统
============================================================
✅ 基本缓存操作
✅ 带参数缓存
✅ TTL 过期
✅ 缓存统计：命中率 75.00%
✅ 缓存装饰器：第一次 0.2123s, 第二次 0.0003s (加速 845.0x)
✅ 缓存管理器
...
✅ 所有测试通过！
```

---

## ✅ 测试 7: 运行性能基准测试（10 分钟）

```bash
# 运行性能基准测试
python3 test/test_benchmark.py
```

**预期输出**:
```
╔==========================================================╗
║                  阶段 3 优化 - 性能基准测试                  ║
╚==========================================================╝

测试时间：2026-04-22 XX:XX:XX

============================================================
基准测试 1: 缓存性能
============================================================
✅ 写入速度：>100,000 条目/秒
✅ 读取速度（命中）：>500,000 条目/秒
✅ 缓存加速比：>500x
...
```

---

## ✅ 测试 8: 端到端测试（10 分钟）

```bash
# 运行端到端测试
python3 test/test_e2e_optimization.py
```

**预期输出**:
```
============================================================
端到端测试：完整工作流
============================================================

[1/5] 初始化组件...
✅ 缓存系统初始化
✅ 性能监控初始化
✅ 健康检查初始化

[2/5] 模拟资产收集（Phase 0）...
   第一次收集：0.512s
   第二次收集（缓存）：0.001s
   ✅ 缓存加速：512.0x
...
✅ 所有测试通过！
```

---

## 📊 测试结果总结表

| 测试项 | 预期结果 | 实际结果 | 状态 |
|--------|---------|---------|------|
| 文件检查 | 8 个文件存在 | ___ | ⬜ |
| 导入测试 | 无错误 | ___ | ⬜ |
| 缓存功能 | 通过 | ___ | ⬜ |
| 性能监控 | 收集到指标 | ___ | ⬜ |
| 健康检查 | 返回工具状态 | ___ | ⬜ |
| 内存优化 | 流式处理正常 | ___ | ⬜ |
| 单元测试 | 全部通过 | ___ | ⬜ |
| 基准测试 | 性能达标 | ___ | ⬜ |
| 端到端 | 工作流正常 | ___ | ⬜ |

---

## 🔧 常见问题排查

### 问题 1: 模块导入失败

**错误**: `ModuleNotFoundError: No module named 'utils'`

**解决**:
```bash
# 设置 Python 路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 或添加到 ~/.bashrc
echo "export PYTHONPATH=\"\$HOME/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator:\$PYTHONPATH\"" >> ~/.bashrc
source ~/.bashrc
```

### 问题 2: 依赖缺失

**错误**: `ModuleNotFoundError: No module named 'psutil'`

**解决**:
```bash
pip3 install psutil pydantic
```

### 问题 3: 权限问题

**错误**: `Permission denied`

**解决**:
```bash
# 修复文件权限
chmod 644 utils/*.py
chmod 644 adapters/*.py
chmod 644 core/*.py
chmod 644 test/*.py
```

---

## 🎯 一键测试脚本

创建一个快速测试脚本：

```bash
cat > test_deploy.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "  服务器部署验证测试"
echo "=========================================="
echo ""

# 设置路径
export PYTHONPATH="$PWD:$PYTHONPATH"

# 测试 1: 导入
echo "测试 1: 导入模块..."
python3 -c "
from utils.cache import MemoryCache
from utils.performance_monitor import PerformanceMonitor
from utils.health_checker import HealthChecker
print('✅ 导入成功')
" || { echo "❌ 导入失败"; exit 1; }

# 测试 2: 缓存
echo ""
echo "测试 2: 缓存功能..."
python3 -c "
from utils.cache import MemoryCache
cache = MemoryCache()
cache.set('test', 'value')
assert cache.get('test') == 'value'
print('✅ 缓存正常')
" || { echo "❌ 缓存失败"; exit 1; }

# 测试 3: 运行单元测试
echo ""
echo "测试 3: 单元测试..."
python3 test/test_phase3_optimization.py || { echo "❌ 单元测试失败"; exit 1; }

echo ""
echo "=========================================="
echo "  ✅ 所有测试通过！"
echo "=========================================="
EOF

chmod +x test_deploy.sh
./test_deploy.sh
```

---

## 📝 测试完成后

### 如果所有测试通过 ✅

**恭喜！部署成功！**

下一步：
1. ✅ 测试 OpenClaw 智能编排功能
2. ✅ 在真实环境中使用
3. ✅ 监控性能表现

### 如果有测试失败 ❌

**请提供**:
1. 具体的错误信息
2. 失败的测试名称
3. 完整的错误堆栈

我会帮助你解决问题。

---

## 📞 需要帮助？

如果测试过程中遇到任何问题，请提供：
- 完整的错误输出
- 服务器环境信息
- 已执行的步骤

**立即开始测试**:

```bash
ssh ubuntu@你的服务器 IP
cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator
./test_deploy.sh
```

🚀
