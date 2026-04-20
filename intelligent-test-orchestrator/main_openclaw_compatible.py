#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能测试编排器 - OpenClaw 主入口（兼容版本）

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

# 设置日志 - 同时输出到 stdout 和日志文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('intelligent_test.log', encoding='utf-8')
    ]
)
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
            
            # 打印开始信息（同时使用 print 和 logger）
            msg = f"🚀 开始智能安全测试\n🎯 目标：{target}\n📊 模式：{test_mode}\n⏱️  时间限制：{time_limit}分钟"
            print(msg, flush=True)
            logger.info(msg)
            
            # =========================================
            # 阶段 1: 资产收集
            # =========================================
            msg = "🎯 阶段 1/5: 资产收集中..."
            print(msg, flush=True)
            logger.info(msg)
            
            assets = await self._execute_phase_0(target, config)
            
            msg = f"✅ 发现 {len(assets)} 个资产"
            print(msg, flush=True)
            logger.info(msg)
            
            # =========================================
            # 阶段 2: 风险画像
            # =========================================
            msg = "🧠 阶段 2/5: 风险画像生成中..."
            print(msg, flush=True)
            logger.info(msg)
            
            risk_report = await self._execute_phase_1(assets, config)
            
            msg = f"⚠️  风险评分：{risk_report.get('overall_score', 0)}/100"
            print(msg, flush=True)
            logger.info(msg)
            
            # 将风险报告添加到 config 中供后续阶段使用
            config['risk_report'] = risk_report
            config['assets'] = assets
            
            # =========================================
            # 阶段 3: 漏洞检测
            # =========================================
            msg = "🔍 阶段 3/5: 漏洞检测中..."
            print(msg, flush=True)
            logger.info(msg)
            
            vulnerabilities = await self._execute_phase_2(assets, config)
            
            msg = f"🐛 发现 {len(vulnerabilities)} 个漏洞"
            print(msg, flush=True)
            logger.info(msg)
            
            # =========================================
            # 阶段 4: 漏洞验证
            # =========================================
            msg = "🔬 阶段 4/5: 漏洞验证中..."
            print(msg, flush=True)
            logger.info(msg)
            
            verified_vulns = await self._execute_phase_3(vulnerabilities, config)
            
            msg = f"✔️  已验证 {len(verified_vulns)} 个漏洞"
            print(msg, flush=True)
            logger.info(msg)
            
            # =========================================
            # 阶段 5: 报告生成
            # =========================================
            msg = "📄 阶段 5/5: 报告生成中..."
            print(msg, flush=True)
            logger.info(msg)
            
            report_path = await self._execute_phase_4(
                assets=assets,
                vulnerabilities=vulnerabilities,
                verified_vulns=verified_vulns,
                risk_report=risk_report,
                config=config
            )
            
            msg = f"📊 报告已生成：{report_path}"
            print(msg, flush=True)
            logger.info(msg)
            
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
                "message": summary,  # 添加 message 字段，OpenClaw 可能使用这个
                "text": summary,     # 添加 text 字段，某些版本使用这个
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
                    "end_time": end_time.isoformat(),
                    "summary": summary
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
            
            # 打印最终结果（JSON 格式）
            print("\n" + "="*60, flush=True)
            print("测试结果:", flush=True)
            print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
            print("="*60, flush=True)
            
            logger.info(f"测试完成：{summary}")
            
            return result
            
        except Exception as e:
            # 错误处理
            error_msg = f"❌ 错误：{str(e)}"
            print(error_msg, flush=True)
            logger.error(error_msg, exc_info=True)
            
            error_result = {
                "success": False,
                "message": f"测试失败：{str(e)}",
                "text": f"测试失败：{str(e)}",
                "data": None,
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
                "error_traceback": logging traceback.format_exc()
            }
            
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
            "custom_options": custom_options or {}
        }
    
    async def _execute_phase_0(self, target: str, config: Dict[str, Any]) -> List[Dict]:
        """执行 Phase-0: 资产收集"""
        adapter = Phase0Adapter()
        return await adapter.collect(target)
    
    async def _execute_phase_1(self, assets: List[Dict], config: Dict[str, Any]) -> Dict:
        """执行 Phase-1: 风险画像"""
        profiler = RiskProfiler()
        return profiler.profile(assets)
    
    async def _execute_phase_2(self, assets: List[Dict], config: Dict[str, Any]) -> List[Dict]:
        """执行 Phase-2: 漏洞检测"""
        adapter = Phase2Adapter()
        return await adapter.scan(assets, config)
    
    async def _execute_phase_3(self, vulnerabilities: List[Dict], config: Dict[str, Any]) -> List[Dict]:
        """执行 Phase-3: 漏洞验证"""
        validator = Phase3Validator()
        return await validator.verify(vulnerabilities, config)
    
    async def _execute_phase_4(
        self,
        assets: List[Dict],
        vulnerabilities: List[Dict],
        verified_vulns: List[Dict],
        risk_report: Dict,
        config: Dict[str, Any]
    ) -> Path:
        """执行 Phase-4: 报告生成"""
        reporter = Phase4Reporter()
        
        # 构建报告数据
        report_data = {
            "target": config["target"],
            "test_mode": config["test_mode"],
            "start_time": config.get("start_time", datetime.now().isoformat()),
            "end_time": datetime.now().isoformat(),
            "duration": f"{(datetime.now() - datetime.fromisoformat(config.get('start_time', datetime.now().isoformat()))).total_seconds():.2f} 秒",
            "assets_count": len(assets),
            "risk_score": risk_report.get('overall_score', 0),
            "risk_level": self._get_risk_level(risk_report.get('overall_score', 0)),
            "vulnerabilities_count": len(vulnerabilities),
            "verified_vulns_count": len(verified_vulns),
            "vulnerabilities": verified_vulns,
            "assets": assets
        }
        
        # 生成报告
        report_format = config.get("report_format", ReportFormat.HTML)
        report_files = reporter.generate(report_data, [report_format])
        
        return list(report_files.values())[0] if report_files else Path("report.html")
    
    def _get_risk_level(self, score: float) -> str:
        """根据风险评分获取风险等级"""
        if score >= 80:
            return "🔴 极高风险"
        elif score >= 60:
            return "🟠 高风险"
        elif score >= 40:
            return "🟡 中等风险"
        elif score >= 20:
            return "🔵 低风险"
        else:
            return "🟢 安全"
    
    def _generate_summary(
        self,
        assets_count: int,
        vulnerabilities_count: int,
        verified_count: int,
        risk_score: float,
        execution_time: float
    ) -> str:
        """生成摘要信息"""
        return (
            f"✅ 测试完成，发现 {vulnerabilities_count} 个漏洞"
            f"（已验证 {verified_count} 个），"
            f"风险评分 {risk_score}/100，"
            f"耗时 {execution_time:.2f} 秒"
        )


