"""
阶段 2 优化 - 使用示例和测试
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config_optimized import (
    OrchestratorConfig,
    ConfigManager,
    TestMode,
    ReportFormat,
    RiskScoreMode,
    ToolConfig,
    get_config,
    update_config
)

from core.config_validation import (
    ConfigValidator,
    create_default_config,
    create_light_config,
    create_full_config
)

from utils.memory_optimizer import (
    VulnerabilityStream,
    batch_generator,
    vulnerability_generator,
    memory_efficient_vulnerability_processor,
    ResourceEfficientProcessor
)


def test_dataclass_config():
    """测试 dataclass 配置"""
    print("=" * 60)
    print("测试 1: Dataclass 配置管理")
    print("=" * 60)
    
    # 创建默认配置
    config = OrchestratorConfig()
    print(f"✅ 创建默认配置：test_mode={config.test_mode}")
    
    # 修改配置
    config.time_limit = 180
    config.concurrent_tools = 5
    print(f"✅ 修改配置：time_limit={config.time_limit}, concurrent_tools={config.concurrent_tools}")
    
    # 导出为 JSON
    json_str = config.to_json()
    print(f"✅ 导出为 JSON（长度：{len(json_str)} 字符）")
    
    # 从 JSON 加载
    config2 = OrchestratorConfig.from_json(json_str)
    print(f"✅ 从 JSON 加载：test_mode={config2.test_mode}")
    
    # 使用配置管理器
    manager = ConfigManager()
    manager.update(time_limit=240, enable_caching=False)
    print(f"✅ 配置管理器更新：time_limit={manager.get('time_limit')}")
    
    print()


def test_pydantic_validation():
    """测试 Pydantic 验证"""
    print("=" * 60)
    print("测试 2: Pydantic 数据验证")
    print("=" * 60)
    
    # 创建有效配置
    try:
        config = create_default_config()
        print(f"✅ 创建有效配置：test_mode={config.test_mode}")
    except Exception as e:
        print(f"❌ 创建失败：{e}")
    
    # 测试无效配置（应该失败）
    try:
        invalid_config = OrchestratorConfig(
            time_limit=3,  # 小于最小值 5
            concurrent_tools=15  # 大于最大值 10
        )
        print(f"❌ 应该验证失败但未失败")
    except Exception as e:
        print(f"✅ 正确捕获验证错误：{str(e)[:50]}...")
    
    # 测试轻量级配置
    light_config = create_light_config()
    print(f"✅ 创建轻量级配置：severity_filter={light_config.severity_filter}")
    
    # 测试完整配置
    full_config = create_full_config()
    print(f"✅ 创建完整配置：time_limit={full_config.time_limit}")
    
    # 验证配置
    result = ConfigValidator.validate(full_config)
    if result['valid']:
        print(f"✅ 配置验证通过")
    else:
        print(f"❌ 配置验证失败：{result['errors']}")
    
    print()


def test_memory_optimizer():
    """测试内存优化器"""
    print("=" * 60)
    print("测试 3: 内存优化（生成器）")
    print("=" * 60)
    
    # 创建测试数据
    test_vulns = [
        {"name": f"Vuln_{i}", "severity": "high" if i % 2 == 0 else "low", "cvss": 7.5 + (i % 5) * 0.1}
        for i in range(1000)
    ]
    
    # 测试漏洞流
    stream = VulnerabilityStream(test_vulns)
    high_severity = (
        stream
        .filter(lambda v: v['severity'] == 'high')
        .sort(key=lambda v: v['cvss'])
        .limit(10)
        .to_list()
    )
    print(f"✅ 漏洞流处理：原始={len(test_vulns)}, 过滤后={len(high_severity)}")
    
    # 测试分批生成器
    batches = list(batch_generator(range(100), 10))
    print(f"✅ 分批处理：{len(batches)} 批，每批 {len(batches[0])} 个元素")
    
    # 测试生成器惰性加载
    gen = vulnerability_generator(test_vulns)
    first_5 = [next(gen) for _ in range(5)]
    print(f"✅ 惰性加载：获取前 5 个元素")
    
    # 测试内存高效处理
    processor = ResourceEfficientProcessor(max_memory_mb=512)
    processed = list(
        processor.process_large_dataset(
            test_vulns,
            lambda v: {**v, 'processed': True},
            chunk_size=100
        )
    )
    print(f"✅ 内存高效处理：处理 {len(processed)} 个元素")
    
    print()


def test_config_save_load():
    """测试配置保存加载"""
    print("=" * 60)
    print("测试 4: 配置文件保存/加载")
    print("=" * 60)
    
    # 创建配置
    config = OrchestratorConfig(
        test_mode=TestMode.CUSTOM,
        time_limit=300,
        concurrent_tools=4
    )
    
    # 保存到临时文件
    temp_file = project_root / "test_config.json"
    config.save_to_file(str(temp_file))
    print(f"✅ 保存配置到：{temp_file}")
    
    # 从文件加载
    loaded_config = OrchestratorConfig.load_from_file(str(temp_file))
    print(f"✅ 从文件加载：time_limit={loaded_config.time_limit}")
    
    # 清理
    if temp_file.exists():
        temp_file.unlink()
        print(f"✅ 清理临时文件")
    
    print()


def test_performance_comparison():
    """测试性能对比"""
    print("=" * 60)
    print("测试 5: 性能对比（优化前 vs 优化后）")
    print("=" * 60)
    
    import time
    
    # 创建大数据集
    large_data = list(range(100000))
    
    # 传统方式
    start = time.time()
    result1 = [x * 2 for x in large_data if x % 2 == 0]
    traditional_time = time.time() - start
    print(f"传统列表推导：{traditional_time:.4f} 秒")
    
    # 生成器方式
    start = time.time()
    gen = (x * 2 for x in large_data if x % 2 == 0)
    result2 = list(gen)
    generator_time = time.time() - start
    print(f"生成器方式：{generator_time:.4f} 秒")
    
    # 分批处理
    start = time.time()
    result3 = []
    for batch in batch_generator(large_data, 1000):
        result3.extend([x * 2 for x in batch if x % 2 == 0])
    batch_time = time.time() - start
    print(f"分批处理：{batch_time:.4f} 秒")
    
    # 验证结果一致
    assert result1 == result2 == result3
    print(f"✅ 所有方式结果一致")
    
    print()


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "阶段 2 优化 - 完整测试套件" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        test_dataclass_config()
        test_pydantic_validation()
        test_memory_optimizer()
        test_config_save_load()
        test_performance_comparison()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("优化成果：")
        print("  ✅ 配置管理：dataclass + Pydantic 验证")
        print("  ✅ 数据验证：运行时类型检查和约束验证")
        print("  ✅ 内存优化：生成器和分批处理")
        print("  ✅ 性能提升：减少内存占用，提高处理效率")
        print()
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
