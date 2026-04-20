#!/usr/bin/env python3
"""
知识库进化器 - 基于测试结果自动更新安全知识

核心功能：根据历史测试结果、新发现的漏洞、技术特征变化等，
自动更新技术特征数据库、CVE知识库、风险评估规则等，
实现安全知识的持续进化和时效性管理。
"""

import json
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class KnowledgeEntry:
    """知识条目"""
    entry_id: str                    # 知识标识
    entry_type: str                  # 知识类型: technology, cve, vulnerability_pattern, risk_rule
    name: str                        # 知识名称
    content: Dict[str, Any]          # 知识内容
    confidence: float                # 置信度 (0-1)
    created_at: str                  # 创建时间
    last_updated: str                # 最后更新时间
    last_verified: str               # 最后验证时间
    
    # 时效性管理
    time_sensitivity: float          # 时效敏感度 (0-1, 越高越容易过时)
    decay_rate: float                # 衰减率 (每天置信度降低的比例)
    expiration_days: Optional[int]   # 过期天数 (None表示永不过期)
    
    # 来源追踪
    source: str                      # 知识来源
    evidence_count: int              # 证据数量
    verification_history: List[str]  # 验证历史
    
    def calculate_current_confidence(self) -> float:
        """计算当前置信度（考虑时间衰减）"""
        if not self.last_verified:
            return self.confidence
        
        try:
            last_verified_date = datetime.fromisoformat(self.last_verified)
            days_since_verification = (datetime.now() - last_verified_date).days
            
            # 时间衰减
            time_decay = math.exp(-self.decay_rate * days_since_verification)
            
            # 基础置信度 × 时间衰减因子
            current_confidence = self.confidence * time_decay
            
            # 如果有过期时间，检查是否过期
            if self.expiration_days and days_since_verification > self.expiration_days:
                current_confidence *= 0.5  # 过期后置信度减半
            
            return max(current_confidence, 0.0)
            
        except Exception:
            return self.confidence
    
    def get_summary(self) -> Dict[str, Any]:
        """获取知识摘要"""
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "name": self.name,
            "confidence": self.confidence,
            "current_confidence": self.calculate_current_confidence(),
            "last_updated": self.last_updated,
            "evidence_count": self.evidence_count
        }


@dataclass
class KnowledgeUpdate:
    """知识更新记录"""
    update_id: str                   # 更新标识
    entry_id: str                    # 知识条目ID
    update_type: str                 # 更新类型: create, update, confidence_adjust, deprecate, verify
    old_value: Optional[Any]         # 旧值
    new_value: Any                   # 新值
    reason: str                      # 更新原因
    evidence: List[str]              # 支持证据
    timestamp: str                   # 更新时间
    
    def get_summary(self) -> Dict[str, Any]:
        """获取更新摘要"""
        return {
            "update_id": self.update_id,
            "entry_id": self.entry_id,
            "update_type": self.update_type,
            "reason": self.reason[:80] + "..." if len(self.reason) > 80 else self.reason,
            "evidence_count": len(self.evidence),
            "timestamp": self.timestamp
        }


