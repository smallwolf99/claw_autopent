# httpx Skill 快速使用指南

## 安装要求

确保已安装 httpx：

```bash
# 使用 Go 安装（推荐）
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# 或设置环境变量指定路径
export HTTPX_PATH=/path/to/httpx
```

## 基础用法

### 1. 单目标探测

```bash
# 快速探测
python main.py -u http://example.com

# 带额外参数
python main.py -u http://example.com --opts "-title -tech-detect"
```

### 2. 批量扫描

```bash
# 从文件读取目标
python main.py -l urls.txt

# 自定义参数
python main.py -l urls.txt --opts "-status-code -title -web-server"
```

### 3. 高并发模式

```bash
# 50 并发，200 请求/秒
python main.py -l urls.txt --concurrency 50 --rate-limit 200
```

### 4. 兼容旧版

```bash
# 使用 --targets 参数（兼容旧版）
python main.py --targets "http://a.com,http://b.com"
```

## 完整参数说明

| 参数 | 简写 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `--url` | `-u` | 单个目标 URL | - | `-u http://example.com` |
| `--list` | `-l` | 目标文件路径 | - | `-l urls.txt` |
| `--targets` | - | 目标（兼容旧版） | - | `--targets "url1,url2"` |
| `--opts` | - | httpx 额外参数 | `-status-code -title -web-server` | `--opts "-title -tech"` |
| `--format` | - | 输出格式 | `json` | `--format text` |
| `--parse` | - | 二次结构化输出 | `false` | `--parse` |
| `--concurrency` | - | 并发数 | `25` | `--concurrency 50` |
| `--rate-limit` | - | 速率限制 | `100` | `--rate-limit 200` |
| `--timeout` | - | 超时时间 | `300` | `--timeout 600` |

## 常用场景

### 场景 1：快速存活检测

```bash
python main.py -l urls.txt --opts "-status-code" --format text
```

### 场景 2：完整信息采集

```bash
python main.py -l urls.txt --opts "-title -tech-detect -web-server -status-code -content-type"
```

### 场景 3：大规模扫描

```bash
python main.py -l large_urls.txt --concurrency 100 --rate-limit 500 --timeout 600
```

### 场景 4：生成报告

```bash
# JSON 输出
python main.py -l urls.txt --format json --parse > report.json

# 文本输出
python main.py -l urls.txt --format text > report.txt
```

## 程序化调用

### Python API

```python
from main import scan, run_httpx, parse_httpx_json

# 方式 1：使用标准 scan 接口
result = scan(
    targets=["http://a.com", "http://b.com"],
    opts="-status-code -title",
    output_format="json",
    concurrency=25,
    rate_limit=100
)

print(f"发现 {result['count']} 个目标")
for item in result['results']:
    print(f"  {item['url']}: {item.get('status_code')}")

# 方式 2：直接调用 run_httpx
output = run_httpx(
    targets="urls.txt",
    opts="-title -tech-detect",
    output_format="json",
    concurrency=50
)

# 解析结果
results = parse_httpx_json(output)
```

### 目标格式支持

```python
# 单个 URL
scan(targets="http://example.com")

# URL 列表
scan(targets=["http://a.com", "http://b.com"])

# 文件路径
scan(targets="urls.txt")

# 逗号分隔
scan(targets="http://a.com,http://b.com,http://c.com")
```

## 输出格式

### JSON 输出（默认）

```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "url": "http://example.com",
      "status_code": 200,
      "title": "Example Domain",
      "webserver": "nginx"
    },
    {
      "url": "http://test.com",
      "status_code": 404,
      "title": "Not Found"
    }
  ]
}
```

### 错误输出

```json
{
  "status": "error",
  "command": "httpx -u http://invalid",
  "exit_code": 1,
  "stderr": "...",
  "reason": "httpx 执行失败 (退出码：1)"
}
```

## 最佳实践

### 1. 控制并发和速率

```bash
# 小批量（<100 目标）
python main.py -l urls.txt --concurrency 25 --rate-limit 100

# 中批量（100-1000 目标）
python main.py -l urls.txt --concurrency 50 --rate-limit 200

# 大批量（>1000 目标）
python main.py -l urls.txt --concurrency 100 --rate-limit 500
```

### 2. 合理设置超时

```bash
# 小批量：60 秒
python main.py -l urls.txt --timeout 60

# 大批量：根据数量动态调整（自动）
python main.py -l 1000_urls.txt --timeout 300  # 会自动调整为 10000 秒
```

### 3. 错误处理

```python
result = scan(targets="urls.txt")

if result.get("status") == "error":
    print(f"扫描失败：{result.get('reason')}")
    # 重试或记录日志
else:
    print(f"成功扫描 {result.get('count')} 个目标")
```

## 故障排除

### 问题 1：找不到 httpx

```
警告：未找到 httpx 可执行文件
请安装：go install github.com/projectdiscovery/httpx/cmd/httpx@latest
```

**解决：**
```bash
# 安装 httpx
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# 或设置环境变量
export HTTPX_PATH=/root/go/bin/httpx
```

### 问题 2：权限错误

```
PermissionError: [Errno 13] Permission denied
```

**解决：**
```bash
# 添加执行权限
chmod +x /path/to/httpx
```

### 问题 3：超时

```
status: error, reason: 执行超时 (300 秒)
```

**解决：**
```bash
# 增加超时时间
python main.py -l urls.txt --timeout 600

# 或降低并发
python main.py -l urls.txt --concurrency 10
```

## 更多信息

- 完整文档：[SKILL.md](SKILL.md)
- 优化总结：[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)
- 测试脚本：[tests/test_httpx_skill.py](tests/test_httpx_skill.py)
