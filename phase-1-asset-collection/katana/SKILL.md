---
name: katana
description: >
  This skill should be used when the user wants to crawl web pages, enumerate web directories,
  discover endpoints, parse JavaScript files, or extract URLs/forms from a target website using
  Katana — a fast, headless-capable web crawler by ProjectDiscovery. Triggers include
  "crawl website", "web directory enumeration", "discover endpoints", "katana crawl",
  "find hidden pages", "JS endpoint extraction", or any request involving web content discovery.
---

# Katana Web 爬虫枚举 Skill

## 概述

Katana 是 ProjectDiscovery 开发的高速 Web 爬虫，专注于自动化渗透测试管线。核心能力：
- **双重模式**：无头（headless）和非无头爬取
- **JS 解析**：从 JavaScript 文件中提取端点（`jsluice`）
- **表单发现**：提取表单、输入字段、文本域等
- **深度定制**：范围控制、过滤、速率限制、代理
- **多格式输出**：JSON Lines / TXT / CSV / HTML

## 工作流程

### 第一步：环境检测

验证 katana 是否已安装：

```bash
katana -version
```

- 若存在，记录版本后继续。
- 若不存在，调用 `scripts/auto_install.py` 引导安装并配置 PATH。

---

### 安装流程（含 PATH 永久配置）

当 katana 未安装时，执行 `scripts/auto_install.py`（推荐方式）：

```bash
python scripts/auto_install.py
```

该脚本自动完成：
1. 检测平台（Windows/Linux/macOS + 架构）
2. 获取最新版本号
3. 通过国内镜像下载预编译二进制
4. 解压到 `~/bin`
5. 调用 `add_to_path.py` 永久写入用户 PATH
6. 验证安装成功

也支持手动安装（参见 `references/install_guide.md`）。

---

### 第二步：理解用户意图

收集以下参数（若未提供则主动询问，一次最多 2 个）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 目标 URL | **必填** | 爬取入口，如 `https://example.com` |
| 爬取深度 | 3 | 最大递归深度（1-10） |
| 爬取模式 | 非无头 | `headless`（JS 渲染）或普通 |
| JS 端点解析 | 否 | 是否解析 JS 文件中的 API 端点 |
| 表单提取 | 否 | 是否提取表单和输入字段 |
| 输出格式 | `jsonl` | `jsonl` / `txt` / `csv` |
| 是否过滤 | 否 | 按扩展名/正则/状态码过滤 |
| 是否限速 | 否 | 控制并发/延迟 |
| 输出路径 | 终端 | 保存到文件 |

---

### 第三步：构建并执行命令

#### 基础命令模板

```bash
katana -u <url> [options]
```

#### 常用场景命令速查

**场景 1：快速爬取（默认深度 3，非无头）**

```bash
katana -u https://example.com -silent
```

**场景 2：JavaScript 端点解析（推荐，深度爬取）**

```bash
katana -u https://example.com -jc -d 5 -silent
```

**场景 3：无头爬取（渲染 JS，适用于 SPA / Angular / React）**

```bash
katana -u https://example.com -hl -silent
```

**场景 4：JS 解析 + 无头 + 深度 10（全面探测）**

```bash
katana -u https://example.com -hl -jc -d 10 -silent
```

**场景 5：提取表单和输入字段**

```bash
katana -u https://example.com -fx -silent -j -o forms.jsonl
```

**场景 6：提取 XHR/AJAX 请求**

```bash
katana -u https://example.com -hl -xhr -silent -j -o xhr.jsonl
```

**场景 7：限定爬取范围（仅同域名）**

```bash
katana -u https://example.com -cs ".*example\\.com.*" -silent
```

**场景 8：排除外部链接，仅显示范围内结果**

```bash
katana -u https://example.com -cos ".*google\\.com.*" -silent
```

**场景 9：按扩展名过滤（保留 php/html/js，排除 css/png）**

```bash
katana -u https://example.com -em php,html,js -silent
```

**场景 10：按状态码正则过滤**

```bash
katana -u https://example.com -fdc "status_code >= 200 && status_code < 400" -silent
```

**场景 11：限速 + 延迟（每秒 50 请求，间隔 200ms）**

```bash
katana -u https://example.com -rl 50 -rd 0.2 -silent
```

**场景 12：使用代理**

```bash
katana -u https://example.com -proxy http://127.0.0.1:7890 -silent
```

**场景 13：批量爬取（URL 列表）**

```bash
katana -list urls.txt -jc -silent -oJ -o results.jsonl
```

**场景 14：完整报告（JSON + 响应体 + 存储目录）**

```bash
katana -u https://example.com -jc -hl -d 5 \
  -j -srd ./katana_responses \
  -o katana_full.jsonl
```

#### 输出字段控制

使用 `-f` 指定输出字段：

| 字段 | 说明 |
|------|------|
| `url` | 完整 URL（默认） |
| `path` | URL 路径部分 |
| `fqdn` | 完全限定域名 |
| `rdn` | 根域名 |
| `file` | 文件名 |
| `key` / `value` / `kv` | 表单字段 |
| `dir` | 目录路径 |
| `qurl` | 带查询参数的 URL |

---

### 第四步：解析与展示结果

**若未找到任何结果：**
- 检查目标 URL 是否可访问
- 尝试加 `-v` 查看详细日志
- 确认是否被 WAF/403 拦截，可尝试加 `-proxy`
- 建议切换到 headless 模式（`hl`）重试

**若找到结果：**
1. 展示总 URL 数、唯一域名数
2. 按类型分类展示（页面、表单、JS、API）
3. 展示发现的表单数量（若启用了 `-fx`）
4. 说明可进一步使用 `parse_results.py` 进行分析

---

### 第五步：结果后处理（按需）

使用 `scripts/parse_results.py` 分析 katana JSON Lines 输出：

```bash
python scripts/parse_results.py katana_output.jsonl \
    --out report.csv --md report.md --stats
```

`parse_results.py` 支持：
- 按文件类型（html/php/api/js/json 等）分类统计
- 按路径深度分组
- 提取唯一 URL / 参数
- 导出 CSV / Markdown
- 统计各字段（表单、key=value）分布

---

## 安全与合规提醒

> ⚠️ **重要**：爬虫会对目标服务器产生实际 HTTP 请求，必须确保：
> 1. 你拥有目标网站的合法授权，或目标属于你自己
> 2. 在授权渗透测试范围内使用，控制好爬取速率
> 3. 遵守 robots.txt 和网站服务条款
> 4. 不要在生产环境使用 `-rl` 高速率设置

---

## 参考资料

| 文件 | 说明 |
|------|------|
| `references/install_guide.md` | 安装指南（含国内镜像） |
| `references/options_reference.md` | 完整命令行选项速查 |
| `scripts/auto_install.py` | 一键安装脚本（含 PATH 配置） |
| `scripts/add_to_path.py` | 跨平台永久 PATH 配置 |
| `scripts/parse_results.py` | JSON Lines 结果解析报告生成器 |
