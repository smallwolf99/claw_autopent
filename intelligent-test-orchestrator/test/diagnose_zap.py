#!/usr/bin/env python3
"""
ZAP 诊断工具（增强版）

检查 ZAP-CLI 配置、端口、运行状态，支持自定义路径
"""

import subprocess
import sys
import os


def run_command(cmd: str, timeout: int = 10, use_shell: bool = False) -> dict:
    """运行命令并返回结果"""
    try:
        if use_shell:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'timeout',
            'message': f'命令执行超时 ({timeout}秒)'
        }
    except FileNotFoundError as e:
        return {
            'success': False,
            'error': 'not_found',
            'message': f'命令未找到：{str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def find_zapcli_path() -> str:
    """查找 zap-cli 的路径"""
    print("\n1. 查找 zap-cli 路径...")
    
    # 可能的路径列表
    possible_paths = [
        "zap-cli",  # PATH 中
        "/home/ubuntu/.local/bin/zap-cli",
        "/home/ubuntu/.local/bin/zap-cli",
        "~/.local/bin/zap-cli",
        "/usr/local/bin/zap-cli",
        "/usr/bin/zap-cli",
    ]
    
    # 先尝试 which 命令
    result = run_command("which zap-cli", use_shell=True)
    if result['success'] and result['stdout']:
        path = result['stdout'].strip()
        print(f"   ✅ 通过 which 找到：{path}")
        return path
    
    # 尝试各个路径
    for path in possible_paths:
        # 展开 ~
        expanded_path = os.path.expanduser(path)
        
        if os.path.exists(expanded_path):
            print(f"   ✅ 找到 zap-cli: {expanded_path}")
            return expanded_path
    
    print(f"   ❌ 未找到 zap-cli")
    print(f"      请检查以下路径:")
    for path in possible_paths:
        print(f"        - {path}")
    
    return "zap-cli"  # 返回默认，让系统尝试


def check_zapcli_installed(zapcli_path: str) -> bool:
    """检查 zap-cli 是否可用"""
    print(f"\n2. 检查 zap-cli 是否可用 (路径：{zapcli_path})...")
    
    # 尝试不同的命令来验证 zap-cli
    commands_to_try = [
        f"{zapcli_path} --help",  # 帮助命令
        f"{zapcli_path} help",    # 另一种帮助格式
    ]
    
    for cmd in commands_to_try:
        result = run_command(cmd, timeout=5)
        
        if result['success']:
            # 提取第一行作为版本信息
            output_lines = result['stdout'].split('\n')
            version_info = output_lines[0] if output_lines else "unknown"
            print(f"   ✅ zap-cli 可用：{version_info[:100]}")
            return True
    
    # 所有命令都失败
    print(f"   ❌ zap-cli 不可用")
    if result.get('error') == 'not_found':
        print(f"      错误：命令未找到")
    else:
        error_msg = result.get('stderr', result.get('error', 'unknown'))
        print(f"      错误：{error_msg[:200]}")
    return False


def check_zap_running(zapcli_path: str) -> bool:
    """检查 ZAP 是否运行"""
    print(f"\n3. 检查 ZAP 服务是否运行 (使用：{zapcli_path})...")
    
    # 尝试不同的端口
    ports_to_try = [8080, 8090, 8081]
    
    for port in ports_to_try:
        cmd = f"{zapcli_path} -p {port} status"
        result = run_command(cmd, timeout=5)
        
        if result['success']:
            print(f"   ✅ ZAP 运行在端口 {port}")
            return True
        else:
            error_msg = result.get('stderr', 'unknown error')
            if error_msg:
                print(f"   ❌ 端口 {port}: {error_msg[:100]}")
    
    print(f"   ❌ ZAP 服务未响应（尝试了端口：{', '.join(map(str, ports_to_try))}）")
    return False


def check_zap_listening() -> dict:
    """检查哪个进程在监听 8080 端口"""
    print("\n4. 检查 8080 端口监听状态...")
    
    try:
        # 尝试 ss 命令（更现代）
        result = run_command("ss -tlnp | grep :8080", use_shell=True, timeout=5)
        
        if result['success'] and result['stdout']:
            print(f"   ✅ 端口 8080 正在监听：{result['stdout'].strip()}")
            return {'listening': True, 'info': result['stdout'].strip()}
        
        # 尝试 netstat
        result = run_command("netstat -tlnp | grep :8080", use_shell=True, timeout=5)
        
        if result['success'] and result['stdout']:
            print(f"   ✅ 端口 8080 正在监听：{result['stdout'].strip()}")
            return {'listening': True, 'info': result['stdout'].strip()}
        
        print(f"   ❌ 端口 8080 未被监听或未找到")
        return {'listening': False}
    
    except Exception as e:
        print(f"   ⚠️ 无法检查端口状态：{e}")
        return {'listening': False, 'error': str(e)}


def test_zap_quick_scan(zapcli_path: str, target: str = "http://demo.testfire.net") -> bool:
    """测试 ZAP 快速扫描"""
    print(f"\n5. 测试 ZAP 快速扫描（目标：{target}）...")
    
    cmd = f"{zapcli_path} -p 8080 quick-scan -s all {target}"
    print(f"   执行命令：{cmd}")
    
    result = run_command(cmd, timeout=60)
    
    if result['success']:
        print(f"   ✅ ZAP 扫描成功")
        if result['stdout']:
            print(f"   输出：{result['stdout'][:200]}")
        return True
    else:
        print(f"   ❌ ZAP 扫描失败")
        print(f"   返回码：{result.get('returncode', 'N/A')}")
        if result.get('stderr'):
            print(f"   错误：{result['stderr'][:200]}")
        if result.get('error'):
            print(f"   异常：{result['error']}")
        return False


def print_environment_info():
    """打印环境信息"""
    print("\n0. 环境信息...")
    print(f"   PATH: {os.environ.get('PATH', 'N/A')[:200]}")
    print(f"   HOME: {os.environ.get('HOME', 'N/A')}")
    print(f"   用户：{os.environ.get('USER', 'unknown')}")
    
    # 检查 .local/bin 是否在 PATH 中
    local_bin = "/home/ubuntu/.local/bin"
    if local_bin in os.environ.get('PATH', ''):
        print(f"   ✅ {local_bin} 在 PATH 中")
    else:
        print(f"   ⚠️  {local_bin} 不在 PATH 中")
        print(f"      建议添加到 ~/.bashrc:")
        print(f"      export PATH=$HOME/.local/bin:$PATH")


def print_summary(zapcli_path: str, config: dict):
    """打印总结"""
    print("\n" + "=" * 60)
    print("ZAP 配置诊断总结")
    print("=" * 60)
    
    print(f"\nzap-cli 路径：{zapcli_path}")
    print(f"zap-cli 可用：{'✅ 是' if config['zapcli_available'] else '❌ 否'}")
    print(f"ZAP 服务运行：{'✅ 是' if config['zap_running'] else '❌ 否'}")
    print(f"端口 8080 监听：{'✅ 是' if config['port_8080_listening'].get('listening') else '❌ 否'}")
    
    if config['port_8080_listening'].get('info'):
        print(f"   详情：{config['port_8080_listening']['info']}")
    
    print("\n" + "=" * 60)
    
    if config['zapcli_available'] and config['zap_running']:
        print("\n✅ ZAP 配置正常，可以进行扫描")
    elif config['zapcli_available'] and not config['zap_running']:
        print("\n⚠️  ZAP 服务未运行，请启动 ZAP:")
        print(f"   命令：{zapcli_path} start")
        print(f"   或：{zapcli_path} -p 8080 start")
    elif not config['zapcli_available']:
        print("\n❌ zap-cli 不可用")
        print("\n解决方案:")
        print("  1. 如果已安装，添加到 PATH:")
        print("     export PATH=$HOME/.local/bin:$PATH")
        print("     echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc")
        print("     source ~/.bashrc")
        print("\n  2. 如果未安装:")
        print("     pip3 install --user zap-cli")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("ZAP-CLI 诊断工具（增强版）")
    print("=" * 60)
    
    # 打印环境信息
    print_environment_info()
    
    # 查找 zap-cli 路径
    zapcli_path = find_zapcli_path()
    
    # 检查配置
    config = {
        'zapcli_available': check_zapcli_installed(zapcli_path),
        'zap_running': check_zap_running(zapcli_path),
        'port_8080_listening': check_zap_listening()
    }
    
    print_summary(zapcli_path, config)
    
    # 如果 ZAP 运行，询问是否测试扫描
    if config['zap_running'] and config['zapcli_available']:
        response = input("\n是否测试 ZAP 快速扫描？(y/n): ")
        if response.lower() in ['y', 'yes', '是']:
            test_zap_quick_scan(zapcli_path)
    
    return 0 if (config['zapcli_available'] and config['zap_running']) else 1


if __name__ == '__main__':
    sys.exit(main())
