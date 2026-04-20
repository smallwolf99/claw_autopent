# httpx

## 简介
httpx — 高性能 Web 资产探测工具。适用于大批量 URL/Web资产存活性检测、指纹识别、状态码/标题采集、服务识别等场景。

## 使用场景
- 渗透测试信息收集
- 资产盘点与测绘
- API/Web端点普查

## 支持参数
详见 skill.json/interface schema

## 用法示例
- 单目标探测：
    httpx -u http://example.com -title -status-code
- 批量探测：
    httpx -l urls.txt -title -tech-detect -web-server -status-code

## 安全说明
请遵守测试规范，避免对未知目标批量扫描。

## 作者
安小易（AI渗透测试专家）

# 细节及API用法见 main.py。
