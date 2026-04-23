# katana Skill 快速使用指南

## 安装要求

确保已安装 katana：

```bash
# 使用 Go 安装（推荐）
go install github.com/projectdiscovery/katana/cmd/katana@latest

# 或设置环境变量指定路径
export KATANA_PATH=/path/to/katana
```

## 基础用法

### 1. 单目标爬取

```bash
# 快速爬取（默认深度 3）
python main.py -u https://example.com

# 带 JS 端点解析
python main.py -u https://example.com --js-crawl
```

### 2. 批量爬取

```bash
# 从文件读取目标
python main.py -l urls.txt --depth 3

# 自定义参数
python main.py -l urls.txt --js-crawl --form-extraction
```

### 3. 无头模式（适用于 SPA/React/Angular）

```bash
# 无头爬取
python main.py -u https://example.com --headless

# 无头 + JS 解析 + 深度 5
python main.py -u https://example.com --headless --js-crawl --depth 5
```

### 4. 表单提取

```bash
python main.py -u https://example.com --form-extraction
```

### 5. 高并发模式

```bash
# 50 并发，100 请求/秒
python main.py -l urls.txt --concurrency 50 --rate-limit 100
```

## 完整参数说明

| 参数 | 简写 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `--url` | `-u` | 单个目标 URL | - | `-u http://example.com` |
| `--list` | `-l` | 目标文件路径 | - | `-l urls.txt` |
| `--depth` | `-d` | 爬取深度（1-10） | `3` | `--depth 5` |
| `--headless` | `-hl` | 无头模式 | `false` | `--headless` |
| `--js-crawl` | `-jc` | JS 端点解析 | `false` | `--js-crawl` |
| `--form-extraction` | `-fx` | 表单提取 | `false` | `--form-extraction` |
| `--xhr-crawl` | - | XHR 请求爬取 | `false` | `--xhr-crawl` |
| `--scope` | - | 范围过滤正则 | - | `--scope ".*example\\.com.*"` |
| `--extensions` | - | 扩展名匹配 | - | `--extensions "php,html,js"` |
| `--filter-status` | - | 状态码过滤 | - | `--filter-status "status_code >= 200"` |
| `--rate-limit` | - | 速率限制（请求/秒） | `50` | `--rate-limit 100` |
| `--delay` | - | 请求延迟（秒） | `0.2` | `--delay 0.5` |
| `--proxy` | - | 代理地址 | - | `--proxy "http://127.0.0.1:7890"` |
| `--format` | - | 输出格式 | `jsonl` | `--format json` |
| `--output` | `-o` | 输出文件路径 | - | `-o results.jsonl` |
| `--concurrency` | `-c` | 并发数 | `10` | `--concurrency 50` |
| `--timeout` | - | 超时时间（秒） | `300` | `--timeout 600` |
| `--parse` | - | 二次结构化输出 | `false` | `--parse` |

## 常用场景

### 场景 1：快速爬取

```bash
python main.py -u https://example.com
```

### 场景 2：JS 端点深度解析（推荐）

```bash
python main.py -u https://example.com --js-crawl --depth 5
```

### 场景 3：无头爬取（SPA 应用）

```bash
python main.py -u https://example.com --headless --js-crawl
```

### 场景 4：全面探测

```bash
python main.py -u https://example.com --headless --js-crawl --depth 10 --form-extraction
```

### 场景 5：表单和输入字段提取

```bash
python main.py -u https://example.com --form-extraction --output forms.jsonl
```

### 场景 6：限定爬取范围

```bash
# 仅爬取同域名
python main.py -u https://example.com --scope ".*example\\.com.*"

# 排除外部链接
python main.py -u https://example.com --exclude-scope ".*google\\.com.*"
```

### 场景 7：按扩展名过滤

```bash
# 保留 php/html/js，排除 css/png
python main.py -u https://example.com --extensions "php,html,js"
```

### 场景 8：限速爬取

```bash
# 每秒 30 请求，延迟 0.5 秒
python main.py -u https://example.com --rate-limit 30 --delay 0.5
```

### 场景 9：使用代理

```bash
python main.py -u https://example.com --proxy "http://127.0.0.1:7890"
```

### 场景 10：生成报告

```bash
# JSON 输出
python main.py -u https://example.com --format json --parse > report.json

# 保存到文件
python main.py -u https://example.com --output results.jsonl
```

## 程序化调用

### Python API

