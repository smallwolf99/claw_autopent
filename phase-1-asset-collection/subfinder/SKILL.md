---
name: subfinder
description: >
  This skill should be used when the user wants to enumerate subdomains of a target domain
  using Subfinder — a fast passive subdomain discovery tool. Handles installation checks,
  command construction, result parsing, and output formatting. Use when the user asks to
  "find subdomains", "enumerate subdomains", "run subfinder", "discover subdomains for a domain",
  or any similar request involving passive DNS reconnaissance.
---

# Subfinder 子域名枚举 Skill

## 概述

Subfinder 是由 ProjectDiscovery 开发的高速被动子域名枚举工具，支持 40+ 被动信息源（VirusTotal、Shodan、CertStream、Hunter 等）。本 skill 提供完整的枚举工作流，涵盖工具安装、PATH 自动配置、枚举执行、httpx 存活验证、结果解析与安全提示。

## 工作流程

### 第一步：环境检测

验证 subfinder 是否已安装并可执行：

```bash
subfinder -version
```

- 若命令存在，记录版本后继续。
- 若命令不存在，按照以下"安装流程"引导用户完成安装。

---

### 安装流程（含 PATH 自动配置）

当 subfinder 未安装时，按顺序执行：

**Step 1：创建安装目录**

```bash
# Linux/macOS
mkdir -p ~/bin

# Windows PowerShell
New-Item -ItemType Directory -Path "$env:USERPROFILE\bin" -Force
```

**Step 2：下载二进制**

使用 `scripts/auto_install.py` 自动完成（推荐），或手动下载：

```bash
# 直接下载（国内建议使用镜像）
https://ghfast.top/https://github.com/projectdiscovery/subfinder/releases/download/v2.13.0/subfinder_2.13.0_windows_amd64.zip
```

详细步骤见 `references/install_guide.md`。

**Step 3：永久配置 PATH（关键步骤）**

安装完成后，使用 `scripts/add_to_path.py` 将工具目录永久写入用户 PATH：

```bash
# Windows
python scripts/add_to_path.py "C:\Users\<用户名>\bin"

# Linux/macOS
python scripts/add_to_path.py "~/bin"
```

该脚本自动处理：
- Windows：调用 `setx` 写入注册表（永久生效，无需手动加环境变量）
- Linux/macOS：追加 export 到 `~/.bashrc` 或 `~/.zshrc`
- 自动去重，避免重复添加
- 支持 `--dry-run` 预览模式

**Step 4：验证安装**

```bash
subfinder -version
```

---

### 第二步：理解用户意图

收集以下信息（若用户未提供则主动询问，但一次最多问 2 个）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 目标域名 | **必填** | 例如 `example.com` |
| 输出格式 | `json` | `txt` / `json` |
| 是否存活验证 | 否 | 枚举后调用 httpx 验证 |
| API Key 是否配置 | 未知 | 影响枚举深度 |
| 是否递归枚举 | 否 | 是否枚举子域的子域 |

---

### 第三步：执行枚举

**基础枚举命令：**

```bash
subfinder -d <domain> -silent -oJ -o output.json
```

**选项速查：**

| 场景 | 命令 |
|------|------|
| 基础枚举，输出终端 | `subfinder -d example.com -silent` |
| 保存文本 | `subfinder -d example.com -silent -o output.txt` |
| JSON 含 source 字段 | `subfinder -d example.com -silent -oJ -o output.json` |
| 批量多域名 | `subfinder -dL domains.txt -silent -o output.txt` |
| 提高并发（20） | `subfinder -d example.com -silent -t 20` |
| 递归枚举 | `subfinder -d example.com -silent -recursive` |
| 指定数据源 | `subfinder -d example.com -silent -s censys,shodan,virustotal` |

---

### 第四步：httpx 存活验证（可选）

当用户要求"验证存活"或"检查哪些可访问"时，使用 `scripts/run_httpx.py`：

**推荐一键流程（枚举 → 存活验证 → 报告）：**

```bash
# 方式 A：管道联动
subfinder -d example.com -silent | python scripts/run_httpx.py - \
    --status --title --tech --waf --output httpx_results.jsonl \
    --csv report.csv --md report.md

# 方式 B：文件输入
subfinder -d example.com -silent -o subdomains.txt
python scripts/run_httpx.py subdomains.txt \
    --status --title --tech --output httpx_results.jsonl \
    --csv report.csv --md report.md
```

**run_httpx.py 常用选项：**

| 选项 | 说明 |
|------|------|
| `--status` | 提取 HTTP 状态码 |
| `--title` | 提取页面标题 |
| `--tech` | 检测技术栈（Nginx、Vue、React 等） |
| `--waf` | 检测 WAF 防护 |
| `--probe` | 发送 HTTP 探测（更可靠但更慢） |
| `--match-regex 200\|301\|302` | 仅保留匹配状态码 |
| `--filter-regex 404\|403` | 过滤掉指定状态码 |
| `--threads 100` | 并发数（默认 50） |
| `--csv report.csv` | 导出 CSV |
| `--md report.md` | 导出 Markdown 报告 |

**自动安装 httpx**：若 httpx 未安装，脚本会自动尝试 `go install` → `pip install` → `docker` 三种方式。

---

### 第五步：结果解析与展示

**若未找到子域名：**
- 说明可能原因（无 API Key、目标无公开记录、域名拼写错误）
- 建议配置 API Key（参见 `references/api_keys_setup.md`）

**若找到子域名：**
1. 展示总数统计
2. 按字母顺序列出所有子域名（前 50 条，超出提示可用 `--out` 导出）
3. 若有 JSON 输出，解析并高亮显示信息源分布
4. 若启用了 httpx，附加存活率、技术栈、WAF 检测等摘要

**进一步分析**：使用 `scripts/parse_results.py` 对 subfinder 输出文件进行：
- 去重统计
- 按一级域名分组
- 导出 CSV/Markdown 表格
- 统计各数据源贡献数量

```bash
python scripts/parse_results.py output.json --out report.csv --md report.md
```

---

## 安全与合规提醒

> ⚠️ **重要**：每次执行枚举前，必须向用户展示以下提醒：
>
> "Subfinder 仅执行**被动**信息收集（不直接扫描目标服务器），但仍请确保：
> 1. 你拥有目标域名的合法授权，或目标域名属于你自己
> 2. 在授权渗透测试范围内使用
> 3. 遵守相关法律法规和平台服务条款"

## 参考资料

| 文件 | 说明 |
|------|------|
| `references/install_guide.md` | 安装指南（含国内镜像方案） |
| `references/api_keys_setup.md` | 40+ 数据源 API Key 配置 |
| `references/sources_list.md` | 完整数据源列表 |
| `scripts/add_to_path.py` | 跨平台永久 PATH 配置 |
| `scripts/run_httpx.py` | httpx 存活验证脚本 |
| `scripts/parse_results.py` | subfinder 结果解析脚本 |
