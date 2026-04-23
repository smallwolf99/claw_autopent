#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-2 漏洞检测适配器 - 真实工具调用版本

集成工具:
- Nuclei: 模板化漏洞扫描
- Afrog: PoC 验证扫描
- Nikto: Web 漏洞扫描
- ZAP-CLI: OWASP Zed Attack Proxy 全栈扫描
- SQLMap: SQL 注入自动化检测工具

提供统一的异步接口，调用这些工具并标准化输出。
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# 使用统一日志模块
from utils.logger import setup_logger

# 使用通用工具调用基类
from adapters.base_tool_adapter import BaseToolAdapter


class Phase2Adapter(BaseToolAdapter):
    """Phase-2 漏洞检测适配器（真实工具调用）"""
    
    ZAPCLI_PATHS = [
        "zap-cli",  # PATH 中
        "/home/ubuntu/.local/bin/zap-cli",
        "~/.local/bin/zap-cli",
        "/usr/local/bin/zap-cli",
        "/usr/bin/zap-cli",
    ]
    
    def __init__(self, max_concurrent: int = 3):
        """初始化 Phase-2 适配器"""
        super().__init__(max_concurrent=max_concurrent)
        self.zapcli_path = self._find_zapcli_path()
        self.tools = {
            'nuclei': self._call_nuclei,
            'afrog': self._call_afrog,
            'nikto': self._call_nikto,
            'zap': self._call_zap,
            'sqlmap': self._call_sqlmap,
        }
        self.logger.info(f"Phase-2 漏洞检测适配器初始化完成（真实工具调用）")
        self.logger.info(f"ZAP-CLI 路径：{self.zapcli_path}")
    
    def _find_zapcli_path(self) -> str:
        """查找 zap-cli 的可执行路径"""
        import os
        import subprocess
        
        for path in self.ZAPCLI_PATHS:
            expanded_path = os.path.expanduser(path)
            try:
                # 检查文件是否存在且可执行
                if os.path.isfile(expanded_path) and os.access(expanded_path, os.X_OK):
                    return expanded_path
            except:
                continue
        
        # 尝试 which 命令
        try:
            result = subprocess.run(
                ["which", "zap-cli"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        # 默认返回 zap-cli，让系统尝试在 PATH 中查找
        return "zap-cli"
    
    async def detect(self, assets: List[Dict[str, Any]], 
                    test_strategy: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行漏洞检测
        
        Args:
            assets: 资产列表
            test_strategy: 测试策略（可选）
            
        Returns:
            漏洞列表
        """
        self.logger.info(f"开始漏洞检测：{len(assets)} 个资产")
        
        vulnerabilities = []
        
        # 对每个资产执行检测
        for asset in assets:
            vulns = await self._scan_asset(asset, test_strategy)
            vulnerabilities.extend(vulns)
        
        self.logger.info(f"漏洞检测完成：发现 {len(vulnerabilities)} 个漏洞")
        return vulnerabilities
    
    async def _scan_asset(self, asset: Dict[str, Any], 
                         test_strategy: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """扫描单个资产"""
        target = asset.get('url') or asset.get('host', '')
        if not target:
            return []
        
        # 根据测试策略选择工具
        tools_to_use = self._select_tools(asset, test_strategy)
        
        tasks = []
        for tool_name in tools_to_use:
            if tool_name in self.tools:
                tasks.append(self.tools[tool_name](target, asset))
        
        # 使用基类的并发控制
        results = await self.gather_with_concurrency(tasks, concurrency=3)
        
        vulnerabilities = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"工具执行失败：{result}")
                continue
            if result:
                vulnerabilities.extend(result)
        
        return vulnerabilities
    
    def _select_tools(self, asset: Dict[str, Any], 
                     test_strategy: Optional[Dict[str, Any]]) -> List[str]:
        """根据资产和策略选择工具"""
        tools = ['nuclei']  # 默认使用 Nuclei
        
        # 如果是 Web 资产，添加 Nikto、ZAP 和 SQLMap
        if asset.get('type') == 'web' or 'url' in asset:
            tools.append('nikto')
            tools.append('zap')
            tools.append('sqlmap')
        
        # 如果策略指定了工具，使用指定的
        if test_strategy and 'tools' in test_strategy:
            return test_strategy['tools']
        
        return tools
    
    async def _call_nuclei(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Nuclei 进行模板化漏洞扫描"""
        self.logger.info(f"调用 Nuclei: {target}")
        
        cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 10 -retries 2 -severity high,critical"
        
        def parse_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
            vulnerabilities = []
            if stdout.strip():
                for line in stdout.split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            vuln = self._normalize_nuclei_vuln(data, target)
                            if vuln:
                                vulnerabilities.append(vuln)
                        except json.JSONDecodeError:
                            continue
            
            if not vulnerabilities and stderr:
                self.logger.warning(f"Nuclei 错误：{stderr[:200]}")
            
            return vulnerabilities
        
        return await self.call_tool_with_retry(
            cmd=cmd,
            timeout=900,
            parse_func=parse_output,
            max_retries=2
        )
    
    def _normalize_nuclei_vuln(self, data: Dict[str, Any], target: str) -> Optional[Dict[str, Any]]:
        """标准化 Nuclei 漏洞格式"""
        try:
            return {
                "type": "vulnerability",
                "target": target,
                "tool": "nuclei",
                "name": data.get('info', {}).get('name', 'Unknown'),
                "severity": data.get('info', {}).get('severity', 'info').lower(),
                "description": data.get('info', {}).get('description', ''),
                "evidence": data.get('matched-at', ''),
                "references": data.get('info', {}).get('reference', []),
                "tags": data.get('info', {}).get('tags', []),
                "cwe_id": data.get('info', {}).get('classification', {}).get('cwe-id', []),
                "cvss_score": data.get('info', {}).get('classification', {}).get('cvss-metrics', ''),
                "remediation": f"参考 Nuclei 模板：{data.get('template-id', '')}",
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"解析 Nuclei 漏洞失败：{e}")
            return None
    
    async def _call_afrog(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Afrog 进行 PoC 验证扫描"""
        self.logger.info(f"调用 Afrog: {target}")
        
        cmd = f"afrog -target {target} -json -silent"
        
        def parse_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
            vulnerabilities = []
            if stdout.strip():
                try:
                    data = json.loads(stdout.strip())
                    if isinstance(data, list):
                        for item in data:
                            vuln = self._normalize_afrog_vuln(item, target)
                            if vuln:
                                vulnerabilities.append(vuln)
                    elif isinstance(data, dict):
                        vuln = self._normalize_afrog_vuln(data, target)
                        if vuln:
                            vulnerabilities.append(vuln)
                except json.JSONDecodeError:
                    pass
            
            return vulnerabilities
        
        return await self.call_tool(
            cmd=cmd,
            timeout=300,
            parse_func=parse_output
        )
    
    def _normalize_afrog_vuln(self, data: Dict[str, Any], target: str) -> Optional[Dict[str, Any]]:
        """标准化 Afrog 漏洞格式"""
        try:
            return {
                "type": "vulnerability",
                "target": target,
                "tool": "afrog",
                "name": data.get('Name', 'Unknown'),
                "severity": data.get('Severity', 'info').lower(),
                "description": data.get('Description', ''),
                "evidence": data.get('FullURL', ''),
                "references": [],
                "tags": data.get('Tags', []),
                "cwe_id": [],
                "cvss_score": '',
                "remediation": data.get('Remediation', ''),
                "confidence": 0.85
            }
        except Exception as e:
            logger.error(f"解析 Afrog 漏洞失败：{e}")
            return None
    
    async def _call_nikto(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Nikto 进行 Web 漏洞扫描"""
        self.logger.info(f"调用 Nikto: {target}")
        
        cmd = f"nikto -h {target} -timeout 30"
        
        def parse_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
            if not stdout.strip():
                return []
            
            vulnerabilities = []
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('+'):
                    continue
                
                vuln = {
                    "type": "vulnerability",
                    "target": target,
                    "tool": "nikto",
                    "name": "Nikto Detection",
                    "severity": "medium",
                    "description": line[1:].strip(),
                    "evidence": line,
                    "references": [],
                    "tags": [],
                    "cwe_id": [],
                    "cvss_score": '',
                    "remediation": "检查相关配置和安全设置",
                    "confidence": 0.7
                }
                
                if 'OSVDB-' in line:
                    import re
                    osvdb_match = re.search(r'OSVDB-(\d+)', line)
                    if osvdb_match:
                        vuln['references'].append(f"https://osvdb.org/show/osvdb/{osvdb_match.group(1)}")
                
                line_lower = line.lower()
                if any(word in line_lower for word in ['critical', 'dangerous', 'exploit']):
                    vuln['severity'] = 'high'
                    vuln['confidence'] = 0.85
                
                vulnerabilities.append(vuln)
            
            return vulnerabilities
        
        return await self.call_tool(
            cmd=cmd,
            timeout=600,
            parse_func=parse_output
        )
    
    def _parse_nikto_text(self, output: str, target: str) -> List[Dict[str, Any]]:
        """解析 Nikto 文本输出"""
        vulnerabilities = []
        
        # Nikto 输出格式示例：
        # + /: Contains about 3436 images.
        # + /admin.php: PHP admin page found.
        # + OSVDB-1234: /test.php: Vulnerable script found
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('+'):
                continue
            
            # 提取漏洞信息
            vuln = {
                "type": "vulnerability",
                "target": target,
                "tool": "nikto",
                "name": "Nikto Detection",
                "severity": "medium",
                "description": line[1:].strip(),  # 去掉开头的 +
                "evidence": line,
                "references": [],
                "tags": [],
                "cwe_id": [],
                "cvss_score": '',
                "remediation": "检查相关配置和安全设置",
                "confidence": 0.7
            }
            
            # 尝试提取 OSVDB 编号
            if 'OSVDB-' in line:
                import re
                osvdb_match = re.search(r'OSVDB-(\d+)', line)
                if osvdb_match:
                    vuln['references'].append(f"https://osvdb.org/show/osvdb/{osvdb_match.group(1)}")
            
            # 根据关键词判断严重程度
            line_lower = line.lower()
            if any(word in line_lower for word in ['critical', 'dangerous', 'exploit']):
                vuln['severity'] = 'high'
                vuln['confidence'] = 0.85
            elif any(word in line_lower for word in ['warning', 'caution']):
                vuln['severity'] = 'medium'
                vuln['confidence'] = 0.7
            
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _normalize_nikto_vuln(self, data: Dict[str, Any], target: str) -> Optional[Dict[str, Any]]:
        """标准化 Nikto 漏洞格式"""
        try:
            severity_map = {
                'CRITICAL': 'critical',
                'HIGH': 'high',
                'MEDIUM': 'medium',
                'LOW': 'low',
                'INFO': 'info'
            }
            
            return {
                "type": "vulnerability",
                "target": target,
                "tool": "nikto",
                "name": data.get('id', 'Unknown'),
                "severity": severity_map.get(data.get('severity', 'info'), 'info'),
                "description": data.get('msg', ''),
                "evidence": f"{target}{data.get('url', '')}",
                "references": data.get('references', []),
                "tags": [],
                "cwe_id": [],
                "cvss_score": '',
                "remediation": '',
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"解析 Nikto 漏洞失败：{e}")
            return None
    
    async def _call_zap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 ZAP-CLI 进行 Web 应用扫描"""
        self.logger.info(f"调用 ZAP-CLI: {target}")
        
        # 检查 ZAP 是否运行
        zap_running = await self._check_zap_status()
        if not zap_running:
            self.logger.warning("ZAP 服务未运行，尝试启动 ZAP...")
            # 尝试自动启动 ZAP
            started = await self._try_start_zap()
            if not started:
                self.logger.warning("无法启动 ZAP，跳过 ZAP 扫描")
                self.logger.info("请手动启动 ZAP: zap-cli start")
                return []
            # 等待 ZAP 启动
            await asyncio.sleep(3)
        
        report_file = f"/tmp/zap_report_{abs(hash(target))}.json"
        cmd = f"{self.zapcli_path} -p 8080 quick-scan -s all -f json -o {report_file} {target}"
        
        self.logger.info(f"执行 ZAP 扫描：{cmd}")
        
        def parse_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
            vulnerabilities = []
            try:
                import os
                if os.path.exists(report_file):
                    self.logger.info(f"读取 ZAP 报告：{report_file}")
                    with open(report_file, 'r') as f:
                        data = json.load(f)
                        sites = data.get('site', [])
                        if sites:
                            alerts = sites[0].get('alerts', [])
                            self.logger.info(f"ZAP 发现 {len(alerts)} 个警报")
                            for alert in alerts:
                                normalized = self._normalize_zap_vuln(alert, target)
                                if normalized:
                                    vulnerabilities.append(normalized)
                    
                    # 清理临时文件
                    if os.path.exists(report_file):
                        os.remove(report_file)
                else:
                    self.logger.warning(f"ZAP 报告文件不存在：{report_file}")
                    self.logger.error(f"可能原因:")
                    self.logger.error(f"  1. ZAP 扫描失败或被中断")
                    self.logger.error(f"  2. 目标无法访问：{target}")
                    self.logger.error(f"  3. ZAP 配置问题")
                    self.logger.debug(f"stdout: {stdout[:1000] if stdout else 'empty'}")
                    self.logger.debug(f"stderr: {stderr[:1000] if stderr else 'empty'}")
                    
            except (FileNotFoundError, json.JSONDecodeError, KeyError, IndexError) as e:
                self.logger.error(f"读取 ZAP 报告失败：{e}")
                self.logger.error(f"报告文件：{report_file}")
                self.logger.debug(f"stdout: {stdout[:1000] if stdout else 'empty'}")
                self.logger.debug(f"stderr: {stderr[:1000] if stderr else 'empty'}")
            
            return vulnerabilities
        
        # 使用 call_tool_with_retry 增加重试机制
        return await self.call_tool_with_retry(
            cmd=cmd,
            timeout=900,
            parse_func=parse_output,
            max_retries=2,
            retry_delay=5
        )
    
    def normalize_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """标准化漏洞格式
        
        Args:
            vulnerabilities: 原始漏洞列表
            
        Returns:
            标准化漏洞列表
        """
        normalized = []
        
        for vuln in vulnerabilities:
            # 基础字段
            norm_vuln = {
                "id": vuln.get('id', 'UNKNOWN'),
                "name": vuln.get('name', 'Unknown Vulnerability'),
                "severity": vuln.get('severity', 'info').lower(),
                "target": vuln.get('target', ''),
                "description": vuln.get('description', ''),
                "tool": vuln.get('tool', 'unknown'),
                "verified": vuln.get('verified', False),
                "cvss_score": vuln.get('cvss_score'),
                "references": vuln.get('references', []),
                "remediation": vuln.get('remediation', '')
            }
            
            # ZAP 特有字段
            if vuln.get('tool') == 'zap':
                norm_vuln["cwe_id"] = vuln.get('cwe_id', [])
                norm_vuln["confidence"] = vuln.get('confidence', 0.8)
            
            # Nuclei 特有字段
            elif vuln.get('tool') == 'nuclei':
                norm_vuln["tags"] = vuln.get('tags', [])
                norm_vuln["template_id"] = vuln.get('template_id', '')
            
            # SQLMap 特有字段
            elif vuln.get('tool') == 'sqlmap':
                norm_vuln["injection_type"] = vuln.get('injection_type', '')
                norm_vuln["technique"] = vuln.get('technique', '')
            
            normalized.append(norm_vuln)
        
        return normalized
    
    async def _try_start_zap(self) -> bool:
        """尝试启动 ZAP 服务"""
        try:
            self.logger.info("尝试启动 ZAP 服务...")
            cmd = f"{self.zapcli_path} start"
            result = await asyncio.create_subprocess_exec(
                *cmd.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=30)
            
            if result.returncode == 0:
                self.logger.info("ZAP 服务启动成功")
                return True
            else:
                stderr_text = stderr.decode('utf-8', errors='replace').strip()
                self.logger.warning(f"启动 ZAP 失败：{stderr_text}")
                return False
                
        except Exception as e:
            self.logger.warning(f"启动 ZAP 异常：{e}")
            return False
    
    async def _check_zap_status(self) -> bool:
        """检查 ZAP 服务是否运行"""
        try:
            # 尝试不同的端口和命令组合
            commands_to_try = [
                f"{self.zapcli_path} -p 8080 status",  # 指定端口 8080
                f"{self.zapcli_path} status",  # 默认端口
                f"{self.zapcli_path} -p 8090 status",  # 备用端口
            ]
            
            for cmd in commands_to_try:
                try:
                    self.logger.debug(f"尝试检查 ZAP 状态：{cmd}")
                    result = await asyncio.create_subprocess_exec(
                        *cmd.split(),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=5)
                    
                    if result.returncode == 0:
                        self.logger.info("ZAP 服务运行正常")
                        return True
                    
                    # 记录错误信息
                    stderr_text = stderr.decode('utf-8', errors='replace').strip()
                    if stderr_text:
                        self.logger.debug(f"ZAP 状态检查响应：{stderr_text}")
                        
                except Exception as e:
                    self.logger.debug(f"命令 {cmd} 执行失败：{e}")
                    continue
            
            # 所有命令都失败
            self.logger.warning("ZAP 服务未响应（尝试了多个端口：8080, 默认，8090）")
            return False
            
        except Exception as e:
            self.logger.debug(f"检查 ZAP 状态失败：{e}")
            return False
    
    def _normalize_zap_vuln(self, data: Dict[str, Any], target: str) -> Optional[Dict[str, Any]]:
        """标准化 ZAP 漏洞格式"""
        try:
            severity_map = {
                'High': 'high',
                'Medium': 'medium',
                'Low': 'low',
                'Informational': 'info'
            }
            
            return {
                "type": "vulnerability",
                "target": target,
                "tool": "zap",
                "name": data.get('name', 'Unknown'),
                "severity": severity_map.get(data.get('riskdesc', '').split(' ')[0], 'info'),
                "description": data.get('desc', ''),
                "evidence": data.get('evidence', ''),
                "references": data.get('solution', []),
                "tags": [],
                "cwe_id": [data.get('cweid', '')] if data.get('cweid') else [],
                "wasc_id": [data.get('wascid', '')] if data.get('wascid') else [],
                "cvss_score": '',
                "remediation": data.get('solution', ''),
                "confidence": 0.85,
                "instances": data.get('instances', [])
            }
        except Exception as e:
            logger.error(f"解析 ZAP 漏洞失败：{e}")
            return None
    
    async def _call_sqlmap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 SQLMap 进行 SQL 注入检测"""
        self.logger.info(f"调用 SQLMap: {target}")
        
        cmd = f"sqlmap --batch --level=1 --risk=1 --output-dir=/tmp/sqlmap_{hash(target)} -u \"{target}\""
        
        def parse_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
            vulnerabilities = []
            if not stdout.strip():
                return vulnerabilities
            
            # 检测 SQL 注入的关键字
            sql_injection_keywords = [
                'is vulnerable',
                'SQL injection',
                'back-end DBMS',
                'injected parameter',
                'Type: '
            ]
            
            # 简单判断是否发现漏洞
            for keyword in sql_injection_keywords:
                if keyword.lower() in stdout.lower():
                    vulnerabilities.append({
                        "type": "vulnerability",
                        "target": target,
                        "tool": "sqlmap",
                        "name": "SQL Injection",
                        "severity": "high",
                        "description": f"检测到 SQL 注入漏洞",
                        "evidence": target,
                        "references": [],
                        "tags": ["sqli", "injection"],
                        "cwe_id": ["CWE-89"],
                        "cvss_score": '',
                        "remediation": "使用参数化查询，避免 SQL 拼接",
                        "confidence": 0.9,
                        "details": stdout[:1000]
                    })
                    break
            
            return vulnerabilities
        
        return await self.call_tool_with_retry(
            cmd=cmd,
            timeout=600,
            parse_func=parse_output,
            max_retries=1
        )
