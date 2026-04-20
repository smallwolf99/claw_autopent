#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险画像系统 - 风险评估核心引擎

核心功能：将标准化资产对象转换为结构化风险评分，为智能测试规划提供数据基础。

风险评估维度：
1. 技术栈风险 (40%) - 基于技术版本、CVE 数量、置信度
2. 暴露面风险 (30%) - 基于端点数量、复杂度、认证要求
3. 业务风险 (20%) - 基于业务类型、数据敏感性
4. 配置风险 (10%) - 基于服务配置
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RiskScore:
    """风险评分数据结构"""
    overall_score: float  # 总体风险分 (0-100)
    tech_risk: float     # 技术栈风险分 (0-100)
    exposure_risk: float # 暴露面风险分 (0-100)
    business_risk: float # 业务风险分 (0-100)
    config_risk: float   # 配置风险分 (0-100)
    
    # 权重分配 (可配置)
    weights = {
        'tech': 0.4,       # 技术栈风险权重
        'exposure': 0.3,   # 暴露面风险权重
        'business': 0.2,   # 业务风险权重
        'config': 0.1      # 配置风险权重
    }
    
    # 风险等级划分
    risk_levels = {
        (0, 20): "🟢 安全",
        (20, 40): "🟡 低风险",
        (40, 60): "🟠 中风险",
        (60, 80): "🟣 高风险",
        (80, 100): "🔴 危急"
    }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "overall_score": round(self.overall_score, 2),
            "tech_risk": round(self.tech_risk, 2),
            "exposure_risk": round(self.exposure_risk, 2),
            "business_risk": round(self.business_risk, 2),
            "config_risk": round(self.config_risk, 2),
            "risk_level": self.get_risk_level(),
            "weights": self.weights
        }
    
    def get_risk_level(self) -> str:
        """获取风险等级描述"""
        for (low, high), level in self.risk_levels.items():
            if low <= self.overall_score < high:
                return level
        return "未知风险"


