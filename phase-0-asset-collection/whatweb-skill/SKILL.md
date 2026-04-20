# WhatWeb

## 简介
WhatWeb — Web指纹识别与技术栈探测工具。适合批量分析URL/Web资产暴露的服务器、Web组件、CMS、脚本语言、中间件等技术要素。

## 使用场景
- 渗透测试目标指纹识别
- 资产基础技术盘点/映射
- 异常资产变更检测

## 支持参数
详见 skill.json/interface schema

## 用法示例
- 单目标识别：
    whatweb http://example.com
- 批量识别：
    whatweb -i urls.txt

## 安全说明
请遵守目标授权，一些扫描模式可能有较强攻击特征。

## 作者
安小易（AI渗透测试专家）

# 细节接口请见 main.py
