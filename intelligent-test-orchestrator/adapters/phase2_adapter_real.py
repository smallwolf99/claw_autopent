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
import subprocess
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase2Adapter:
    """Phase-2 漏洞检测适配器（真实工具调用）"""
    
    def __init__(self):
        """初始化 Phase-2 适配器"""
        self.tools = {
            'nuclei': self._call_nuclei,
            'afrog': self._call_afrog,
            'nikto': self._call_nikto,
            'zap': self._call_zap,
            'sqlmap': self._call_sqlmap,
        }
        logger.info("Phase-2 漏洞检测适配器初始化完成（真实工具调用）")
    
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
                logger.error(f"工具执行失败：{result}")
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
        logger.info(f"调用 Nuclei: {target}")
        
        try:
            # 真实调用 Nuclei
            # -u: 目标 URL
            # -jsonl: JSON Lines 输出（兼容新版 Nuclei）
            # -silent: 静默模式
            # -timeout: 超时时间（秒）
            # -rate-limit: 每秒请求数限制（避免请求过快）
            cmd = f"nuclei -u {target} -jsonl -silent -timeout 30 -rate-limit 5"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 分钟超时
            )
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            # 记录详细日志
            if process.returncode != 0:
                logger.warning(f"Nuclei 返回码非 0: {process.returncode}")
                if error_output:
                    logger.warning(f"Nuclei 错误：{error_output[:500]}")
                # 继续尝试解析输出（可能有部分结果）
                # 返回码 2 通常表示参数错误或配置问题
                if process.returncode == 2:
                    logger.error(f"Nuclei 参数错误，请检查命令：{cmd}")
            
            # 解析 JSON 输出（每行一个 JSON 对象）
            vulnerabilities = []
            if output.strip():
                for line in output.split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            vuln = self._normalize_nuclei_vuln(data, target)
                            if vuln:
                                vulnerabilities.append(vuln)
                        except json.JSONDecodeError as e:
                            logger.debug(f"解析 Nuclei JSON 行失败：{e}")
                            continue
                
                logger.info(f"Nuclei 发现 {len(vulnerabilities)} 个漏洞")
            else:
                logger.info("Nuclei 没有输出（可能没有漏洞或模板未加载）")
                if error_output:
                    logger.warning(f"Nuclei 错误输出：{error_output[:200]}")
            
            return vulnerabilities
            
        except asyncio.TimeoutError:
            logger.warning(f"Nuclei 扫描超时：{target}")
            return []
        except Exception as e:
            logger.error(f"Nuclei 调用失败：{e}")
            return []
    
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
        logger.info(f"调用 Afrog: {target}")
        
        try:
            # 真实调用 Afrog
            # -target: 目标
            # -json: JSON 输出
            # -silent: 静默模式
            cmd = f"afrog -target {target} -json -silent"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300
            )
            
            if process.returncode != 0:
                logger.warning(f"Afrog 执行失败：{stderr.decode()}")
                return []
            
            # 解析 JSON 输出
            vulnerabilities = []
            output = stdout.decode().strip()
            if output:
                try:
                    data = json.loads(output)
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
                    logger.error(f"解析 Afrog JSON 失败")
            
            logger.info(f"Afrog 发现 {len(vulnerabilities)} 个漏洞")
            return vulnerabilities
            
        except asyncio.TimeoutError:
            logger.warning(f"Afrog 扫描超时：{target}")
            return []
        except Exception as e:
            logger.error(f"Afrog 调用失败：{e}")
            return []
    
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
        logger.info(f"调用 Nikto: {target}")
        
        try:
            # 尝试使用 JSON 格式输出
            # 注意：旧版本 Nikto 可能不支持 -Format json
            cmd = f"nikto -h {target} -Format json -timeout 10"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 分钟超时
            )
            
            output = stdout.decode()
            error_output = stderr.decode()
            
            # 如果返回码非 0，记录错误但不返回空
            if process.returncode != 0:
                logger.warning(f"Nikto 返回码非 0: {process.returncode}")
                if error_output:
                    logger.warning(f"Nikto 错误：{error_output[:200]}")
                # 继续尝试解析输出（可能有部分结果）
            
            # 解析 Nikto JSON 输出
            vulnerabilities = []
            if output.strip():
                try:
                    data = json.loads(output)
                    if isinstance(data, dict):
                        vulns = data.get('vulnerabilities', [])
                        if vulns:
                            for vuln in vulns:
                                normalized = self._normalize_nikto_vuln(vuln, target)
                                if normalized:
                                    vulnerabilities.append(normalized)
                            logger.info(f"Nikto 发现 {len(vulnerabilities)} 个漏洞")
                        else:
                            logger.info("Nikto 未发现漏洞（JSON 中 vulnerabilities 为空）")
                    else:
                        logger.warning(f"Nikto 输出格式异常：{type(data)}")
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 Nikto JSON 失败：{e}")
                    logger.warning(f"输出内容：{output[:200]}")
                    # 尝试文本解析（备用方案）
                    vulnerabilities = self._parse_nikto_text(output, target)
            else:
                logger.info("Nikto 没有输出内容")
            
            logger.info(f"Nikto 发现 {len(vulnerabilities)} 个漏洞")
            return vulnerabilities
            
        except asyncio.TimeoutError:
            logger.warning(f"Nikto 扫描超时：{target}")
            return []
        except Exception as e:
            logger.error(f"Nikto 调用失败：{e}")
            return []
    
    def _parse_nikto_text(self, output: str, target: str) -> List[Dict[str, Any]]:
        """解析 Nikto 文本输出（备用方案）"""
        vulnerabilities = []
        
        # 简单的文本解析逻辑
        lines = output.split('\n')
        for line in lines:
            if '+' in line and any(keyword in line.lower() for keyword in ['vuln', 'error', 'warning', 'found']):
                vulnerabilities.append({
                    "type": "vulnerability",
                    "target": target,
                    "tool": "nikto",
                    "name": "Nikto Detection",
                    "severity": "medium",
                    "description": line.strip(),
                    "evidence": line.strip(),
                    "references": [],
                    "tags": [],
                    "cwe_id": [],
                    "cvss_score": '',
                    "remediation": "检查相关配置",
                    "confidence": 0.7
                })
        
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
        logger.info(f"调用 ZAP-CLI: {target}")
        
        try:
            # 真实调用 ZAP-CLI
            # -p: ZAP 代理端口（服务器使用 8080）
            # 快速扫描模式
            cmd = f"zap-cli -p 8080 quick-scan -s all -f json -o /tmp/zap_report_{hash(target)}.json {target}"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=900  # 15 分钟超时
            )
            
            if process.returncode != 0:
                logger.warning(f"ZAP-CLI 执行失败：{stderr.decode()}")
                return []
            
            # 读取 JSON 报告
            report_file = f"/tmp/zap_report_{hash(target)}.json"
            vulnerabilities = []
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    alerts = data.get('site', [{}])[0].get('alerts', [])
                    for alert in alerts:
                        normalized = self._normalize_zap_vuln(alert, target)
                        if normalized:
                            vulnerabilities.append(normalized)
                
                # 清理临时文件
                import os
                if os.path.exists(report_file):
                    os.remove(report_file)
                    
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"读取 ZAP 报告失败：{e}")
            
            logger.info(f"ZAP-CLI 发现 {len(vulnerabilities)} 个漏洞")
            return vulnerabilities
            
        except asyncio.TimeoutError:
            logger.warning(f"ZAP-CLI 扫描超时：{target}")
            return []
        except Exception as e:
            logger.error(f"ZAP-CLI 调用失败：{e}")
            return []
    
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
        logger.info(f"调用 SQLMap: {target}")
        
        try:
            # 真实调用 SQLMap
            # --batch: 非交互模式
            # --level=1: 测试级别
            # --risk=1: 风险级别
            # --output-dir: 输出目录
            cmd = f"sqlmap --batch --level=1 --risk=1 --output-dir=/tmp/sqlmap_{hash(target)} -u \"{target}\""
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 分钟超时
            )
            
            if process.returncode != 0:
                logger.warning(f"SQLMap 执行失败：{stderr.decode()}")
                return []
            
            # 解析 SQLMap 输出
            vulnerabilities = []
            output = stdout.decode()
            
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
                if keyword.lower() in output.lower():
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
                        "details": output[:1000]  # 截取部分输出作为详情
                    })
                    break
            
            logger.info(f"SQLMap 发现 {len(vulnerabilities)} 个 SQL 注入漏洞")
            return vulnerabilities
            
        except asyncio.TimeoutError:
            logger.warning(f"SQLMap 扫描超时：{target}")
            return []
        except Exception as e:
            logger.error(f"SQLMap 调用失败：{e}")
            return []
