<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* 封面页样式 */
        .cover-page {
            background: linear-gradient(135deg, #e8eaf6 0%, #e3f2fd 50%, #ede7f6 100%);
            width: 210mm;
            height: 297mm;
            padding: 30mm 20mm;
            margin: 0;
            color: #1a2332;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            page-break-after: always;
            box-sizing: border-box;
        }
        
        .cover-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            z-index: 1;
        }
        
        .cover-title {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            background: linear-gradient(135deg, #1a2332 0%, #233140 50%, #2a3f50 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 2px 2px 4px rgba(26, 35, 50, 0.3), 0 0 20px rgba(26, 35, 50, 0.15);
            letter-spacing: 2px;
        }
        
        .cover-subtitle {
            font-size: 1.4em;
            margin-bottom: 60px;
            text-align: center;
            color: #374785;
            font-weight: 300;
            letter-spacing: 1px;
        }
        
        .cover-info-box {
            background: rgba(255,255,255,0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(26, 35, 50, 0.2);
            border-radius: 12px;
            padding: 30px 35px;
            margin-bottom: 35px;
            box-shadow: 0 2px 8px rgba(26, 35, 50, 0.04);
        }
        
        .cover-info-item {
            display: flex;
            padding: 14px 0;
            border-bottom: 1px solid rgba(26, 35, 50, 0.15);
            font-size: 1.05em;
        }
        
        .cover-info-item:last-child {
            border-bottom: none;
        }
        
        .cover-info-label {
            font-weight: 600;
            width: 130px;
            flex-shrink: 0;
            color: #1a2332;
        }
        
        .cover-info-value {
            flex: 1;
            color: #233140;
            font-weight: 500;
        }
        
        .cover-footer {
            text-align: center;
            margin-top: 50px;
            position: relative;
            z-index: 1;
        }
        
        .cover-footer-warning {
            color: #d32f2f;
            font-weight: 700;
            font-size: 1em;
            letter-spacing: 1.5px;
            margin: 8px 0;
        }
        
        /* 隐藏页眉页脚 */
        .cover-page .page-footer {
            display: none !important;
        }
        
        /* 打印样式 */
        @media print {
            .cover-page {
                width: 210mm;
                margin: 0;
                padding: 30mm 20mm;
                box-shadow: none;
                page-break-after: always;
                position: relative;
                box-sizing: border-box;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color-adjust: exact;
            }
        }
    </style>
</head>
<body>
    <!-- 封面页 -->
    <div class="cover-page">
        <div class="cover-content">
            <h1 class="cover-title">安全渗透测试报告</h1>
            <p class="cover-subtitle">Security Penetration Testing Report</p>
            
            <div class="cover-info-box">
                <div class="cover-info-item">
                    <span class="cover-info-label">目标系统</span>
                    <span class="cover-info-value">{{ report.target_name }}</span>
                </div>
                <div class="cover-info-item">
                    <span class="cover-info-label">目标 URL</span>
                    <span class="cover-info-value">{{ report.target_url }}</span>
                </div>
                <div class="cover-info-item">
                    <span class="cover-info-label">测试时间</span>
                    <span class="cover-info-value">{{ report.test_time }}</span>
                </div>
                <div class="cover-info-item">
                    <span class="cover-info-label">测试人员</span>
                    <span class="cover-info-value">安小易 (安全测试数字员工)</span>
                </div>
                <div class="cover-info-item">
                    <span class="cover-info-label">风险等级</span>
                    <span class="cover-info-value" style="color: #d32f2f; font-weight: bold;">{{ report.risk_level }}</span>
                </div>
            </div>
            
            <div class="cover-footer">
                <p class="cover-footer-warning">机密文件 · 授权访问 · 严禁外传</p>
                <p class="cover-footer-warning">CONFIDENTIAL - AUTHORIZED PERSONNEL ONLY</p>
            </div>
        </div>
    </div>
</body>
</html>

---

# 📋 安全渗透测试报告

## 📋 报告信息
- **目标系统**: {{ report.target_name }}
- **目标 URL**: {{ report.target_url }}
- **IP 地址**: {{ report.target_ip }}
- **端口**: {{ report.target_port }}
- **测试时间**: {{ report.test_time }}
- **测试人员**: 安小易 (安全测试数字员工)
- **授权状态**: 甲方授权
- **报告版本**: 1.0
- **报告日期**: {{ report.report_date }}

## 📊 执行摘要

### ⚠️ 整体安全态势：**{{ report.overall_risk }}**
本次对{{ report.target_name }}进行渗透测试，共发现漏洞{{ report.total_vulnerabilities }}个，其中高危漏洞{{ report.high_count }}个；中危漏洞{{ report.medium_count }}个；低危漏洞{{ report.low_count }}个；信息暴露{{ report.info_count }}个。因此判定其安全风险为**{{ report.risk_level }}**。

### 🔴 关键发现:
1. **全面高危漏洞验证**: 12 个专项测试发现系统级安全漏洞
2. **多重 RCE 漏洞**: 命令注入、文件包含、文件上传均可直接执行系统命令
3. **数据完全暴露**: 数据库、用户凭证、会话信息完全泄露
4. **认证完全失效**: 暴力破解、弱会话 ID、CSRF 等使认证系统形同虚设
5. **设计级安全缺陷**: 多个核心逻辑错误和安全设计失败

### 🎯 风险评估矩阵
| 风险等级 | 数量 | 影响描述 |
|---------|------|----------|
| **🔴 高危** | {{ report.high_count }} | 系统完全控制、数据完全泄露、认证完全绕过 |
| **🟠 中危** | {{ report.medium_count }} | 配置问题、信息泄露、功能缺陷 |
| **🟡 低危** | {{ report.low_count }} | 信息泄露、配置问题、潜在风险 |
| **🔵 信息** | {{ report.info_count }} | 版本信息、技术栈指纹、暴露面信息 |

### 📈 修复紧迫性：**立即**
所有验证的高危漏洞应立即修复，具体修复建议详见"结论与建议"章节。

---

## 📋 测试概述

### 🎯 测试范围
本次安全测试覆盖{{ report.target_name }}的全面安全评估，包括：

1. **初始安全测试**: 资产发现、端口扫描、基线评估
2. **深度渗透测试**: 自动 + 手动结合，发现深层漏洞
3. **专项漏洞测试**: 12 个核心漏洞模块的深入验证

### 🛠️ 测试方法
- **工具自动化扫描**: 端口扫描、子域名枚举、指纹识别、漏洞扫描
- **手动深度挖掘**: 代码分析、逻辑漏洞发现、绕过技术测试
- **PoC 验证**: 每个漏洞的实际利用验证
- **风险驱动测试**: 基于风险等级分配测试资源和深度

---

## 🔴 漏洞发现汇总

### 1. 漏洞名称：**SQL 注入** (已验证)

- **漏洞地址**: `/vulnerabilities/sqli/`
- **风险等级**: 🔴 高危
- **发现时间**: 2026-04-03 11:30
- **PoC 验证**: `$id = $_GET['id'];` 直接拼接到 SQL 查询
- **PoC 验证结果**: ✅ 成功提取数据库信息
- **影响**: 数据库完全暴露，用户凭证泄露
- **修复建议**: 
  - 使用参数化查询（Prepared Statements）
  - 输入验证和过滤
  - 最小权限原则

### 2. 漏洞名称：**命令注入** (已验证)
- **漏洞地址**: `/vulnerabilities/exec/`
- **风险等级**: 🔴 高危 (RCE)
- **发现时间**: 2026-04-03 11:35
- **PoC 验证**: `shell_exec('ping -c 4 '.$target);` 直接拼接
- **PoC 验证结果**: ✅ 成功执行系统命令`ls -la`
- **影响**: 系统完全控制，任意命令执行
- **修复建议**:
  - 避免使用系统命令执行函数
  - 使用 escapeshellarg() 等转义函数
  - 白名单验证输入

---

## 📊 风险等级汇总

### 🔴 高危漏洞 (12 个)
1. **直接 RCE 攻击**:
   - 命令注入：系统命令执行
   - 文件包含：PHP 代码执行
   - 文件上传：Webshell 上传执行

2. **数据完全泄露**:
   - SQL 注入：数据库完全暴露
   - 弱会话 ID：会话完全可预测
   - API 安全：密码哈希暴露
   - 暴力破解：凭证完全暴露

3. **认证完全失效**:
   - CSRF 漏洞：账户完全被盗用
   - 加密模块：加密流程完全失效
   - 弱会话 ID：会话完全可劫持

4. **设计级安全缺陷**:
   - Insecure CAPTCHA：逻辑设计错误
   - SQL 盲注：信息泄露设计缺陷

---

## 📝 结论与建议

### 🎯 总体评估
系统存在严重安全隐患，建议立即进行全面安全加固。

### 📋 修复优先级
1. **紧急**（24 小时内）: 所有高危 RCE 漏洞
2. **高**（1 周内）: 数据泄露相关漏洞
3. **中**（2 周内）: 认证和会话管理问题
4. **低**（1 个月内）: 配置优化和信息泄露

### 📞 技术支持
如有任何疑问，请联系安全测试团队。

---

**报告结束**
