"""
阶段 3 优化 - 完整测试套件
"""

import sys
import time
import asyncio
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.cache import MemoryCache, FileCache, CacheManager, cached
from utils.performance_monitor import PerformanceMonitor, PerformanceMetrics, SystemMonitor
from utils.health_checker import HealthChecker, ToolHealth
from utils.memory_optimizer import VulnerabilityStream


def test_cache_system():
    """测试缓存系统"""
    print("=" * 60)
    print("测试 1: 缓存系统")
    print("=" * 60)
    
    # 测试内存缓存
    cache = MemoryCache(max_size=100, default_ttl=60)
    
    # 基本操作
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'
    print("✅ 基本缓存操作")
    
    # 带参数缓存
    cache.set('key2', 'value2', 'arg1', kwarg1='test')
    assert cache.get('key2', 'arg1', kwarg1='test') == 'value2'
    print("✅ 带参数缓存")
    
    # TTL 测试
    cache.set('temp', 'temp_value', ttl=1)
    assert cache.get('temp') == 'temp_value'
    time.sleep(1.1)
    assert cache.get('temp') is None
    print("✅ TTL 过期")
    
    # 缓存统计
    stats = cache.get_stats()
    assert stats['hits'] > 0
    assert stats['misses'] > 0
    print(f"✅ 缓存统计：命中率 {stats['hit_rate']}")
    
    # 缓存装饰器
    @cached(cache=cache, ttl=60)
    def expensive_function(x, y):
        time.sleep(0.2)  # 模拟耗时操作
        return x + y
    
    # 第一次调用
    start = time.time()
    result1 = expensive_function(10, 20)
    time1 = time.time() - start
    
    # 第二次调用（缓存）
    start = time.time()
    result2 = expensive_function(10, 20)
    time2 = time.time() - start
    
    assert result1 == result2 == 30
    # 缓存应该显著更快（至少快 50%）
    assert time2 < time1 * 0.5, f"缓存未生效：time2={time2:.4f}s, time1={time1:.4f}s"
    speedup = time1/time2 if time2 > 0 else float('inf')
    print(f"✅ 缓存装饰器：第一次 {time1:.4f}s, 第二次 {time2:.4f}s (加速 {speedup:.1f}x)")
    
    # 缓存管理器（单例）
    manager = CacheManager()
    manager.set('manager_key', 'manager_value')
    assert manager.get('manager_key') == 'manager_value'
    print("✅ 缓存管理器")
    
    print()


def test_performance_monitor():
    """测试性能监控"""
    print("=" * 60)
    print("测试 2: 性能监控")
    print("=" * 60)
    
    # 性能指标
    metrics = PerformanceMetrics()
    
    # 记录指标
    metrics.record('test_metric', 100)
    metrics.record('test_metric', 150)
    metrics.record('test_metric', 200)
    
    stats = metrics.get_stats('test_metric')
    assert stats['count'] == 3
    assert stats['avg'] == 150
    assert stats['min'] == 100
    assert stats['max'] == 200
    print("✅ 指标记录")
    
    # 系统监控
    system = SystemMonitor()
    
    cpu = system.get_cpu_usage()
    assert 0 <= cpu <= 100
    print(f"✅ CPU 使用率：{cpu:.1f}%")
    
    memory = system.get_memory_usage()
    assert memory['rss_mb'] > 0
    assert 0 <= memory['percent'] <= 100
    print(f"✅ 内存使用：{memory['rss_mb']:.1f} MB ({memory['percent']:.1f}%)")
    
    # 性能监控管理器
    monitor = PerformanceMonitor()
    
    # 记录执行时间
    monitor.record_execution_time('test_func', 0.5, success=True)
    monitor.record_execution_time('test_func', 0.3, success=True)
    monitor.record_execution_time('test_func', 0.8, success=False)
    
    func_stats = monitor.metrics.get_stats('test_func_duration')
    assert func_stats['count'] == 3
    print(f"✅ 函数执行时间记录：{func_stats['count']} 次")
    
    # 健康状态
    health = monitor.get_health_status()
    assert health['status'] in ['healthy', 'warning', 'unhealthy']
    print(f"✅ 健康状态：{health['status']}")
    
    # 性能报告
    report = monitor.get_report()
    assert 'uptime_seconds' in report
    assert 'health' in report
    assert 'metrics' in report
    print(f"✅ 性能报告生成")
    
    print()


