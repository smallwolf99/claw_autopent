#!/usr/bin/env python3
"""
风险画像系统 - 风险评估核心引擎

核心功能：将标准化资产对象转换为结构化风险评分，为智能测试规划提供数据基础。

风险评估维度：
1. 技术栈风险 (40%) - 基于技术版本、CVE数量、置信度
2. 暴露面风险 (30%) - 基于端点数量、复杂度、认证要求
3. 业务风险 (20%) - 基于业务类型、数据敏感性、合规要求
4. 配置风险 (10%) - 基于服务配置、默认设置、已知配置错误

输出：0-100分的综合风险评分 + 详细风险分解报告
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
            "overall_score": self.overall_score,
            "tech_risk": self.tech_risk,
            "exposure_risk": self.exposure_risk,
            "business_risk": self.business_risk,
            "config_risk": self.config_risk,
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
        
        # 业务类型风险系数 (敏感度越高，风险系数越大)
        self.business_type_risk_factors = {
            'banking': 1.5,        # 银行/金融系统 - 最高风险
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
        
        logger.info(f"风险画像引擎初始化完成，权重配置: {self.weights}")
    
    def assess_asset(self, asset: Dict[str, Any]) -> RiskScore:
        """评估资产风险
        
        Args:
            asset: 标准化资产对象 (StandardizedAsset格式)
            
        Returns:
            RiskScore: 风险评估结果
        """
        logger.info(f"开始评估资产风险: {asset.get('url', '未知URL')}")
        
        # 提取资产组件
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
        
        # 限制在0-100范围内
        overall_score = max(0, min(100, overall_score))
        
        logger.info(f"风险评估完成: 总体风险分={overall_score:.1f}")
        logger.debug(f"详细风险分: 技术={tech_risk:.1f}, 暴露面={exposure_risk:.1f}, "
                    f"业务={business_risk:.1f}, 配置={config_risk:.1f}")
        
        return RiskScore(
            overall_score=overall_score,
            tech_risk=tech_risk,
            exposure_risk=exposure_risk,
            business_risk=business_risk,
            config_risk=config_risk
        )
    
    def _calculate_tech_risk(self, technologies: List[Dict[str, Any]]) -> float:
        """计算技术栈风险
        
        Args:
            technologies: 技术栈列表
            
        Returns:
            float: 技术栈风险分 (0-100)
        """
        if not technologies:
            return 0.0
        
        total_risk = 0.0
        max_possible_risk = 0.0
        
        for tech in technologies:
            tech_name = tech.get('name', '未知技术')
            version = tech.get('version')
            cves = tech.get('cves', [])
            confidence = tech.get('confidence', 0.5)
            
            # 1. 版本风险 (越旧的版本风险越高)
            version_risk = self._calculate_version_risk(version)
            
            # 2. CVE风险 (每个CVE增加风险)
            cve_risk = len(cves) * 2.0  # 每个CVE计2分
            
            # 3. 置信度调整 (低置信度增加不确定性风险)
            confidence_adjustment = 1.0 + (1.0 - confidence)  # 0.5置信度 => 1.5倍风险
            
            # 4. CVSS阈值调整 (如果有)
            cvss_threshold = tech.get('cvss_threshold', 5.0)
            cvss_factor = min(2.0, cvss_threshold / 5.0)  # 基准5.0
            
            # 计算该技术的风险
            tech_risk = (version_risk + cve_risk) * confidence_adjustment * cvss_factor
            total_risk += tech_risk
            
            # 记录最大可能风险 (用于归一化)
            max_possible_risk += 20.0  # 每项技术最大20分
        
        # 归一化到0-100分
        if max_possible_risk > 0:
            normalized_risk = (total_risk / max_possible_risk) * 100
        else:
            normalized_risk = 0.0
        
        return min(100.0, normalized_risk)
    
    def _calculate_version_risk(self, version: Optional[str]) -> float:
        """计算版本风险
        
        版本越旧，风险越高。基于版本号解析和年龄评估。
        
        Args:
            version: 版本字符串，如"7.0.70"、"1.8.2"或None
            
        Returns:
            float: 版本风险分 (0-10)
        """
        if not version:
            return 3.0  # 未知版本有一定风险
        
        try:
            # 尝试解析版本号
            parts = version.split('.')
            major = int(parts[0]) if parts[0].isdigit() else 0
            
            # 简单版本风险评估
            if major == 0:
                return 8.0  # 0.x版本通常不稳定
            elif major <= 1:
                return 7.0  # 1.x版本较旧
            elif major <= 3:
                return 5.0  # 2-3.x版本中等
            elif major <= 5:
                return 3.0  # 4-5.x版本较新
            elif major <= 7:
                return 2.0  # 6-7.x版本很新
            else:
                return 1.0  # 8.x+版本最新
                
        except (ValueError, IndexError):
            return 4.0  # 解析失败，中等风险
    
    def _calculate_exposure_risk(self, endpoints: List[Dict[str, Any]]) -> float:
        """计算暴露面风险
        
        Args:
            endpoints: 端点列表
            
        Returns:
            float: 暴露面风险分 (0-100)
        """
        if not endpoints:
            return 10.0  # 没有端点可能是隐藏的
        
        total_risk = 0.0
        num_endpoints = len(endpoints)
        
        for endpoint in endpoints:
            endpoint_risk = 0.0
            
            # 1. 路径风险 (某些路径风险更高)
            path = endpoint.get('path', '')
            if any(high_risk in path for high_risk in ['/admin', '/config', '/debug', '/test']):
                endpoint_risk += 5.0
            elif any(medium_risk in path for medium_risk in ['/api', '/v1', '/rest', '/graphql']):
                endpoint_risk += 3.0
            
            # 2. 方法风险 (危险方法增加风险)
            methods = endpoint.get('methods', [])
            for method in methods:
                if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint_risk += 2.0  # 写入操作风险更高
                elif method in ['GET', 'HEAD', 'OPTIONS']:
                    endpoint_risk += 0.5  # 读取操作风险较低
            
            # 3. 认证风险 (不需要认证的端点风险更高)
            if not endpoint.get('auth_required', False):
                endpoint_risk += 3.0
            
            # 4. 会话风险 (基于会话的端点风险中等)
            if endpoint.get('session_based', False):
                endpoint_risk += 1.0
            
            # 5. 参数风险 (参数越多，风险越高)
            parameters = endpoint.get('parameters', [])
            endpoint_risk += min(5.0, len(parameters) * 0.5)
            
            total_risk += endpoint_risk
        
        # 考虑端点数量的影响 (端点越多，整体风险越高)
        quantity_factor = min(2.0, num_endpoints / 10.0)  # 超过10个端点时加倍风险
        
        # 计算平均风险并调整
        avg_endpoint_risk = (total_risk / num_endpoints) if num_endpoints > 0 else 0
        total_risk = avg_endpoint_risk * num_endpoints * quantity_factor
        
        # 归一化到0-100分 (假设最大风险: 每个端点20分 * 数量系数)
        max_risk_per_endpoint = 20.0
        normalized_risk = min(100.0, total_risk / (max_risk_per_endpoint * num_endpoints) * 100) if num_endpoints > 0 else 0
        
        return normalized_risk
    
    def _calculate_business_risk(self, business_hints: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """计算业务风险
        
        Args:
            business_hints: 业务类型提示
            metadata: 资产元数据
            
        Returns:
            float: 业务风险分 (0-100)
        """
        business_type = business_hints.get('type', 'unknown')
        confidence = business_hints.get('confidence', 0.5)
        
        # 1. 业务类型基础风险
        base_risk = self.business_type_risk_factors.get(business_type, 1.0) * 20.0
        
        # 2. 置信度调整
        confidence_adjustment = 1.0 + (1.0 - confidence) * 0.5  # 最大1.5倍
        
        # 3. 元数据中提取额外风险因素
        metadata_risk = 0.0
        risk_level = metadata.get('risk_level', 'medium')
        
        if risk_level == 'critical':
            metadata_risk += 20.0
        elif risk_level == 'high':
            metadata_risk += 15.0
        elif risk_level == 'medium':
            metadata_risk += 10.0
        elif risk_level == 'low':
            metadata_risk += 5.0
        
        # 4. 业务关键词风险
        keywords = business_hints.get('keywords', [])
        keyword_risk = min(15.0, len(keywords) * 2.0)
        
        # 计算总业务风险
        total_business_risk = (base_risk + metadata_risk + keyword_risk) * confidence_adjustment
        
        return min(100.0, total_business_risk)
    
    def _calculate_config_risk(self, asset: Dict[str, Any]) -> float:
        """计算配置风险
        
        目前基于简单启发式规则，后续可扩展为配置检查引擎
        
        Args:
            asset: 完整资产对象
            
        Returns:
            float: 配置风险分 (0-100)
        """
        config_risk = 0.0
        
        # 1. 基于端点的配置风险启发
        endpoints = asset.get('endpoints', [])
        for endpoint in endpoints:
            # 如果端点不需要认证但有敏感参数，配置风险增加
            if not endpoint.get('auth_required', False):
                parameters = endpoint.get('parameters', [])
                sensitive_params = ['password', 'token', 'key', 'secret', 'credential']
                if any(param in sensitive_params for param in parameters):
                    config_risk += 5.0
        
        # 2. 基于技术栈的配置风险
        technologies = asset.get('technologies', [])
        for tech in technologies:
            tech_name = tech.get('name', '').lower()
            # 某些技术有已知的默认配置风险
            if 'tomcat' in tech_name:
                config_risk += 8.0  # Tomcat默认配置风险较高
            elif 'apache' in tech_name:
                config_risk += 5.0
            elif 'nginx' in tech_name:
                config_risk += 4.0
        
        # 3. 基于URL的配置风险启发
        url = asset.get('url', '')
        if 'http://' in url and not 'https://' in url:
            config_risk += 10.0  # 使用HTTP而不是HTTPS
        
        return min(100.0, config_risk)
    
    def generate_risk_report(self, asset: Dict[str, Any], risk_score: RiskScore) -> Dict[str, Any]:
        """生成详细的风险报告
        
        Args:
            asset: 原始资产对象
            risk_score: 风险评估结果
            
        Returns:
            Dict: 结构化风险报告
        """
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "engine_version": "1.0.0",
                "asset_url": asset.get('url', '未知URL')
            },
            "risk_summary": risk_score.to_dict(),
            "asset_overview": {
                "technologies": asset.get('technologies', []),
                "endpoints_count": len(asset.get('endpoints', [])),
                "business_type": asset.get('business_hints', {}).get('type', '未知'),
                "business_confidence": asset.get('business_hints', {}).get('confidence', 0.0)
            },
            "risk_breakdown": {
                "tech_breakdown": self._generate_tech_breakdown(asset.get('technologies', [])),
                "exposure_breakdown": self._generate_exposure_breakdown(asset.get('endpoints', [])),
                "recommendations": self._generate_recommendations(risk_score, asset)
            }
        }
        
        return report
    
    def _generate_tech_breakdown(self, technologies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成技术栈风险分解"""
        breakdown = []
        
        for tech in technologies:
            tech_name = tech.get('name', '未知技术')
            version = tech.get('version', '未知版本')
            cves = tech.get('cves', [])
            confidence = tech.get('confidence', 0.5)
            
            # 评估该技术的关键风险因素
            risk_factors = []
            
            if not version or version == 'unknown':
                risk_factors.append("版本未知 (增加不确定性)")
            elif self._calculate_version_risk(version) > 5.0:
                risk_factors.append(f"版本较旧 ({version})")
            
            if cves:
                risk_factors.append(f"有{len(cves)}个已知CVE")
            
            if confidence < 0.7:
                risk_factors.append(f"识别置信度较低 ({confidence:.1%})")
            
            breakdown.append({
                "name": tech_name,
                "version": version,
                "cve_count": len(cves),
                "confidence": confidence,
                "risk_factors": risk_factors
            })
        
        return breakdown
    
    def _generate_exposure_breakdown(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成暴露面风险分解"""
        if not endpoints:
            return []
        
        breakdown = []
        high_risk_endpoints = []
        
        for endpoint in endpoints:
            path = endpoint.get('path', '未知路径')
            methods = endpoint.get('methods', [])
            auth_required = endpoint.get('auth_required', False)
            
            # 风险标记
            risk_flags = []
            
            if not auth_required:
                risk_flags.append("无需认证")
            
            for method in methods:
                if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    risk_flags.append(f"{method}方法 (写入操作)")
            
            if risk_flags:
                endpoint_info = {
                    "path": path,
                    "methods": methods,
                    "risk_flags": risk_flags
                }
                
                # 高风险端点单独列出
                if not auth_required and any(m in methods for m in ['POST', 'PUT', 'DELETE']):
                    high_risk_endpoints.append(endpoint_info)
                else:
                    breakdown.append(endpoint_info)
        
        # 高风险端点放在前面
        breakdown = high_risk_endpoints + breakdown
        
        return breakdown[:10]  # 只返回前10个最有风险的端点
    
    def _generate_recommendations(self, risk_score: RiskScore, asset: Dict[str, Any]) -> List[str]:
        """生成基于风险的测试建议"""
        recommendations = []
        
        # 总体风险建议
        overall_level = risk_score.get_risk_level()
        if "危急" in overall_level or "高风险" in overall_level:
            recommendations.append("🔥 **立即进行深度安全测试** - 系统存在严重安全风险")
        elif "中风险" in overall_level:
            recommendations.append("⚠️ **建议进行全面的安全评估** - 系统存在潜在安全风险")
        
        # 技术栈相关建议
        if risk_score.tech_risk > 60:
            recommendations.append("🔧 **优先验证已知CVE** - 技术栈存在多个高危漏洞")
        
        # 暴露面相关建议
        if risk_score.exposure_risk > 60:
            recommendations.append("🛡️ **重点测试认证绕过** - 系统暴露面较大，认证机制需验证")
        
        # 业务相关建议
        if risk_score.business_risk > 60:
            recommendations.append("🏦 **深度业务逻辑测试** - 系统处理敏感业务，需要逻辑安全验证")
        
        # 具体技术建议
        technologies = asset.get('technologies', [])
        for tech in technologies:
            tech_name = tech.get('name', '')
            if 'Tomcat' in tech_name:
                recommendations.append("🐱 **Tomcat CVE专项验证** - 检查CVE-2020-9484等已知漏洞")
            elif 'JQuery' in tech_name:
                recommendations.append("📜 **JQuery XSS专项测试** - 检查原型污染和DOM XSS漏洞")
        
        return recommendations


def main():
    """主函数：示例使用风险画像引擎"""
    print("🧠 风险画像系统 - 示例运行")
    
    # 创建风险画像引擎
    profiler = RiskProfiler()
    
    # 加载示例资产数据 (使用zero.webappsecurity.com的资产)
    asset_path = Path(__file__).parent.parent / "assets" / "zero_asset.json"
    
    if asset_path.exists():
        with open(asset_path, 'r') as f:
            asset = json.load(f)
        
        # 评估风险
        risk_score = profiler.assess_asset(asset)
        
        # 生成报告
        report = profiler.generate_risk_report(asset, risk_score)
        
        # 输出摘要
        print(f"\n📊 风险评估摘要:")
        print(f"   目标: {report['asset_overview']['business_type']} 系统")
        print(f"   总体风险分: {risk_score.overall_score:.1f}/100")
        print(f"   风险等级: {risk_score.get_risk_level()}")
        print(f"   技术栈数量: {len(report['asset_overview']['technologies'])}")
        print(f"   端点数量: {report['asset_overview']['endpoints_count']}")
        
        # 显示关键建议
        print(f"\n🎯 关键测试建议:")
        for i, rec in enumerate(report['risk_breakdown']['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        # 保存完整报告
        output_path = Path(__file__).parent.parent / "deliverables" / "risk_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 完整风险报告已保存到: {output_path}")
        
    else:
        print(f"❌ 找不到示例资产文件: {asset_path}")
        print("请先创建 zero_asset.json 文件")


if __name__ == "__main__":
    main()