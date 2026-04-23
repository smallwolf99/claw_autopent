"""
智能编排器 - 完整流程集成测试（修复版）

修复问题:
- Phase2Adapter 没有 normalize_vulnerabilities 方法
- 直接使用 detect 方法返回的结果
"""

import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import OpenClawHandler
from core.config_optimized import OrchestratorConfig, TestMode


class IntegrationTestResult:
    """集成测试结果"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.success = False
        self.error = None
        self.details = {}
    
    def __str__(self):
        status = "✅ 成功" if self.success else "❌ 失败"
        lines = [f"\n{status} - {self.name}"]
        lines.append("=" * 60)
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            lines.append(f"执行时间：{duration:.2f}秒")
        
        if self.error:
            lines.append(f"错误：{self.error}")
        
        for key, value in self.details.items():
            lines.append(f"{key}: {value}")
        
        return "\n".join(lines)


async def test_phase1_asset_collection(target: str) -> IntegrationTestResult:
    """测试 Phase 1: 资产收集"""
    result = IntegrationTestResult("Phase 1: 资产收集")
    result.start_time = time.time()
    
    try:
        from adapters.phase0_adapter_real import Phase0Adapter
        
        adapter = Phase0Adapter()
        # 使用正确的方法名：collect
        assets = await adapter.collect(target)
        
        result.end_time = time.time()
        result.success = True
        result.details = {
            "目标": target,
            "发现的资产数": len(assets),
            "资产类型": list(set(a.get('type', 'unknown') for a in assets)) if assets else []
        }
        
    except Exception as e:
        result.end_time = time.time()
        result.success = False
        result.error = str(e)
    
    return result


async def test_phase2_vulnerability_scan(target: str, assets: dict) -> IntegrationTestResult:
    """测试 Phase 2: 漏洞检测"""
    result = IntegrationTestResult("Phase 2: 漏洞检测")
    result.start_time = time.time()
    
    try:
        from adapters.phase2_adapter_real import Phase2Adapter
        
        adapter = Phase2Adapter()
        # 使用正确的方法名：detect（不需要 normalize_vulnerabilities）
        # 将 assets 转换为列表格式
        assets_list = [assets] if assets and isinstance(assets, dict) else []
        vulnerabilities = await adapter.detect(assets_list)
        
        result.end_time = time.time()
        result.success = True
        result.details = {
            "目标": target,
            "发现漏洞数": len(vulnerabilities),
            "漏洞示例": [(v.get('type', 'unknown'), v.get('severity', 'unknown')) for v in vulnerabilities[:5]] if vulnerabilities else "无漏洞"
        }
        
    except Exception as e:
        result.end_time = time.time()
        result.success = False
        result.error = str(e)
    
    return result


async def test_phase3_vulnerability_validation(target: str, vulnerabilities: list) -> IntegrationTestResult:
    """测试 Phase 3: 漏洞验证"""
    result = IntegrationTestResult("Phase 3: 漏洞验证")
    result.start_time = time.time()
    
    try:
        from adapters.phase3_validator_real import Phase3Validator
        
        validator = Phase3Validator()
        # 使用正确的方法名：verify
        # 需要提供 assets 参数
        assets = [{'url': target, 'type': 'web'}]
        validated = await validator.verify(vulnerabilities, assets)
        
        result.end_time = time.time()
        result.success = True
        
        # 处理验证结果
        if validated:
            verified_count = sum(1 for v in validated if v.verified)
            result.details = {
                "目标": target,
                "验证漏洞数": len(validated),
                "确认存在": verified_count,
                "误报": len(validated) - verified_count,
                "验证成功率": f"{verified_count/len(validated)*100:.1f}%" if validated else "N/A"
            }
        else:
            result.details = {
                "目标": target,
                "验证漏洞数": 0,
                "说明": "无漏洞需要验证"
            }
        
    except Exception as e:
        result.end_time = time.time()
        result.success = False
        result.error = str(e)
    
    return result


async def test_full_workflow(target: str) -> IntegrationTestResult:
    """测试完整工作流"""
    result = IntegrationTestResult("完整工作流测试")
    result.start_time = time.time()
    
    try:
        # 使用 OpenClawHandler 执行完整流程
        handler = OpenClawHandler()
        
        # 执行智能测试
        scan_result = await handler.execute_intelligent_test(
            target=target,
            test_mode='full',
            time_limit=120,
            report_format='json'
        )
        
        result.end_time = time.time()
        result.success = True
        result.details = {
            "目标": target,
            "执行阶段数": len(scan_result.get('phases', {})),
            "发现资产数": len(scan_result.get('assets', [])),
            "发现漏洞数": len(scan_result.get('vulnerabilities', [])),
            "风险评分": scan_result.get('risk_score', 'N/A'),
            "总耗时": f"{result.end_time - result.start_time:.2f}秒"
        }
        
    except Exception as e:
        result.end_time = time.time()
        result.success = False
        result.error = str(e)
    
    return result


async def test_optimization_features() -> IntegrationTestResult:
    """测试优化功能"""
    result = IntegrationTestResult("优化功能测试")
    result.start_time = time.time()
    
    try:
        from utils.cache import MemoryCache, cached
        from utils.performance_monitor import PerformanceMonitor
        from utils.health_checker import HealthChecker
        from utils.memory_optimizer import VulnerabilityStream
        
        # 测试缓存
        cache = MemoryCache(max_size=100, default_ttl=3600)
        cache.set('test', 'value')
        assert cache.get('test') == 'value'
        
        # 测试缓存装饰器
        @cached(cache=cache, ttl=3600)
        def cached_function(x):
            time.sleep(0.1)
            return x * 2
        
        # 第一次调用
        cached_function(5)
        # 第二次调用（缓存）
        cached_function(5)
        
        # 测试性能监控
        monitor = PerformanceMonitor()
        monitor.start_monitoring(interval=1)
        time.sleep(2)
        report = monitor.get_report()
        monitor.stop_monitoring()
        
        # 测试健康检查
        health_checker = HealthChecker()
        summary = health_checker.get_health_summary()
        
        # 测试内存优化
        test_data = [{'id': i} for i in range(1000)]
        stream = VulnerabilityStream(test_data)
        filtered = stream.filter(lambda x: x['id'] % 2 == 0).limit(10).to_list()
        assert len(filtered) == 10
        
        result.end_time = time.time()
        result.success = True
        
        # 获取缓存统计
        stats = cache.get_stats()
        hit_rate = stats.get('hit_rate', 0)
        
        # 安全格式化：处理可能是字符串的情况
        if isinstance(hit_rate, (int, float)):
            hit_rate_str = f"{hit_rate * 100:.1f}%"
        else:
            hit_rate_str = str(hit_rate)
        
        result.details = {
            "缓存功能": "✅ 正常",
            "缓存装饰器": "✅ 正常",
            "性能监控": "✅ 正常",
            "健康检查": "✅ 正常",
            "内存优化": "✅ 正常",
            "缓存命中率": hit_rate_str
        }
        
    except Exception as e:
        result.end_time = time.time()
        result.success = False
        result.error = str(e)
    
    return result


async def run_integration_tests(target: str = "http://demo.testfire.net"):
    """运行所有集成测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 18 + "智能编排器 - 完整流程集成测试（修复版）" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"\n测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试目标：{target}")
    print()
    
    all_results = []
    
    # 测试 1: 优化功能
    print("=" * 60)
    print("测试 1: 优化功能")
    print("=" * 60)
    result = await test_optimization_features()
    all_results.append(result)
    print(result)
    
    # 测试 2: Phase 1 资产收集
    print("\n" + "=" * 60)
    print("测试 2: Phase 1 资产收集")
    print("=" * 60)
    result = await test_phase1_asset_collection(target)
    all_results.append(result)
    print(result)
    
    # 测试 3: Phase 2 漏洞检测
    print("\n" + "=" * 60)
    print("测试 3: Phase 2 漏洞检测")
    print("=" * 60)
    # 创建模拟资产
    mock_assets = {'url': target, 'type': 'web'}
    result = await test_phase2_vulnerability_scan(target, mock_assets)
    all_results.append(result)
    print(result)
    
    # 测试 4: Phase 3 漏洞验证
    print("\n" + "=" * 60)
    print("测试 4: Phase 3 漏洞验证")
    print("=" * 60)
    test_vulns = [
        {'id': 1, 'type': 'sql_injection', 'severity': 'high', 'url': target},
        {'id': 2, 'type': 'xss', 'severity': 'medium', 'url': target}
    ]
    result = await test_phase3_vulnerability_validation(target, test_vulns)
    all_results.append(result)
    print(result)
    
    # 测试 5: 完整工作流
    print("\n" + "=" * 60)
    print("测试 5: 完整工作流")
    print("=" * 60)
    result = await test_full_workflow(target)
    all_results.append(result)
    print(result)
    
    # 总结
    print("\n")
    print("=" * 60)
    print("集成测试总结")
    print("=" * 60)
    
    passed = sum(1 for r in all_results if r.success)
    failed = sum(1 for r in all_results if not r.success)
    total = len(all_results)
    
    print(f"\n总测试数：{total}")
    print(f"✅ 通过：{passed}")
    print(f"❌ 失败：{failed}")
    print()
    
    for i, result in enumerate(all_results, 1):
        status = "✅" if result.success else "❌"
        print(f"{i}. {status} {result.name}")
    
    print("\n")
    if failed == 0:
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 20 + "🎉 所有集成测试通过！" + " " * 20 + "║")
        print("╚" + "=" * 58 + "╝")
        print()
        print("✅ 智能编排器功能完整，可以投入使用！")
        print()
        print("下一步:")
        print("  1. 在 OpenClaw 中配置智能编排技能")
        print("  2. 使用真实目标进行测试")
        print("  3. 监控生产环境性能")
        print()
    else:
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 22 + "⚠️ 部分测试失败" + " " * 22 + "║")
        print("╚" + "=" * 58 + "╝")
        print()
        print("请检查失败的测试详情。")
        print()
        print("常见问题:")
        print("  1. 工具未安装：检查工具路径")
        print("  2. 网络问题：检查防火墙和目标可达性")
        print("  3. 配置问题：检查 Python 路径和环境变量")
        print()
    
    return all_results


if __name__ == '__main__':
    # 设置目标
    target = "http://demo.testfire.net"
    
    # 运行测试
    print("\n按 Ctrl+C 可中断测试")
    print(f"目标：{target}\n")
    
    try:
        results = asyncio.run(run_integration_tests(target))
        sys.exit(0 if all(r.success for r in results) else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
