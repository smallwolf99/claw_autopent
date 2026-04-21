#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-2 漏洞检测适配器

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
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase2Adapter:
    """Phase-2 漏洞检测适配器"""
    
    def __init__(self):
        """初始化 Phase-2 适配器"""
        self.tools = {
            'nuclei': self._call_nuclei,
            'afrog': self._call_afrog,
            'nikto': self._call_nikto,
            'zap': self._call_zap,
            'sqlmap': self._call_sqlmap,  # 新增 SQLMap
        }
        logger.info("Phase-2 漏洞检测适配器初始化完成（集成 ZAP-CLI + SQLMap）")
    
    async def detect(self, assets: List[Dict[str, Any]], 
                    test_strategy: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行漏洞检测
        
        Args:
            assets: 资产列表
            test_strategy: 测试策略（可选）
            
        Returns:
            漏洞列表
        """
        logger.info(f"开始漏洞检测：{len(assets)} 个资产")
        
        vulnerabilities = []
        
        # 对每个资产执行检测
        for asset in assets:
            vulns = await self._scan_asset(asset, test_strategy)
            vulnerabilities.extend(vulns)
        
        logger.info(f"漏洞检测完成：发现 {len(vulnerabilities)} 个漏洞")
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
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        vulnerabilities = []
        for result in results:
            if isinstance(result, Exception):
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
            tools.append('zap')  # ZAP 专注于 Web 应用扫描
            tools.append('sqlmap')  # SQLMap 专项检测 SQL 注入
        
        # 如果有高风险，添加 Afrog
        if test_strategy:
            risk_score = test_strategy.get('risk_score', 0)
            if risk_score >= 60:
                tools.append('afrog')
        
        return tools
    
    async def _call_nuclei(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Nuclei 进行模板化漏洞扫描"""
        logger.info(f"调用 Nuclei: {target}")
        
        try:
            # 模拟调用
            # cmd = f"nuclei -u {target} -json -o /tmp/nuclei.json"
            # result = await asyncio.create_subprocess_shell(cmd, ...)
            
            # 模拟返回
            await asyncio.sleep(0.5)
            return [
                {
                    "id": "CVE-2021-44228",
                    "name": "Apache Log4j2 RCE",
                    "severity": "critical",
                    "target": target,
                    "description": "Apache Log4j2 远程代码执行漏洞",
                    "tool": "nuclei",
                    "verified": False
                },
                {
                    "id": "CVE-2020-5410",
                    "name": "Spring Framework RCE",
                    "severity": "high",
                    "target": target,
                    "description": "Spring Framework 远程代码执行漏洞",
                    "tool": "nuclei",
                    "verified": False
                }
            ]
        except Exception as e:
            logger.error(f"Nuclei 调用失败：{e}")
            return []
    
    async def _call_afrog(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Afrog 进行 PoC 验证扫描"""
        logger.info(f"调用 Afrog: {target}")
        
        try:
            # 模拟调用
            # cmd = f"afrog -t {target} -json"
            
            # 模拟返回
            await asyncio.sleep(0.5)
            return [
                {
                    "id": "CVE-2017-12617",
                    "name": "Apache Tomcat RCE",
                    "severity": "high",
                    "target": target,
                    "description": "Apache Tomcat PUT 方法任意文件上传",
                    "tool": "afrog",
                    "verified": True
                }
            ]
        except Exception as e:
            logger.error(f"Afrog 调用失败：{e}")
            return []
    
    async def _call_nikto(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 Nikto 进行 Web 漏洞扫描"""
        logger.info(f"调用 Nikto: {target}")
        
        try:
            # 模拟调用
            # cmd = f"nikto -h {target} -Format json"
            
            # 模拟返回
            await asyncio.sleep(0.5)
            return [
                {
                    "id": "NIKTO-001",
                    "name": "Directory Indexing Enabled",
                    "severity": "medium",
                    "target": target,
                    "description": "目录列表功能已启用，可能泄露敏感信息",
                    "tool": "nikto",
                    "verified": False
                },
                {
                    "id": "NIKTO-002",
                    "name": "Sensitive File Exposure",
                    "severity": "low",
                    "target": target,
                    "description": "敏感文件暴露（.git/config）",
                    "tool": "nikto",
                    "verified": False
                }
            ]
        except Exception as e:
            logger.error(f"Nikto 调用失败：{e}")
            return []
    
    async def _call_zap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 ZAP-CLI 进行 Web 应用漏洞扫描
        
        ZAP (OWASP Zed Attack Proxy) 是一个功能全面的 Web 应用安全扫描器
        
        Args:
            target: 扫描目标 URL
            asset: 资产信息
            
        Returns:
            漏洞列表
        """
        logger.info(f"调用 ZAP-CLI: {target}")
        
        try:
            # 真实调用示例（取消注释以使用）
            # 启动 ZAP 扫描
            # cmd_start = f"zap-cli start-options '--port 8080'"
            # await asyncio.create_subprocess_shell(cmd_start)
            
            # 打开目标 URL
            # cmd_open = f"zap-cli open-url {target}"
            # await asyncio.create_subprocess_shell(cmd_open)
            
            # 执行主动扫描
            # cmd_scan = f"zap-cli active-scan --scanners all {target}"
            # process = await asyncio.create_subprocess_shell(cmd_scan)
            # await process.wait()
            
            # 获取扫描结果（JSON 格式）
            # cmd_report = f"zap-cli report -o /tmp/zap_report.json -f json"
            # result = await asyncio.create_subprocess_shell(cmd_report, stdout=asyncio.subprocess.PIPE)
            # output, _ = await result.communicate()
            # vulns = json.loads(output)
            
            # 模拟返回（实际使用时替换为真实结果）
            await asyncio.sleep(0.8)  # ZAP 扫描时间较长
            
            return [
                {
                    "id": "ZAP-001",
                    "name": "SQL Injection",
                    "severity": "high",
                    "target": target,
                    "description": "发现 SQL 注入漏洞，攻击者可窃取数据库数据",
                    "tool": "zap",
                    "verified": False,
                    "zap_risk": "High",
                    "zap_confidence": "Medium",
                    "zap_solution": "使用参数化查询或预编译语句",
                    "zap_reference": "https://owasp.org/www-community/attacks/SQL_Injection"
                },
                {
                    "id": "ZAP-002",
                    "name": "Cross-Site Scripting (Reflected)",
                    "severity": "medium",
                    "target": target,
                    "description": "发现反射型 XSS 漏洞，攻击者可注入恶意脚本",
                    "tool": "zap",
                    "verified": False,
                    "zap_risk": "Medium",
                    "zap_confidence": "Medium",
                    "zap_solution": "对所有用户输入进行适当的 HTML 编码",
                    "zap_reference": "https://owasp.org/www-community/attacks/xss/"
                },
                {
                    "id": "ZAP-003",
                    "name": "Missing Anti-clickjacking Header",
                    "severity": "low",
                    "target": target,
                    "description": "缺少 X-Frame-Options 头部，可能存在点击劫持风险",
                    "tool": "zap",
                    "verified": False,
                    "zap_risk": "Low",
                    "zap_confidence": "High",
                    "zap_solution": "添加 X-Frame-Options: DENY 或 SAMEORIGIN 头部",
                    "zap_reference": "https://owasp.org/www-community/attacks/Clickjacking"
                },
                {
                    "id": "ZAP-004",
                    "name": "Cookie Without Secure Flag",
                    "severity": "medium",
                    "target": target,
                    "description": "Cookie 未设置 Secure 标志，可能通过非 HTTPS 连接泄露",
                    "tool": "zap",
                    "verified": False,
                    "zap_risk": "Medium",
                    "zap_confidence": "High",
                    "zap_solution": "为 Cookie 设置 Secure 和 HttpOnly 标志",
                    "zap_reference": "https://owasp.org/www-community/controls/SecureCookieAttribute"
                }
            ]
        except Exception as e:
            logger.error(f"ZAP-CLI 调用失败：{e}")
            return []
    
    async def _call_sqlmap(self, target: str, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """调用 SQLMap 进行 SQL 注入自动化检测
        
        SQLMap 是业界最强大的 SQL 注入检测和利用工具
        
        Args:
            target: 扫描目标 URL
            asset: 资产信息
            
        Returns:
            漏洞列表
        """
        logger.info(f"调用 SQLMap: {target}")
        
        try:
            # 真实调用示例（取消注释以使用）
            # 基础扫描
            # cmd = f"sqlmap -u \"{target}\" --batch --forms --crawl=1 --json"
            
            # 深度扫描（包含 POST 数据）
            # cmd = f"sqlmap -u \"{target}\" --batch --forms --crawl=2 --technique=BEUSTQ --json"
            
            # 执行命令
            # process = await asyncio.create_subprocess_shell(
            #     cmd,
            #     stdout=asyncio.subprocess.PIPE,
            #     stderr=asyncio.subprocess.PIPE
            # )
            # stdout, stderr = await process.communicate()
            
            # 解析 JSON 输出
            # if stdout:
            #     vulns = json.loads(stdout)
            # else:
            #     vulns = []
            
            # 模拟返回（实际使用时替换为真实结果）
            await asyncio.sleep(1.0)  # SQLMap 扫描时间较长
            
            return [
                {
                    "id": "SQLMAP-001",
                    "name": "SQL Injection - Boolean-based Blind",
                    "severity": "high",
                    "target": target,
                    "description": "发现布尔盲注 SQL 注入漏洞，可提取数据库数据",
                    "tool": "sqlmap",
                    "verified": True,  # SQLMap 验证过的
                    "sqlmap_type": "boolean-based blind",
                    "sqlmap_technique": "B",
                    "sqlmap_payload": "id=1' AND 1234=1234",
                    "sqlmap_dbms": "MySQL",
                    "sqlmap_database": "target_db",
                    "sqlmap_table": "users",
                    "sqlmap_column": "id, username, password",
                    "sqlmap_confidence": 95
                },
                {
                    "id": "SQLMAP-002",
                    "name": "SQL Injection - Time-based Blind",
                    "severity": "high",
                    "target": target,
                    "description": "发现时间盲注 SQL 注入漏洞，可通过延迟提取数据",
                    "tool": "sqlmap",
                    "verified": True,
                    "sqlmap_type": "time-based blind",
                    "sqlmap_technique": "T",
                    "sqlmap_payload": "id=1' AND SLEEP(5)",
                    "sqlmap_dbms": "MySQL",
                    "sqlmap_database": "target_db",
                    "sqlmap_table": "users",
                    "sqlmap_column": "id, username, password",
                    "sqlmap_confidence": 90
                },
                {
                    "id": "SQLMAP-003",
                    "name": "SQL Injection - UNION Query",
                    "severity": "critical",
                    "target": target,
                    "description": "发现 UNION 查询 SQL 注入漏洞，可直接获取数据库内容",
                    "tool": "sqlmap",
                    "verified": True,
                    "sqlmap_type": "UNION query",
                    "sqlmap_technique": "U",
                    "sqlmap_payload": "id=1' UNION SELECT NULL,username,password FROM users--",
                    "sqlmap_dbms": "MySQL",
                    "sqlmap_database": "target_db",
                    "sqlmap_table": "users",
                    "sqlmap_column": "id, username, password",
                    "sqlmap_confidence": 98
                }
            ]
        except Exception as e:
            logger.error(f"SQLMap 调用失败：{e}")
            return []
    
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
                norm_vuln['zap_risk'] = vuln.get('zap_risk', '')
                norm_vuln['zap_confidence'] = vuln.get('zap_confidence', '')
                norm_vuln['zap_solution'] = vuln.get('zap_solution', '')
                norm_vuln['zap_reference'] = vuln.get('zap_reference', '')
                # 将 ZAP 的解决方案添加到 remediation 字段
                if not norm_vuln['remediation'] and norm_vuln['zap_solution']:
                    norm_vuln['remediation'] = norm_vuln['zap_solution']
                # 将 ZAP 的参考链接添加到 references 字段
                if norm_vuln['zap_reference'] and norm_vuln['zap_reference'] not in norm_vuln['references']:
                    norm_vuln['references'].append(norm_vuln['zap_reference'])
            
            # SQLMap 特有字段
            if vuln.get('tool') == 'sqlmap':
                norm_vuln['sqlmap_type'] = vuln.get('sqlmap_type', '')
                norm_vuln['sqlmap_technique'] = vuln.get('sqlmap_technique', '')
                norm_vuln['sqlmap_payload'] = vuln.get('sqlmap_payload', '')
                norm_vuln['sqlmap_dbms'] = vuln.get('sqlmap_dbms', '')
                norm_vuln['sqlmap_database'] = vuln.get('sqlmap_database', '')
                norm_vuln['sqlmap_table'] = vuln.get('sqlmap_table', '')
                norm_vuln['sqlmap_column'] = vuln.get('sqlmap_column', '')
                norm_vuln['sqlmap_confidence'] = vuln.get('sqlmap_confidence', 0)
                # SQLMap 验证过的漏洞标记为已验证
                if vuln.get('verified'):
                    norm_vuln['verified'] = True
                # 添加 SQL 注入修复建议
                if not norm_vuln['remediation']:
                    norm_vuln['remediation'] = "使用参数化查询或预编译语句；对所有用户输入进行严格的验证和过滤；使用 ORM 框架"
                # 添加参考链接
                sqli_references = [
                    "https://owasp.org/www-community/attacks/SQL_Injection",
                    "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
                ]
                for ref in sqli_references:
                    if ref not in norm_vuln['references']:
                        norm_vuln['references'].append(ref)
            
            normalized.append(norm_vuln)
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        normalized.sort(key=lambda x: severity_order.get(x['severity'], 5))
        
        return normalized
