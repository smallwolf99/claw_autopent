#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟 OpenClaw 调用测试

这个脚本模拟 OpenClaw 智能体的调用流程，让你在没有安装 OpenClaw 的情况下
也能测试 intelligent-test-orchestrator 的完整功能。
"""

import subprocess
import json
import sys
import io
import os
from pathlib import Path
from datetime import datetime

# 设置标准输出编码为 UTF-8（Windows 兼容性）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'


def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def simulate_user_input():
    """模拟用户输入自然语言"""
    print_separator("👤 用户输入（自然语言）")
    
    examples = [
        "帮我测试一下 http://zero.webappsecurity.com，做完整的安全测试",
        "快速扫描 example.com，主要看高危漏洞",
        "对 192.168.1.100 进行渗透测试，生成 PDF 报告"
    ]
    
    print("\n示例输入：")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    return examples[0]


def simulate_openclaw_understanding(user_input: str):
    """模拟 OpenClaw 理解意图"""
    print_separator("🤖 OpenClaw 智能体 - 意图理解")
    
    # 简单的关键词匹配（模拟）
    intent = "安全测试"
    target = None
    test_mode = "full"
    
    if "http://" in user_input or "https://" in user_input:
        target = user_input.split("http")[1].split(",")[0].split(" ")[0]
        target = f"http{target}"
    elif ".com" in user_input or ".cn" in user_input:
        target = user_input.split(".com")[0] + ".com"
    
    if "快速" in user_input or "fast" in user_input:
        test_mode = "light"
    elif "自定义" in user_input or "custom" in user_input:
        test_mode = "custom"
    
    print(f"\n📋 意图识别结果:")
    print(f"  • 意图：{intent}")
    print(f"  • 目标：{target or '未识别'}")
    print(f"  • 模式：{test_mode}")
    
    # 触发词匹配
    triggers = ["测试", "安全测试", "渗透测试", "扫描"]
    matched = [t for t in triggers if t in user_input]
    
    print(f"\n🎯 触发词匹配:")
    print(f"  • 匹配到：{', '.join(matched) if matched else '无'}")
    print(f"  • 匹配技能：intelligent-test-orchestrator")
    
    return {
        "target": target or "http://zero.webappsecurity.com",
        "test_mode": test_mode,
        "time_limit": 120,
        "report_format": "html"
    }


def simulate_openclaw_call(params: dict):
    """模拟 OpenClaw 调用 Skill"""
    print_separator("🔌 OpenClaw → Skill 调用")
    
    print(f"\n📤 调用接口:")
    print(f"  • 接口名：execute_intelligent_test")
    print(f"  • 参数：{json.dumps(params, indent=4, ensure_ascii=False)}")
    
    print(f"\n⏳ 执行中...\n")
    
    # 实际调用 main.py
    main_py = Path(__file__).parent / "main.py"
    
    # 设置环境变量确保 UTF-8 编码
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(main_py), json.dumps(params, ensure_ascii=False)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env,
        cwd=str(Path(__file__).parent)
    )
    
    # 打印进度反馈（stdout）
    if result.stdout:
        print("📊 进度反馈:")
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                print(f"  {line}")
    
    return result.stdout


def display_result(output: str):
    """显示结果"""
    print_separator("📊 测试结果")
    
    try:
        # 解析 JSON 结果（最后一行）
        lines = output.strip().split('\n')
        json_start = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start >= 0:
            json_str = '\n'.join(lines[json_start:])
            result = json.loads(json_str)
            
            print(f"\n✅ 调用成功！")
            print(f"\n📋 返回结果:")
            print(f"  • success: {result.get('success', False)}")
            print(f"  • summary: {result.get('summary', 'N/A')}")
            
            if result.get('data'):
                data = result['data']
                print(f"\n📊 详细数据:")
                print(f"  • 目标：{data.get('target', 'N/A')}")
                print(f"  • 发现资产：{data.get('assets_found', 0)} 个")
                print(f"  • 发现漏洞：{data.get('vulnerabilities_found', 0)} 个")
                print(f"  • 已验证：{data.get('verified_vulns', 0)} 个")
                print(f"  • 风险评分：{data.get('risk_score', 0)}/100")
                print(f"  • 报告路径：{data.get('report_path', 'N/A')}")
                print(f"  • 执行时间：{data.get('execution_time', 0):.2f} 秒")
                
                if data.get('report_url'):
                    print(f"\n🔗 报告链接：{data['report_url']}")
            
            if result.get('actions'):
                print(f"\n🎯 可用操作:")
                for action in result['actions']:
                    print(f"  • {action.get('label', 'N/A')} ({action.get('type', 'N/A')})")
            
            return result.get('success', False)
        else:
            print("❌ 无法解析 JSON 结果")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误：{e}")
        print(f"\n原始输出:\n{output}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False


def run_demo():
    """运行演示"""
    print("\n" + "🎉" * 35)
    print("  " * 15 + "智能测试编排器 - OpenClaw 调用模拟演示")
    print("🎉" * 35)
    
    print(f"\n📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 工作目录：{Path(__file__).parent}")
    
    # 1. 用户输入
    user_input = simulate_user_input()
    print(f"\n💬 用户说：{user_input}")
    
    # 2. OpenClaw 理解
    params = simulate_openclaw_understanding(user_input)
    
    # 3. 调用 Skill
    output = simulate_openclaw_call(params)
    
    # 4. 显示结果
    success = display_result(output)
    
    # 5. 总结
    print_separator("📋 测试总结")
    
    if success:
        print("\n✅ 测试通过！")
        print("\n💡 说明:")
        print("  • 当前使用模拟数据测试（Task 27 未完成）")
        print("  • 真实环境中，OpenClaw 会自动完成上述所有步骤")
        print("  • 用户只需输入自然语言即可")
    else:
        print("\n❌ 测试失败，请检查错误信息")
    
    print("\n" + "=" * 70 + "\n")
    
    return success


def interactive_mode():
    """交互模式"""
    print_separator("🎮 交互模式")
    print("\n💡 提示：输入测试目标，按 Enter 执行测试（输入 'q' 退出）")
    
    while True:
        try:
            target = input("\n🎯 请输入测试目标：").strip()
            
            if target.lower() == 'q':
                print("\n👋 退出测试")
                break
            
            if not target:
                target = "http://zero.webappsecurity.com"
            
            params = {
                "target": target,
                "test_mode": "full",
                "time_limit": 120,
                "report_format": "html"
            }
            
            print(f"\n🚀 开始测试：{target}")
            output = simulate_openclaw_call(params)
            display_result(output)
            
        except KeyboardInterrupt:
            print("\n\n👋 中断测试")
            break
        except Exception as e:
            print(f"\n❌ 错误：{e}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  智能测试编排器 - OpenClaw 调用模拟测试")
    print("=" * 70)
    
    print("\n请选择测试模式:")
    print("  1. 演示模式（自动执行完整流程）")
    print("  2. 交互模式（手动输入测试目标）")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == '2':
        interactive_mode()
    else:
        run_demo()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 程序错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
