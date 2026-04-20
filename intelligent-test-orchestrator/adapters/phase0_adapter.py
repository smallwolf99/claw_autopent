#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-0 资产收集适配器

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
        logger.info("Phase-0 资产收集适配器初始化完成")
    
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
            # 模拟调用（实际使用时替换为真实命令）
            # cmd = f"whatweb --color=never --quiet {target}"
            # result = await asyncio.create_subprocess_shell(cmd, ...)
            
            # 模拟返回
            await asyncio.sleep(0.3)
            return [{
                "type": "web",
                "url": target,
                "technologies": [
                    {"name": "Nginx", "version": "1.18.0", "confidence": 0.9},
                    {"name": "PHP", "version": "7.4.3", "confidence": 0.8}
                ],
                "source": "whatweb"
            }]
        except Exception as e:
            logger.error(f"WhatWeb 调用失败：{e}")
            return []
    
    async def _call_nmap(self, target: str) -> List[Dict[str, Any]]:
        """调用 Nmap 进行端口扫描"""
        logger.info(f"调用 Nmap: {target}")
        
        try:
            # 模拟调用
            # cmd = f"nmap -sV -sC -oX - {target}"
            
            # 模拟返回
            await asyncio.sleep(0.3)
            return [{
                "type": "port",
                "host": target,
                "ports": [
                    {"port": 80, "protocol": "tcp", "service": "http", "version": "nginx 1.18.0"},
                    {"port": 443, "protocol": "tcp", "service": "https", "version": "nginx 1.18.0"}
                ],
                "source": "nmap"
            }]
        except Exception as e:
            logger.error(f"Nmap 调用失败：{e}")
            return []
    
    async def _call_httpx(self, target: str) -> List[Dict[str, Any]]:
        """调用 Httpx 进行 Web 探测"""
        logger.info(f"调用 Httpx: {target}")
        
        try:
            # 模拟调用
            # cmd = f"httpx -u {target} -json"
            
            # 模拟返回
            await asyncio.sleep(0.3)
            return [{
                "type": "web",
                "url": target,
                "status_code": 200,
                "title": "Test Site",
                "tech": ["nginx", "php"],
                "source": "httpx"
            }]
        except Exception as e:
            logger.error(f"Httpx 调用失败：{e}")
            return []
    
    async def _call_subfinder(self, target: str) -> List[Dict[str, Any]]:
        """调用 Subfinder 进行子域名收集"""
        logger.info(f"调用 Subfinder: {target}")
        
        try:
            # 模拟调用
            # cmd = f"subfinder -d {target} -json"
            
            # 模拟返回
            await asyncio.sleep(0.3)
            domain = target.split('//')[-1].split('/')[0]
            return [{
                "type": "subdomain",
                "domain": domain,
                "subdomains": [
                    f"www.{domain}",
                    f"api.{domain}",
                    f"admin.{domain}"
                ],
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
                "status_code": asset.get('status_code'),
                "title": asset.get('title'),
                "source": asset.get('source')
            }
        }
    
    def _normalize_port_asset(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """标准化端口资产"""
        return {
            "host": asset.get('host', ''),
            "ports": asset.get('ports', []),
            "metadata": {
                "source": asset.get('source')
            }
        }
    
    def _normalize_subdomain_asset(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """标准化子域名资产"""
        domain = asset.get('domain', '')
        subdomains = asset.get('subdomains', [])
        
        return [{
            "type": "subdomain",
            "domain": domain,
            "subdomain": sub,
            "metadata": {
                "source": asset.get('source')
            }
        } for sub in subdomains]
