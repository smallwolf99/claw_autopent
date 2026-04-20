#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase-4 报告生成模块

支持格式:
- HTML: 交互式报告，包含图表和样式
- Markdown: 轻量级文本报告
- PDF: 专业打印格式
- JSON: 原始数据导出

提供专业、美观的安全测试报告。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ReportData:
    """报告数据"""
    target: str
    test_mode: str
    start_time: str
    end_time: str
    duration: str
    assets_count: int
    risk_score: float
    risk_level: str
    vulnerabilities_count: int
    verified_vulns_count: int
    vulnerabilities: List[Dict[str, Any]]
    assets: List[Dict[str, Any]]


class Phase4Reporter:
    """Phase-4 报告生成器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """初始化报告生成器
        
        Args:
            output_dir: 输出目录，默认为当前目录的 reports 子目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / 'reports'
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Phase-4 报告生成器初始化完成，输出目录：{self.output_dir}")
    
    def generate(self, report_data: Dict[str, Any], 
                formats: Optional[List[str]] = None) -> Dict[str, str]:
        """生成报告
        
        Args:
            report_data: 报告数据
            formats: 报告格式列表，默认 ['html', 'markdown', 'json']
            
        Returns:
            生成的报告文件路径
        """
        if formats is None:
            formats = ['html', 'markdown', 'json']
        
        report_files = {}
        
        # 生成时间戳文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"pentest_report_{timestamp}"
        
        # 生成各种格式的报告
        for fmt in formats:
            try:
                if fmt == 'html':
                    path = self._generate_html(report_data, f"{base_name}.html")
                    report_files['html'] = str(path)
                elif fmt == 'markdown':
                    path = self._generate_markdown(report_data, f"{base_name}.md")
                    report_files['markdown'] = str(path)
                elif fmt == 'json':
                    path = self._generate_json(report_data, f"{base_name}.json")
                    report_files['json'] = str(path)
                elif fmt == 'pdf':
                    path = self._generate_pdf(report_data, f"{base_name}.pdf")
                    report_files['pdf'] = str(path)
            except Exception as e:
                logger.error(f"生成{fmt}报告失败：{e}")
        
        logger.info(f"报告生成完成：{len(report_files)} 个文件")
        return report_files
    
    def _generate_html(self, report_data: Dict[str, Any], filename: str) -> Path:
        """生成 HTML 报告"""
        logger.info("生成 HTML 报告...")
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>安全测试报告 - {report_data.get('target', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .card h3 {{ color: #667eea; margin-bottom: 10px; font-size: 0.9em; text-transform: uppercase; }}
        .card .value {{ font-size: 2.5em; font-weight: bold; color: #333; }}
        .risk-score {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }}
        .risk-score .value {{ color: white; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        th {{ background: #667eea; color: white; padding: 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 15px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .severity {{ padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; text-transform: uppercase; }}
        .severity.critical {{ background: #dc3545; color: white; }}
        .severity.high {{ background: #fd7e14; color: white; }}
        .severity.medium {{ background: #ffc107; color: #333; }}
        .severity.low {{ background: #28a745; color: white; }}
        .severity.info {{ background: #17a2b8; color: white; }}
        .verified {{ color: #28a745; font-weight: bold; }}
        .footer {{ text-align: center; padding: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 安全测试报告</h1>
        <p>目标：{report_data.get('target', 'Unknown')}</p>
        <p>测试时间：{report_data.get('start_time', 'N/A')}</p>
    </div>
    
    <div class="summary">
        <div class="card risk-score">
            <h3>风险评分</h3>
            <div class="value">{report_data.get('risk_score', 0)}/100</div>
        </div>
        <div class="card">
            <h3>风险等级</h3>
            <div class="value">{report_data.get('risk_level', 'Unknown')}</div>
        </div>
        <div class="card">
            <h3>发现资产</h3>
            <div class="value">{report_data.get('assets_count', 0)}</div>
        </div>
        <div class="card">
            <h3>发现漏洞</h3>
            <div class="value">{report_data.get('vulnerabilities_count', 0)}</div>
        </div>
        <div class="card">
            <h3>已验证漏洞</h3>
            <div class="value">{report_data.get('verified_vulns_count', 0)}</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📋 漏洞列表</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>严重程度</th>
                    <th>目标</th>
                    <th>验证状态</th>
                    <th>置信度</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 添加漏洞行
        vulnerabilities = report_data.get('vulnerabilities', [])
        for vuln in vulnerabilities[:20]:  # 限制显示 20 个
            severity = vuln.get('severity', 'info')
            verified = '✔ 已验证' if vuln.get('verified') else '✘ 未验证'
            confidence = f"{vuln.get('confidence', 0)*100:.0f}%" if vuln.get('confidence') else 'N/A'
            
            html_content += f"""
                <tr>
                    <td><code>{vuln.get('vuln_id', vuln.get('id', 'N/A'))}</code></td>
                    <td><strong>{vuln.get('name', 'Unknown')}</strong></td>
                    <td><span class="severity {severity}">{severity}</span></td>
                    <td>{vuln.get('target', 'N/A')}</td>
                    <td class="verified">{verified}</td>
                    <td>{confidence}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>报告生成时间：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p>智能测试编排器 - Automated Security Testing Framework</p>
    </div>
</body>
</html>
"""
        
        # 写入文件
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    def _generate_markdown(self, report_data: Dict[str, Any], filename: str) -> Path:
        """生成 Markdown 报告"""
        logger.info("生成 Markdown 报告...")
        
        md_content = f"""# 🔒 安全测试报告

## 基本信息

- **测试目标**: {report_data.get('target', 'Unknown')}
- **测试模式**: {report_data.get('test_mode', 'full')}
- **测试时间**: {report_data.get('start_time', 'N/A')}
- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 风险概览

| 指标 | 数值 |
|------|------|
| **风险评分** | {report_data.get('risk_score', 0)}/100 |
| **风险等级** | {report_data.get('risk_level', 'Unknown')} |
| **发现资产** | {report_data.get('assets_count', 0)} |
| **发现漏洞** | {report_data.get('vulnerabilities_count', 0)} |
| **已验证漏洞** | {report_data.get('verified_vulns_count', 0)} |

## 漏洞列表

"""
        
        # 添加漏洞详情
        vulnerabilities = report_data.get('vulnerabilities', [])
        for i, vuln in enumerate(vulnerabilities[:20], 1):
            severity = vuln.get('severity', 'info').upper()
            verified = '✅ 已验证' if vuln.get('verified') else '❌ 未验证'
            confidence = f"{vuln.get('confidence', 0)*100:.0f}%" if vuln.get('confidence') else 'N/A'
            
            md_content += f"""### {i}. {vuln.get('name', 'Unknown')}

- **漏洞 ID**: {vuln.get('vuln_id', vuln.get('id', 'N/A'))}
- **严重程度**: {severity}
- **目标**: {vuln.get('target', 'N/A')}
- **验证状态**: {verified}
- **置信度**: {confidence}
- **描述**: {vuln.get('description', 'N/A')}

"""
        
        md_content += f"""---

## 附录

### 测试工具

- Phase-0: 资产收集（WhatWeb, Nmap, Httpx, Subfinder）
- Phase-1: 风险画像（智能分析）
- Phase-2: 漏洞检测（Nuclei, Afrog, Nikto）
- Phase-3: 漏洞验证（交叉验证）
- Phase-4: 报告生成（多格式支持）

---

*报告由智能测试编排器自动生成*
"""
        
        # 写入文件
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return file_path
    
    def _generate_json(self, report_data: Dict[str, Any], filename: str) -> Path:
        """生成 JSON 报告"""
        logger.info("生成 JSON 报告...")
        
        # 写入文件
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def _generate_pdf(self, report_data: Dict[str, Any], filename: str) -> Path:
        """生成 PDF 报告（使用 weasyprint）"""
        logger.info("生成 PDF 报告...")
        
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # 生成临时 HTML
            html_content = self._generate_pdf_html(report_data)
            
            # 配置字体
            fonts = FontConfiguration()
            
            # 生成 PDF
            html_doc = HTML(string=html_content)
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                }
                .page-break {
                    page-break-before: always;
                }
                h1, h2, h3 {
                    page-break-after: avoid;
                }
                table {
                    page-break-inside: avoid;
                }
            ''')
            
            pdf_path = self.output_dir / filename
            html_doc.write_pdf(pdf_path, stylesheets=[css], font_config=fonts)
            
            logger.info(f"PDF 报告生成成功：{pdf_path}")
            return pdf_path
            
        except ImportError:
            logger.error("PDF 生成需要安装 weasyprint: pip install weasyprint")
            # 生成一个说明文件替代
            placeholder_path = self.output_dir / filename.replace('.pdf', '_placeholder.txt')
            with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write("PDF 生成需要安装 weasyprint 库\n")
                f.write("安装命令：pip install weasyprint\n")
                f.write(f"\n报告数据已保存到：{self.output_dir / filename.replace('.pdf', '.json')}\n")
            return placeholder_path
            
        except Exception as e:
            logger.error(f"PDF 生成失败：{e}")
            raise
    
    def _generate_pdf_html(self, report_data: Dict[str, Any]) -> str:
        """生成适合 PDF 的 HTML 内容"""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>安全测试报告 - {report_data.get('target', 'Unknown')}</title>
</head>
<body>
    <div class="header">
        <h1>🔒 安全测试报告</h1>
        <p><strong>目标:</strong> {report_data.get('target', 'Unknown')}</p>
        <p><strong>测试时间:</strong> {report_data.get('start_time', 'N/A')}</p>
        <p><strong>报告生成时间:</strong> {report_data.get('end_time', 'N/A')}</p>
        <p><strong>执行时长:</strong> {report_data.get('duration', 'N/A')}</p>
    </div>
    
    <div class="summary">
        <h2>执行摘要</h2>
        <table>
            <tr>
                <td><strong>风险评分</strong></td>
                <td><strong>{report_data.get('risk_score', 0)}/100</strong></td>
            </tr>
            <tr>
                <td><strong>风险等级</strong></td>
                <td><strong>{report_data.get('risk_level', 'Unknown')}</strong></td>
            </tr>
            <tr>
                <td><strong>发现资产</strong></td>
                <td><strong>{report_data.get('assets_count', 0)} 个</strong></td>
            </tr>
            <tr>
                <td><strong>发现漏洞</strong></td>
                <td><strong>{report_data.get('vulnerabilities_count', 0)} 个</strong></td>
            </tr>
            <tr>
                <td><strong>已验证漏洞</strong></td>
                <td><strong>{report_data.get('verified_vulns_count', 0)} 个</strong></td>
            </tr>
        </table>
    </div>
    
    <div class="page-break"></div>
    
    <div class="vulnerabilities">
        <h2>漏洞详情</h2>
        <table>
            <thead>
                <tr>
                    <th>编号</th>
                    <th>漏洞名称</th>
                    <th>严重程度</th>
                    <th>目标</th>
                    <th>验证状态</th>
                    <th>置信度</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 添加漏洞列表
        vulns = report_data.get('vulnerabilities', [])
        for i, vuln in enumerate(vulns, 1):
            severity = vuln.get('severity', 'info').upper()
            verified = '✅ 已验证' if vuln.get('verified') else '❌ 未验证'
            confidence = f"{vuln.get('confidence', 0)*100:.0f}%" if vuln.get('confidence') else 'N/A'
            
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{vuln.get('name', 'Unknown')}</strong><br/>
                        <small>ID: {vuln.get('vuln_id', vuln.get('id', 'N/A'))}</small>
                    </td>
                    <td>{severity}</td>
                    <td>{vuln.get('target', 'N/A')}</td>
                    <td>{verified}</td>
                    <td>{confidence}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
    
    <div class="page-break"></div>
    
    <div class="appendix">
        <h2>附录</h2>
        
        <h3>测试工具</h3>
        <ul>
            <li>Phase-0: 资产收集（WhatWeb, Nmap, Httpx, Subfinder）</li>
            <li>Phase-1: 风险画像（智能分析）</li>
            <li>Phase-2: 漏洞检测（Nuclei, Afrog, Nikto）</li>
            <li>Phase-3: 漏洞验证（交叉验证）</li>
            <li>Phase-4: 报告生成（多格式支持）</li>
        </ul>
        
        <h3>免责声明</h3>
        <p>本报告仅供授权的安全测试使用。未经书面许可，不得将本报告用于任何非法目的。</p>
        
        <p style="text-align: center; margin-top: 50px;">
            <em>报告由智能测试编排器自动生成</em>
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def generate_summary(self, report_data: Dict[str, Any]) -> str:
        """生成摘要信息"""
        return (
            f"✅ 测试完成，发现 {report_data.get('vulnerabilities_count', 0)} 个漏洞"
            f"（已验证 {report_data.get('verified_vulns_count', 0)} 个），"
            f"风险评分 {report_data.get('risk_score', 0)}/100"
        )
