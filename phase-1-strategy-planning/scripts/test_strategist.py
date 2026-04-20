#!/usr/bin/env python3
"""
测试策略生成器 - 基于资产信息+规则引擎生成针对性测试策略

核心功能：
1. 整合多个数据源（WhatWeb, Nmap, Subfinder等）的资产信息
2. 应用规则引擎生成测试动作
3. 聚合和优化测试计划
4. 生成可执行的命令行列表和策略报告

输入: 标准化资产集合 + 规则引擎
输出: 测试策略文档 + 可执行命令列表
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re
from enum import Enum

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

# 导入其他模块
try:
    from asset_normalizer import AssetNormalizer, StandardizedAsset
    from rule_engine import RuleEngine, RuleActionType, TestPriority
except ImportError:
    # 在技能开发期间可能需要相对导入
    import sys
    sys.path.append(str(Path(__file__).parent))
    from asset_normalizer import AssetNormalizer, StandardizedAsset
    from rule_engine import RuleEngine, RuleActionType, TestPriority

class TestCategory(str, Enum):
    """测试分类"""
    CVE_VALIDATION = "cve_validation"
    CONFIGURATION_TEST = "configuration_test"
    AUTHENTICATION_TEST = "authentication_test"
    BUSINESS_LOGIC_TEST = "business_logic_test"
    DATA_PROTECTION_TEST = "data_protection_test"
    SESSION_SECURITY_TEST = "session_security_test"
    FILE_UPLOAD_TEST = "file_upload_test"
    API_SECURITY_TEST = "api_security_test"
    INFRASTRUCTURE_TEST = "infrastructure_test"
    INFORMATION_DISCLOSURE = "information_disclosure"

class TestAction(BaseModel):
    """测试动作"""
    id: str
    category: TestCategory
    name: str
    description: str
    priority: TestPriority = TestPriority.MEDIUM
    estimated_time_minutes: int = 30
    tools: List[str] = Field(default_factory=list)
    commands: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    expected_outcomes: List[str] = Field(default_factory=list)
    risk_level: str = "medium"
    
    @property
    def is_critical(self):
        return self.priority in [TestPriority.CRITICAL, TestPriority.HIGH]

class TestStrategy(BaseModel):
    """测试策略"""
    target_name: str
    target_url: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    total_estimated_time_minutes: int = 0
    total_actions: int = 0
    
    # 分组测试动作
    critical_actions: List[TestAction] = Field(default_factory=list)
    high_priority_actions: List[TestAction] = Field(default_factory=list)
    medium_priority_actions: List[TestAction] = Field(default_factory=list)
    low_priority_actions: List[TestAction] = Field(default_factory=list)
    
    # 按类别分组
    actions_by_category: Dict[str, List[TestAction]] = Field(default_factory=dict)
    
    # 执行计划
    execution_plan: List[Dict[str, Any]] = Field(default_factory=list)
    
    def calculate_totals(self):
        """计算总时间和数量"""
        all_actions = (self.critical_actions + self.high_priority_actions + 
                       self.medium_priority_actions + self.low_priority_actions)
        
        self.total_actions = len(all_actions)
        self.total_estimated_time_minutes = sum(
            action.estimated_time_minutes for action in all_actions
        )
        
        # 按类别分组
        for action in all_actions:
            category = action.category.value
            if category not in self.actions_by_category:
                self.actions_by_category[category] = []
            self.actions_by_category[category].append(action)
    
    def generate_execution_plan(self):
        """生成执行计划"""
        self.execution_plan = []
        
        # 第一阶段：紧急测试 (critical + high)
        urgent_actions = self.critical_actions + self.high_priority_actions
        if urgent_actions:
            urgent_time = sum(a.estimated_time_minutes for a in urgent_actions)
            self.execution_plan.append({
                "phase": 1,
                "name": "紧急测试",
                "description": "立即需要修复的高风险问题",
                "estimated_time_minutes": urgent_time,
                "actions": [action.dict() for action in urgent_actions]
            })
        
        # 第二阶段：核心测试 (medium)
        medium_actions = self.medium_priority_actions
        if medium_actions:
            medium_time = sum(a.estimated_time_minutes for a in medium_actions)
            self.execution_plan.append({
                "phase": 2,
                "name": "核心测试",
                "description": "重要的安全配置和功能测试",
                "estimated_time_minutes": medium_time,
                "actions": [action.dict() for action in medium_actions]
            })
        
        # 第三阶段：彻底测试 (low + 专项)
        low_actions = self.low_priority_actions
        if low_actions:
            # 按类别分组低优先级动作
            low_by_category = {}
            for action in low_actions:
                category = action.category.value
                if category not in low_by_category:
                    low_by_category[category] = []
                low_by_category[category].append(action)
            
            for category, actions in low_by_category.items():
                cat_time = sum(a.estimated_time_minutes for a in actions)
                self.execution_plan.append({
                    "phase": 3,
                    "name": f"{category}专项测试",
                    "description": f"特定类别的深度测试",
                    "estimated_time_minutes": cat_time,
                    "actions": [action.dict() for action in actions]
                })
    
    def to_markdown(self) -> str:
        """生成Markdown格式的策略报告"""
        self.calculate_totals()
        self.generate_execution_plan()
        
        lines = []
        
        # 标题
        lines.append(f"# 🧠 智能测试策略 - {self.target_name}")
        lines.append("")
        lines.append(f"**生成时间**: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**目标系统**: {self.target_url or '未知URL'}")
        lines.append(f"**总测试项**: {self.total_actions} 个")
        lines.append(f"**预计总时间**: {self.total_estimated_time_minutes} 分钟")
        lines.append("")
        
        # 执行摘要
        lines.append("## 📊 执行摘要")
        lines.append("")
        
        priority_counts = {
            "🔴 紧急": len(self.critical_actions),
            "🟠 高优先级": len(self.high_priority_actions),
            "🟡 中优先级": len(self.medium_priority_actions),
            "🟢 低优先级": len(self.low_priority_actions),
        }
        
        lines.append("### 测试优先级分布")
        for priority, count in priority_counts.items():
            if count > 0:
                lines.append(f"- {priority}: {count} 个测试项")
        lines.append("")
        
        lines.append("### 测试类别分布")
        for category, actions in self.actions_by_category.items():
            lines.append(f"- **{category}**: {len(actions)} 个测试项")
        lines.append("")
        
        # 执行计划
        lines.append("## 🚀 执行计划")
        lines.append("")
        
        for phase in self.execution_plan:
            lines.append(f"### 阶段 {phase['phase']}: {phase['name']}")
            lines.append(f"**描述**: {phase['description']}")
            lines.append(f"**预计时间**: {phase['estimated_time_minutes']} 分钟")
            lines.append("")
            
            for action in phase['actions'][:5]:  # 只显示前5个动作
                lines.append(f"#### {action['name']}")
                lines.append(f"- **优先级**: {action['priority']}")
                lines.append(f"- **描述**: {action['description']}")
                if action['tools']:
                    lines.append(f"- **工具**: {', '.join(action['tools'])}")
                if action['commands']:
                    lines.append("- **命令**:")
                    for cmd in action['commands'][:3]:  # 只显示前3个命令
                        lines.append(f"  ```bash\n  {cmd}\n  ```")
                lines.append("")
            
            if len(phase['actions']) > 5:
                lines.append(f"*...还有 {len(phase['actions']) - 5} 个测试项*")
                lines.append("")
        
        # 详细测试项清单
        lines.append("## 📋 详细测试项清单")
        lines.append("")
        
        # 按优先级分组显示所有测试项
        priority_groups = [
            ("🔴 紧急测试", self.critical_actions),
            ("🟠 高优先级", self.high_priority_actions),
            ("🟡 中优先级", self.medium_priority_actions),
            ("🟢 低优先级", self.low_priority_actions),
        ]
        
        for priority_name, actions in priority_groups:
            if not actions:
                continue
            
            lines.append(f"### {priority_name}")
            lines.append("")
            
            for action in actions:
                lines.append(f"#### {action.name}")
                lines.append(f"- **类别**: {action.category.value}")
                lines.append(f"- **预计时间**: {action.estimated_time_minutes} 分钟")
                lines.append(f"- **风险等级**: {action.risk_level}")
                lines.append(f"- **描述**: {action.description}")
                
                if action.tools:
                    lines.append(f"- **建议工具**: {', '.join(action.tools)}")
                
                if action.expected_outcomes:
                    lines.append("- **预期结果**:")
                    for outcome in action.expected_outcomes:
                        lines.append(f"  - {outcome}")
                
                if action.commands:
                    lines.append("- **执行命令**:")
                    for cmd in action.commands:
                        lines.append(f"  ```bash\n  {cmd}\n  ```")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def to_commands_list(self) -> str:
        """生成可执行的命令行列表"""
        commands = []
        commands.append("#!/bin/bash")
        commands.append(f"# 智能测试规划引擎 - {self.target_name}")
        commands.append(f"# 生成时间: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        commands.append(f"# 目标: {self.target_url or '未知URL'}")
        commands.append("")
        
        # 按优先级和类别组织命令
        all_actions = (self.critical_actions + self.high_priority_actions + 
                       self.medium_priority_actions + self.low_priority_actions)
        
        category_actions = {}
        for action in all_actions:
            category = action.category.value
            if category not in category_actions:
                category_actions[category] = []
            category_actions[category].extend(action.commands)
        
        for category, cmd_list in category_actions.items():
            if not cmd_list:
                continue
                
            commands.append(f"echo '🚀 开始 {category} 测试...'")
            commands.append(f"echo '======================================='")
            commands.append("")
            
            for i, cmd in enumerate(cmd_list, 1):
                commands.append(f"# {category} 测试 {i}")
                commands.append(cmd)
                commands.append("")
            
            commands.append(f"echo '✅ {category} 测试完成'")
            commands.append("sleep 2")
            commands.append("")
        
        commands.append("echo '🎉 所有测试执行完成！'")
        commands.append(f"echo '总计执行 {len(all_actions)} 个测试项'")
        
        return "\n".join(commands)

class TestStrategist:
    """测试策略生成器主类"""
    
    def __init__(self, rules_dir: Optional[Path] = None, knowledge_base_dir: Optional[Path] = None):
        # 初始化组件
        self.asset_normalizer = AssetNormalizer()
        self.rule_engine = RuleEngine(rules_dir)
        self.knowledge_base = self._load_knowledge_base(knowledge_base_dir)
        
        # 缓存和状态
        self.strategies: Dict[str, TestStrategy] = {}
        
    def _load_knowledge_base(self, knowledge_base_dir: Optional[Path]) -> Dict[str, Any]:
        """加载知识库"""
        if not knowledge_base_dir:
            # 尝试从默认位置加载
            default_path = Path(__file__).parent.parent / "data" / "technology_db.json"
            knowledge_base_dir = default_path.parent
        
        knowledge_base = {}
        
        try:
            # 加载技术数据库
            tech_db_path = knowledge_base_dir / "technology_db.json"
            if tech_db_path.exists():
                with open(tech_db_path, 'r') as f:
                    knowledge_base['technologies'] = json.load(f)
            
            # 加载规则模板
            rules_template_path = knowledge_base_dir / "rule_templates"
            if rules_template_path.exists():
                knowledge_base['rule_templates'] = {}
                for file_path in rules_template_path.glob("*.yaml"):
                    with open(file_path, 'r') as f:
                        template_name = file_path.stem
                        knowledge_base['rule_templates'][template_name] = yaml.safe_load(f)
            
        except Exception as e:
            print(f"⚠️ 知识库加载失败: {e}")
        
        return knowledge_base
    
    def add_asset_data(self, source_type: str, data_source: Union[str, Path, Dict]):
        """添加资产数据源"""
        try:
            if source_type == "whatweb":
                self.asset_normalizer.normalize_from_file(Path(data_source))
            elif source_type == "nmap":
                self.asset_normalizer.normalize_from_file(Path(data_source))
            elif source_type == "json":
                if isinstance(data_source, (str, Path)):
                    self.asset_normalizer.normalize_from_file(Path(data_source))
                elif isinstance(data_source, dict):
                    # 直接处理字典数据
                    pass
            else:
                print(f"⚠️ 不支持的数据源类型: {source_type}")
                
        except Exception as e:
            print(f"❌ 资产数据加载失败 ({source_type}): {e}")
    
    def generate_strategy(self, target_name: str) -> TestStrategy:
        """为目标生成测试策略"""
        print(f"🧠 开始为 {target_name} 生成测试策略...")
        
        # 获取所有标准化资产
        assets = self.asset_normalizer.get_assets()
        if not assets:
            raise ValueError("没有可用的资产数据")
        
        print(f"📊 分析 {len(assets)} 个资产...")
        
        # 为每个资产评估规则并收集测试动作
        all_test_actions = []
        
        for asset in assets:
            asset_dict = asset.dict() if hasattr(asset, 'dict') else asset
            
            # 应用规则引擎
            matched_actions = self.rule_engine.evaluate_asset(asset_dict)
            
            for action_data in matched_actions:
                # 将规则动作转换为测试动作
                test_action = self._convert_to_test_action(action_data, asset_dict)
                if test_action:
                    all_test_actions.append(test_action)
        
        print(f"🎯 生成 {len(all_test_actions)} 个测试动作")
        
        # 创建测试策略
        strategy = TestStrategy(
            target_name=target_name,
            target_url=assets[0].url if assets else None
        )
        
        # 按优先级分组测试动作
        for action in all_test_actions:
            if action.priority == TestPriority.CRITICAL:
                strategy.critical_actions.append(action)
            elif action.priority == TestPriority.HIGH:
                strategy.high_priority_actions.append(action)
            elif action.priority == TestPriority.MEDIUM:
                strategy.medium_priority_actions.append(action)
            else:
                strategy.low_priority_actions.append(action)
        
        # 计算汇总信息
        strategy.calculate_totals()
        strategy.generate_execution_plan()
        
        # 保存策略
        self.strategies[target_name] = strategy
        
        return strategy
    
    def _convert_to_test_action(self, action_data: Dict[str, Any], asset: Dict[str, Any]) -> Optional[TestAction]:
        """将规则动作转换为测试动作"""
        try:
            action_type = action_data['action_type']
            params = action_data['params']
            rule_name = action_data['rule_name']
            
            # 根据动作类型创建不同的测试动作
            if action_type == RuleActionType.ADD_TEST.value:
                # 生成唯一ID
                import hashlib
                action_id = hashlib.md5(f"{rule_name}_{asset.get('url', 'unknown')}".encode()).hexdigest()[:8]
                
                # 确定优先级
                priority_str = params.get('priority', 'medium')
                try:
                    priority = TestPriority(priority_str)
                except ValueError:
                    priority = TestPriority.MEDIUM
                
                # 创建基础测试动作
                test_action = TestAction(
                    id=action_id,
                    category=params.get('category', TestCategory.CVE_VALIDATION),
                    name=f"{rule_name} - {asset.get('url', 'unknown')[0:30]}",
                    description=params.get('description', f"基于规则 {rule_name} 生成的测试"),
                    priority=priority,
                    estimated_time_minutes=params.get('estimated_time_minutes', 30),
                    tools=params.get('tools', []),
                    commands=params.get('commands', []),
                    conditions=[],  # 可以从action_data中提取
                    expected_outcomes=params.get('expected_outcomes', []),
                    risk_level=params.get('risk_level', 'medium')
                )
                
                return test_action
            
            elif action_type == RuleActionType.GENERATE_COMMAND.value:
                # 处理命令生成动作
                pass
            
            elif action_type == RuleActionType.SELECT_TOOL.value:
                # 处理工具选择动作
                pass
            
            return None
            
        except Exception as e:
            print(f"⚠️ 动作转换失败: {action_data.get('rule_name', 'unknown')} - {e}")
            return None
    
    def export_strategy(self, target_name: str, output_dir: Path, formats: List[str] = None):
        """导出测试策略到文件"""
        if target_name not in self.strategies:
            raise ValueError(f"找不到策略: {target_name}")
        
        if formats is None:
            formats = ['markdown', 'commands', 'json']
        
        strategy = self.strategies[target_name]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_filename = target_name.replace(' ', '_').replace('/', '_').replace(':', '_')
        
        exported_files = []
        
        # 导出Markdown报告
        if 'markdown' in formats:
            md_path = output_dir / f"{base_filename}_strategy.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(strategy.to_markdown())
            exported_files.append(md_path)
            print(f"📄 Markdown报告已保存到: {md_path}")
        
        # 导出命令列表
        if 'commands' in formats:
            sh_path = output_dir / f"{base_filename}_commands.sh"
            with open(sh_path, 'w') as f:
                f.write(strategy.to_commands_list())
            sh_path.chmod(0o755)  # 添加执行权限
            exported_files.append(sh_path)
            print(f"⚡ 命令列表已保存到: {sh_path}")
        
        # 导出JSON数据
        if 'json' in formats:
            json_path = output_dir / f"{base_filename}_strategy.json"
            with open(json_path, 'w') as f:
                json.dump(strategy.dict(), f, indent=2, default=str)
            exported_files.append(json_path)
            print(f"📊 JSON数据已保存到: {json_path}")
        
        return exported_files

def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试策略生成器")
    parser.add_argument("--target", type=str, required=True, help="目标名称")
    parser.add_argument("--whatweb", type=str, help="WhatWeb JSON文件")
    parser.add_argument("--nmap", type=str, help="Nmap XML文件")
    parser.add_argument("--rules", type=str, default="rules/", help="规则目录")
    parser.add_argument("--output", type=str, default="strategies/", help="输出目录")
    parser.add_argument("--format", type=str, choices=['markdown', 'commands', 'all'], default='all', help="输出格式")
    
    args = parser.parse_args()
    
    # 初始化生成器
    print("🚀 启动智能测试规划引擎...")
    strategist = TestStrategist(rules_dir=Path(args.rules))
    
    # 添加资产数据
    if args.whatweb:
        print(f"📄 添加WhatWeb数据: {args.whatweb}")
        strategist.add_asset_data("whatweb", args.whatweb)
    
    if args.nmap:
        print(f"📄 添加Nmap数据: {args.nmap}")
        strategist.add_asset_data("nmap", args.nmap)
    
    # 生成策略
    try:
        strategy = strategist.generate_strategy(args.target)
        
        # 确定导出格式
        formats = []
        if args.format == 'all':
            formats = ['markdown', 'commands', 'json']
        elif args.format == 'markdown':
            formats = ['markdown']
        elif args.format == 'commands':
            formats = ['commands']
        
        # 导出策略
        exported_files = strategist.export_strategy(
            args.target,
            Path(args.output),
            formats
        )
        
        print(f"\n🎉 策略生成完成！")
        print(f"📊 总计: {strategy.total_actions} 个测试项")
        print(f"⏱️  预计时间: {strategy.total_estimated_time_minutes} 分钟")
        
        for file_path in exported_files:
            print(f"📁 生成文件: {file_path}")
        
    except Exception as e:
        print(f"❌ 策略生成失败: {e}")

if __name__ == "__main__":
    main()