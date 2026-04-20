#!/usr/bin/env python3
"""
技术特征提取器 - 智能测试规划引擎阶段三

从各种资产收集工具的输出（Nmap、WhatWeb、Httpx等）提取统一的技术特征。
支持多种输入格式，输出标准化的TechnicalFeature对象。
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# 导入核心数据结构
from unknown_tech_handler import TechnicalFeature


@dataclass
class ExtractionResult:
    """特征提取结果"""
    success: bool
    features: List[TechnicalFeature]
    errors: List[str]
    source_file: str


class FeatureExtractor:
    """技术特征提取器"""
    
    def __init__(self):
        """初始化特征提取器"""
        self.supported_formats = ["json", "xml", "txt"]
        self.extraction_rules = self._load_extraction_rules()
    
    def _load_extraction_rules(self) -> Dict[str, Any]:
        """加载特征提取规则"""
        return {
            "protocol_patterns": {
                "HTTP/1.1": r"HTTP/1\.[01]",
                "HTTP/2": r"HTTP/2",
                "AJP": r"AJP|Apache JServ Protocol",
                "MySQL": r"MySQL|mysql",
                "FTP": r"FTP|ftp",
                "SSH": r"SSH|ssh",
            },
            "technology_signatures": {
                "Apache": r"Apache/?([\d\.]+)?",
                "Nginx": r"Nginx/?([\d\.]+)?",
                "Tomcat": r"Tomcat/?([\d\.]+)?|Coyote",
                "IIS": r"IIS/?([\d\.]+)?|Microsoft-IIS",
                "Spring": r"Spring|X-Application-Context",
                "Django": r"Django",
                "WordPress": r"WordPress|wp-content|wp-includes",
            },
            "header_mappings": {
                "Server": "server",
                "X-Powered-By": "powered_by",
                "X-Application-Context": "app_context",
                "X-Frame-Options": "frame_options",
                "X-Content-Type-Options": "content_type_options",
            }
        }
    
    def extract_from_json(self, json_path: str) -> ExtractionResult:
        """
        从JSON格式资产数据提取特征
        
        Args:
            json_path: JSON文件路径
            
        Returns:
            ExtractionResult: 提取结果
        """
        features = []
        errors = []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return ExtractionResult(
                success=False,
                features=[],
                errors=[f"读取JSON文件失败: {e}"],
                source_file=json_path
            )
        
        # 处理不同格式的JSON数据
        if isinstance(data, list):
            # 资产列表
            for asset in data:
                try:
                    feature = self._extract_from_single_asset(asset)
                    if feature:
                        features.append(feature)
                except Exception as e:
                    errors.append(f"处理资产失败: {e}")
        elif isinstance(data, dict):
            # 单个资产或包含资产的字典
            if "assets" in data:
                # 包含资产列表的字典
                for asset in data.get("assets", []):
                    try:
                        feature = self._extract_from_single_asset(asset)
                        if feature:
                            features.append(feature)
                    except Exception as e:
                        errors.append(f"处理资产失败: {e}")
            else:
                # 单个资产
                try:
                    feature = self._extract_from_single_asset(data)
                    if feature:
                        features.append(feature)
                except Exception as e:
                    errors.append(f"处理资产失败: {e}")
        
        return ExtractionResult(
            success=len(features) > 0,
            features=features,
            errors=errors,
            source_file=json_path
        )
    
    def _extract_from_single_asset(self, asset: Dict[str, Any]) -> Optional[TechnicalFeature]:
        """
        从单个资产字典提取技术特征
        
        Args:
            asset: 资产字典
            
        Returns:
            Optional[TechnicalFeature]: 提取的技术特征
        """
        # 检查是否为多技术资产（如zero_asset.json格式）
        if "technologies" in asset and isinstance(asset["technologies"], list):
            # 对于有多个技术的资产，提取第一个主要技术
            if asset["technologies"]:
                main_tech = asset["technologies"][0]
                return self._extract_from_technology_info(asset, main_tech)
        
        # 1. 提取基本信息
        tech_type = self._extract_technology_type(asset)
        name = self._extract_technology_name(asset)
        version = self._extract_version(asset)
        confidence = self._calculate_confidence(asset)
        
        # 2. 提取特征向量
        protocol_features = self._extract_protocol_features(asset)
        header_features = self._extract_header_features(asset)
        response_features = self._extract_response_features(asset)
        behavioral_features = self._extract_behavioral_features(asset)
        
        # 3. 构建技术特征对象
        feature = TechnicalFeature(
            technology_type=tech_type,
            name=name,
            version=version,
            confidence=confidence,
            protocol_features=protocol_features,
            header_features=header_features,
            response_features=response_features,
            behavioral_features=behavioral_features
        )
        
        return feature
    
    def _extract_from_technology_info(self, asset: Dict[str, Any], tech_info: Dict[str, Any]) -> TechnicalFeature:
        """
        从技术信息字典提取特征（专门处理zero_asset.json格式）
        
        Args:
            asset: 资产字典
            tech_info: 技术信息字典
            
        Returns:
            TechnicalFeature: 提取的技术特征
        """
        tech_name = tech_info.get("name", "未知")
        tech_version = tech_info.get("version")
        tech_confidence = tech_info.get("confidence", 0.5)
        
        # 确定技术类型
        tech_type = self._infer_technology_type_from_name(tech_name)
        
        # 提取协议特征
        protocol_features = []
        if "Tomcat" in tech_name or "Apache" in tech_name:
            protocol_features = ["HTTP/1.1", "AJP"]
        elif "Nginx" in tech_name:
            protocol_features = ["HTTP/1.1", "HTTP/2"]
        elif "MySQL" in tech_name:
            protocol_features = ["MySQL Protocol"]
        
        # 提取头部特征
        header_features = {}
        if "Tomcat" in tech_name:
            header_features = {
                "Server": "Apache-Coyote/1.1",
                "X-Powered-By": "JSP/2.3"
            }
        elif "Nginx" in tech_name:
            header_features = {"Server": f"nginx/{tech_version or 'unknown'}"}
        
        # 提取响应特征
        response_features = [tech_name]
        if "Tomcat" in tech_name:
            response_features.extend(["Apache Tomcat", "Tomcat Manager"])
        elif "WordPress" in tech_name:
            response_features.extend(["wp-content", "wp-includes"])
        
        # 提取行为特征
        behavioral_features = []
        if tech_type == "web_server":
            behavioral_features = ["static-file-serving", "reverse-proxy"]
        elif tech_type == "web_framework":
            behavioral_features = ["request-routing", "template-rendering"]
        elif tech_type == "cms":
            behavioral_features = ["content-management", "plugin-architecture"]
        
        # 从资产中提取额外行为特征
        if "endpoints" in asset:
            endpoints = asset["endpoints"]
            if any(ep.get("auth_required") for ep in endpoints):
                behavioral_features.append("authentication")
            if any(ep.get("session_based") for ep in endpoints):
                behavioral_features.append("session-management")
        
        return TechnicalFeature(
            technology_type=tech_type,
            name=tech_name,
            version=tech_version,
            confidence=tech_confidence,
            protocol_features=protocol_features,
            header_features=header_features,
            response_features=response_features,
            behavioral_features=behavioral_features
        )
    
    def _infer_technology_type_from_name(self, tech_name: str) -> str:
        """从技术名称推断技术类型"""
        tech_name_lower = tech_name.lower()
        
        if any(x in tech_name_lower for x in ["tomcat", "nginx", "apache", "iis"]):
            return "web_server"
        elif any(x in tech_name_lower for x in ["spring", "django", "flask", "rails"]):
            return "web_framework"
        elif any(x in tech_name_lower for x in ["wordpress", "joomla", "drupal"]):
            return "cms"
        elif any(x in tech_name_lower for x in ["mysql", "postgresql", "mongodb", "oracle"]):
            return "database"
        elif any(x in tech_name_lower for x in ["jquery", "bootstrap", "react", "angular"]):
            return "javascript_library"
        else:
            return "unknown"
    
    def _extract_technology_type(self, asset: Dict[str, Any]) -> str:
        """从资产提取技术类型"""
        # 尝试从不同字段获取技术类型
        if "technology_type" in asset:
            return asset["technology_type"]
        
        if "category" in asset:
            return asset["category"]
        
        # 基于端口推断
        port = asset.get("port", 0)
        if port in [80, 443, 8080, 8443]:
            return "web_server"
        elif port in [3306, 5432, 1433, 27017]:
            return "database"
        elif port in [22, 21, 23, 25]:
            return "service"
        elif port in [8000, 8001, 8002]:
            return "application"
        
        return "unknown"
    
    def _extract_technology_name(self, asset: Dict[str, Any]) -> Optional[str]:
        """从资产提取技术名称"""
        # 尝试从不同字段获取
        if "name" in asset and asset["name"]:
            return asset["name"]
        
        if "technology" in asset and asset["technology"]:
            return asset["technology"]
        
        if "product" in asset and asset["product"]:
            return asset["product"]
        
        if "server" in asset and asset["server"]:
            return asset["server"]
        
        # 从指纹信息提取
        if "fingerprint" in asset:
            fp = asset["fingerprint"]
            if isinstance(fp, dict):
                return fp.get("technology", None)
        
        return None
    
    def _extract_version(self, asset: Dict[str, Any]) -> Optional[str]:
        """从资产提取版本号"""
        # 直接版本字段
        if "version" in asset and asset["version"]:
            return asset["version"]
        
        # 从产品版本提取
        if "product_version" in asset and asset["product_version"]:
            return asset["product_version"]
        
        # 从指纹信息提取
        if "fingerprint" in asset:
            fp = asset["fingerprint"]
            if isinstance(fp, dict):
                return fp.get("version", None)
        
        # 从服务器头部提取版本
        if "headers" in asset:
            headers = asset["headers"]
            if isinstance(headers, dict):
                server = headers.get("Server", "")
                if server:
                    # 尝试从Server头部提取版本
                    match = re.search(r'/([\d\.]+)', server)
                    if match:
                        return match.group(1)
        
        return None
    
    def _calculate_confidence(self, asset: Dict[str, Any]) -> float:
        """计算技术识别置信度"""
        confidence = 0.5  # 基础置信度
        
        # 有明确的技术名称
        if asset.get("name") or asset.get("technology"):
            confidence += 0.2
        
        # 有版本信息
        if asset.get("version") or asset.get("product_version"):
            confidence += 0.1
        
        # 有指纹信息
        if "fingerprint" in asset:
            confidence += 0.15
        
        # 有多个特征
        feature_count = 0
        if asset.get("protocols"):
            feature_count += len(asset.get("protocols", []))
        if asset.get("headers"):
            feature_count += len(asset.get("headers", {}))
        if asset.get("responses"):
            feature_count += len(asset.get("responses", []))
        
        if feature_count >= 3:
            confidence += 0.15
        elif feature_count >= 1:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_protocol_features(self, asset: Dict[str, Any]) -> List[str]:
        """提取协议特征"""
        protocols = []
        
        # 直接从protocols字段获取
        if "protocols" in asset and isinstance(asset["protocols"], list):
            protocols.extend(asset["protocols"])
        
        # 从端口和服务推断
        port = asset.get("port", 0)
        service = asset.get("service", "")
        
        if port == 80 or "http" in service.lower():
            protocols.append("HTTP/1.1")
        if port == 443 or "https" in service.lower():
            protocols.append("HTTPS")
        if port == 8009 or "ajp" in service.lower():
            protocols.append("AJP")
        if port == 3306 or "mysql" in service.lower():
            protocols.append("MySQL Protocol")
        if port == 22 or "ssh" in service.lower():
            protocols.append("SSH")
        
        # 从指纹信息提取
        if "fingerprint" in asset:
            fp = asset["fingerprint"]
            if isinstance(fp, dict) and "protocols" in fp:
                protocols.extend(fp["protocols"])
        
        return list(set(protocols))  # 去重
    
    def _extract_header_features(self, asset: Dict[str, Any]) -> Dict[str, str]:
        """提取HTTP头部特征"""
        headers = {}
        
        # 直接从headers字段获取
        if "headers" in asset and isinstance(asset["headers"], dict):
            headers.update(asset["headers"])
        
        # 从响应信息提取
        if "response" in asset:
            response = asset["response"]
            if isinstance(response, dict) and "headers" in response:
                headers.update(response["headers"])
        
        # 从指纹信息提取
        if "fingerprint" in asset:
            fp = asset["fingerprint"]
            if isinstance(fp, dict) and "headers" in fp:
                headers.update(fp["headers"])
        
        return headers
    
    def _extract_response_features(self, asset: Dict[str, Any]) -> List[str]:
        """提取响应体特征"""
        responses = []
        
        # 直接从responses字段获取
        if "responses" in asset and isinstance(asset["responses"], list):
            responses.extend(asset["responses"])
        
        # 从响应体提取关键词
        if "response_body" in asset:
            body = asset["response_body"]
            if isinstance(body, str):
                # 提取技术关键词
                tech_keywords = ["Apache", "Nginx", "Tomcat", "IIS", "Spring", 
                               "Django", "WordPress", "Joomla", "Drupal"]
                for keyword in tech_keywords:
                    if keyword.lower() in body.lower():
                        responses.append(keyword)
        
        # 从指纹信息提取
        if "fingerprint" in asset:
            fp = asset["fingerprint"]
            if isinstance(fp, dict) and "responses" in fp:
                responses.extend(fp["responses"])
        
        return list(set(responses))  # 去重
    
    def _extract_behavioral_features(self, asset: Dict[str, Any]) -> List[str]:
        """提取行为特征"""
        behaviors = []
        
        # 从behavior字段直接获取
        if "behavior" in asset and isinstance(asset["behavior"], list):
            behaviors.extend(asset["behavior"])
        
        # 从技术类型推断
        tech_type = asset.get("technology_type", "")
        if tech_type == "web_framework":
            behaviors.append("request-routing")
            behaviors.append("template-rendering")
        elif tech_type == "database":
            behaviors.append("query-processing")
            behaviors.append("data-storage")
        elif tech_type == "web_server":
            behaviors.append("static-file-serving")
            behaviors.append("reverse-proxy")
        
        # 从功能推断
        if asset.get("has_admin_interface"):
            behaviors.append("admin-interface")
        if asset.get("has_authentication"):
            behaviors.append("authentication")
        if asset.get("has_session_management"):
            behaviors.append("session-management")
        
        return list(set(behaviors))  # 去重
    
    def extract_from_risk_report(self, risk_report_path: str) -> List[TechnicalFeature]:
        """
        从风险报告提取技术特征
        
        Args:
            risk_report_path: 风险报告路径
            
        Returns:
            List[TechnicalFeature]: 提取的技术特征列表
        """
        features = []
        
        try:
            with open(risk_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
        except Exception as e:
            print(f"⚠️ 读取风险报告失败: {e}")
            return features
        
        # 从风险报告中提取资产信息
        if "assessed_assets" in report:
            for asset in report["assessed_assets"]:
                feature = self._extract_from_single_asset(asset)
                if feature:
                    features.append(feature)
        
        # 从技术栈信息提取
        if "technology_stack" in report:
            for tech in report["technology_stack"]:
                feature = TechnicalFeature(
                    technology_type=tech.get("category", "unknown"),
                    name=tech.get("name"),
                    version=tech.get("version"),
                    confidence=tech.get("confidence", 0.5),
                    protocol_features=tech.get("protocols", []),
                    header_features=tech.get("headers", {}),
                    response_features=tech.get("responses", []),
                    behavioral_features=tech.get("behavior", [])
                )
                features.append(feature)
        
        return features
    
    def demo_extraction(self, asset_path: str):
        """演示特征提取功能"""
        print("=" * 60)
        print("技术特征提取器演示")
        print("=" * 60)
        
        print(f"\n📁 从文件提取: {asset_path}")
        
        # 执行提取
        result = self.extract_from_json(asset_path)
        
        if result.success:
            print(f"\n✅ 提取成功!")
            print(f"  提取到 {len(result.features)} 个技术特征")
            
            for i, feature in enumerate(result.features[:3], 1):  # 只显示前3个
                print(f"\n  特征 {i}:")
                print(f"    类型: {feature.technology_type}")
                print(f"    名称: {feature.name or '未知'}")
                print(f"    版本: {feature.version or '未知'}")
                print(f"    置信度: {feature.confidence:.1%}")
                print(f"    协议特征: {feature.protocol_features[:3]}")
                print(f"    头部特征: {len(feature.header_features)}个")
                print(f"    响应特征: {feature.response_features[:3]}")
                print(f"    行为特征: {feature.behavioral_features[:3]}")
            
            if len(result.features) > 3:
                print(f"\n  ... 还有 {len(result.features) - 3} 个特征")
        else:
            print(f"\n❌ 提取失败")
            for error in result.errors:
                print(f"  错误: {error}")
        
        if result.errors:
            print(f"\n⚠️ 警告: {len(result.errors)} 个非致命错误")
            for error in result.errors[:3]:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        print("演示完成 ✅")
        print("=" * 60)
        
        return result


# ============================================
# 演示代码
# ============================================

if __name__ == "__main__":
    extractor = FeatureExtractor()
    
    # 演示从资产文件提取
    asset_path = "../assets/zero_asset.json"
    result = extractor.demo_extraction(asset_path)
    
    # 保存提取结果
    if result.success:
        output_path = "../deliverables/extracted_features.json"
        
        # 转换为可序列化格式
        features_data = []
        for feature in result.features:
            features_data.append({
                "technology_type": feature.technology_type,
                "name": feature.name,
                "version": feature.version,
                "confidence": feature.confidence,
                "protocol_features": feature.protocol_features,
                "header_features": feature.header_features,
                "response_features": feature.response_features,
                "behavioral_features": feature.behavioral_features
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(features_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 提取结果已保存到: {output_path}")
        print(f"  共 {len(features_data)} 个技术特征")