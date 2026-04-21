#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 报告生成测试

测试 PDF 报告生成功能
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from adapters.phase4_reporter import Phase4Reporter


def test_pdf_generation():
    """测试 PDF 报告生成"""
    print("\n" + "="*70)
    print("  PDF 报告生成测试")
    print("="*70 + "\n")
    
    # 准备测试数据
    report_data = {
        'target': 'http://demo-test.example.com',
        'test_mode': 'full',
        'start_time': '2026-04-21T00:28:41.835955',
        'end_time': '2026-04-21T00:28:47.830745',
        'duration': '5.99 秒',
        'assets_count': 6,
        'risk_score': 16.63,
        'risk_level': '🟢 安全',
        'vulnerabilities_count': 10,
        'verified_vulns_count': 10,
        'vulnerabilities': [
            {
                'vuln_id': 'CVE-2021-44228',
                'name': 'Apache Log4j2 远程代码执行漏洞',
                'severity': 'critical',
                'target': 'http://demo-test.example.com:8080',
                'description': 'Apache Log4j2 存在 JNDI 注入漏洞，攻击者可执行任意代码',
                'verified': True,
                'confidence': 0.95,
                'exploit_chain': [
                    '1. 识别目标使用 Log4j2',
                    '2. 发送恶意 JNDI 请求',
                    '3. 触发远程代码执行',
                    '4. 获取系统权限'
                ]
            },
            {
                'vuln_id': 'CVE-2020-5410',
                'name': 'Spring Framework RCE',
                'severity': 'high',
                'target': 'http://demo-test.example.com:80',
                'description': 'Spring Framework 存在 RCE 漏洞',
                'verified': True,
                'confidence': 0.90,
                'exploit_chain': [
                    '1. 识别 Spring 版本',
                    '2. 构造恶意请求',
                    '3. 执行远程代码'
                ]
            },
            {
                'vuln_id': 'NIKTO-001',
                'name': '目录索引启用',
                'severity': 'medium',
                'target': 'http://demo-test.example.com/admin/',
                'description': '服务器启用了目录索引，可能泄露敏感信息',
                'verified': True,
                'confidence': 1.0,
                'exploit_chain': []
            },
            {
                'vuln_id': 'NIKTO-002',
                'name': '敏感文件暴露',
                'severity': 'low',
                'target': 'http://demo-test.example.com/.git/config',
                'description': '.git 配置文件可公开访问',
                'verified': True,
                'confidence': 1.0,
                'exploit_chain': []
            }
        ],
        'assets': [
            {'type': 'web', 'url': 'http://demo-test.example.com'},
            {'type': 'port', 'port': 80, 'service': 'http'},
            {'type': 'port', 'port': 443, 'service': 'https'},
            {'type': 'port', 'port': 8080, 'service': 'http-proxy'}
        ]
    }
    
    # 创建报告生成器
    reporter = Phase4Reporter()
    
    print("📄 生成测试报告（所有格式）...")
    print(f"  • 目标：{report_data['target']}")
    print(f"  • 漏洞数：{report_data['vulnerabilities_count']}")
    print(f"  • 风险评分：{report_data['risk_score']}/100")
    print()
    
    try:
        # 生成所有格式的报告
        report_files = reporter.generate(report_data, ['html', 'markdown', 'json', 'pdf'])
        
        print("✅ 报告生成完成！\n")
        print("📁 生成的文件:")
        for fmt, path in report_files.items():
            file_size = Path(path).stat().st_size if Path(path).exists() else 0
            print(f"  • {fmt.upper():10s}: {path}")
            print(f"             大小：{file_size:,} 字节")
        
        # 验证 PDF 文件
        pdf_path = report_files.get('pdf')
        if pdf_path and Path(pdf_path).exists():
            if pdf_path.endswith('.pdf'):
                print(f"\n✅ PDF 报告生成成功！")
                print(f"   文件：{Path(pdf_path).name}")
                print(f"   大小：{Path(pdf_path).stat().st_size:,} 字节")
            else:
                print(f"\n⚠️  PDF 生成需要安装 weasyprint")
                print(f"   已生成占位文件：{Path(pdf_path).name}")
                print(f"   安装命令：pip install weasyprint")
        else:
            print(f"\n❌ PDF 文件未生成")
        
        print("\n" + "="*70)
        print("  测试完成")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = test_pdf_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
