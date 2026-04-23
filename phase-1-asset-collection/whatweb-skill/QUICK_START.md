# whatweb Skill 快速使用指南

## 安装

确保已安装 whatweb：

```bash
# Kali/Debian/Ubuntu
apt-get install whatweb

# 或使用 Ruby gem
gem install whatweb

# 或设置环境变量
export WHATWEB_PATH=/path/to/whatweb  # Linux/macOS
set WHATWEB_PATH=C:\path\to\whatweb.exe  # Windows
```

## 基本使用

### 1. 命令行使用

```bash
# 单 URL 基础识别
python main.py -u https://example.com

# JSON 格式输出（结构化）
python main.py -u https://example.com --format json

# 高攻击性模式（更准确但更慢）
python main.py -u https://example.com --aggression 3

# 指定插件（只检测 CMS 和 Web 服务器）
python main.py -u https://example.com --plugins "CMS,WebServer"

# 批量扫描（从文件读取 URL 列表）
python main.py -l urls.txt --timeout 600

# 详细输出
python main.py -u https://example.com --verbose

# 彩色输出（仅文本模式）
python main.py -u https://example.com --color

# 自定义参数
python main.py -u https://example.com --opts "--no-errors"
```

### 2. 程序化调用

```python
from main import scan

# 基础扫描
result = scan(
    targets="https://example.com",
    output_format="json",
    aggression=1,
    timeout=300
)

# 批量扫描
result = scan(
    targets=["https://example.com", "https://test.com"],
    output_format="json",
    aggression=2,
    plugins="CMS,WebServer",
    timeout=600
)

# 从文件扫描
result = scan(
    targets="urls.txt",
    output_format="json",
    aggression=1,
    timeout=600
)

# 处理结果
if result.get("status") == "success":
    print(f"扫描 {result['count']} 个目标")
    print(f"发现技术栈：{len(result['technologies'])} 项")
    
    # 列出所有检测到的技术
    for tech in result.get('technologies', []):
        print(f"  - {tech['target']}: {tech['technology']} {tech.get('version', '')}")
```

### 3. 高级功能

#### 攻击性级别控制

```python
# 级别 1：快速、被动检测（推荐）
result = scan(
    targets="https://example.com",
    aggression=1
)

# 级别 3：平衡模式
result = scan(
    targets="https://example.com",
    aggression=3
)

# 级别 5：最激进、最准确（可能触发 WAF）
result = scan(
    targets="https://example.com",
    aggression=5
)
```

#### 插件筛选

```python
# 只检测 CMS
result = scan(
    targets="https://example.com",
    plugins="CMS"
)

# 检测 Web 服务器和编程语言
result = scan(
    targets="https://example.com",
    plugins="WebServer,ProgrammingLanguage"
)

# 检测多个类别
result = scan(
    targets="https://example.com",
    plugins="CMS,WebServer,JavaScriptLibrary,WebFramework"
)
```

#### 性能调优

```python
# 大规模扫描优化
result = scan(
    targets="large_url_list.txt",
    aggression=1,        # 快速模式
    plugins="",          # 使用所有插件
    timeout=600,         # 延长超时
    verbose=False        # 关闭详细输出
)
```

## 输出格式

### JSON 输出（推荐）

```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "target": "https://example.com",
      "plugins": [
        {"name": "NGINX", "version": "1.18.0"},
        {"name": "PHP", "version": "7.4.3"},
        {"name": "WordPress", "version": "5.8.1"}
      ]
    }
  ],
  "technologies": [
    {
      "target": "https://example.com",
      "technology": "NGINX",
      "version": "1.18.0",
      "module": ""
    }
  ],
  "unique_targets": 1
}
```

### 文本输出

```
http://example.com [200 OK] Country:US
NGINX[1.18.0]
PHP[7.4.3]
WordPress[5.8.1]
```

## 完整参数说明

```
python main.py [选项]

目标选择:
  -u, --url URL         单个目标 URL
  -l, --list LIST       目标文件路径（每行一个 URL）
  --targets TARGETS     目标（兼容旧版）

输出格式:
  --format {json,text}  输出格式（默认：json）
  --parse               二次结构化 JSON 输出

扫描选项:
  --opts OPTS           附加参数（可选）
  -a, --aggression 1-5  攻击性级别（默认：1）
  -p, --plugins PLUGINS 指定插件（逗号分隔）
  --timeout TIMEOUT     超时时间（秒，默认：300）
  -v, --verbose         详细输出
  --color               彩色输出（仅文本模式）
```

