#!/usr/bin/env python3
"""
ZAP 扫描失败诊断工具

帮助诊断 ZAP-CLI 扫描失败的常见问题
"""

import subprocess
import sys
import os
import time


def run_command(cmd: str, timeout: int = 30) -> dict:
    """运行命令并返回详细结果"""
    try:
        print(f"执行：{cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'timeout',
            'message': f'命令执行超时 ({timeout}秒)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def check_zap_running():
    """检查 ZAP 服务状态"""
    print("\n" + "=" * 60)
    print("步骤 1: 检查 ZAP 服务状态")
    print("=" * 60)
    
    result = run_command("zap-cli -p 8080 status", timeout=10)
    
    if result['success']:
        print("✅ ZAP 服务运行正常")
        return True
    else:
        print("❌ ZAP 服务未运行或无法访问")
        if result.get('stderr'):
            print(f"错误信息：{result['stderr'][:200]}")
        return False


def check_zap_listening():
    """检查 8080 端口监听"""
    print("\n" + "=" * 60)
    print("步骤 2: 检查 8080 端口监听")
    print("=" * 60)
    
    result = run_command("ss -tlnp | grep :8080", timeout=5)
    
    if result['success'] and result['stdout']:
        print(f"✅ 端口 8080 正在监听:")
        print(f"   {result['stdout'].strip()}")
        return True
    else:
        print("❌ 端口 8080 未被监听")
        return False


def test_target_access(target: str):
    """测试目标可达性"""
    print("\n" + "=" * 60)
    print(f"步骤 3: 测试目标可达性 ({target})")
    print("=" * 60)
    
    # 使用 curl 测试
    result = run_command(f"curl -I --connect-timeout 10 {target}", timeout=15)
    
    if result['success']:
        print(f"✅ 目标可访问")
        lines = result['stdout'].split('\n')[:5]
        for line in lines:
            print(f"   {line}")
        return True
    else:
        print(f"❌ 目标无法访问")
        if result.get('stderr'):
            print(f"错误：{result['stderr'][:200]}")
        return False


def test_zap_quick_scan(target: str):
    """测试 ZAP 快速扫描"""
    print("\n" + "=" * 60)
    print("步骤 4: 测试 ZAP 快速扫描")
    print("=" * 60)
    
    report_file = f"/tmp/zap_test_report_{int(time.time())}.json"
    cmd = f"zap-cli -p 8080 quick-scan -s all -f json -o {report_file} {target}"
    
    print(f"执行命令：{cmd}")
    print(f"报告文件：{report_file}")
    
    result = run_command(cmd, timeout=120)
    
    print(f"\n返回码：{result.get('returncode', 'N/A')}")
    
    if result['success']:
        print("✅ ZAP 扫描成功")
        
        # 检查报告文件
        if os.path.exists(report_file):
            import json
            with open(report_file, 'r') as f:
                data = json.load(f)
                sites = data.get('site', [])
                if sites:
                    alerts = sites[0].get('alerts', [])
                    print(f"✅ 报告生成成功，发现 {len(alerts)} 个警报")
                    
                    # 显示前 3 个警报
                    for i, alert in enumerate(alerts[:3], 1):
                        print(f"   {i}. {alert.get('name', 'Unknown')}")
                else:
                    print("⚠️  报告为空")
            
            # 清理
            os.remove(report_file)
            print(f"已清理临时文件：{report_file}")
        else:
            print(f"❌ 报告文件不存在：{report_file}")
        
        return True
    else:
        print("❌ ZAP 扫描失败")
        if result.get('stdout'):
            print(f"\n标准输出:\n{result['stdout'][:500]}")
        if result.get('stderr'):
            print(f"\n错误输出:\n{result['stderr'][:500]}")
        return False


def check_zapcli_path():
    """检查 zap-cli 路径"""
    print("\n" + "=" * 60)
    print("步骤 0: 检查 zap-cli 路径")
    print("=" * 60)
    
    result = run_command("which zap-cli", timeout=5)
    
    if result['success'] and result['stdout']:
        path = result['stdout'].strip()
        print(f"✅ zap-cli 路径：{path}")
        
        # 检查是否可执行
        if os.access(path, os.X_OK):
            print(f"✅ 文件可执行")
        else:
            print(f"❌ 文件不可执行")
        
        # 检查版本
        result = run_command(f"{path} --help", timeout=5)
        if result['success']:
            first_line = result['stdout'].split('\n')[0]
            print(f"✅ 命令正常：{first_line[:100]}")
        
        return True
    else:
        print("❌ 未找到 zap-cli")
        return False


def diagnose_zap_scan(target: str = "http://demo.testfire.net"):
    """完整诊断流程"""
    print("\n" + "=" * 60)
    print("ZAP 扫描失败诊断工具")
    print("=" * 60)
    print(f"目标：{target}")
    
    # 步骤 0: 检查路径
    path_ok = check_zapcli_path()
    
    # 步骤 1: 检查服务状态
    zap_ok = check_zap_running()
    
    # 步骤 2: 检查端口
    port_ok = check_zap_listening()
    
    # 步骤 3: 测试目标
    target_ok = test_target_access(target)
    
    # 步骤 4: 测试扫描（仅当前面都正常时）
    scan_ok = False
    if path_ok and zap_ok and port_ok and target_ok:
        scan_ok = test_zap_quick_scan(target)
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    checks = [
        ("zap-cli 路径", path_ok),
        ("ZAP 服务运行", zap_ok),
        ("8080 端口监听", port_ok),
        ("目标可访问", target_ok),
        ("ZAP 扫描测试", scan_ok) if path_ok and zap_ok else ("ZAP 扫描测试", None)
    ]
    
    for name, status in checks:
        if status is None:
            print(f"⚪ {name}: 跳过（前置条件不满足）")
        elif status:
            print(f"✅ {name}: 正常")
        else:
            print(f"❌ {name}: 失败")
    
    print("\n" + "=" * 60)
    
    # 提供建议
    all_ok = all(status for _, status in checks if status is not None)
    
    if all_ok:
        print("\n✅ 所有检查通过，ZAP 配置正常")
        print("\n如果实际扫描仍失败，可能原因:")
        print("  1. 扫描超时（增加 timeout 参数）")
        print("  2. 目标响应慢（网络问题）")
        print("  3. ZAP 配置限制（检查 ZAP 日志）")
    else:
        print("\n❌ 发现问题，请按以下步骤修复:")
        
        if not path_ok:
            print("\n1. 安装或配置 zap-cli:")
            print("   pip3 install --user zap-cli")
            print("   export PATH=$HOME/.local/bin:$PATH")
        
        if not zap_ok:
            print("\n2. 启动 ZAP 服务:")
            print("   zap-cli start")
            print("   或")
            print("   zap-cli -p 8080 start")
        
        if not port_ok and zap_ok:
            print("\n3. 检查 ZAP 绑定端口:")
            print("   zap-cli status")
            print("   netstat -tlnp | grep zap")
        
        if not target_ok:
            print("\n4. 检查目标可达性:")
            print(f"   ping {target}")
            print(f"   curl -v {target}")
    
    print("\n" + "=" * 60)
    
    return all_ok


def main():
    """主函数"""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "http://demo.testfire.net"
    
    print(f"\n使用目标：{target}")
    print("按 Ctrl+C 可中断诊断\n")
    
    try:
        success = diagnose_zap_scan(target)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 诊断异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
