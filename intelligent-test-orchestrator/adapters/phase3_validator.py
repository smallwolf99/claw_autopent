#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-3 漏洞验证模块

核心功能:
1. 漏洞验证器 - 多工具交叉验证
2. 误报过滤 - 基于规则过滤
3. 利用链生成 - 自动化攻击路径

提供高可信度的漏洞验证结果。
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """验证结果"""
    vuln_id: str
    name: str
    severity: str
    verified: bool
    confidence: float  # 0.0 - 1.0
    tool_results: Dict[str, bool] = field(default_factory=dict)
    false_positive_reason: Optional[str] = None
    exploit_chain: Optional[List[str]] = None


class Phase3Validator:
    """Phase-3 漏洞验证器"""
    
    def __init__(self):
        """初始化验证器"""
        # 误报过滤规则
        self.false_positive_rules = [
            {
                'id': 'FP-001',
                'pattern': 'timeout',
                'reason': '网络超时可能导致误报'
            },
            {
                'id': 'FP-002',
                'pattern': 'connection refused',
                'reason': '连接被拒绝可能导致误报'
            },
            {
                'id': 'FP-003',
                'pattern': '404',
                'reason': '404 错误可能导致误报'
            }
        ]
        
        # 漏洞验证规则
        self.verification_rules = {
            'critical': {'min_tools': 2, 'require_exploit': True},
            'high': {'min_tools': 2, 'require_exploit': False},
            'medium': {'min_tools': 1, 'require_exploit': False},
            'low': {'min_tools': 1, 'require_exploit': False}
        }
        
        logger.info("Phase-3 漏洞验证器初始化完成")
    
    async def verify(self, vulnerabilities: List[Dict[str, Any]], 
                    assets: List[Dict[str, Any]]) -> List[VerificationResult]:
        """验证漏洞
        
        Args:
            vulnerabilities: 漏洞列表
            assets: 资产列表
            
        Returns:
            验证结果列表
        """
        logger.info(f"开始验证漏洞：{len(vulnerabilities)} 个")
        
        verified_results = []
        
        # 按严重程度分组
        vulns_by_severity = self._group_by_severity(vulnerabilities)
        
        # 优先验证高危漏洞
        for severity in ['critical', 'high', 'medium', 'low']:
            vulns = vulns_by_severity.get(severity, [])
            for vuln in vulns:
                result = await self._verify_single_vuln(vuln, assets)
                verified_results.append(result)
        
        # 过滤误报
        verified_results = self._filter_false_positives(verified_results)
        
        # 生成利用链
        for result in verified_results:
            if result.verified and result.confidence >= 0.8:
                result.exploit_chain = self._generate_exploit_chain(result, assets)
        
        verified_count = sum(1 for r in verified_results if r.verified)
        logger.info(f"漏洞验证完成：{verified_count}/{len(verified_results)} 个已验证")
        
        return verified_results
    
    def _group_by_severity(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """按严重程度分组"""
        groups = {}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info')
            if severity not in groups:
                groups[severity] = []
            groups[severity].append(vuln)
        return groups
    
    async def _verify_single_vuln(self, vuln: Dict[str, Any], 
                                 assets: List[Dict[str, Any]]) -> VerificationResult:
        """验证单个漏洞"""
        vuln_id = vuln.get('id', 'UNKNOWN')
        name = vuln.get('name', 'Unknown')
        severity = vuln.get('severity', 'info')
        
        logger.info(f"验证漏洞：{vuln_id} - {name}")
        
        # 多工具交叉验证
        tool_results = await self._cross_verify(vuln, assets)
        
        # 计算置信度
        confidence = self._calculate_confidence(tool_results, severity)
        
        # 判断是否验证通过
        verified = self._is_verified(tool_results, confidence, severity)
        
        return VerificationResult(
            vuln_id=vuln_id,
            name=name,
            severity=severity,
            verified=verified,
            confidence=confidence,
            tool_results=tool_results
        )
    
    async def _cross_verify(self, vuln: Dict[str, Any], 
                           assets: List[Dict[str, Any]]) -> Dict[str, bool]:
        """多工具交叉验证"""
        tool_results = {}
        
        # 根据漏洞类型选择验证方法
        vuln_id = vuln.get('id', '')
        
        # 模拟不同工具的验证
        # 实际实现中，这里会调用真实的验证工具
        
        if 'CVE' in vuln_id:
            # CVE 漏洞 - 使用 PoC 验证
            tool_results['poc_verify'] = await self._poc_verify(vuln, assets)
            tool_results['signature_match'] = await self._signature_verify(vuln, assets)
        else:
            # Web 漏洞 - 使用特征验证
            tool_results['web_scan'] = await self._web_verify(vuln, assets)
            tool_results['manual_check'] = await self._manual_verify(vuln, assets)
        
        return tool_results
    
    async def _poc_verify(self, vuln: Dict[str, Any], assets: List[Dict[str, Any]]) -> bool:
        """PoC 验证"""
        await asyncio.sleep(0.2)  # 模拟验证时间
        # 模拟返回
        return True
    
    async def _signature_verify(self, vuln: Dict[str, Any], assets: List[Dict[str, Any]]) -> bool:
        """特征验证"""
        await asyncio.sleep(0.2)
        return True
    
    async def _web_verify(self, vuln: Dict[str, Any], assets: List[Dict[str, Any]]) -> bool:
        """Web 漏洞验证"""
        await asyncio.sleep(0.2)
        return True
    
    async def _manual_verify(self, vuln: Dict[str, Any], assets: List[Dict[str, Any]]) -> bool:
        """手工验证辅助"""
        await asyncio.sleep(0.2)
        return True
    
    def _calculate_confidence(self, tool_results: Dict[str, bool], severity: str) -> float:
        """计算置信度"""
        if not tool_results:
            return 0.0
        
        # 基础置信度 = 验证通过的工具数 / 总工具数
        passed_tools = sum(1 for result in tool_results.values() if result)
        total_tools = len(tool_results)
        base_confidence = passed_tools / total_tools
        
        # 根据工具数量加权
        tool_bonus = min(0.2, (total_tools - 1) * 0.1)
        
        # 根据严重程度调整
        severity_weight = {
            'critical': 1.0,
            'high': 0.95,
            'medium': 0.9,
            'low': 0.85
        }.get(severity, 0.8)
        
        confidence = (base_confidence + tool_bonus) * severity_weight
        return min(1.0, confidence)
    
    def _is_verified(self, tool_results: Dict[str, bool], confidence: float, 
                    severity: str) -> bool:
        """判断是否验证通过"""
        rules = self.verification_rules.get(severity, {'min_tools': 1})
        min_tools = rules.get('min_tools', 1)
        
        # 验证通过的工具数
        passed_tools = sum(1 for result in tool_results.values() if result)
        
        # 需要达到最小工具数且置信度足够
        return passed_tools >= min_tools and confidence >= 0.6
    
    def _filter_false_positives(self, results: List[VerificationResult]) -> List[VerificationResult]:
        """过滤误报"""
        filtered = []
        
        for result in results:
            is_fp = False
            fp_reason = None
            
            # 应用误报规则
            for rule in self.false_positive_rules:
                if rule['pattern'].lower() in result.name.lower():
                    is_fp = True
                    fp_reason = rule['reason']
                    break
            
            if not is_fp:
                filtered.append(result)
            else:
                logger.info(f"过滤误报：{result.vuln_id} - {fp_reason}")
                result.false_positive_reason = fp_reason
        
        return filtered
    
    def _generate_exploit_chain(self, result: VerificationResult, 
                               assets: List[Dict[str, Any]]) -> List[str]:
        """生成利用链"""
        chain = []
        
        # 根据漏洞类型生成利用步骤
        if 'RCE' in result.name or 'Remote Code Execution' in result.name:
            chain = [
                "1. 识别目标服务版本",
                "2. 发送恶意请求触发漏洞",
                "3. 上传 Webshell 或执行命令",
                "4. 验证权限获取"
            ]
        elif 'SQL Injection' in result.name:
            chain = [
                "1. 探测注入点",
                "2. 判断注入类型",
                "3. 提取数据库信息",
                "4. 获取敏感数据"
            ]
        elif 'XSS' in result.name:
            chain = [
                "1. 构造恶意 Payload",
                "2. 注入到目标页面",
                "3. 诱导用户触发",
                "4. 窃取 Cookie 或会话"
            ]
        else:
            chain = [
                "1. 识别漏洞类型",
                "2. 准备利用工具",
                "3. 执行漏洞利用",
                "4. 验证利用结果"
            ]
        
        return chain
    
    def to_dict(self, results: List[VerificationResult]) -> List[Dict[str, Any]]:
        """转换为字典格式"""
        return [
            {
                'vuln_id': r.vuln_id,
                'name': r.name,
                'severity': r.severity,
                'verified': r.verified,
                'confidence': r.confidence,
                'tool_results': r.tool_results,
                'false_positive_reason': r.false_positive_reason,
                'exploit_chain': r.exploit_chain
            }
            for r in results
        ]
