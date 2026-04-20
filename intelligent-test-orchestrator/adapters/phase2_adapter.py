#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-2 漏洞检测适配器

集成工具:
- Nuclei: 模板化漏洞扫描
- Afrog: PoC 验证扫描
- Nikto: Web 漏洞扫描

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
        }
        logger.info("Phase-2 漏洞检测适配器初始化完成")
    
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
        
        # 如果是 Web 资产，添加 Nikto
        if asset.get('type') == 'web' or 'url' in asset:
            tools.append('nikto')
        
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
    
    def normalize_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """标准化漏洞格式
        
        Args:
            vulnerabilities: 原始漏洞列表
            
        Returns:
            标准化漏洞列表
        """
        normalized = []
        
        for vuln in vulnerabilities:
            normalized.append({
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
            })
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        normalized.sort(key=lambda x: severity_order.get(x['severity'], 5))
        
        return normalized
