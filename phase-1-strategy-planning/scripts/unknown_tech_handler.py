#!/usr/bin/env python3
"""
未知技术处理核心引擎 - 智能测试规划引擎阶段三

核心功能：处理未知或未识别技术，基于特征匹配推导安全假设，
生成合适的测试策略。当遇到无法直接识别的技术时，本引擎提供
智能决策支持。

核心模块：
1. TechnicalFeature - 技术特征数据结构
2. SimilarityMatcher - 相似度匹配引擎
3. SecurityInferencer - 安全推理引擎
4. UnknownTechHandler - 主协调处理器
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import difflib


# ============================================
# 数据结构定义
# ============================================

class SecurityAttribute(Enum):
    """安全属性枚举"""
    AUTH_REQUIRED = "auth_required"           # 是否需要身份认证
    ENCRYPTION_DEFAULT = "encryption_default" # 是否默认启用加密
    EXPOSED_ADMIN = "exposed_admin"           # 管理接口是否默认暴露
    DEFAULT_CREDENTIALS = "default_credentials" # 是否存在默认凭证
    CONFIG_COMPLEXITY = "config_complexity"   # 配置复杂性
    CVE_HISTORY = "cve_history"               # 历史CVE记录


@dataclass
class TechnicalFeature:
    """技术特征数据结构"""
    technology_type: str                    # 技术类型 (web_framework, database, etc.)
    name: Optional[str] = None              # 技术名称 (可能为空，表示未知)
    version: Optional[str] = None           # 版本信息 (可能为空)
    confidence: float = 0.0                 # 识别置信度 (0-1)
    
    # 特征向量
    protocol_features: List[str] = field(default_factory=list)     # 协议特征
    header_features: Dict[str, str] = field(default_factory=dict)  # HTTP头部特征
    response_features: List[str] = field(default_factory=list)     # 响应体特征  
    behavioral_features: List[str] = field(default_factory=list)   # 行为特征
    
    # 安全属性（如果有的话）
    security_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_feature_vector(self) -> Dict[str, List[str]]:
        """将特征转换为向量表示"""
        return {
            "protocols": self.protocol_features,
            "headers": list(self.header_features.keys()) + list(self.header_features.values()),
            "responses": self.response_features,
            "behavior": self.behavioral_features
        }


@dataclass
class SimilarityResult:
    """相似度匹配结果"""
    target_feature: TechnicalFeature           # 目标技术特征
    best_match_name: str                       # 最佳匹配技术名称
    best_match_version: str                    # 最佳匹配版本
    similarity_score: float                    # 相似度分数 (0-1)
    confidence: float                          # 匹配置信度 (0-1)
    matched_reason: str                        # 匹配原因描述
    matched_features: Dict[str, float]         # 各特征的匹配分数
    security_assumptions: List[str]            # 安全假设列表
    alternative_matches: List[Dict[str, Any]]  # 替代匹配选项
    
    def __str__(self):
        return f"匹配: {self.best_match_name} v{self.best_match_version} (分数: {self.similarity_score:.3f}, 置信度: {self.confidence:.1%})"


@dataclass
class SecurityDecision:
    """安全决策结果"""
    technology_info: SimilarityResult        # 技术识别结果
    risk_assessment: Dict[str, float]        # 风险评估
    recommended_actions: List[str]           # 推荐测试动作
    confidence_level: str                    # 置信级别 (high/medium/low)
    testing_strategy: Dict[str, Any]         # 测试策略详情
    uncertainty_factors: List[str]           # 不确定性因素
    
    def get_summary(self):
        """获取决策摘要"""
        return {
            "技术假设": self.technology_info.best_match_name,
            "风险评分": self.risk_assessment.get("total_risk", 0.0),
            "置信级别": self.confidence_level,
            "推荐测试数": len(self.recommended_actions),
            "不确定性因素": len(self.uncertainty_factors)
        }


# ============================================
# 相似度匹配引擎
# ============================================

class SimilarityMatcher:
    """相似度匹配引擎"""
    
    def __init__(self, tech_database_path: str):
        """
        初始化匹配引擎
        
        Args:
            tech_database_path: 技术数据库文件路径
        """
        self.database = self._load_tech_database(tech_database_path)
        self.feature_weights = self.database.get("feature_risk_weights", {
            "protocols": 0.15,
            "headers": 0.25,
            "responses": 0.30,
            "behavior": 0.30
        })
        
    def _load_tech_database(self, path: str) -> Dict[str, Any]:
        """加载技术数据库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载技术数据库失败: {e}")
            return self._create_default_database()
    
    def _create_default_database(self) -> Dict[str, Any]:
        """创建默认数据库（回退方案）"""
        return {
            "known_technologies": [],
            "feature_risk_weights": {
                "protocols": 0.15,
                "headers": 0.25,
                "responses": 0.30,
                "behavior": 0.30
            }
        }
    
    def calculate_similarity(self, feature1: Dict[str, List[str]], 
                            feature2: Dict[str, List[str]]) -> float:
        """
        计算两个特征向量之间的相似度
        
        Args:
            feature1: 第一个特征向量
            feature2: 第二个特征向量
            
        Returns:
            float: 加权相似度分数 (0-1)
        """
        if not feature1 or not feature2:
            return 0.0
        
        weighted_similarity = 0.0
        feature_scores = {}
        
        for feature_type in ["protocols", "headers", "responses", "behavior"]:
            if feature_type not in feature1 or feature_type not in feature2:
                continue
                
            list1 = feature1.get(feature_type, [])
            list2 = feature2.get(feature_type, [])
            
            if not list1 and not list2:
                # 两者都为空，无法计算
                similarity = 0.0
            elif not list1 or not list2:
                # 一个为空一个不为空，相似度很低
                similarity = 0.1 if (list1 or list2) else 0.0
            else:
                # 计算Jaccard相似度
                set1 = set(list1)
                set2 = set(list2)
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                similarity = intersection / union if union > 0 else 0.0
            
            weight = self.feature_weights.get(feature_type, 0.25)
            weighted_similarity += similarity * weight
            feature_scores[feature_type] = similarity
        
        # 确保总分在0-1范围内
        total_weight = sum(self.feature_weights.get(ft, 0.25) for ft in ["protocols", "headers", "responses", "behavior"])
        if total_weight > 0:
            weighted_similarity = weighted_similarity / total_weight
        
        return min(max(weighted_similarity, 0.0), 1.0), feature_scores
    
    def find_best_match(self, target_feature: TechnicalFeature) -> SimilarityResult:
        """
        为目标技术特征寻找最佳匹配
        
        Args:
            target_feature: 目标技术特征
            
        Returns:
            SimilarityResult: 匹配结果
        """
        target_vector = target_feature.to_feature_vector()
        best_match = None
        best_score = 0.0
        best_feature_scores = {}
        all_matches = []
        
        known_techs = self.database.get("known_technologies", [])
        
        for tech in known_techs:
            # 构建已知技术的特征向量
            tech_vector = {
                "protocols": tech.get("features", {}).get("protocols", []),
                "headers": self._extract_header_features(tech),
                "responses": tech.get("features", {}).get("responses", []),
                "behavior": tech.get("features", {}).get("behavior", [])
            }
            
            # 计算相似度
            score, feature_scores = self.calculate_similarity(target_vector, tech_vector)
            
            match_info = {
                "name": tech.get("name", ""),
                "category": tech.get("category", ""),
                "version": tech.get("common_versions", ["unknown"])[0],
                "score": score,
                "feature_scores": feature_scores
            }
            
            all_matches.append(match_info)
            
            if score > best_score:
                best_score = score
                best_match = tech
                best_feature_scores = feature_scores
        
        # 如果没有匹配到任何技术
        if not best_match:
            return self._create_no_match_result(target_feature)
        
        # 构建匹配原因
        match_reason = self._build_match_reason(best_feature_scores, best_match)
        
        # 构建安全假设
        security_assumptions = self._extract_security_assumptions(best_match)
        
        # 计算置信度
        confidence = self._calculate_confidence(best_score, target_feature.confidence)
        
        # 排序其他匹配选项
        alternative_matches = sorted(
            [m for m in all_matches if m["name"] != best_match.get("name")],
            key=lambda x: x["score"],
            reverse=True
        )[:3]  # 只保留前3个备选
        
        return SimilarityResult(
            target_feature=target_feature,
            best_match_name=best_match.get("name", "Unknown"),
            best_match_version=best_match.get("common_versions", ["unknown"])[0],
            similarity_score=best_score,
            confidence=confidence,
            matched_reason=match_reason,
            matched_features=best_feature_scores,
            security_assumptions=security_assumptions,
            alternative_matches=alternative_matches
        )
    
    def _extract_header_features(self, tech: Dict[str, Any]) -> List[str]:
        """从技术定义中提取头部特征"""
        headers = tech.get("features", {}).get("headers", [])
        header_features = []
        
        for header in headers:
            # 处理 "Server: Apache-Coyote/" 这样的格式
            if ":" in header:
                key, value = header.split(":", 1)
                header_features.append(key.strip())
                header_features.append(value.strip())
            else:
                header_features.append(header)
        
        return header_features
    
    def _build_match_reason(self, feature_scores: Dict[str, float], best_match: Dict[str, Any]) -> str:
        """构建匹配原因描述"""
        reasons = []
        
        # 找出匹配度最高的特征类型
        max_score_feature = max(feature_scores.items(), key=lambda x: x[1]) if feature_scores else ("", 0.0)
        
        if max_score_feature[1] > 0.7:
            feature_name_map = {
                "protocols": "协议特征",
                "headers": "HTTP头部特征", 
                "responses": "响应体特征",
                "behavior": "行为特征"
            }
            reasons.append(f"基于{feature_name_map.get(max_score_feature[0], max_score_feature[0])}的高度匹配")
        
        # 检查是否有具体的技术特征
        tech_name = best_match.get("name", "")
        if any(x in tech_name.lower() for x in ["tomcat", "spring", "nginx", "mysql", "wordpress"]):
            reasons.append(f"匹配到知名技术栈: {tech_name}")
        
        if not reasons:
            reasons.append("基于多个特征的组合匹配")
        
        return " | ".join(reasons)
    
    def _extract_security_assumptions(self, tech: Dict[str, Any]) -> List[str]:
        """从匹配的技术中提取安全假设"""
        assumptions = []
        security_profile = tech.get("security_profile", {})
        
        if security_profile.get("default_credentials") == "common":
            assumptions.append("可能存在默认凭证，建议进行凭证猜解测试")
        
        if security_profile.get("exposed_admin") in ["yes", "public_with_auth"]:
            assumptions.append("管理接口可能暴露，需要检查访问控制和认证")
        
        if security_profile.get("cve_history") in ["many", "some"]:
            assumptions.append("历史CVE记录较多，建议进行CVE专项验证")
        
        if security_profile.get("config_complexity") == "high":
            assumptions.append("配置复杂性高，可能包含安全配置错误")
        
        if not assumptions:
            assumptions.append("基于已知技术的安全特征进行一般性安全测试")
        
        return assumptions
    
    def _calculate_confidence(self, similarity_score: float, feature_confidence: float) -> float:
        """计算总体置信度"""
        # 结合相似度分数和技术特征置信度
        base_confidence = similarity_score * 0.7 + feature_confidence * 0.3
        
        # 应用非线性调整
        if similarity_score > 0.8:
            adjusted = base_confidence * 1.2  # 高相似度提升置信度
        elif similarity_score > 0.5:
            adjusted = base_confidence  # 中等相似度保持不变
        else:
            adjusted = base_confidence * 0.8  # 低相似度降低置信度
        
        return min(max(adjusted, 0.0), 1.0)
    
    def _create_no_match_result(self, target_feature: TechnicalFeature) -> SimilarityResult:
        """创建无匹配结果"""
        return SimilarityResult(
            target_feature=target_feature,
            best_match_name="未知技术",
            best_match_version="未知",
            similarity_score=0.0,
            confidence=0.1,
            matched_reason="无匹配的已知技术，特征可能为全新或高度定制",
            matched_features={},
            security_assumptions=["由于无法匹配已知技术，建议采用保守测试策略"],
            alternative_matches=[]
        )