class KnowledgeBaseEvolver:
    """知识库进化器"""
    
    def __init__(self, knowledge_base_path: str = "tech_database.json"):
        """
        初始化知识库进化器
        
        Args:
            knowledge_base_path: 知识库文件路径
        """
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_entries: Dict[str, KnowledgeEntry] = {}
        self.update_history: List[KnowledgeUpdate] = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self) -> bool:
        """加载知识库"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为KnowledgeEntry对象
            for entry_id, entry_data in data.get("technologies", {}).items():
                entry = KnowledgeEntry(
                    entry_id=f"tech_{entry_id}",
                    entry_type="technology",
                    name=entry_data.get("name", entry_id),
                    content=entry_data,
                    confidence=entry_data.get("confidence", 0.8),
                    created_at=entry_data.get("created_at", datetime.now().isoformat()),
                    last_updated=entry_data.get("last_updated", datetime.now().isoformat()),
                    last_verified=entry_data.get("last_verified", ""),
                    time_sensitivity=entry_data.get("time_sensitivity", 0.3),
                    decay_rate=entry_data.get("decay_rate", 0.001),
                    expiration_days=entry_data.get("expiration_days"),
                    source=entry_data.get("source", "manual"),
                    evidence_count=entry_data.get("evidence_count", 1),
                    verification_history=entry_data.get("verification_history", [])
                )
                self.knowledge_entries[entry.entry_id] = entry
            
            print(f"✅ 加载 {len(self.knowledge_entries)} 条技术知识")
            return True
            
        except FileNotFoundError:
            print(f"⚠️ 知识库文件不存在: {self.knowledge_base_path}")
            return False
        except Exception as e:
            print(f"⚠️ 加载知识库失败: {e}")
            return False
    
    def evolve_from_test_results(self, test_records: List[Dict[str, Any]]) -> List[KnowledgeUpdate]:
        """
        基于测试结果进化知识库
        
        Args:
            test_records: 历史测试记录列表
            
        Returns:
            List[KnowledgeUpdate]: 知识更新列表
        """
        print("🧬 基于测试结果进化知识库...")
        self.update_history = []
        
        # 1. 分析技术特征与测试效果的关联
        print("  步骤1: 分析技术特征与测试效果关联...")
        tech_effectiveness = self._analyze_technology_effectiveness(test_records)
        
        # 2. 更新技术知识置信度
        print("  步骤2: 更新技术知识置信度...")
        self._update_technology_confidence(tech_effectiveness)
        
        # 3. 发现新的技术特征
        print("  步骤3: 发现新的技术特征...")
        self._discover_new_technology_features(test_records)
        
        # 4. 识别CVE验证状态
        print("  步骤4: 识别CVE验证状态...")
        self._verify_cve_status(test_records)
        
        # 5. 更新风险评估规则
        print("  步骤5: 更新风险评估规则...")
        self._update_risk_assessment_rules(test_records)
        
        # 6. 处理过期知识
        print("  步骤6: 处理过期知识...")
        self._handle_expired_knowledge()
        
        print(f"✅ 生成 {len(self.update_history)} 条知识更新")
        return self.update_history
    
    def _analyze_technology_effectiveness(self, test_records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """分析技术类型的测试效果"""
        tech_stats = defaultdict(lambda: {
            "test_count": 0,
            "success_count": 0,
            "avg_quality_score": 0.0,
            "total_vulns": 0
        })
        
        for record in test_records:
            tech_features = record.get("technology_features", {})
            tech_type = tech_features.get("technology_type", "unknown")
            
            stats = tech_stats[tech_type]
            stats["test_count"] += 1
            
            quality_score = record.get("quality_score", 0)
            if quality_score >= 70:
                stats["success_count"] += 1
            
            stats["avg_quality_score"] += quality_score
            stats["total_vulns"] += len(record.get("discovered_vulnerabilities", []))
        
        # 计算平均值
        for tech_type, stats in tech_stats.items():
            if stats["test_count"] > 0:
                stats["avg_quality_score"] /= stats["test_count"]
                stats["success_rate"] = stats["success_count"] / stats["test_count"]
                stats["avg_vulns_per_test"] = stats["total_vulns"] / stats["test_count"]
        
        return dict(tech_stats)
    
    def _update_technology_confidence(self, tech_effectiveness: Dict[str, Dict[str, float]]):
        """基于测试效果更新技术知识置信度"""
        for tech_type, stats in tech_effectiveness.items():
            if stats["test_count"] < 3:
                continue  # 数据不足
            
            # 查找相关技术知识
            for entry_id, entry in self.knowledge_entries.items():
                if entry.entry_type == "technology":
                    entry_name = entry.name.lower()
                    if tech_type.lower() in entry_name or tech_type.lower() in entry_id:
                        # 计算新的置信度
                        success_rate = stats.get("success_rate", 0.5)
                        avg_quality = stats.get("avg_quality_score", 50) / 100.0
                        
                        # 综合效果指标
                        effectiveness_score = (success_rate * 0.6 + avg_quality * 0.4)
                        
                        # 调整置信度
                        old_confidence = entry.confidence
                        if effectiveness_score > 0.7:
                            # 效果好，提升置信度
                            new_confidence = min(old_confidence + 0.05, 0.95)
                            update_reason = f"测试效果优秀：成功率{success_rate:.1%}, 平均质量{avg_quality:.1%}"
                        elif effectiveness_score < 0.4:
                            # 效果差，降低置信度
                            new_confidence = max(old_confidence - 0.1, 0.3)
                            update_reason = f"测试效果不佳：成功率{success_rate:.1%}, 平均质量{avg_quality:.1%}"
                        else:
                            # 效果一般，微调
                            new_confidence = old_confidence + (effectiveness_score - 0.5) * 0.1
                        
                        if abs(new_confidence - old_confidence) > 0.02:
                            update = KnowledgeUpdate(
                                update_id=f"upd_{entry_id}_{len(self.update_history)}",
                                entry_id=entry_id,
                                update_type="confidence_adjust",
                                old_value=old_confidence,
                                new_value=new_confidence,
                                reason=update_reason,
                                evidence=[f"基于{stats['test_count']}次测试，成功率{success_rate:.1%}"],
                                timestamp=datetime.now().isoformat()
                            )
                            self.update_history.append(update)
                            entry.confidence = new_confidence
                            entry.last_updated = update.timestamp
    
    def _discover_new_technology_features(self, test_records: List[Dict[str, Any]]):
        """从测试记录中发现新的技术特征"""
        # 收集所有技术特征
        all_features = defaultdict(list)
        
        for record in test_records:
            tech_features = record.get("technology_features", {})
            for key, value in tech_features.items():
                if isinstance(value, list):
                    all_features[key].extend(value)
                else:
                    all_features[key].append(value)
        
        # 统计特征频率
        feature_counts = {}
        for key, values in all_features.items():
            from collections import Counter
            feature_counts[key] = Counter(values)
        
        # 发现高频新特征
        for feature_name, counts in feature_counts.items():
            for feature_value, count in counts.items():
                if count >= 5:  # 出现5次以上
                    # 检查是否已存在于知识库
                    exists = False
                    for entry in self.knowledge_entries.values():
                        if feature_name in entry.content:
                            if isinstance(entry.content[feature_name], list):
                                if feature_value in entry.content[feature_name]:
                                    exists = True
                            elif entry.content[feature_name] == feature_value:
                                exists = True
                    
                    if not exists:
                        # 发现新特征，创建更新记录
                        update = KnowledgeUpdate(
                            update_id=f"new_feature_{feature_name}_{len(self.update_history)}",
                            entry_id="pending",  # 待分配到具体技术
                            update_type="create",
                            old_value=None,
                            new_value={"feature": feature_name, "value": feature_value, "frequency": count},
                            reason=f"发现新技术特征：{feature_name}={feature_value} (出现{count}次)",
                            evidence=[f"在{count}次测试中观察到该特征"],
                            timestamp=datetime.now().isoformat()
                        )
                        self.update_history.append(update)
    
    def _verify_cve_status(self, test_records: List[Dict[str, Any]]):
        """验证CVE的实际可利用性"""
        cve_stats = defaultdict(lambda: {"found": 0, "not_found": 0, "tests": 0})
        
        for record in test_records:
            tech_features = record.get("technology_features", {})
            discovered_vulns = record.get("discovered_vulnerabilities", [])
            
            # 统计CVE出现情况
            for vuln in discovered_vulns:
                cve_id = vuln.get("cve_id")
                if cve_id:
                    cve_stats[cve_id]["found"] += 1
            
            cve_stats["total"]["tests"] += 1
        
        # 生成CVE验证状态更新
        for cve_id, stats in cve_stats.items():
            if cve_id == "total":
                continue
            
            if stats["found"] >= 3:
                # CVE被多次验证，提升置信度
                update = KnowledgeUpdate(
                    update_id=f"cve_verified_{cve_id}",
                    entry_id=f"cve_{cve_id}",
                    update_type="verify",
                    old_value=None,
                    new_value={"verification_status": "confirmed", "found_count": stats["found"]},
                    reason=f"CVE {cve_id} 在{stats['found']}次测试中被成功利用",
                    evidence=[f"{stats['found']}次成功利用记录"],
                    timestamp=datetime.now().isoformat()
                )
                self.update_history.append(update)
    
    def _update_risk_assessment_rules(self, test_records: List[Dict[str, Any]]):
        """基于测试结果更新风险评估规则"""
        # 分析不同风险等级的实际表现
        risk_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for record in test_records:
            predicted_risk = record.get("planned_strategy", {}).get("predicted_risk", "medium")
            actual_vulns = len(record.get("discovered_vulnerabilities", []))
            
            # 简化风险判断
            if actual_vulns >= 3:
                actual_risk = "high"
            elif actual_vulns >= 1:
                actual_risk = "medium"
            else:
                actual_risk = "low"
            
            risk_accuracy[predicted_risk]["total"] += 1
            if predicted_risk == actual_risk:
                risk_accuracy[predicted_risk]["correct"] += 1
        
        # 生成规则调整建议
        for risk_level, stats in risk_accuracy.items():
            if stats["total"] >= 5:
                accuracy = stats["correct"] / stats["total"]
                if accuracy < 0.5:
                    update = KnowledgeUpdate(
                        update_id=f"risk_rule_adjust_{risk_level}",
                        entry_id=f"risk_rule_{risk_level}",
                        update_type="update",
                        old_value=None,
                        new_value={"accuracy": accuracy, "suggestion": "需要调整风险评估规则"},
                        reason=f"{risk_level}风险预测准确率仅{accuracy:.1%}，需要优化",
                        evidence=[f"{stats['correct']}/{stats['total']} 准确"],
                        timestamp=datetime.now().isoformat()
                    )
                    self.update_history.append(update)
    
    def _handle_expired_knowledge(self):
        """处理过期知识"""
        current_time = datetime.now()
        
        for entry_id, entry in self.knowledge_entries.items():
            if entry.expiration_days:
                try:
                    last_verified = datetime.fromisoformat(entry.last_verified) if entry.last_verified else None
                    if last_verified:
                        days_since = (current_time - last_verified).days
                        if days_since > entry.expiration_days:
                            update = KnowledgeUpdate(
                                update_id=f"expired_{entry_id}",
                                entry_id=entry_id,
                                update_type="deprecate",
                                old_value=entry.confidence,
                                new_value=entry.confidence * 0.5,
                                reason=f"知识已过期{days_since - entry.expiration_days}天",
                                evidence=[f"最后验证时间：{entry.last_verified}"],
                                timestamp=current_time.isoformat()
                            )
                            self.update_history.append(update)
                except Exception:
                    pass
    
    def add_new_knowledge(self, entry_type: str, name: str, content: Dict[str, Any],
                         source: str = "auto_discovery", confidence: float = 0.7) -> str:
        """添加新知识"""
        entry_id = f"{entry_type}_{name.lower().replace(' ', '_')}_{len(self.knowledge_entries)}"
        
        entry = KnowledgeEntry(
            entry_id=entry_id,
            entry_type=entry_type,
            name=name,
            content=content,
            confidence=confidence,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            last_verified="",
            time_sensitivity=0.3,
            decay_rate=0.001,
            expiration_days=None,
            source=source,
            evidence_count=1,
            verification_history=[]
        )
        
        self.knowledge_entries[entry_id] = entry
        
        update = KnowledgeUpdate(
            update_id=f"create_{entry_id}",
            entry_id=entry_id,
            update_type="create",
            old_value=None,
            new_value=content,
            reason=f"添加新知识：{name}",
            evidence=[f"来源：{source}"],
            timestamp=datetime.now().isoformat()
        )
        self.update_history.append(update)
        
        return entry_id
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """获取知识进化摘要"""
        if not self.update_history:
            return {"total_updates": 0}
        
        # 按类型统计
        type_counts = defaultdict(int)
        for update in self.update_history:
            type_counts[update.update_type] += 1
        
        # 按知识类型统计
        entry_type_counts = defaultdict(int)
        for entry in self.knowledge_entries.values():
            entry_type_counts[entry.entry_type] += 1
        
        # 计算平均置信度
        avg_confidence = sum(e.confidence for e in self.knowledge_entries.values()) / len(self.knowledge_entries)
        
        return {
            "total_knowledge_entries": len(self.knowledge_entries),
            "knowledge_types": dict(entry_type_counts),
            "total_updates": len(self.update_history),
            "update_types": dict(type_counts),
            "average_confidence": avg_confidence,
            "recent_updates": [u.get_summary() for u in self.update_history[-5:]]
        }
    
    def save_knowledge_base(self, output_path: Optional[str] = None) -> bool:
        """保存知识库"""
        output_path = output_path or self.knowledge_base_path
        
        try:
            # 转换为可序列化格式
            data = {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(self.knowledge_entries),
                "technologies": {}
            }
            
            for entry_id, entry in self.knowledge_entries.items():
                data["technologies"][entry_id] = {
                    "name": entry.name,
                    "content": entry.content,
                    "confidence": entry.confidence,
                    "current_confidence": entry.calculate_current_confidence(),
                    "created_at": entry.created_at,
                    "last_updated": entry.last_updated,
                    "last_verified": entry.last_verified,
                    "time_sensitivity": entry.time_sensitivity,
                    "decay_rate": entry.decay_rate,
                    "expiration_days": entry.expiration_days,
                    "source": entry.source,
                    "evidence_count": entry.evidence_count,
                    "verification_history": entry.verification_history
                }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 保存 {len(self.knowledge_entries)} 条知识到 {output_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ 保存知识库失败: {e}")
            return False


def demo_knowledge_evolver():
    """演示知识库进化器"""
    print("=" * 70)
    print("知识库进化器演示")
    print("=" * 70)
    
    # 创建知识库进化器
    evolver = KnowledgeBaseEvolver()
    
    # 如果没有现有知识库，初始化一些示例数据
    if not evolver.knowledge_entries:
        print("\n🎯 初始化示例知识库...")
        evolver.add_new_knowledge(
            entry_type="technology",
            name="Apache Tomcat",
            content={
                "technology_type": "web_server",
                "protocols": ["HTTP/1.1", "AJP"],
                "default_ports": [8080, 8009],
                "common_vulnerabilities": ["CVE-2020-1938", "CVE-2017-12615"]
            },
            source="manual",
            confidence=0.85
        )
        
        evolver.add_new_knowledge(
            entry_type="technology",
            name="MySQL Database",
            content={
                "technology_type": "database",
                "protocols": ["MySQL Protocol"],
                "default_ports": [3306],
                "common_vulnerabilities": ["CVE-2012-2122", "CVE-2016-6662"]
            },
            source="manual",
            confidence=0.9
        )
    
    print(f"\n📊 初始知识库状态:")
    print(f"  总知识条目: {len(evolver.knowledge_entries)}")
    for entry_id, entry in evolver.knowledge_entries.items():
        print(f"  • {entry.name}: 置信度={entry.confidence:.2f}, "
              f"当前置信度={entry.calculate_current_confidence():.2f}")
    
    # 模拟测试结果
    print(f"\n🧪 加载模拟测试结果...")
    test_records = []
    for i in range(20):
        record = {
            "test_id": f"test_{i:04d}",
            "technology_features": {
                "technology_type": ["web_server", "database", "cms"][i % 3],
                "protocols": ["HTTP/1.1", "AJP"][:i%2+1]
            },
            "planned_strategy": {
                "predicted_risk": ["low", "medium", "high"][i % 3]
            },
            "discovered_vulnerabilities": [
                {"cve_id": "CVE-2020-1938"} if i % 4 == 0 else {}
            ] if i % 2 == 0 else [],
            "quality_score": 60.0 + i * 2
        }
        test_records.append(record)
    
    print(f"  加载 {len(test_records)} 条测试记录")
    
    # 进化知识库
    updates = evolver.evolve_from_test_results(test_records)
    
    # 显示进化结果
    summary = evolver.get_evolution_summary()
    print(f"\n🧬 知识进化结果:")
    print(f"  总知识条目: {summary['total_knowledge_entries']}")
    print(f"  知识类型: {summary.get('knowledge_types', {})}")
    print(f"  总更新数: {summary['total_updates']}")
    print(f"  更新类型: {summary.get('update_types', {})}")
    print(f"  平均置信度: {summary['average_confidence']:.3f}")
    
    if summary['total_updates'] > 0:
        print(f"\n📝 最近5条更新:")
        for i, update in enumerate(summary['recent_updates'], 1):
            print(f"  {i}. {update['update_type']}: {update['reason']}")
    
    # 保存知识库
    print(f"\n💾 保存更新后的知识库...")
    evolver.save_knowledge_base("evolved_knowledge_base.json")
    
    print("\n" + "=" * 70)
    print("知识库进化器演示完成 ✅")
    print("=" * 70)


if __name__ == "__main__":
    demo_knowledge_evolver()