## 常见使用场景

### 场景 1: 快速资产普查

```bash
# 快速扫描多个目标（攻击性级别 1）
python main.py -l targets.txt --format json --aggression 1 -o quick_scan.json
```

### 场景 2: 深度技术栈分析

```bash
# 详细扫描单个目标（攻击性级别 3）
python main.py -u https://target.com --aggression 3 --verbose --format json
```

### 场景 3: CMS 专项检测

```bash
# 只检测 CMS 相关
python main.py -u https://target.com --plugins "CMS" --format json
```

### 场景 4: 批量扫描

```bash
# 批量扫描并保存结果
python main.py -l urls.txt --timeout 600 --format json -o results.json
```

### 场景 5: 生成报告

```bash
# 扫描并生成结构化报告
python main.py -u https://target.com --format json --parse > report.json
python -c "import json; data=json.load(open('report.json')); print(f'检测到 {len(data[\"technologies\"])} 项技术')"
```

## 与其他工具联动

### 与 httpx 联动

```bash
# httpx 存活检测 → whatweb 指纹识别
python ../httpx-skill/main.py -l targets.txt --format json | \
  jq -r '.results[].url' | \
  xargs -I {} python main.py -u {} --format json
```

### 与 subfinder 联动

```bash
# subfinder 子域名枚举 → whatweb 指纹识别
python ../subfinder/main.py -d example.com --format txt | \
  sed 's/^/https:\/\//' | \
  python main.py -l - --timeout 600
```

## 常见问题

### Q: 未找到 whatweb 可执行文件？

**A:** 安装 whatweb 或设置环境变量：

```bash
# Kali/Debian/Ubuntu
apt-get install whatweb

# 或使用 Ruby gem
gem install whatweb

# 设置环境变量
export WHATWEB_PATH=/path/to/whatweb  # Linux/macOS
set WHATWEB_PATH=C:\path\to\whatweb.exe  # Windows
```

### Q: 扫描结果为空？

**A:** 可能原因：
1. 目标无法访问
2. 目标无 Web 服务
3. 防火墙/WAF 拦截
4. 超时时间过短

建议：
- 增加超时：`--timeout 600`
- 降低攻击性：`--aggression 1`
- 使用详细模式：`--verbose` 查看详细信息

### Q: 如何提高扫描速度？

**A:**
1. 降低攻击性：`--aggression 1`（最快）
2. 指定插件：`--plugins "CMS"`（只检测特定类别）
3. 减少超时：`--timeout 60`
4. 批量扫描时使用文件：`-l urls.txt`

### Q: 如何避免触发 WAF？

**A:**
1. 使用最低攻击性：`--aggression 1`
2. 增加延迟（使用 opts）：`--opts "--wait 2"`
3. 限制插件：`--plugins "WebServer"`（被动检测）
4. 使用代理：`--opts "--proxy http://127.0.0.1:8080"`

## 最佳实践

### 1. 快速侦察

```bash
# 快速获取技术栈信息（只使用被动检测）
python main.py -u target.com --aggression 1 --plugins "WebServer"
```

### 2. 深度分析

```bash
# 全面技术栈分析
python main.py -u target.com --aggression 3 --verbose --format json
```

### 3. 批量处理

```bash
# 批量扫描并保存 JSON 结果
python main.py -l urls.txt --timeout 600 --format json -o results.json
```

### 4. 专项检测

```bash
# CMS 专项检测
python main.py -l cms-targets.txt --plugins "CMS,WebFramework" --aggression 2
```

### 5. 完整流程

```bash
# 子域名枚举 → 存活检测 → 指纹识别 → 生成报告
python ../subfinder/main.py -d target.com --format txt > subs.txt
python ../httpx-skill/main.py -l subs.txt --format json > alive.txt
python main.py -l alive.txt --format json -o fingerprint.json
```

## 参考资料

- `SKILL.md` - 完整功能说明
- `OPTIMIZATION_SUMMARY.md` - 优化总结
- [main.py](file://d:\TRAE\advanced-pentester-v1.2\phase-1-asset-collection\whatweb-skill\main.py) - 核心代码
- [skill.json](file://d:\TRAE\advanced-pentester-v1.2\phase-1-asset-collection\whatweb-skill\skill.json) - Skill 配置
