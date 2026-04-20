# Katana 完整命令行选项速查

> 来源：[ProjectDiscovery Katana 官方文档](https://docs.projectdiscovery.io/opensource/katana/usage)

## 输入参数（INPUT）

| 标志 | 说明 | 示例 |
|------|------|------|
| `-u` | 目标 URL | `katana -u https://example.com` |
| `-list` | URL 列表文件（每行一个） | `katana -list urls.txt` |

---

## 爬取策略（STRATEGY）

| 标志 | 说明 | 默认值 |
|------|------|--------|
| `-d`, `-depth` | 最大爬取深度 | 3 |
| `-s`, `-strategy` | 访问策略：`depth-first` / `breadth-first` | depth-first |
| `-ct`, `-crawl-duration` | 最大爬取持续时间 | 无限制 |
| `-iqp`, `-ignore-query-params` | 忽略相同路径的不同查询参数 | false |

---

## 无头浏览器（HEADLESS）

| 标志 | 说明 |
|------|------|
| `-hl`, `-headless` | 启用无头爬取（渲染 JS） |
| `-sc`, `-system-chrome` | 使用本地 Chrome 而非内置 Chromium |
| `-sb`, `-show-browser` | 显示浏览器窗口（调试用） |
| `-nos`, `-no-sandbox` | 以 --no-sandbox 模式启动 Chrome |
| `-scp`, `-system-chrome-path` | 指定 Chrome 路径 |
| `-cdd`, `-chrome-data-dir` | Chrome 数据目录路径 |
| `-cwu`, `-chrome-ws-url` | 使用远程 Chrome WebSocket URL |
| `-noi`, `-no-incognito` | 不用无痕模式启动 |

> 💡 **建议**：普通网站用非无头（默认）即可；SPA（React/Vue/Angular）或需要 JS 渲染的页面用 `-hl`。

---

## JavaScript 解析（JS PARSING）

| 标志 | 说明 |
|------|------|
| `-jc`, `-js-crawl` | 启用 JavaScript 文件中的端点解析/爬取 |
| `-jsl`, `-jsluice` | 启用 jsluice 解析（更深入但内存占用高） |
| `-xhr`, `-xhr-extraction` | 提取 XHR/AJAX 请求 URL 和方法 |

---

## 表单与数据提取（EXTRACTION）

| 标志 | 说明 |
|------|------|
| `-fx`, `-form-extraction` | 提取表单、输入、文本域、选择元素 |
| `-aff`, `-automatic-form-fill` | 启用自动表单填充（实验性） |

---

## 范围控制（SCOPE）

| 标志 | 说明 |
|------|------|
| `-cs`, `-crawl-scope` | 包含的正则范围（逗号分隔） |
| `-cos`, `-crawl-out-scope` | 排除的正则范围 |
| `-fs`, `-field-scope` | 范围字段：`dn`（域名）/ `rdn`（根域名）/ `fqdn`（完整域名）|
| `-ns`, `-no-scope` | 禁用默认主机范围限制 |
| `-do`, `-display-out-scope` | 也显示范围外的端点 |

---

## 过滤选项（FILTER）

| 标志 | 说明 | 示例 |
|------|------|------|
| `-em`, `-extension-match` | 保留指定扩展名 | `-em php,html,js` |
| `-ef`, `-extension-filter` | 排除指定扩展名 | `-ef png,css,jpg` |
| `-mr`, `-match-regex` | 匹配 URL 的正则 | `-mr ".*admin.*"` |
| `-fr`, `-filter-regex` | 过滤 URL 的正则 | `-fr ".*logout.*"` |
| `-mdc`, `-match-condition` | DSL 条件匹配响应 | `-mdc "status_code == 200"` |
| `-fdc`, `-filter-condition` | DSL 条件过滤响应 | `-fdc "len(body) < 1000"` |

**DSL 条件运算符：**
- 比较：`==`, `!=`, `>`, `<`, `>=`, `<=`
- 字符串：`contains()`, `matches()`, `startswith()`, `endswith()`
- 响应字段：`status_code`, `body`, `header`, `content_length`

---

## 速率限制（RATE LIMIT）

| 标志 | 说明 | 默认值 |
|------|------|--------|
| `-c`, `-concurrency` | 并发爬虫数 | 10 |
| `-p`, `-parallelism` | 并行处理的输入数 | 10 |
| `-rl`, `-rate-limit` | 每秒最大请求数 | 150 |
| `-rlm`, `-rate-limit-minute` | 每分钟最大请求数 | - |
| `-rd`, `-delay` | 每个请求间延迟（秒） | 0 |

---

## 网络配置（NETWORK）

| 标志 | 说明 |
|------|------|
| `-timeout` | 请求超时（秒） | 10 |
| `-retry` | 重试次数 | 1 |
| `-proxy` | HTTP/SOCKS5 代理 | - |
| `-H`, `-headers` | 自定义 HTTP 头 |
| `-r`, `-resolvers` | 自定义 DNS 解析器 |
| `-tlsi`, `-tls-impersonate` | TLS JA3 随机化（绕过检测） |

---

## 已知文件发现（KNOWN FILES）

| 标志 | 说明 |
|------|------|
| `-kf`, `-known-files` | 爬取已知文件类型：`all` / `robotstxt` / `sitemapxml` |

---

## 输出选项（OUTPUT）

| 标志 | 说明 |
|------|------|
| `-o`, `-output` | 输出文件路径 |
| `-j`, `-jsonl` | JSON Lines 格式输出（含完整元数据） |
| `-f`, `-field` | 输出字段（见下方字段表） |
| `-silent` | 仅显示输出（静默模式） |
| `-v`, `-verbose` | 详细输出 |
| `-nc`, `-no-color` | 禁用 ANSI 颜色 |
| `-sr`, `-store-response` | 存储完整 HTTP 响应 |
| `-srd`, `-store-response-dir` | 响应存储目录 |
| `-or`, `-omit-raw` | JSONL 中省略原始请求/响应 |
| `-ob`, `-omit-body` | JSONL 中省略响应体 |

### 输出字段参考

| 字段 | 说明 |
|------|------|
| `url` | 完整 URL |
| `path` | URL 路径 |
| `fqdn` | 完全限定域名 |
| `rdn` | 根域名 |
| `rurl` | 根 URL（无路径） |
| `qurl` | 带查询参数的 URL |
| `qpath` | 带查询参数的路径 |
| `file` | 文件名 |
| `ufile` | URL 解码后的文件名 |
| `key` | 表单字段名 |
| `value` | 表单字段值 |
| `kv` | key=value 格式 |
| `dir` | 目录路径 |
| `udir` | URL 解码后的目录 |

---

## 调试与维护

| 标志 | 说明 |
|------|------|
| `-version` | 显示版本 |
| `-up`, `-update` | 更新到最新版本 |
| `-duc`, `-disable-update-check` | 禁用自动更新检查 |
| `-health-check` | 运行诊断检查 |
| `-elog`, `-error-log` | 请求错误日志文件 |
| `-debug` | 调试输出 |

---

## 常用组合命令模板

### 基础爬取
```bash
katana -u https://example.com -silent
```

### JS 端点深度爬取
```bash
katana -u https://example.com -jc -d 5 -silent
```

### 无头 + JS + 完整输出
```bash
katana -u https://example.com -hl -jc -d 10 -j -o results.jsonl
```

### 表单提取
```bash
katana -u https://example.com -fx -silent -j -o forms.jsonl
```

### 参数枚举发现
```bash
katana -u https://example.com -jc -jc -f kv -silent
```
