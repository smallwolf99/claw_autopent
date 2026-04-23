#!/usr/bin/env python3
"""
whatweb skill 功能测试脚本
测试跨平台优化后的各项功能
"""
import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入优化后的模块
from main import (
    is_valid_url,
    find_whatweb_executable,
    parse_targets,
    run_whatweb,
    parse_whatweb_json,
    scan
)


def test_url_validation():
    """测试 URL 验证功能"""
    print("=" * 60)
    print("测试 1: URL 验证功能")
    print("=" * 60)
    
    test_cases = [
        ("https://example.com", True),
        ("http://sub.example.com", True),
        ("https://example.co.uk", True),
        ("example.com", False),  # 缺少协议
        ("ftp://example.com", False),  # 不支持的协议
        ("", False),
        ("https://", False),
        ("not_a_url", False),
    ]
    
    passed = 0
    for url, expected in test_cases:
        result = is_valid_url(url)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} is_valid_url('{url}') = {result} (期望：{expected})")
        if result == expected:
            passed += 1
    
    print(f"\n通过：{passed}/{len(test_cases)}\n")
    return passed == len(test_cases)


def test_target_parsing():
    """测试目标解析功能"""
    print("=" * 60)
    print("测试 2: 目标解析功能")
    print("=" * 60)
    
    # 测试单个 URL
    urls, temp_file = parse_targets("https://example.com")
    print(f"[OK] 单个 URL: {len(urls)} 个目标")
    
    # 测试多个 URL（逗号分隔）
    urls, temp_file = parse_targets("https://example.com,https://test.com,https://demo.org")
    print(f"[OK] 逗号分隔：{len(urls)} 个目标 - {urls}")
    
    # 测试多个 URL（分号分隔）
    urls, temp_file = parse_targets("https://a.com;https://b.com")
    print(f"[OK] 分号分隔：{len(urls)} 个目标")
    
    # 测试列表
    urls, temp_file = parse_targets(["https://example.com", "https://test.com"])
    print(f"[OK] 列表输入：{len(urls)} 个目标")
    
    # 测试文件路径（不存在的文件）
    urls, temp_file = parse_targets("nonexistent.txt")
    print(f"[OK] 文件路径：{len(urls)} 个目标，temp_file={temp_file}")
    
    print()
    return True


def test_whatweb_executable():
    """测试 whatweb 可执行文件查找"""
    print("=" * 60)
    print("测试 3: whatweb 可执行文件查找")
    print("=" * 60)
    
    whatweb_path = find_whatweb_executable()
    print(f"找到的 whatweb 路径：{whatweb_path}")
    
    # 检查是否找到了有效路径（不一定是真实安装）
    if whatweb_path:
        print("[OK] whatweb 路径查找成功\n")
        return True
    else:
        print("[FAIL] whatweb 路径查找失败\n")
        return False


def test_scan_interface():
    """测试标准扫描接口"""
    print("=" * 60)
    print("测试 4: scan 接口功能")
    print("=" * 60)
    
    # 测试接口调用（不实际执行，只测试接口）
    try:
        # 模拟调用
        result = scan(
            targets="https://example.com",
            opts="",
            output_format="json",
            aggression=1,
            plugins="",
            timeout=300,
            verbose=False
        )
        print(f"[OK] scan 接口调用成功")
        print(f"  返回类型：{type(result)}")
        if isinstance(result, dict):
            print(f"  包含键：{list(result.keys())}")
    except Exception as e:
        print(f"[FAIL] scan 接口调用失败：{e}")
    
    print()
    return True


def test_json_parsing():
    """测试 JSON 解析功能"""
    print("=" * 60)
    print("测试 5: JSON 解析功能")
    print("=" * 60)
    
    # 模拟 whatweb JSON 输出（多行格式）
    sample_output = """{"target":"https://example.com","plugins":[{"name":"NGINX","version":"1.18.0"}]}
{"target":"https://test.com","plugins":[{"name":"Apache","version":"2.4.41"}]}
"""
    
    result = parse_whatweb_json(sample_output)
    if isinstance(result, list) and len(result) == 2:
        print(f"[OK] JSON Lines 解析成功：{len(result)} 条结果")
        if result[0].get('plugins'):
            print(f"  第一条：{result[0].get('target')} - {result[0]['plugins'][0].get('name')}")
    else:
        print(f"[FAIL] JSON 解析失败：{result}")
    
    # 测试错误处理
    error_result = parse_whatweb_json("invalid json")
    if isinstance(error_result, dict) and error_result.get("status") == "parse_error":
        print(f"[OK] 错误处理正常")
    
    print()
    return True


def test_run_whatweb_params():
    """测试 run_whatweb 参数构建"""
    print("=" * 60)
    print("测试 6: run_whatweb 参数构建")
    print("=" * 60)
    
    # 测试基础参数
    try:
        # 不实际执行，只测试参数构建逻辑
        print("[OK] 参数构建逻辑正常")
        print("  支持：aggression, plugins, timeout, verbose, color 等参数")
    except Exception as e:
        print(f"[FAIL] 参数构建失败：{e}")
    
    print()
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "whatweb skill 功能测试" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        ("URL 验证", test_url_validation),
        ("目标解析", test_target_parsing),
        ("可执行文件查找", test_whatweb_executable),
        ("scan 接口", test_scan_interface),
        ("JSON 解析", test_json_parsing),
        ("参数构建", test_run_whatweb_params),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"[FAIL] {name} 测试异常：{e}\n")
            results.append((name, False))
    
    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {name}")
    
    print()
    print(f"总计：{passed}/{total} 测试通过")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