```python
from main import crawl, run_katana, parse_katana_jsonl

# 方式 1：使用标准 crawl 接口
result = crawl(
    targets=["https://a.com", "https://b.com"],
    depth=5,
    headless=False,
    js_crawl=True,
    form_extraction=False,
    output_format="jsonl",
    rate_limit=50,
    delay=0.2,
    timeout=300,
    concurrency=10
)

print(f"发现 {result['count']} 个 URL，{result['unique_urls']} 个唯一 URL")
for item in result['results']:
    print(f"  {item['url']}")

# 方式 2：直接调用 run_katana
output = run_katana(
    targets="https://example.com",
    depth=3,
    headless=True,
    js_crawl=True,
    form_extraction=True,
    output_format="jsonl",
    rate_limit=30,
    delay=0.5
)

# 解析结果
results = parse_katana_jsonl(output)
```

### 目标格式支持

```python
# 单个 URL
crawl(targets="https://example.com")

# URL 列表
crawl(targets=["https://a.com", "https://b.com"])

# 文件路径
crawl(targets="urls.txt")

# 逗号分隔
crawl(targets="https://a.com,https://b.com,https://c.com")
```

## 输出格式

### JSON Lines 输出（默认）

```jsonl
{"url":"https://example.com/page1","path":"/page1","method":"GET"}
{"url":"https://example.com/page2","path":"/page2","method":"POST"}
```

### 结构化输出（--parse）

```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "url": "https://example.com/page1",
      "path": "/page1",
      "method": "GET"
    },
    {
      "url": "https://example.com/page2",
      "path": "/page2",
      "method": "POST"
    }
  ],
  "unique_urls": 2
}
```

### 错误输出

```json
{
  "status": "error",
  "command": "katana -u https://invalid",
  "exit_code": 1,
  "stderr": "...",
  "reason": "katana 执行失败 (退出码：1)"
}
```

## 最佳实践

### 1. 选择合适的爬取模式

```bash
# 传统网站（非 SPA）
python main.py -u https://example.com --depth 3

# 单页应用（React/Angular/Vue）
python main.py -u https://example.com --headless --js-crawl

# 深度探测
python main.py -u https://example.com --headless --js-crawl --depth 10
```

### 2. 控制爬取速率

```bash
# 小批量（<100 URL）
python main.py -l urls.txt --rate-limit 50 --delay 0.2

# 中批量（100-500 URL）
python main.py -l urls.txt --rate-limit 100 --delay 0.1

# 大批量（>500 URL）
python main.py -l urls.txt --rate-limit 200 --delay 0.05
```

### 3. 范围控制

```bash
# 仅爬取主域名
python main.py -u https://example.com --scope ".*example\\.com.*"

# 包含子域名
python main.py -u https://example.com --scope ".*\\.example\\.com.*"

# 排除特定域名
python main.py -u https://example.com --exclude-scope ".*google\\.com.*"
```

### 4. 错误处理

```python
result = crawl(targets="urls.txt")

if result.get("status") == "error":
    print(f"爬取失败：{result.get('reason')}")
    # 重试或记录日志
else:
    print(f"成功爬取 {result.get('count')} 个 URL")
```

## 故障排除

### 问题 1：找不到 katana

```
警告：未找到 katana 可执行文件
请安装：go install github.com/projectdiscovery/katana/cmd/katana@latest
```

**解决：**
```bash
# 安装 katana
go install github.com/projectdiscovery/katana/cmd/katana@latest

# 或设置环境变量
export KATANA_PATH=/root/go/bin/katana
```

### 问题 2：爬取超时

```
status: error, reason: 执行超时 (300 秒)
```

**解决：**
```bash
# 增加超时时间
python main.py -l urls.txt --timeout 600

# 或降低深度
python main.py -l urls.txt --depth 2

# 或降低并发
python main.py -l urls.txt --concurrency 5
```

### 问题 3：被 WAF 拦截

```bash
# 使用代理
python main.py -u https://example.com --proxy "http://127.0.0.1:7890"

# 降低速率
python main.py -u https://example.com --rate-limit 10 --delay 1.0

# 切换到无头模式
python main.py -u https://example.com --headless
```

### 问题 4：爬取结果为空

**可能原因：**
- 目标 URL 不可访问
- 被 robots.txt 限制
- 范围过滤过严

**解决：**
```bash
# 添加详细日志（移除 -silent）
python main.py -u https://example.com 2>&1 | head -20

# 检查范围过滤
python main.py -u https://example.com --scope "" --exclude-scope ""
```

## 后处理

使用 `scripts/parse_results.py` 分析结果：

```bash
# 统计摘要
python scripts/parse_results.py katana_output.jsonl --stats

# 导出 CSV 和 Markdown 报告
python scripts/parse_results.py katana_output.jsonl --out report.csv --md report.md

# 按类型筛选
python scripts/parse_results.py katana_output.jsonl --type js --md js_endpoints.md
```

## 更多信息

- 完整文档：[SKILL.md](SKILL.md)
- 安装指南：[references/install_guide.md](references/install_guide.md)
- 选项速查：[references/options_reference.md](references/options_reference.md)
- 结果解析：[scripts/parse_results.py](scripts/parse_results.py)
