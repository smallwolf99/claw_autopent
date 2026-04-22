"""
健康检查模块 - 工具状态检测和自动恢复
"""

import asyncio
import subprocess
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import time
from pathlib import Path


class ToolHealth:
    """工具健康状态"""
    
    def __init__(self, tool_name: str):
        """初始化工具健康状态
        
        Args:
            tool_name: 工具名称
        """
        self.tool_name = tool_name
        self.installed = False
        self.path: Optional[str] = None
        self.version: Optional[str] = None
        self.last_check: Optional[float] = None
        self.check_count = 0
        self.fail_count = 0
        self.status = 'unknown'  # unknown, healthy, warning, unhealthy
        self.error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'tool_name': self.tool_name,
            'installed': self.installed,
            'path': self.path,
            'version': self.version,
            'status': self.status,
            'last_check': self.last_check,
            'check_count': self.check_count,
            'fail_count': self.fail_count,
            'error_message': self.error_message
        }


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        """初始化健康检查器"""
        self._tools: Dict[str, ToolHealth] = {}
        self._lock = threading.RLock()
        self._registered_tools = {
            'whatweb': self._check_whatweb,
            'nmap': self._check_nmap,
            'httpx': self._check_httpx,
            'subfinder': self._check_subfinder,
            'nuclei': self._check_nuclei,
            'afrog': self._check_afrog,
            'nikto': self._check_nikto,
            'zap-cli': self._check_zap_cli,
            'sqlmap': self._check_sqlmap,
            'python3': self._check_python3,
            'git': self._check_git,
        }
    
    def register_tool(self, tool_name: str, check_func) -> None:
        """注册自定义工具检查
        
        Args:
            tool_name: 工具名称
            check_func: 检查函数
        """
        with self._lock:
            self._registered_tools[tool_name] = check_func
    
    def _check_command_exists(self, tool_name: str) -> Optional[str]:
        """检查命令是否存在
        
        Returns:
            工具路径，不存在则返回 None
        """
        return shutil.which(tool_name)
    
    def _get_version(self, tool_name: str, version_args: List[str] = ['--version']) -> Optional[str]:
        """获取工具版本"""
        try:
            result = subprocess.run(
                [tool_name] + version_args,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip().split('\n')[0]
        except Exception:
            return None
    
    async def _check_whatweb(self) -> ToolHealth:
        """检查 WhatWeb"""
        health = ToolHealth('whatweb')
        health.path = self._check_command_exists('whatweb')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('whatweb')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'WhatWeb 未安装'
        
        return health
    
    async def _check_nmap(self) -> ToolHealth:
        """检查 Nmap"""
        health = ToolHealth('nmap')
        health.path = self._check_command_exists('nmap')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('nmap')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Nmap 未安装'
        
        return health
    
    async def _check_httpx(self) -> ToolHealth:
        """检查 httpx"""
        health = ToolHealth('httpx')
        health.path = self._check_command_exists('httpx')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('httpx')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'httpx 未安装'
        
        return health
    
    async def _check_subfinder(self) -> ToolHealth:
        """检查 subfinder"""
        health = ToolHealth('subfinder')
        health.path = self._check_command_exists('subfinder')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('subfinder')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'subfinder 未安装'
        
        return health
    
    async def _check_nuclei(self) -> ToolHealth:
        """检查 Nuclei"""
        health = ToolHealth('nuclei')
        health.path = self._check_command_exists('nuclei')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('nuclei')
            # 检查模板是否更新
            try:
                result = subprocess.run(
                    ['nuclei', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                health.status = 'healthy'
            except Exception as e:
                health.status = 'warning'
                health.error_message = f'Nuclei 执行失败：{str(e)}'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Nuclei 未安装'
        
        return health
    
    async def _check_afrog(self) -> ToolHealth:
        """检查 Afrog"""
        health = ToolHealth('afrog')
        health.path = self._check_command_exists('afrog')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('afrog')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Afrog 未安装'
        
        return health
    
    async def _check_nikto(self) -> ToolHealth:
        """检查 Nikto"""
        health = ToolHealth('nikto')
        health.path = self._check_command_exists('nikto')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('nikto')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Nikto 未安装'
        
        return health
    
    async def _check_zap_cli(self) -> ToolHealth:
        """检查 ZAP-CLI"""
        health = ToolHealth('zap-cli')
        health.path = self._check_command_exists('zap-cli')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('zap-cli')
            # 检查 ZAP 是否可连接
            try:
                result = subprocess.run(
                    ['zap-cli', '-p', '8080', 'status'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    health.status = 'healthy'
                else:
                    health.status = 'warning'
                    health.error_message = 'ZAP 服务未运行或无法连接'
            except Exception as e:
                health.status = 'warning'
                health.error_message = f'ZAP 连接检查失败：{str(e)}'
        else:
            health.status = 'unhealthy'
            health.error_message = 'ZAP-CLI 未安装'
        
        return health
    
    async def _check_sqlmap(self) -> ToolHealth:
        """检查 SQLMap"""
        health = ToolHealth('sqlmap')
        health.path = self._check_command_exists('sqlmap')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('sqlmap')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'SQLMap 未安装'
        
        return health
    
    async def _check_python3(self) -> ToolHealth:
        """检查 Python3"""
        health = ToolHealth('python3')
        health.path = self._check_command_exists('python3')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('python3')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Python3 未安装'
        
        return health
    
    async def _check_git(self) -> ToolHealth:
        """检查 Git"""
        health = ToolHealth('git')
        health.path = self._check_command_exists('git')
        health.installed = health.path is not None
        
        if health.installed:
            health.version = self._get_version('git')
            health.status = 'healthy'
        else:
            health.status = 'unhealthy'
            health.error_message = 'Git 未安装'
        
        return health
    
    async def check_tool(self, tool_name: str) -> ToolHealth:
        """检查单个工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具健康状态
        """
        with self._lock:
            if tool_name not in self._registered_tools:
                health = ToolHealth(tool_name)
                health.status = 'unknown'
                health.error_message = f'未知的工具：{tool_name}'
                return health
            
            check_func = self._registered_tools[tool_name]
        
        try:
            health = await check_func()
        except Exception as e:
            health = ToolHealth(tool_name)
            health.status = 'unhealthy'
            health.error_message = f'检查失败：{str(e)}'
        
        # 更新统计
        with self._lock:
            health.last_check = time.time()
            health.check_count += 1
            if health.status != 'healthy':
                health.fail_count += 1
            
            self._tools[tool_name] = health
        
        return health
    
    async def check_all_tools(self) -> Dict[str, ToolHealth]:
        """检查所有工具
        
        Returns:
            工具健康状态字典
        """
        tasks = [self.check_tool(name) for name in self._registered_tools.keys()]
        results = await asyncio.gather(*tasks)
        
        return {result.tool_name: result for result in results}
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康摘要"""
        with self._lock:
            total = len(self._tools)
            healthy = sum(1 for t in self._tools.values() if t.status == 'healthy')
            warning = sum(1 for t in self._tools.values() if t.status == 'warning')
            unhealthy = sum(1 for t in self._tools.values() if t.status == 'unhealthy')
            
            installed = sum(1 for t in self._tools.values() if t.installed)
            
            return {
                'total_tools': total,
                'healthy': healthy,
                'warning': warning,
                'unhealthy': unhealthy,
                'installed': installed,
                'not_installed': total - installed,
                'health_rate': f"{healthy / total * 100:.1f}%" if total > 0 else "N/A"
            }
    
    def print_health_report(self) -> None:
        """打印健康报告"""
        summary = self.get_health_summary()
        
        print("\n" + "=" * 60)
        print("  工具健康检查报告")
        print("=" * 60)
        print(f"\n总计：{summary['total_tools']} 个工具")
        print(f"✅ 健康：{summary['healthy']}")
        print(f"⚠️  警告：{summary['warning']}")
        print(f"❌ 异常：{summary['unhealthy']}")
        print(f"📦 已安装：{summary['installed']}")
        print(f"📦 未安装：{summary['not_installed']}")
        print(f"📊 健康率：{summary['health_rate']}")
        
        print("\n工具详情:")
        print("-" * 60)
        
        for tool_name, health in sorted(self._tools.items()):
            icon = "✅" if health.status == 'healthy' else "⚠️" if health.status == 'warning' else "❌"
            installed_str = "✓" if health.installed else "✗"
            
            print(f"{icon} {tool_name:15} [{installed_str}] {health.status:10} {health.version or ''}")
            
            if health.error_message:
                print(f"   └─ {health.error_message}")
        
        print("=" * 60 + "\n")


class AutoHealer:
    """自动恢复器"""
    
    def __init__(self, checker: HealthChecker):
        """初始化自动恢复器
        
        Args:
            checker: 健康检查器实例
        """
        self.checker = checker
        self._auto_heal_enabled = False
        self._heal_thread: Optional[threading.Thread] = None
        self._heal_interval = 300  # 5 分钟
    
    def enable_auto_heal(self, interval: int = 300) -> None:
        """启用自动恢复
        
        Args:
            interval: 检查间隔（秒）
        """
        if self._auto_heal_enabled:
            return
        
        self._heal_interval = interval
        self._auto_heal_enabled = True
        
        def heal_loop():
            while self._auto_heal_enabled:
                # 检查工具状态
                asyncio.run(self.checker.check_all_tools())
                
                # 尝试恢复失败的工具
                for tool_name, health in self.checker._tools.items():
                    if health.fail_count >= 3:
                        self._attempt_heal(tool_name)
                
                time.sleep(self._heal_interval)
        
        self._heal_thread = threading.Thread(target=heal_loop, daemon=True)
        self._heal_thread.start()
    
    def disable_auto_heal(self) -> None:
        """禁用自动恢复"""
        self._auto_heal_enabled = False
        if self._heal_thread:
            self._heal_thread.join(timeout=10)
    
    def _attempt_heal(self, tool_name: str) -> None:
        """尝试恢复工具
        
        Args:
            tool_name: 工具名称
        """
        print(f"🔧 尝试恢复工具：{tool_name}")
        
        # 这里可以实现具体的恢复逻辑
        # 例如：重启服务、清理缓存、重新安装等
        
        # 示例：重置失败计数
        with self.checker._lock:
            if tool_name in self.checker._tools:
                self.checker._tools[tool_name].fail_count = 0


# 便捷函数
def get_health_checker() -> HealthChecker:
    """获取健康检查器实例"""
    return HealthChecker()


async def check_tool_health(tool_name: str) -> ToolHealth:
    """检查工具健康"""
    checker = get_health_checker()
    return await checker.check_tool(tool_name)


async def check_all_tools_health() -> Dict[str, ToolHealth]:
    """检查所有工具健康"""
    checker = get_health_checker()
    return await checker.check_all_tools()


def print_tools_health_report() -> None:
    """打印工具健康报告"""
    checker = get_health_checker()
    checker.print_health_report()
