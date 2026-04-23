# httpx

## 简介
httpx — 高性能 Web 资产探测工具。适用于大批量 URL/Web资产存活性检测、指纹识别、状态码/标题采集、服务识别等场景。

## 特性
- **跨平台**：支持 Windows/Linux/macOS
- **智能解析**：自动识别 URL、文件路径、逗号分隔列表
- **高性能**：支持并发控制和速率限制
- **自动管理**：临时文件自动清理

## 使用场景
- 渗透测试信息收集
- 资产盘点与测绘
- API/Web端点普查

## 用法示例

### 单目标探测
```bash
python main.py -u http://example.com
```

### 批量探测
```bash
python main.py -l urls.txt --opts "-title -tech-detect"
```

### 高并发模式
```bash
python main.py -l urls.txt --concurrency 50 --rate-limit 200
```

### 兼容旧版
```bash
python main.py --targets "http://example.com,http://test.com"
```

## 完整参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-u/--url` | 单个目标 URL | - |
| `-l/--list` | 目标文件路径 | - |
| `--targets` | 目标（兼容旧版） | - |
| `--opts` | httpx 额外参数 | -status-code -title -web-server |
| `--format` | 输出格式 (text/json) | json |
| `--parse` | 二次结构化 JSON 输出 | false |
| `--concurrency` | 并发数 | 25 |
| `--rate-limit` | 速率限制 (请求/秒) | 100 |
| `--timeout` | 超时时间 (秒) | 300 |

## 安全说明
请遵守测试规范，避免对未知目标批量扫描。

## 作者
安小易（AI渗透测试专家）

## 细节及 API 用法见 main.py。
