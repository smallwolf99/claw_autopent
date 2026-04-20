#!/usr/bin/env python3
"""
测试脚本 - 验证 OpenClaw 调用流程

此脚本用于测试 intelligent-test-orchestrator 的基本功能。
在核心代码迁移完成前（Task 27），使用模拟数据测试流程。
"""

import subprocess
import json
import sys
from pathlib import Path


def test_basic_call():
    """测试基本调用"""
    print("=" * 60)
    print("测试 1: 基本调用（完整流程）")
    print("=" * 60)
    
    test_input = {
        "target": "http://zero.webappsecurity.com",
        "test_mode": "full",
        "time_limit": 120,
        "report_format": "html"
    }
    
    # 调用 main.py
    main_py = Path(__file__).parent / "main.py"
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(main_py), json.dumps(test_input)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=str(Path(__file__).parent)
    )
    
    # 打印输出
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    # 验证结果
    try:
        output = json.loads(result.stdout)
        assert output["success"] == True, "测试应该成功"
        assert "summary" in output, "应该包含摘要"
        assert "data" in output, "应该包含数据"
        print("\n✅ 测试 1 通过！")
        return True
    except Exception as e:
        print(f"\n❌ 测试 1 失败：{e}")
        return False


def test_light_mode():
    """测试快速模式"""
    print("\n" + "=" * 60)
    print("测试 2: 快速模式（light）")
    print("=" * 60)
    
    test_input = {
        "target": "http://zero.webappsecurity.com",
        "test_mode": "light",
        "time_limit": 30,
        "report_format": "markdown"
    }
    
    main_py = Path(__file__).parent / "main.py"
    result = subprocess.run(
        [sys.executable, str(main_py), json.dumps(test_input)],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    try:
        output = json.loads(result.stdout)
        assert output["success"] == True, "测试应该成功"
        print("\n✅ 测试 2 通过！")
        return True
    except Exception as e:
        print(f"\n❌ 测试 2 失败：{e}")
        return False


def test_custom_mode():
    """测试自定义模式"""
    print("\n" + "=" * 60)
    print("测试 3: 自定义模式")
    print("=" * 60)
    
    test_input = {
        "target": "http://example.com",
        "test_mode": "custom",
        "time_limit": 60,
        "report_format": "json",
        "custom_options": {
            "skip_verification": True,
            "concurrent_tools": 3
        }
    }
    
    main_py = Path(__file__).parent / "main.py"
    result = subprocess.run(
        [sys.executable, str(main_py), json.dumps(test_input)],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    try:
        output = json.loads(result.stdout)
        assert output["success"] == True, "测试应该成功"
        print("\n✅ 测试 3 通过！")
        return True
    except Exception as e:
        print(f"\n❌ 测试 3 失败：{e}")
        return False


def test_invalid_input():
    """测试无效输入"""
    print("\n" + "=" * 60)
    print("测试 4: 无效输入（缺少 target）")
    print("=" * 60)
    
    test_input = {
        "test_mode": "full"
        # 缺少必需的的 target 字段
    }
    
    main_py = Path(__file__).parent / "main.py"
    result = subprocess.run(
        [sys.executable, str(main_py), json.dumps(test_input)],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    try:
        output = json.loads(result.stdout)
        # 应该返回错误
        assert output["success"] == False, "应该返回错误"
        print("\n✅ 测试 4 通过！")
        return True
    except Exception as e:
        print(f"\n❌ 测试 4 失败：{e}")
        return False


def test_stdin_mode():
    """测试 stdin 输入模式"""
    print("\n" + "=" * 60)
    print("测试 5: stdin 输入模式")
    print("=" * 60)
    
    test_input = {
        "target": "http://example.com",
        "test_mode": "light"
    }
    
    main_py = Path(__file__).parent / "main.py"
    result = subprocess.run(
        [sys.executable, str(main_py)],
        input=json.dumps(test_input),
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent)
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    try:
        output = json.loads(result.stdout)
        assert output["success"] == True, "测试应该成功"
        print("\n✅ 测试 5 通过！")
        return True
    except Exception as e:
        print(f"\n❌ 测试 5 失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("🧪 开始测试 Intelligent Test Orchestrator")
    print(f"📂 工作目录：{Path(__file__).parent}")
    print()
    
    results = []
    
    # 运行测试
    results.append(("基本调用", test_basic_call()))
    results.append(("快速模式", test_light_mode()))
    results.append(("自定义模式", test_custom_mode()))
    results.append(("无效输入", test_invalid_input()))
    results.append(("stdin 模式", test_stdin_mode()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
