#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-2 工具诊断脚本

用途：诊断工具调用失败的具体原因
"""

import asyncio
import subprocess
import sys

async def diagnose_tools():
    """诊断所有工具"""
    
    print("=" * 70)
    print("  Phase-2 工具诊断")
    print("=" * 70)
    print()
    
    test_target = "http://demo.testfire.net"
    
    # 1. 诊断 Nikto
    print("-" * 70)
    print("1. 诊断 Nikto")
    print("-" * 70)
    
    cmd = f"nikto -h {test_target} -Format json -timeout 10"
    print(f"命令：{cmd}")
    print()
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=30
        )
        
        print(f"返回码：{process.returncode}")
        print(f"STDOUT (前 500 字符):")
        print(stdout.decode()[:500])
        print()
        print(f"STDERR (前 500 字符):")
        print(stderr.decode()[:500])
        print()
        
        # 尝试解析 JSON
        import json
        try:
            data = json.loads(stdout.decode())
            print("✅ JSON 解析成功")
            print(f"   漏洞数：{len(data.get('vulnerabilities', []))}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            print("   输出可能不是 JSON 格式")
        
    except asyncio.TimeoutError:
        print("❌ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行失败：{e}")
    
    print()
    
    # 2. 诊断 Nuclei
    print("-" * 70)
    print("2. 诊断 Nuclei")
    print("-" * 70)
    
    cmd = f"nuclei -u {test_target} -json -silent -timeout 10"
    print(f"命令：{cmd}")
    print()
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=30
        )
        
        print(f"返回码：{process.returncode}")
        print(f"STDOUT (前 500 字符):")
        print(stdout.decode()[:500])
        print()
        print(f"STDERR (前 500 字符):")
        print(stderr.decode()[:500])
        print()
        
        # 检查输出
        if process.returncode == 0:
            print("✅ Nuclei 执行成功")
            if stdout:
                print("   有输出内容")
            else:
                print("   ⚠️  但没有输出内容（可能没有漏洞）")
        else:
            print(f"❌ Nuclei 执行失败，返回码：{process.returncode}")
        
    except asyncio.TimeoutError:
        print("❌ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行失败：{e}")
    
    print()
    
    # 3. 诊断 ZAP-CLI
    print("-" * 70)
    print("3. 诊断 ZAP-CLI")
    print("-" * 70)
    
    print("检查 ZAP 服务状态...")
    cmd = "zap-cli status"
    print(f"命令：{cmd}")
    print()
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=10
        )
        
        print(f"返回码：{process.returncode}")
        print(f"STDOUT:")
        print(stdout.decode())
        print()
        print(f"STDERR:")
        print(stderr.decode())
        print()
        
        if process.returncode == 0:
            print("✅ ZAP 服务正在运行")
        else:
            print("❌ ZAP 服务未运行")
            print()
            print("启动 ZAP 服务:")
            print("  zap-cli start")
            print()
            print("或使用 Docker:")
            print("  docker run -d -u zap -p 8090:8090 --name zap owasp/zap:stable zap-daemon.sh")
        
    except Exception as e:
        print(f"❌ 检查失败：{e}")
    
    print()
    print("=" * 70)
    print("  诊断完成")
    print("=" * 70)
    print()
    
    # 总结
    print("📋 总结:")
    print()
    print("如果 Nikto JSON 解析失败:")
    print("  - Nikto 版本可能过旧，不支持 -Format json 参数")
    print("  - 解决方案：更新 Nikto 或修改代码支持文本解析")
    print()
    print("如果 Nuclei 执行失败:")
    print("  - 可能缺少模板")
    print("  - 解决方案：nuclei -ut 更新模板")
    print()
    print("如果 ZAP 服务未运行:")
    print("  - 启动 ZAP: zap-cli start")
    print()


if __name__ == '__main__':
    try:
        asyncio.run(diagnose_tools())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 诊断失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
