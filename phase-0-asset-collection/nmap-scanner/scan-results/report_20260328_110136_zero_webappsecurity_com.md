# 🛡️ Nmap扫描报告 - OpenClaw格式

## 基本信息
- **目标**: zero.webappsecurity.com
- **扫描时间**: 2026-03-28 11:01:36
- **工具版本**: 1.0.1-fixed
- **扫描结果**: ✅ 成功

## 文件位置
- **JSON结果**: /home/ubuntu/.openclaw/workspace/tasks/2026-03-28__001__zero-webappsecurity-test/assets/nmap-skill-scan.json
- **本报告**: scan-results/report_20260328_110136_zero_webappsecurity_com.md

## 快速摘要
扫描已成功完成，详细信息请查看JSON结果文件。

如需解析JSON结果，可使用:
```bash
jq '.nmaprun.host.ports.port[] | select(.state.state == "open") | "\(.protocol)/\(.portid): \(.service.name)"' /home/ubuntu/.openclaw/workspace/tasks/2026-03-28__001__zero-webappsecurity-test/assets/nmap-skill-scan.json
```

## 使用说明
此报告由OpenClaw集成nmap扫描工具生成，符合OpenClaw规范。

### 后续操作
1. 查看详细结果: `cat /home/ubuntu/.openclaw/workspace/tasks/2026-03-28__001__zero-webappsecurity-test/assets/nmap-skill-scan.json | jq .`
2. 提取开放端口: `jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | "\(.protocol)/\(.portid)"' /home/ubuntu/.openclaw/workspace/tasks/2026-03-28__001__zero-webappsecurity-test/assets/nmap-skill-scan.json`
3. 生成CSV报告: `jq -r '.nmaprun.host.ports.port[] | select(.state.state == "open") | [.protocol, .portid, .service.name, .service.product] | @csv' /home/ubuntu/.openclaw/workspace/tasks/2026-03-28__001__zero-webappsecurity-test/assets/nmap-skill-scan.json`

## 安全说明
- 本扫描仅用于授权安全测试
- 请在合法范围内使用结果
- 遵循最小影响原则

---

**生成者**: OpenClaw Nmap扫描技能包  
**版本**: 1.0.1-fixed  
**集成状态**: ✅ 已修复路径和验证问题
