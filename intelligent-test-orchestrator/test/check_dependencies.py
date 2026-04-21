#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具依赖检查脚本

检查 Phase-0 和 Phase-2 所需的工具是否已安装
"""

import subprocess
import sys
import shutil
from typing import Dict, List, Optional


class ToolChecker:
    """工具依赖检查器"""
    
    def __init__(self):
        """初始化检查器"""
        # Phase-0 所需工具
        self.phase0_tools = {
            'nmap': {
                'check_cmd': 'nmap --version',
                'install_cmd': 'sudo apt install nmap',
                'description': '端口扫描和网络发现'
            },
            'whatweb': {
                'check_cmd': 'whatweb --version',
                'install_cmd': 'sudo apt install whatweb || gem install whatweb',
                'description': 'Web 技术识别'
            },
            'httpx': {
                'check_cmd': 'httpx -version',
                'install_cmd': 'go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest',
                'description': 'HTTP 探测工具'
            },
            'subfinder': {
                'check_cmd': 'subfinder --version',
                'install_cmd': 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
                'description': '子域名收集'
            }
        }
        
        # Phase-2 所需工具
        self.phase2_tools = {
            'nuclei': {
                'check_cmd': 'nuclei -version',
                'install_cmd': 'go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest',
                'description': '模板化漏洞扫描'
            },
            'afrog': {
                'check_cmd': 'afrog -version',
                'install_cmd': 'go install github.com/zan8in/afrog/v2@latest',
                'description': 'PoC 验证扫描'
            },
            'nikto': {
                'check_cmd': 'nikto -Version',
                'install_cmd': 'sudo apt install nikto || git clone https://github.com/sullo/nikto',
                'description': 'Web 漏洞扫描'
            },
            'zap-cli': {
                'check_cmd': 'zap-cli --version',
                'install_cmd': 'pip3 install zap-cli',
                'description': 'OWASP ZAP 命令行接口'
            },
            'sqlmap': {
                'check_cmd': 'sqlmap --version',
                'install_cmd': 'git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap',
                'description': 'SQL 注入自动化检测'
            }
        }
    
    def check_tool(self, tool_name: str, check_cmd: str) -> bool:
        """检查单个工具是否已安装"""
        try:
            # 首先尝试使用 shutil.which
            if shutil.which(tool_name):
                return True
            
            # 如果找不到，尝试执行检查命令
            result = subprocess.run(
                check_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            return result.returncode == 0
        
        except Exception as e:
            return False
    
    def get_tool_version(self, tool_name: str, check_cmd: str) -> Optional[str]:
        """获取工具版本信息"""
        try:
            result = subprocess.run(
                check_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.decode()[:100]  # 只取前 100 字符
                return output.strip()
            
            return None
        
        except Exception:
            return None
    
    def check_all_tools(self, tools: Dict[str, Dict]) -> Dict[str, bool]:
        """检查所有工具"""
        results = {}
        
        for tool_name, tool_info in tools.items():
            is_installed = self.check_tool(tool_name, tool_info['check_cmd'])
            results[tool_name] = is_installed
        
        return results
    
    def print_report(self, phase_name: str, tools: Dict[str, Dict], 
                     results: Dict[str, bool]):
        """打印检查报告"""
        print()
        print("=" * 70)
        print(f"  {phase_name} 工具依赖检查")
        print("=" * 70)
        print()
        
        installed_count = 0
        total_count = len(tools)
        
        for tool_name, is_installed in results.items():
            tool_info = tools[tool_name]
            
            status = "✅" if is_installed else "❌"
            print(f"{status} {tool_name:<15} {tool_info['description']}")
            
            if is_installed:
                installed_count += 1
                version = self.get_tool_version(tool_name, tool_info['check_cmd'])
                if version:
                    print(f"   版本：{version[:60]}")
            else:
                print(f"   安装：{tool_info['install_cmd']}")
            
            print()
        
        print("-" * 70)
        print(f"总计：{installed_count}/{total_count} 个工具已安装")
        
        if installed_count == total_count:
            print("✅ 所有工具已就绪！")
        else:
            missing = total_count - installed_count
            print(f"⚠️  缺少 {missing} 个工具，请安装后再使用")
        
        print()


def main():
    """主函数"""
    print()
    print("=" * 70)
    print("  智能编排器 - 工具依赖检查")
    print("=" * 70)
    
    checker = ToolChecker()
    
    # 检查 Phase-0 工具
    phase0_results = checker.check_all_tools(checker.phase0_tools)
    checker.print_report("Phase-0 资产收集", checker.phase0_tools, phase0_results)
    
    # 检查 Phase-2 工具
    phase2_results = checker.check_all_tools(checker.phase2_tools)
    checker.print_report("Phase-2 漏洞检测", checker.phase2_tools, phase2_results)
    
    # 总体总结
    print("=" * 70)
    print("  总结")
    print("=" * 70)
    print()
    
    all_installed = all(phase0_results.values()) and all(phase2_results.values())
    
    if all_installed:
        print("✅ 所有工具已安装，可以使用真实模式！")
        print()
        print("下一步:")
        print("  1. 运行 Phase-0 测试：python test_phase0_real.py")
        print("  2. 修改适配器使用真实工具调用")
        print("  3. 在服务器上部署并测试")
    else:
        print("⚠️  部分工具未安装")
        print()
        print("建议:")
        print("  1. 根据上方提示安装缺失的工具")
        print("  2. 或者使用模拟模式进行开发测试")
        print()
        print("如果只想测试 Phase-0，至少需要安装:")
        print("  - nmap")
        print("  - whatweb")
        print()
    
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