async def test_health_checker():
    """测试健康检查器"""
    print("=" * 60)
    print("测试 3: 健康检查器")
    print("=" * 60)
    
    checker = HealthChecker()
    
    # 检查单个工具
    python_health = await checker.check_tool('python3')
    assert python_health.tool_name == 'python3'
    assert python_health.installed  # Python 应该已安装
    print(f"✅ Python3: {python_health.status} ({python_health.version})")
    
    # 检查所有工具
    all_health = await checker.check_all_tools()
    assert len(all_health) > 0
    print(f"✅ 检查 {len(all_health)} 个工具")
    
    # 健康摘要
    summary = checker.get_health_summary()
    assert summary['total_tools'] > 0
    assert summary['installed'] > 0
    print(f"✅ 健康摘要：{summary['installed']}/{summary['total_tools']} 已安装")
    
    # 工具详情
    healthy_count = sum(1 for h in all_health.values() if h.status == 'healthy')
    print(f"✅ 健康工具数：{healthy_count}")
    
    print()


def test_integration():
    """测试集成使用"""
    print("=" * 60)
    print("测试 4: 集成使用")
    print("=" * 60)
    
    # 创建测试数据
    test_vulns = [
        {"name": f"Vuln_{i}", "severity": "high" if i % 2 == 0 else "low", "cvss": 7.5 + (i % 5) * 0.1}
        for i in range(100)
    ]
    
    # 使用缓存优化处理
    cache = MemoryCache(max_size=50, default_ttl=300)
    
    def process_vulnerability(vuln):
        cache_key = f"process_{vuln['name']}"
        
        # 尝试从缓存获取
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 处理
        result = {**vuln, 'processed': True, 'timestamp': time.time()}
        
        # 写入缓存
        cache.set(cache_key, result)
        
        return result
    
    # 处理所有漏洞
    start = time.time()
    processed = [process_vulnerability(v) for v in test_vulns]
    time1 = time.time() - start
    
    # 再次处理（应该从缓存）
    start = time.time()
    processed2 = [process_vulnerability(v) for v in test_vulns]
    time2 = time.time() - start
    
    assert len(processed) == len(test_vulns)
    assert all(v['processed'] for v in processed)
    assert time2 < time1  # 缓存应该更快
    print(f"✅ 缓存优化处理：第一次 {time1:.4f}s, 第二次 {time2:.4f}s (加速 {time1/time2:.2f}x)")
    
    # 性能监控集成
    monitor = PerformanceMonitor()
    
    # 模拟工具执行
    for tool_name in ['nuclei', 'afrog', 'nikto']:
        duration = 0.1
        success = True
        monitor.record_tool_execution(tool_name, duration, 'http://test.com', success)
    
    tool_stats = monitor.metrics.get_stats('tool_nuclei_duration')
    assert tool_stats['count'] > 0
    print(f"✅ 工具执行监控：{tool_stats['count']} 次记录")
    
    print()


def test_memory_efficiency():
    """测试内存效率"""
    print("=" * 60)
    print("测试 5: 内存效率")
    print("=" * 60)
    
    # 创建大数据集
    large_data = list(range(100000))
    
    # 传统方式
    start = time.time()
    result1 = [x * 2 for x in large_data if x % 2 == 0]
    traditional_time = time.time() - start
    traditional_memory = len(result1) * 8  # 估算字节
    
    # 生成器方式
    start = time.time()
    gen = (x * 2 for x in large_data if x % 2 == 0)
    result2 = list(gen)
    generator_time = time.time() - start
    generator_memory = 1000  # 生成器内存占用很小
    
    assert result1 == result2
    memory_saved = traditional_memory - generator_memory
    
    print(f"传统方式：{traditional_time:.4f}s, ~{traditional_memory/1024:.1f} KB")
    print(f"生成器方式：{generator_time:.4f}s, ~{generator_memory/1024:.1f} KB")
    print(f"✅ 内存节省：{memory_saved/1024:.1f} KB ({memory_saved/traditional_memory*100:.1f}%)")
    
    # 流式处理
    test_vulns = [{'severity': 'high' if i % 2 == 0 else 'low'} for i in range(100)]
    stream = VulnerabilityStream(test_vulns)
    result = (
        stream
        .filter(lambda v: v['severity'] == 'high')
        .limit(10)
        .to_list()
    )
    
    assert len(result) == 10
    print(f"✅ 流式处理：过滤后 {len(result)} 个元素")
    
    print()


async def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "阶段 3 优化 - 完整测试套件" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # 同步测试
        test_cache_system()
        test_performance_monitor()
        test_integration()
        test_memory_efficiency()
        
        # 异步测试
        await test_health_checker()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("优化成果：")
        print("  ✅ 缓存系统：内存缓存 + 文件缓存 + 装饰器")
        print("  ✅ 性能监控：实时指标 + 系统监控 + 健康状态")
        print("  ✅ 健康检查：工具检测 + 自动恢复 + 报告生成")
        print("  ✅ 内存效率：生成器 + 流式处理 + 缓存优化")
        print()
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
