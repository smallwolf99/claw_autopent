#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能测试编排器 - OpenClaw 主入口

本模块是 OpenClaw 智能体调用智能测试框架的统一入口。
用户提供测试目标后，OpenClaw 自动调用此接口执行完整的安全测试流程。

使用方式:
    1. 命令行调用：python main.py '{"target": "http://example.com", "test_mode": "full"}'
    2. stdin 调用：echo '{"target": "http://example.com"}' | python main.py
    3. OpenClaw 智能体自动调用（通过触发词匹配）
"""

import asyncio
import json
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置标准输出编码为 UTF-8（Windows 兼容性）
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入迁移后的核心模块（Task 27 完成）
from core.config import TestMode, ReportFormat
from core.risk_profiler import RiskProfiler
from core.test_strategist import TestStrategist
from core.rule_engine import RuleEngine

# 导入工具适配器（Task 28 完成）
from adapters.phase0_adapter import Phase0Adapter
from adapters.phase2_adapter import Phase2Adapter
from adapters.phase3_validator import Phase3Validator
from adapters.phase4_reporter import Phase4Reporter


class OpenClawHandler:
    """
    OpenClaw 接口处理器
    
    负责:
    - 解析 OpenClaw 调用参数
    - 执行智能测试流程
    - 提供简洁的进度反馈
    - 返回结构化结果
    """
    
    def __init__(self):
        """初始化处理器"""
        # TODO: Task 27 - 从 phase-1 迁移核心代码后，实例化真实的编排器
        # self.orchestrator = SecurityTestOrchestrator()
        self.orchestrator = None
    
    async def execute_intelligent_test(
        self,
        target: str,
        test_mode: str = TestMode.FULL,
        time_limit: int = 120,
        report_format: str = ReportFormat.HTML,
        severity_filter: Optional[List[str]] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        OpenClaw 调用接口 - 执行智能安全测试
        
        简洁进度反馈设计:
        - 每个阶段一行输出
        - 使用 emoji 标识状态
        - 关键数据突出显示
        - 避免过多技术细节
        
        Args:
            target: 测试目标 (URL/IP/域名)
            test_mode: 测试模式 (full/light/custom)
            time_limit: 时间限制（分钟）
            report_format: 报告格式 (html/markdown/pdf/json)
            severity_filter: 漏洞严重程度过滤
            custom_options: 自定义选项
        
        Returns:
            测试结果字典，包含 success、summary、data 字段
        """
        start_time = datetime.now()
        
        try:
            # 构建配置
            config = self._build_config(
                target=target,
                test_mode=test_mode,
                time_limit=time_limit,
                report_format=report_format,
                severity_filter=severity_filter,
                custom_options=custom_options
            )
            
            # 打印开始信息
            print(f"🚀 开始智能安全测试", flush=True)
            print(f"🎯 目标：{target}", flush=True)
            print(f"📊 模式：{test_mode}", flush=True)
            print(f"⏱️  时间限制：{time_limit}分钟", flush=True)
            print(flush=True)
            
            # =========================================
            # 阶段 1: 资产收集
            # =========================================
            print("🎯 阶段 1/5: 资产收集中...", flush=True)
            assets = await self._execute_phase_0(target, config)
            print(f"✅ 发现 {len(assets)} 个资产", flush=True)
            print(flush=True)
            
            # =========================================
            # 阶段 2: 风险画像
            # =========================================
            print("🧠 阶段 2/5: 风险画像生成中...", flush=True)
            risk_report = await self._execute_phase_1(assets, config)
            print(f"⚠️  风险评分：{risk_report.get('overall_score', 0)}/100", flush=True)
            print(flush=True)
            
            # 将风险报告添加到 config 中供后续阶段使用
            config['risk_report'] = risk_report
            config['assets'] = assets
            
            # =========================================
            # 阶段 3: 漏洞检测
            # =========================================
            print("🔍 阶段 3/5: 漏洞检测中...", flush=True)
            vulnerabilities = await self._execute_phase_2(assets, config)
            print(f"🐛 发现 {len(vulnerabilities)} 个漏洞", flush=True)
            print(flush=True)
            
            # =========================================
            # 阶段 4: 漏洞验证
            # =========================================
            print("🔬 阶段 4/5: 漏洞验证中...", flush=True)
            verified_vulns = await self._execute_phase_3(vulnerabilities, config)
            print(f"✔️  已验证 {len(verified_vulns)} 个漏洞", flush=True)
            print(flush=True)
            
            # =========================================
            # 阶段 5: 报告生成
            # =========================================
            print("📄 阶段 5/5: 报告生成中...", flush=True)
            report_path = await self._execute_phase_4(
                assets=assets,
                vulnerabilities=vulnerabilities,
                verified_vulns=verified_vulns,
                risk_report=risk_report,
                config=config
            )
            print(f"📊 报告已生成：{report_path}", flush=True)
            print(flush=True)
            
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 生成摘要
            summary = self._generate_summary(
                assets_count=len(assets),
                vulnerabilities_count=len(vulnerabilities),
                verified_count=len(verified_vulns),
                risk_score=risk_report.get('overall_score', 0),
                execution_time=execution_time
            )
            
            # 构建返回结果
            result = {
                "success": True,
                "summary": summary,
                "data": {
                    "target": target,
                    "assets_found": len(assets),
                    "vulnerabilities_found": len(vulnerabilities),
                    "verified_vulns": len(verified_vulns),
                    "risk_score": risk_report.get('overall_score', 0),
                    "report_path": str(report_path),
                    "report_url": f"file://{report_path}",
                    "execution_time": execution_time,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                },
                "actions": [
                    {
                        "label": "查看完整报告",
                        "type": "open_file",
                        "path": str(report_path)
                    },
                    {
                        "label": "导出 PDF",
                        "type": "export_pdf",
                        "path": str(report_path).replace('.html', '.pdf')
                    }
                ]
            }
            
            return result
            
        except Exception as e:
            # 错误处理
            error_result = {
                "success": False,
                "message": f"测试失败：{str(e)}",
                "data": None,
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ 错误：{str(e)}", flush=True)
            return error_result
    
    def _build_config(
        self,
        target: str,
        test_mode: str,
        time_limit: int,
        report_format: str,
        severity_filter: Optional[List[str]],
        custom_options: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        构建测试配置
        
        Args:
            target: 测试目标
            test_mode: 测试模式
            time_limit: 时间限制
            report_format: 报告格式
            severity_filter: 漏洞过滤
            custom_options: 自定义选项
        
        Returns:
            配置字典
        """
        return {
            "target": target,
            "test_mode": test_mode,
            "time_limit": time_limit,
            "report_format": report_format,
            "severity_filter": severity_filter or ["critical", "high", "medium", "low", "info"],
            "custom_options": custom_options or {},
            "start_time": datetime.now()
        }
    
    async def _execute_phase_0(self, target: str, config: Dict) -> List[Dict]:
        """
        Phase-0: 资产收集
        
        Task 28 完成 - 使用真实的资产收集工具
        - WhatWeb: 技术栈识别
        - Nmap: 端口和服务扫描
        - Httpx: Web 探测
        - Subfinder: 子域名发现
        
        Args:
            target: 测试目标
            config: 测试配置
        
        Returns:
            资产列表
        """
        logger.info("Phase-0: 开始资产收集")
        
        # 使用 Phase-0 适配器
        adapter = Phase0Adapter()
        raw_assets = await adapter.collect(target)
        
        # 标准化资产
        normalized_assets = adapter.normalize_assets(raw_assets)
        
        logger.info(f"Phase-0 完成：发现 {len(normalized_assets)} 个资产")
        return normalized_assets
    
    async def _execute_phase_1(self, assets: List[Dict], config: Dict) -> Dict:
        """
        Phase-1: 风险画像
        
        Task 27 完成 - 使用迁移后的风险画像模块
        
        Args:
            assets: 资产列表
            config: 测试配置
        
        Returns:
            风险画像报告
        """
        logger.info("Phase-1: 开始风险画像评估")
        
        # 使用迁移后的风险画像模块
        profiler = RiskProfiler()
        risk_report = profiler.assess(assets)
        
        logger.info(f"Phase-1 完成：风险评分={risk_report.get('overall_score', 0)}/100")
        return risk_report
    
    async def _execute_phase_2(self, assets: List[Dict], config: Dict) -> List[Dict]:
        """
        Phase-2: 漏洞检测
        
        Task 28 完成 - 使用真实的漏洞扫描工具
        - Nuclei: 模板化漏洞扫描
        - Afrog: PoC 验证扫描
        - Nikto: Web 漏洞扫描
        
        Args:
            assets: 资产列表
            config: 测试配置
        
        Returns:
            漏洞列表
        """
        logger.info("Phase-2: 开始漏洞检测")
        
        # 使用 Phase-2 适配器
        adapter = Phase2Adapter()
        raw_vulns = await adapter.detect(assets, config.get('risk_report', {}))
        
        # 标准化漏洞
        normalized_vulns = adapter.normalize_vulnerabilities(raw_vulns)
        
        logger.info(f"Phase-2 完成：发现 {len(normalized_vulns)} 个漏洞")
        return normalized_vulns
    
    async def _execute_phase_3(self, vulnerabilities: List[Dict], config: Dict) -> List[Dict]:
        """
        Phase-3: 漏洞验证
        
        Task 28 完成 - 使用真实的漏洞验证模块
        - 交叉验证：多工具结果对比
        - 误报过滤：基于规则过滤误报
        - 利用链生成：生成漏洞利用路径
        
        Args:
            vulnerabilities: 漏洞列表
            config: 测试配置
        
        Returns:
            已验证的漏洞列表
        """
        logger.info("Phase-3: 开始漏洞验证")
        
        # 使用 Phase-3 验证器
        validator = Phase3Validator()
        assets = config.get('assets', [])
        verified_results = await validator.verify(vulnerabilities, assets)
        
        # 转换为字典格式
        verified_vulns = validator.to_dict(verified_results)
        
        verified_count = sum(1 for r in verified_results if r.verified)
        logger.info(f"Phase-3 完成：{verified_count}/{len(verified_results)} 个漏洞已验证")
        return verified_vulns
    
    async def _execute_phase_4(
        self,
        assets: List[Dict],
        vulnerabilities: List[Dict],
        verified_vulns: List[Dict],
        risk_report: Dict,
        config: Dict
    ) -> str:
        """
        Phase-4: 报告生成
        
        Task 28 完成 - 使用真实的报告生成模块
        - HTML 报告：交互式报告，包含图表和样式
        - Markdown 报告：轻量级文本报告
        - PDF 报告：专业打印格式
        - JSON 报告：原始数据导出
        
        Args:
            assets: 资产列表
            vulnerabilities: 漏洞列表
            verified_vulns: 已验证漏洞
            risk_report: 风险报告
            config: 测试配置
        
        Returns:
            报告文件路径
        """
        logger.info("Phase-4: 开始生成报告")
        
        # 准备报告数据
        report_data = {
            'target': config['target'],
            'test_mode': config['test_mode'],
            'start_time': config['start_time'].isoformat() if isinstance(config['start_time'], datetime) else str(config['start_time']),
            'end_time': datetime.now().isoformat(),
            'duration': f"{(datetime.now() - config['start_time']).total_seconds():.1f}秒" if isinstance(config['start_time'], datetime) else 'N/A',
            'assets_count': len(assets),
            'risk_score': risk_report.get('overall_score', 0),
            'risk_level': risk_report.get('risk_level', 'Unknown'),
            'vulnerabilities_count': len(vulnerabilities),
            'verified_vulns_count': len(verified_vulns),
            'vulnerabilities': verified_vulns,
            'assets': assets
        }
        
        # 使用 Phase-4 报告生成器
        reporter = Phase4Reporter()
        
        # 确定报告格式
        report_format = config.get('report_format', 'html')
        formats = [report_format] if report_format else ['html', 'markdown', 'json']
        
        # 生成报告
        report_files = reporter.generate(report_data, formats)
        
        # 生成摘要
        summary = reporter.generate_summary(report_data)
        logger.info(f"Phase-4 完成：{summary}")
        
        # 返回第一个报告路径
        report_path = list(report_files.values())[0] if report_files else None
        return report_path
    
    def _generate_summary(
        self,
        assets_count: int,
        vulnerabilities_count: int,
        verified_count: int,
        risk_score: float,
        execution_time: float
    ) -> str:
        """
        生成测试摘要
        
        Args:
            assets_count: 资产数量
            vulnerabilities_count: 漏洞数量
            verified_count: 已验证漏洞数量
            risk_score: 风险评分
            execution_time: 执行时间（秒）
        
        Returns:
            摘要字符串
        """
        minutes = int(execution_time // 60)
        seconds = int(execution_time % 60)
        
        summary = (
            f"✅ 测试完成，"
            f"发现 {vulnerabilities_count} 个漏洞（已验证 {verified_count} 个），"
            f"风险评分 {risk_score}/100，"
            f"耗时 {minutes}分{seconds}秒"
        )
        
        return summary


async def main():
    """
    OpenClaw 主函数
    
    支持两种调用方式:
    1. 命令行参数：python main.py '{"target": "http://example.com"}'
    2. stdin 输入：echo '{"target": "http://example.com"}' | python main.py
    """
    try:
        # 解析输入
        if len(sys.argv) > 1:
            # 命令行参数模式
            input_json = sys.argv[1]
            input_data = json.loads(input_json)
        else:
            # stdin 模式
            input_json = sys.stdin.read()
            input_data = json.loads(input_json)
        
        # 创建处理器
        handler = OpenClawHandler()
        
        # 执行测试
        result = await handler.execute_intelligent_test(
            target=input_data.get("target"),
            test_mode=input_data.get("test_mode", TestMode.FULL),
            time_limit=input_data.get("time_limit", 120),
            report_format=input_data.get("report_format", ReportFormat.HTML),
            severity_filter=input_data.get("severity_filter"),
            custom_options=input_data.get("custom_options")
        )
        
        # 输出结果（JSON 格式，OpenClaw 解析）
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        
    except json.JSONDecodeError as e:
        # JSON 解析错误
        error_result = {
            "success": False,
            "message": f"输入格式错误：{str(e)}",
            "data": None
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False), flush=True)
        sys.exit(1)
        
    except Exception as e:
        # 其他错误
        error_result = {
            "success": False,
            "message": f"执行错误：{str(e)}",
            "data": None
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
