#!/usr/bin/env python3
"""
检查 ZAP-CLI 配置和端口设置
"""

import subprocess
import sys

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def main():
    print("=" * 70)
    print("  ZAP-CLI 配置检查")
    print("=" * 70)
    print()
    
    # 1. 检查 zap-cli 版本
    print("[-] 检查 zap-cli 版本...")
    code, stdout, stderr = run_command("zap-cli --version")
    if code == 0:
        print(f"✅ zap-cli 版本：{stdout.strip()}")
    else:
        print(f"❌ zap-cli 版本检查失败：{stderr}")
    print()
    
    # 2. 检查 zap-cli 帮助（查看默认端口）
    print("[-] 检查 zap-cli 帮助信息...")
    code, stdout, stderr = run_command("zap-cli --help")
    if code == 0:
        # 查找端口相关说明
        for line in stdout.split('\n'):
            if 'port' in line.lower() or '-p' in line:
                print(f"  {line.strip()}")
    print()
    
    # 3. 检查当前 ZAP 进程
    print("[-] 检查 ZAP 进程...")
    code, stdout, stderr = run_command("ps aux | grep -i 'zap.*jar.*daemon' | grep -v grep")
    if stdout.strip():
        print("✅ ZAP 进程运行中:")
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("❌ ZAP 进程未运行")
    print()
    
    # 4. 检查端口监听
    print("[-] 检查端口监听...")
    code, stdout, stderr = run_command("netstat -tlnp | grep -i java")
    if stdout.strip():
        print("✅ Java 进程监听端口:")
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("❌ 没有 Java 进程监听端口")
    print()
    
    # 5. 检查 zap-cli 配置
    print("[-] 检查 zap-cli 配置...")
    code, stdout, stderr = run_command("zap-cli --help | grep -i port")
    if stdout.strip():
        print(f"  {stdout.strip()}")
    print()
    
    # 6. 测试连接 8080 端口
    print("[-] 测试连接 8080 端口...")
    code, stdout, stderr = run_command("zap-cli -p 8080 status")
    if code == 0 and "running" in stdout.lower():
        print(f"✅ 8080 端口连接成功：{stdout.strip()}")
    else:
        print(f"❌ 8080 端口连接失败")
        if stderr:
            print(f"   错误：{stderr.strip()}")
    print()
    
    # 7. 测试连接 8090 端口
    print("[-] 测试连接 8090 端口...")
    code, stdout, stderr = run_command("zap-cli -p 8090 status")
    if code == 0 and "running" in stdout.lower():
        print(f"✅ 8090 端口连接成功：{stdout.strip()}")
    else:
        print(f"❌ 8090 端口连接失败")
        if stderr:
            print(f"   错误：{stderr.strip()}")
    print()
    
    # 8. 检查是否有默认端口配置
    print("[-] 检查环境变量...")
    code, stdout, stderr = run_command("env | grep -i zap")
    if stdout.strip():
        print("✅ ZAP 相关环境变量:")
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("ℹ️  没有 ZAP 相关环境变量")
    print()
    
    # 9. 检查 Python 代码中的端口配置
    print("[-] 检查项目中的端口配置...")
    code, stdout, stderr = run_command("grep -r '8090' /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/adapters/ 2>/dev/null | head -5")
    if stdout.strip():
        print("⚠️  发现 8090 端口配置:")
        print(f"  {stdout.strip()}")
    else:
        print("✅ 适配器代码中没有 8090 端口配置")
    print()
    
    print("=" * 70)
    print("  建议")
    print("=" * 70)
    print()
    print("1. 如果 ZAP 运行在 8080 端口，确保所有 zap-cli 命令都使用 -p 8080")
    print("2. 检查是否有其他代码或服务在使用 8090 端口")
    print("3. 查看 Python 错误日志，确认是哪个模块在尝试连接 8090")
    print()
    
    print("=" * 70)
    print("  快速修复命令")
    print("=" * 70)
    print()
    print("# 启动 ZAP (8080 端口)")
    print("cd /home/ubuntu/tools/zap/ZAP_2.17.0")
    print("nohup java -Xmx512m -jar zap-2.17.0.jar -daemon -port 8080 > /tmp/zap.log 2>&1 &")
    print()
    print("# 验证")
    print("zap-cli -p 8080 status")
    print()

if __name__ == "__main__":
    main()