# ============================================
# 安全推理引擎
# ============================================

class SecurityInferencer:
    """安全推理引擎"""
    
    def __init__(self, tech_database_path: str):
        """
        初始化安全推理引擎
        
        Args:
            tech_database_path: 技术数据库文件路径
        """
        self.database = self._load_tech_database(tech_database_path)
        self.category_risk_baselines = self.database.get("category_risk_baselines", {})
        
    def _load_tech_database(self, path: str) -> Dict[str, Any]:
        """加载技术数据库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载技术数据库失败: {e}")
            return {}
    
    def infer_security_decision(self, similarity_result: SimilarityResult) -> SecurityDecision:
        """
        基于相似度结果推理安全决策
        
        Args:
            similarity_result: 相似度匹配结果
            
        Returns:
            SecurityDecision: 安全决策
        """
        # 1. 风险评估
        risk_assessment = self._assess_risk(similarity_result)
        
        # 2. 确定置信级别
        confidence_level = self._determine_confidence_level(similarity_result.confidence)
        
        # 3. 生成推荐动作
        recommended_actions = self._generate_recommended_actions(
            similarity_result, risk_assessment, confidence_level
        )
        
        # 4. 设计测试策略
        testing_strategy = self._design_testing_strategy(
            similarity_result, risk_assessment, confidence_level
        )
        
        # 5. 识别不确定性因素
        uncertainty_factors = self._identify_uncertainty_factors(similarity_result)
        
        return SecurityDecision(
            technology_info=similarity_result,
            risk_assessment=risk_assessment,
            recommended_actions=recommended_actions,
            confidence_level=confidence_level,
            testing_strategy=testing_strategy,
            uncertainty_factors=uncertainty_factors
        )
    
    def _assess_risk(self, similarity_result: SimilarityResult) -> Dict[str, float]:
        """进行风险评估"""
        tech_name = similarity_result.best_match_name
        similarity_score = similarity_result.similarity_score
        confidence = similarity_result.confidence
        
        # 找到对应的技术定义
        matched_tech = None
        for tech in self.database.get("known_technologies", []):
            if tech.get("name") == tech_name:
                matched_tech = tech
                break
        
        if not matched_tech or similarity_score < 0.3:
            # 无匹配或匹配度很低，使用保守风险评估
            return self._assess_unknown_risk(similarity_result)
        
        # 基于已知技术评估风险
        security_profile = matched_tech.get("security_profile", {})
        
        # 技术风险（CVSS基线）
        tech_risk = security_profile.get("cvss_base_score", 5.0)
        
        # 匹配度调整
        match_adjustment = similarity_score * confidence * 2.0
        
        # 暴露风险（基于技术类型）
        tech_category = matched_tech.get("category", "unknown")
        exposure_risk = self.category_risk_baselines.get(tech_category, 5.0)
        
        # 计算总风险
        total_risk = tech_risk * 0.4 + exposure_risk * 0.3 + match_adjustment * 0.3
        
        return {
            "total_risk": min(total_risk, 10.0),
            "tech_risk": tech_risk,
            "exposure_risk": exposure_risk,
            "match_adjustment": match_adjustment,
            "risk_level": self._get_risk_level(total_risk)
        }
    
    def _assess_unknown_risk(self, similarity_result: SimilarityResult) -> Dict[str, float]:
        """评估未知技术的风险"""
        # 保守评估：假设未知技术有一定风险
        base_risk = 6.0  # 中等风险
        
        # 根据特征丰富度调整
        target_vector = similarity_result.target_feature.to_feature_vector()
        feature_count = sum(len(v) for v in target_vector.values())
        
        if feature_count == 0:
            # 无任何特征，风险较低但不确定性高
            adjusted_risk = 4.0
        elif feature_count < 3:
            # 特征较少，不确定性较高
            adjusted_risk = 5.0
        else:
            # 特征较多，可能是一个完整的技术栈
            adjusted_risk = 7.0
        
        return {
            "total_risk": adjusted_risk,
            "tech_risk": base_risk,
            "exposure_risk": 6.0,
            "match_adjustment": 0.0,
            "risk_level": self._get_risk_level(adjusted_risk),
            "is_unknown": True
        }
    
    def _get_risk_level(self, score: float) -> str:
        """根据分数确定风险等级"""
        if score >= 8.0:
            return "高危"
        elif score >= 6.0:
            return "中危"
        elif score >= 4.0:
            return "低危"
        else:
            return "信息"
    
    def _determine_confidence_level(self, confidence: float) -> str:
        """根据置信度确定级别"""
        if confidence >= 0.7:
            return "高"
        elif confidence >= 0.4:
            return "中"
        else:
            return "低"
    
    def _generate_recommended_actions(self, similarity_result: SimilarityResult,
                                     risk_assessment: Dict[str, float],
                                     confidence_level: str) -> List[str]:
        """生成推荐动作"""
        actions = []
        tech_name = similarity_result.best_match_name
        
        # 基本安全测试动作
        base_actions = [
            "端口扫描和服务识别",
            "HTTP头部安全分析",
            "目录和文件枚举"
        ]
        
        # 根据置信度调整
        if confidence_level == "高":
            # 高置信度时，可进行针对性测试
            actions.extend(base_actions)
            actions.append("针对特定技术的CVE验证")
            if similarity_result.similarity_score > 0.7:
                actions.append("默认配置安全检查")
                actions.append("管理接口访问测试")
        elif confidence_level == "中":
            # 中等置信度，保守+探索性测试
            actions.extend(base_actions)
            actions.append("保守的漏洞扫描")
            actions.append("技术特征深度分析")
        else:
            # 低置信度，纯探索性测试
            actions.extend(base_actions)
            actions.append("宽泛的漏洞扫描")
            actions.append("技术指纹收集")
            actions.append("手动安全分析")
        
        # 根据风险评估增加动作
        risk_level = risk_assessment.get("risk_level", "信息")
        if risk_level in ["高危", "中危"]:
            actions.append("重点漏洞验证")
            actions.append("攻击面评估")
        
        return actions
    
    def _design_testing_strategy(self, similarity_result: SimilarityResult,
                                risk_assessment: Dict[str, float],
                                confidence_level: str) -> Dict[str, Any]:
        """设计测试策略"""
        risk_level = risk_assessment.get("risk_level", "信息")
        
        strategy = {
            "核心目标": self._get_testing_objective(confidence_level, risk_level),
            "测试强度": self._get_testing_intensity(risk_level),
            "时间分配": self._get_time_allocation(confidence_level, risk_level),
            "工具选择": self._get_tool_selection(similarity_result, confidence_level),
            "重点区域": self._get_focus_areas(similarity_result)
        }
        
        return strategy
    
    def _get_testing_objective(self, confidence: str, risk_level: str) -> str:
        """确定测试目标"""
        if confidence == "低":
            if risk_level in ["高危", "中危"]:
                return "识别技术类型和安全基线评估"
            else:
                return "技术特征收集和安全概况分析"
        elif confidence == "中":
            if risk_level in ["高危", "中危"]:
                return "针对性漏洞发现和安全配置验证"
            else:
                return "安全配置检查和常见漏洞扫描"
        else:  # 高置信度
            if risk_level in ["高危", "中危"]:
                return "深度漏洞挖掘和攻击路径分析"
            else:
                return "全面安全检查和安全加固建议"
    
    def _get_testing_intensity(self, risk_level: str) -> str:
        """确定测试强度"""
        intensity_map = {
            "高危": "高强度",
            "中危": "中等强度",
            "低危": "低强度",
            "信息": "信息收集强度"
        }
        return intensity_map.get(risk_level, "中等强度")
    
    def _get_time_allocation(self, confidence: str, risk_level: str) -> Dict[str, int]:
        """确定时间分配（分钟）"""
        base_time = {
            "信息收集": 15,
            "漏洞扫描": 30,
            "深度测试": 45,
            "验证和报告": 30
        }
        
        # 根据置信度和风险调整
        if risk_level == "高危":
            base_time["漏洞扫描"] *= 1.5
            base_time["深度测试"] *= 1.5
        elif risk_level == "低危":
            base_time["漏洞扫描"] *= 0.7
            base_time["深度测试"] *= 0.7
        
        if confidence == "低":
            base_time["信息收集"] *= 2.0
            base_time["漏洞扫描"] *= 0.5
        
        return {k: int(v) for k, v in base_time.items()}
    
    def _get_tool_selection(self, similarity_result: SimilarityResult, confidence: str) -> List[str]:
        """确定工具选择"""
        base_tools = ["nmap", "curl", "openssl", "nikto"]
        
        if confidence == "高":
            tech_name = similarity_result.best_match_name.lower()
            if "tomcat" in tech_name:
                base_tools.extend(["tomcat-scanner", "tomcat-war-scanner"])
            elif "wordpress" in tech_name:
                base_tools.extend(["wpscan", "wp-cli"])
            elif "mysql" in tech_name:
                base_tools.extend(["mysql-client", "sqlmap"])
        
        if confidence != "低":
            base_tools.extend(["nuclei", "zap-cli", "afrog"])
        
        return base_tools
    
    def _get_focus_areas(self, similarity_result: SimilarityResult) -> List[str]:
        """确定重点测试区域"""
        focus = ["认证机制", "访问控制", "输入验证", "配置安全"]
        
        # 基于安全假设增加重点
        for assumption in similarity_result.security_assumptions:
            if "默认凭证" in assumption:
                focus.append("默认凭证检查")
            if "管理接口" in assumption:
                focus.append("管理接口安全")
            if "CVE" in assumption:
                focus.append("CVE专项验证")
            if "配置" in assumption:
                focus.append("安全配置审查")
        
        return focus
    
    def _identify_uncertainty_factors(self, similarity_result: SimilarityResult) -> List[str]:
        """识别不确定性因素"""
        factors = []
        
        if similarity_result.similarity_score < 0.5:
            factors.append("技术相似度较低")
        
        if similarity_result.confidence < 0.4:
            factors.append("匹配置信度不足")
        
        target_feature = similarity_result.target_feature
        if not target_feature.name or target_feature.confidence < 0.3:
            factors.append("原始技术识别信息不足")
        
        if not similarity_result.matched_features:
            factors.append("缺乏具体特征匹配")
        
        if not factors:
            factors.append("无明显不确定性因素")
        
        return factors


# ============================================
# 主协调处理器
# ============================================

class UnknownTechHandler:
    """未知技术处理主协调器"""
    
    def __init__(self, tech_database_path: str = "tech_database.json"):
        """
        初始化未知技术处理器
        
        Args:
            tech_database_path: 技术数据库文件路径
        """
        self.tech_db_path = tech_database_path
        self.similarity_matcher = SimilarityMatcher(tech_database_path)
        self.security_inferencer = SecurityInferencer(tech_database_path)
    
    def process_unknown_technology(self, target_feature: TechnicalFeature) -> SecurityDecision:
        """
        处理未知技术
        
        Args:
            target_feature: 目标技术特征
            
        Returns:
            SecurityDecision: 安全决策结果
        """
        print(f"🔍 开始处理未知技术: {target_feature.name or '未识别技术'}")
        
        # 1. 相似度匹配
        similarity_result = self.similarity_matcher.find_best_match(target_feature)
        print(f"  相似度匹配完成: {similarity_result}")
        
        # 2. 安全推理
        security_decision = self.security_inferencer.infer_security_decision(similarity_result)
        print(f"  安全推理完成: 风险{security_decision.risk_assessment.get('risk_level', '未知')}, 置信度{security_decision.confidence_level}")
        
        # 3. 生成决策摘要
        summary = security_decision.get_summary()
        print(f"  决策摘要: {summary}")
        
        return security_decision
    
    def create_feature_from_raw_data(self, 
                                    raw_data: Dict[str, Any]) -> TechnicalFeature:
        """
        从原始数据创建技术特征
        
        Args:
            raw_data: 原始资产数据
            
        Returns:
            TechnicalFeature: 提取的技术特征
        """
        # 这里是一个简化的实现，实际应用需要更复杂的特征提取逻辑
        tech_type = raw_data.get("technology_type", "unknown")
        name = raw_data.get("name", None)
        version = raw_data.get("version", None)
        confidence = raw_data.get("confidence", 0.5)
        
        # 提取特征（简化版）
        protocol_features = raw_data.get("protocols", [])
        header_features = raw_data.get("headers", {})
        response_features = raw_data.get("responses", [])
        behavioral_features = raw_data.get("behavior", [])
        
        return TechnicalFeature(
            technology_type=tech_type,
            name=name,
            version=version,
            confidence=confidence,
            protocol_features=protocol_features,
            header_features=header_features,
            response_features=response_features,
            behavioral_features=behavioral_features
        )
    
    def demo_processing(self):
        """演示未知技术处理流程"""
        print("=" * 60)
        print("未知技术处理演示")
        print("=" * 60)
        
        # 创建示例未知技术
        unknown_tech = TechnicalFeature(
            technology_type="web_server",
            name=None,  # 未知名称
            version=None,
            confidence=0.2,
            protocol_features=["HTTP/1.1", "AJP"],
            header_features={
                "Server": "Apache-Coyote/1.1",
                "X-Powered-By": "JSP/2.3"
            },
            response_features=["Apache Tomcat", "Tomcat Manager"],
            behavioral_features=["servlet-container", "session-management"]
        )
        
        print(f"🧩 示例未知技术特征:")
        print(f"  类型: {unknown_tech.technology_type}")
        print(f"  协议特征: {unknown_tech.protocol_features}")
        print(f"  头部特征: {unknown_tech.header_features}")
        print(f"  识别置信度: {unknown_tech.confidence:.1%}")
        
        # 处理未知技术
        decision = self.process_unknown_technology(unknown_tech)
        
        print("\n📊 安全决策结果:")
        print(f"  最佳匹配: {decision.technology_info.best_match_name}")
        print(f"  相似度: {decision.technology_info.similarity_score:.3f}")
        print(f"  风险评估: {decision.risk_assessment.get('risk_level', '未知')} ({decision.risk_assessment.get('total_risk', 0):.1f}/10)")
        print(f"  置信级别: {decision.confidence_level}")
        print(f"  推荐测试动作: {len(decision.recommended_actions)}个")
        print(f"  不确定性因素: {decision.uncertainty_factors}")
        
        print("\n🎯 测试策略:")
        for key, value in decision.testing_strategy.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("演示完成 ✅")
        print("=" * 60)
        
        return decision


# ============================================
# 演示代码
# ============================================

if __name__ == "__main__":
    # 创建处理器实例
    handler = UnknownTechHandler("tech_database.json")
    
    # 运行演示
    try:
        decision = handler.demo_processing()
        
        # 保存演示结果
        result_path = "../deliverables/unknown_tech_demo_result.txt"
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write("未知技术处理演示结果\n")
            f.write("=" * 50 + "\n")
            f.write(f"最佳匹配: {decision.technology_info.best_match_name}\n")
            f.write(f"相似度: {decision.technology_info.similarity_score:.3f}\n")
            f.write(f"风险评估: {decision.risk_assessment.get('risk_level', '未知')}\n")
            f.write(f"置信级别: {decision.confidence_level}\n")
            f.write(f"推荐测试动作: {decision.recommended_actions}\n")
            
        print(f"\n📁 演示结果已保存到: {result_path}")
        
    except Exception as e:
        print(f"\n⚠️ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()