class RiskProfiler:
    """风险画像引擎"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """初始化风险画像引擎
        
        Args:
            weights: 自定义权重分配，默认使用标准权重
        """
        self.weights = weights or {
            'tech': 0.4,       # 技术栈风险权重
            'exposure': 0.3,   # 暴露面风险权重
            'business': 0.2,   # 业务风险权重
            'config': 0.1      # 配置风险权重
        }
        
        # 业务类型风险系数
        self.business_type_risk_factors = {
            'banking': 1.5,        # 银行/金融系统
            'financial': 1.5,      # 金融系统
            'healthcare': 1.4,     # 医疗健康
            'government': 1.3,     # 政府系统
            'ecommerce': 1.2,      # 电子商务
            'social': 1.1,         # 社交网络
            'education': 1.0,      # 教育
            'enterprise': 0.9,     # 企业门户
            'cms': 0.8,            # 内容管理系统
            'personal': 0.7,       # 个人网站
            'unknown': 1.0         # 未知类型
        }
        
        logger.info("风险画像引擎初始化完成")
    
    def assess(self, assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估资产列表的整体风险
        
        Args:
            assets: 标准化资产对象列表
            
        Returns:
            风险评估报告
        """
        logger.info(f"开始评估 {len(assets)} 个资产的风险")
        
        if not assets:
            return {
                "overall_score": 0.0,
                "risk_level": "无资产",
                "assets_assessed": 0,
                "details": []
            }
        
        # 评估每个资产
        asset_scores = []
        for asset in assets:
            score = self.assess_asset(asset)
            asset_scores.append({
                "asset": asset.get('url', 'unknown'),
                "score": score.to_dict()
            })
        
        # 计算平均风险分
        overall_score = sum(s['score']['overall_score'] for s in asset_scores) / len(asset_scores)
        
        # 确定风险等级
        risk_level = self._get_risk_level_from_score(overall_score)
        
        report = {
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level,
            "assets_assessed": len(assets),
            "high_risk_assets": [s for s in asset_scores if s['score']['overall_score'] >= 60],
            "medium_risk_assets": [s for s in asset_scores if 40 <= s['score']['overall_score'] < 60],
            "low_risk_assets": [s for s in asset_scores if s['score']['overall_score'] < 40],
            "details": asset_scores,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"风险评估完成：总体风险分={overall_score:.1f}, 等级={risk_level}")
        return report
    
    def assess_asset(self, asset: Dict[str, Any]) -> RiskScore:
        """评估单个资产风险
        
        Args:
            asset: 标准化资产对象
            
        Returns:
            RiskScore: 风险评估结果
        """
        technologies = asset.get('technologies', [])
        endpoints = asset.get('endpoints', [])
        business_hints = asset.get('business_hints', {})
        metadata = asset.get('metadata', {})
        
        # 计算各维度风险分
        tech_risk = self._calculate_tech_risk(technologies)
        exposure_risk = self._calculate_exposure_risk(endpoints)
        business_risk = self._calculate_business_risk(business_hints, metadata)
        config_risk = self._calculate_config_risk(asset)
        
        # 加权计算总体风险分
        overall_score = (
            tech_risk * self.weights['tech'] +
            exposure_risk * self.weights['exposure'] +
            business_risk * self.weights['business'] +
            config_risk * self.weights['config']
        )
        
        # 限制在 0-100 范围内
        overall_score = max(0, min(100, overall_score))
        
        return RiskScore(
            overall_score=overall_score,
            tech_risk=tech_risk,
            exposure_risk=exposure_risk,
            business_risk=business_risk,
            config_risk=config_risk
        )
    
    def _calculate_tech_risk(self, technologies: List[Dict[str, Any]]) -> float:
        """计算技术栈风险"""
        if not technologies:
            return 10.0  # 未知技术有一定风险
        
        total_risk = 0.0
        
        for tech in technologies:
            tech_name = tech.get('name', '未知技术')
            version = tech.get('version')
            cves = tech.get('cves', [])
            confidence = tech.get('confidence', 0.5)
            
            # 1. 版本风险
            version_risk = self._calculate_version_risk(version)
            
            # 2. CVE 风险
            cve_risk = len(cves) * 2.0
            
            # 3. 置信度调整
            confidence_adjustment = 1.0 + (1.0 - confidence)
            
            # 计算该技术风险
            tech_risk = (version_risk + cve_risk) * confidence_adjustment
            total_risk += tech_risk
        
        # 归一化
        normalized_risk = min(100.0, total_risk / len(technologies) * 5)
        return normalized_risk
    
    def _calculate_version_risk(self, version: Optional[str]) -> float:
        """计算版本风险"""
        if not version:
            return 5.0
        
        try:
            parts = version.split('.')
            major = int(parts[0]) if parts[0].isdigit() else 0
            
            if major == 0:
                return 8.0
            elif major <= 2:
                return 6.0
            elif major <= 4:
                return 4.0
            elif major <= 6:
                return 2.0
            else:
                return 1.0
        except (ValueError, IndexError):
            return 4.0
    
    def _calculate_exposure_risk(self, endpoints: List[Dict[str, Any]]) -> float:
        """计算暴露面风险"""
        if not endpoints:
            return 20.0  # 没有端点可能是隐藏的
        
        total_risk = 0.0
        
        for endpoint in endpoints:
            endpoint_risk = 0.0
            
            # 1. 路径风险
            path = endpoint.get('path', '')
            if any(high_risk in path for high_risk in ['/admin', '/config', '/debug']):
                endpoint_risk += 10.0
            elif any(medium_risk in path for medium_risk in ['/api', '/v1', '/rest']):
                endpoint_risk += 5.0
            
            # 2. 方法风险
            methods = endpoint.get('methods', [])
            for method in methods:
                if method in ['POST', 'PUT', 'DELETE']:
                    endpoint_risk += 5.0
                elif method in ['GET', 'HEAD']:
                    endpoint_risk += 1.0
            
            # 3. 认证风险
            if not endpoint.get('auth_required', False):
                endpoint_risk += 5.0
            
            total_risk += endpoint_risk
        
        # 归一化
        num_endpoints = len(endpoints)
        normalized_risk = min(100.0, total_risk / num_endpoints * 10) if num_endpoints > 0 else 0
        return normalized_risk
    
    def _calculate_business_risk(self, business_hints: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """计算业务风险"""
        business_type = business_hints.get('type', 'unknown')
        factor = self.business_type_risk_factors.get(business_type, 1.0)
        
        # 基础风险分 * 业务系数
        base_risk = 30.0
        business_risk = base_risk * factor
        
        return min(100.0, business_risk)
    
    def _calculate_config_risk(self, asset: Dict[str, Any]) -> float:
        """计算配置风险"""
        config_risk = 0.0
        
        # 检查是否有默认配置
        metadata = asset.get('metadata', {})
        if metadata.get('has_default_credentials'):
            config_risk += 30.0
        
        if metadata.get('has_directory_listing'):
            config_risk += 20.0
        
        if metadata.get('has_error_pages'):
            config_risk += 10.0
        
        return min(100.0, config_risk)
    
    def _get_risk_level_from_score(self, score: float) -> str:
        """从分数获取风险等级"""
        for (low, high), level in RiskScore.risk_levels.items():
            if low <= score < high:
                return level
        return "未知风险"
