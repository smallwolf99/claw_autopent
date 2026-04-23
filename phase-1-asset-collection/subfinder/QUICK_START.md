# subfinder Skill 快速使用指南

## 安装

确保已安装 subfinder：

```bash
# 使用 Go 安装（推荐）
go install github.com/projectdiscovery/subfinder/cmd/subfinder@latest

# 或设置环境变量
export SUBFINDER_PATH=/path/to/subfinder  # Linux/macOS
set SUBFINDER_PATH=C:\path\to\subfinder.exe  # Windows
```

## 基本使用

### 1. 命令行使用

```bash
# 单域名枚举
python main.py -d example.com

# JSON 格式输出
python main.py -d example.com --format json

# 递归枚举（发现子域的子域）
python main.py -d example.com --recursive

# 指定数据源
python main.py -d example.com --sources "virustotal,shodan,censys"

# 高并发模式
python main.py -d example.com --threads 50

# 批量枚举（从文件读取域名列表）
python main.py -l domains.txt

# 限速枚举（避免触发防护）
python main.py -d example.com --rate-limit 100

# 带超时控制
python main.py -d example.com --timeout 60

# 保存到文件
python main.py -d example.com -o results.json
```

### 2. 程序化调用

```python
from main import enumerate

# 基础枚举
result = enumerate(
    targets="example.com",
    output_format="json",
    recursive=False,
    threads=10,
    timeout=30
)

# 批量枚举
result = enumerate(
    targets=["example.com", "test.com", "demo.org"],
    output_format="json",
    recursive=True,
    sources="virustotal,shodan",
    threads=20
)

# 从文件枚举
result = enumerate(
    targets="domains.txt",
    output_format="json",
    timeout=60
)

# 处理结果
if result.get("status") == "success":
    print(f"发现 {result['count']} 个子域名")
    print(f"唯一域名数：{result['unique_domains']}")
    print(f"使用的数据源：{', '.join(result['sources'])}")
    
    # 列出前 10 个子域名
    for item in result.get("results", [])[:10]:
        print(f"  - {item.get('host')} (来源：{item.get('source')})")
```

### 3. 高级功能

#### 数据源控制

```python
# 指定数据源
result = enumerate(
    targets="example.com",
    sources="virustotal,shodan,censys,threatcrowd"
)

# 排除数据源
result = enumerate(
    targets="example.com",
    sources="",  # 留空表示使用所有
    # 注意：exclude_sources 参数在 run_subfinder 中支持
)
```

#### 性能调优

```python
# 大规模枚举优化
result = enumerate(
    targets="large_domain_list.txt",
    threads=50,           # 高并发
    rate_limit=100,       # 限速保护
    timeout=60,           # 延长超时
    httpx_verify=False    # 暂不验证存活
)
```

## 输出格式

### JSON 输出（推荐）

```json
{
  "status": "success",
  "count": 150,
  "results": [
    {
      "host": "example.com",
      "source": "virustotal",
      "input": "example.com"
    },
    {
      "host": "www.example.com",
      "source": "shodan",
      "input": "example.com"
    }
  ],
  "unique_domains": 145,
  "sources": ["virustotal", "shodan", "censys"]
}
```

### 文本输出

```
www.example.com
mail.example.com
api.example.com
cdn.example.com
```

## 与 httpx 联动

```bash
# 方式 1：管道联动
python main.py -d example.com --format txt | python ../httpx-skill/main.py - \
    --status --title --tech --output httpx_results.jsonl

# 方式 2：文件联动
python main.py -d example.com -o subdomains.txt
python ../httpx-skill/main.py subdomains.txt \
    --status --title --output httpx_results.jsonl
```

## 结果解析

使用内置的解析脚本：

```bash
# 解析 JSON 输出
python scripts/parse_results.py output.json --out report.csv --md report.md

# 去重统计
python scripts/parse_results.py output.json --dedup

# 按一级域名分组
python scripts/parse_results.py output.json --group
```

## 常见问题

### Q: 未找到 subfinder 可执行文件？

**A:** 安装 subfinder 或设置环境变量：

```bash
# 安装
go install github.com/projectdiscovery/subfinder/cmd/subfinder@latest

# 设置环境变量
export SUBFINDER_PATH=/path/to/subfinder  # Linux/macOS
set SUBFINDER_PATH=C:\path\to\subfinder.exe  # Windows
```

### Q: 枚举结果为空？

**A:** 可能原因：
1. 域名无公开子域名记录
2. 需要配置 API Key（参见 `references/api_keys_setup.md`）
3. 数据源被防火墙限制

建议：
- 配置 VirusTotal、Shodan、Censys 等 API Key
- 尝试递归模式：`--recursive`
- 增加数据源：`--sources "virustotal,shodan,certstream"`

### Q: 如何提高枚举速度？

**A:** 
1. 增加并发：`--threads 50`
2. 减少数据源：`--sources "virustotal"`（只用最快的）
3. 关闭递归：不使用 `--recursive`
4. 降低超时：`--timeout 10`

### Q: 如何避免触发防护？

**A:**
1. 限速：`--rate-limit 50`（每秒最多 50 请求）
2. 降低并发：`--threads 5`
3. 使用代理：`--proxy http://127.0.0.1:8080`
4. 延长超时：`--timeout 60`

## 完整参数说明

```
python main.py [选项]

目标选择:
  -d, --domain DOMAIN     单个目标域名
  -l, --list LIST         目标文件路径（每行一个域名）
  --targets TARGETS       目标（兼容旧版）

输出格式:
  --format {json,txt}     输出格式（默认：json）
  -o, --output OUTPUT     输出文件路径

枚举选项:
  --recursive             递归枚举（发现子域的子域）
  --sources SOURCES       指定数据源（逗号分隔）
  --exclude-sources EXCLUDE_SOURCES
                          排除数据源（逗号分隔）

性能选项:
  -t, --threads THREADS   并发线程数（默认：10）
  -rl, --rate-limit RATE_LIMIT
                          速率限制（每秒请求数，0 表示不限）
  --timeout TIMEOUT       枚举超时（秒，默认：30）
  --max-time MAX_TIME     最大执行时间（分钟，0 表示不限）

高级选项:
  --proxy PROXY           代理地址
  --httpx-verify          httpx 存活验证
  --parse                 二次结构化 JSON 输出
```

## 最佳实践

### 1. 快速侦察

```bash
# 快速获取子域名（只使用最快的数据源）
python main.py -d target.com --sources "virustotal" --threads 20
```

### 2. 深度枚举

```bash
# 全面枚举（所有数据源 + 递归）
python main.py -d target.com --recursive --threads 30 --timeout 60
```

### 3. 批量处理

```bash
# 批量枚举多个域名
python main.py -l domains.txt --threads 10 --timeout 300 -o all_results.json
```

### 4. 隐蔽模式

```bash
# 低速枚举（避免触发防护）
python main.py -d target.com --threads 3 --rate-limit 20 --timeout 120
```

### 5. 完整流程

```bash
# 子域名枚举 → httpx 存活验证 → 生成报告
python main.py -d target.com --format txt -o subs.txt
python ../httpx-skill/main.py subs.txt \
    --status --title --tech --waf \
    --output httpx_results.jsonl \
    --csv report.csv --md report.md
```

## 参考资料

- `SKILL.md` - 完整功能说明
- `OPTIMIZATION_SUMMARY.md` - 优化总结
- `references/api_keys_setup.md` - API Key 配置
- `references/install_guide.md` - 安装指南
- `scripts/parse_results.py` - 结果解析脚本
- `scripts/run_httpx.py` - httpx 存活验证脚本
