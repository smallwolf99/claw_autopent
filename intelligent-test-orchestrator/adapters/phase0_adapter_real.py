#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-0 资产收集适配器 - 真实工具调用版本

集成工具:
- WhatWeb: Web 技术识别
- Nmap: 端口扫描
- Httpx: Web 探测
- Subfinder: 子域名收集

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


class Phase0Adapter:
    """Phase-0 资产收集适配器"""
    
    def __init__(self):
        """初始化 Phase-0 适配器"""
        self.tools = {
            'whatweb': self._call_whatweb,
            'nmap': self._call_nmap,
            'httpx': self._call_httpx,
            'subfinder': self._call_subfinder,
        }
        logger.info("Phase-0 资产收集适配器初始化完成（真实工具调用）")
    
    async def collect(self, target: str, tools: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """执行资产收集
        
        Args:
            target: 测试目标（URL/IP/域名）
            tools: 要使用的工具列表，None 表示使用所有工具
            
        Returns:
            资产列表
        """
        logger.info(f"开始资产收集：{target}")
        
        if tools is None:
            tools = list(self.tools.keys())
        
        assets = []
        
        # 并发执行多个工具
        tasks = []
        for tool_name in tools:
            if tool_name in self.tools:
                tasks.append(self.tools[tool_name](target))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整合结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"工具执行失败 {tools[i]}: {result}")
                continue
            
            if result:
                assets.extend(result)
        
        logger.info(f"资产收集完成：发现 {len(assets)} 个资产")
        return assets
    
    async def _call_whatweb(self, target: str) -> List[Dict[str, Any]]:
        """调用 WhatWeb 进行 Web 技术识别"""
        logger.info(f"调用 WhatWeb: {target}")
        
        try:
            # 真实调用 WhatWeb
            cmd = f"whatweb --color=never --quiet {target}"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"WhatWeb 执行失败：{stderr.decode()}")
                return []
            
            # 解析 WhatWeb 输出
            output = stdout.decode()
            technologies = self._parse_whatweb_output(output, target)
            
            return [{
                "type": "web",
                "url": target,
                "technologies": technologies,
                "source": "whatweb"
            }]
            
        except Exception as e:
            logger.error(f"WhatWeb 调用失败：{e}")
            return []
    
    def _parse_whatweb_output(self, output: str, target: str) -> List[Dict[str, Any]]:
        """解析 WhatWeb 输出"""
        technologies = []
        
        # 简单解析，提取技术名称
        # 示例输出：http://example.com [200] Country=RESERVED[ZZ], IP=93.184.216.34, Apache[2.4.52]
        import re
        
        # 提取方括号中的版本信息
        matches = re.findall(r'([A-Za-z]+)\[([^\]]+)\]', output)
        for name, version in matches:
            technologies.append({
                "name": name,
                "version": version,
                "confidence": 0.8
            })
        
        # 如果没有检测到具体技术，至少返回 HTTP 状态
        if not technologies:
            status_match = re.search(r'\[(\d{3})\]', output)
            if status_match:
                technologies.append({
                    "name": "HTTP",
                    "version": f"Status {status_match.group(1)}",
                    "confidence": 1.0
                })
        
        return technologies
    
    async def _call_nmap(self, target: str) -> List[Dict[str, Any]]:
        """调用 Nmap 进行端口扫描"""
        logger.info(f"调用 Nmap: {target}")
        
        try:
            # 真实调用 Nmap（快速扫描模式）
            # -sV: 版本检测
            # -sC: 默认脚本
            # -T4: 快速扫描
            # --open: 只显示开放端口
            cmd = f"nmap -sV -sC -T4 --open -oX - {target}"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Nmap 执行失败：{stderr.decode()}")
                return []
            
            # 解析 Nmap XML 输出
            ports = self._parse_nmap_xml(stdout.decode())
            
            return [{
                "type": "port",
                "host": target,
                "ports": ports,
                "source": "nmap"
            }]
            
        except Exception as e:
            logger.error(f"Nmap 调用失败：{e}")
            return []
    
    def _parse_nmap_xml(self, xml_output: str) -> List[Dict[str, Any]]:
        """解析 Nmap XML 输出"""
        ports = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_output)
            
            for host in root.findall('.//host'):
                for port in host.findall('.//port'):
                    port_id = port.get('portid')
                    protocol = port.get('protocol')
                    
                    state = port.find('state')
                    service = port.find('service')
                    
                    if state is not None and state.get('state') == 'open':
                        port_info = {
                            "port": int(port_id),
                            "protocol": protocol,
                            "state": "open"
                        }
                        
                        if service is not None:
                            port_info["service"] = service.get('name', 'unknown')
                            if service.get('version'):
                                port_info["version"] = service.get('version')
                            if service.get('product'):
                                port_info["product"] = service.get('product')
                        
                        ports.append(port_info)
        
        except Exception as e:
            logger.error(f"解析 Nmap XML 失败：{e}")
        
        return ports
    
    async def _call_httpx(self, target: str) -> List[Dict[str, Any]]:
        """调用 Httpx 进行 Web 探测"""
        logger.info(f"调用 Httpx: {target}")
        
        try:
            # 真实调用 Httpx
            cmd = f"httpx -u {target} -json -silent"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Httpx 执行失败：{stderr.decode()}")
                return []
            
            # 解析 JSON 输出
            output = stdout.decode().strip()
            if output:
                data = json.loads(output)
                return [{
                    "type": "web",
                    "url": target,
                    "status_code": data.get('status_code', 0),
                    "title": data.get('title', ''),
                    "tech": data.get('tech', []),
                    "source": "httpx"
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Httpx 调用失败：{e}")
            return []
    
    async def _call_subfinder(self, target: str) -> List[Dict[str, Any]]:
        """调用 Subfinder 进行子域名收集"""
        logger.info(f"调用 Subfinder: {target}")
        
        try:
            # 提取域名
            domain = target.split('//')[-1].split('/')[0]
            
            # 真实调用 Subfinder
            cmd = f"subfinder -d {domain} -json -silent"
            logger.info(f"执行命令：{cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Subfinder 执行失败：{stderr.decode()}")
                return []
            
            # 解析 JSON 输出（每行一个 JSON 对象）
            subdomains = []
            output = stdout.decode().strip()
            if output:
                for line in output.split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            subdomain = data.get('host', '')
                            if subdomain and subdomain not in subdomains:
                                subdomains.append(subdomain)
                        except:
                            continue
            
            return [{
                "type": "subdomain",
                "domain": domain,
                "subdomains": subdomains,
                "source": "subfinder"
            }]
            
        except Exception as e:
            logger.error(f"Subfinder 调用失败：{e}")
            return []
    
    def normalize_assets(self, assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """标准化资产格式
        
        将不同工具的输出统一为标准化的资产格式。
        
        Args:
            assets: 原始资产列表
            
        Returns:
            标准化资产列表
        """
        normalized = []
        
        for asset in assets:
            asset_type = asset.get('type', 'unknown')
            
            if asset_type == 'web':
                normalized.append(self._normalize_web_asset(asset))
            elif asset_type == 'port':
                normalized.append(self._normalize_port_asset(asset))
            elif asset_type == 'subdomain':
                normalized.extend(self._normalize_subdomain_asset(asset))
        
        return normalized
    
    def _normalize_web_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """标准化 Web 资产"""
        return {
            "url": asset.get('url', ''),
            "technologies": asset.get('technologies', []),
            "endpoints": [],
            "business_hints": {},
            "metadata": {
                "source": asset.get('source', ''),
                "status_code": asset.get('status_code', 0),
                "title": asset.get('title', '')
            }
        }
    
    def _normalize_port_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """标准化端口资产"""
        return {
            "host": asset.get('host', ''),
            "ports": asset.get('ports', []),
            "metadata": {
                "source": asset.get('source', '')
            }
        }
    
    def _normalize_subdomain_asset(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """标准化子域名资产"""
        domain = asset.get('domain', '')
        subdomains = asset.get('subdomains', [])
        
        return [{
            "type": "subdomain",
            "domain": subdomain,
            "parent_domain": domain,
            "metadata": {
                "source": asset.get('source', '')
            }
        } for subdomain in subdomains]