# 主函数入口
async def main_async():
    """异步主函数"""
    handler = OpenClawHandler()
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 从命令行参数获取 JSON
        try:
            input_data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            # 尝试从文件读取
            input_file = sys.argv[1]
            if Path(input_file).exists():
                with open(input_file, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
            else:
                print(f"❌ 无效的 JSON 或文件：{input_file}")
                sys.exit(1)
    else:
        # 从 stdin 读取
        print("请输入 JSON 配置或按 Ctrl+D 结束:")
        try:
            input_text = sys.stdin.read()
            input_data = json.loads(input_text)
        except json.JSONDecodeError:
            print("❌ 无效的 JSON 输入")
            sys.exit(1)
    
    # 执行测试
    result = await handler.execute_intelligent_test(
        target=input_data.get("target", "http://example.com"),
        test_mode=input_data.get("test_mode", TestMode.FULL),
        time_limit=input_data.get("time_limit", 120),
        report_format=input_data.get("report_format", ReportFormat.HTML),
        severity_filter=input_data.get("severity_filter"),
        custom_options=input_data.get("custom_options")
    )
    
    # 输出结果
    print("\n最终结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 返回结果（用于 OpenClaw 调用）
    return result


def main():
    """同步主函数"""
    return asyncio.run(main_async())


if __name__ == "__main__":
    main()
