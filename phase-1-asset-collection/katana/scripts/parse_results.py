#!/usr/bin/env python3
"""
parse_results.py - Katana JSON Lines 结果解析与统计报告生成器

功能：
  - 解析 katana -j 输出的 JSON Lines 文件
  - 按文件类型、路径深度、域名分组统计
  - 提取唯一 URL、参数、API 端点
  - 生成 CSV / Markdown 报告

用法：
  python parse_results.py <输入文件> [选项]

选项：
  --stats                仅显示统计摘要
  --out     <文件路径>   导出 CSV
  --md      <文件路径>   导出 Markdown 报告
  --type     <ext>       仅统计指定文件类型（如 html,php,js,json,api）
  --depth    <n>         最大路径深度

示例：
  python parse_results.py katana.jsonl --stats
  python parse_results.py katana.jsonl --out report.csv --md report.md
  python parse_results.py katana.jsonl --type js --md js_endpoints.md
"""

import sys
import json
import csv
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse, parse_qs


def fix_encoding():
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_jsonl(filepath: Path) -> list[dict]:
    """解析 katana JSON Lines 输出，兼容多种格式：
    1. 普通文本（每行一个 URL）
    2. katana -j 完整 JSON：{"timestamp":"...", "request":{"endpoint":"..."}, "response":{...}}
    3. katana -oJ 简化 JSON：{"url":"...", "source":"...", ...}
    """
    records = []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 纯 URL 行（非 JSON）
            if not line.startswith("{"):
                if line.startswith("http"):
                    records.append({"url": line, "type": "page"})
                continue
            try:
                obj = json.loads(line)
                # 格式1: katana -j 完整格式（含 request/response）
                if "request" in obj:
                    endpoint = obj["request"].get("endpoint", "")
                    method = obj["request"].get("method", "GET")
                    status = obj.get("response", {}).get("status_code", 0)
                    content_type = obj.get("response", {}).get("headers", {}).get("Content-Type", "")
                    if endpoint:
                        records.append({
                            "url": endpoint,
                            "method": method,
                            "status_code": status,
                            "content_type": content_type,
                        })
                # 格式2: 简化格式（含 url 或 endpoint）
                elif "url" in obj:
                    records.append(obj)
                elif "endpoint" in obj:
                    obj["url"] = obj.pop("endpoint")
                    records.append(obj)
            except json.JSONDecodeError:
                pass
    return records


def extract_extension(url: str) -> str:
    """从 URL 中提取文件扩展名"""
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        ext = path.rsplit('.', 1)[-1].lower()
        if len(ext) <= 10 and ext.isalnum():
            return ext
    return ""


def extract_depth(url: str) -> int:
    """计算 URL 路径深度"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        return 0
    return path.count('/') + 1


def extract_params(url: str) -> dict:
    """提取 URL 查询参数"""
    parsed = urlparse(url)
    if parsed.query:
        return parse_qs(parsed.query)
    return {}


def is_api_endpoint(url: str) -> bool:
    """判断是否为 API 端点"""
    path = urlparse(url).path.lower()
    api_indicators = ['/api/', '/rest/', '/graphql', '/v1/', '/v2/', '/v3/',
                      '/endpoint', '/data', '/json', '/rpc', '/soap']
    return any(ind in path for ind in api_indicators) or urlparse(url).query.startswith('api=')


def classify_type(url: str, content_type: str = "") -> str:
    """分类 URL 类型"""
    ext = extract_extension(url)
    ct = content_type.lower() if content_type else ""

    if 'json' in ext or 'json' in ct or 'javascript' not in ext and ('api' in url.lower() or is_api_endpoint(url)):
        if ext in ('json', 'xml'):
            return "api"
    if 'javascript' in ct or ext == 'js':
        return "js"
    if 'stylesheet' in ct or ext in ('css', 'scss', 'sass', 'less'):
        return "css"
    if 'image' in ct or ext in ('png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp', 'bmp'):
        return "image"
    if 'font' in ct or ext in ('woff', 'woff2', 'ttf', 'otf', 'eot'):
        return "font"
    if ext in ('html', 'htm', 'xhtml'):
        return "page"
    if ext in ('php', 'asp', 'aspx', 'jsp', 'do', 'action', 'cgi'):
        return "dynamic"
    if ext in ('txt', 'md', 'rst', 'log'):
        return "doc"
    if ext in ('pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'):
        return "document"
    if is_api_endpoint(url):
        return "api"
    return "other"


def group_stats(records: list[dict]) -> dict:
    """生成统计摘要"""
    total = len(records)

    # 基本信息
    urls = [r.get("url", "") for r in records if r.get("url")]
    unique_urls = set(urls)

    # 按扩展名分类
    ext_counter = Counter()
    type_counter = Counter()
    depth_counter = Counter()
    domain_counter = Counter()
    status_counter = Counter()
    form_counter = 0
    xhr_counter = 0
    param_keys = Counter()
    api_endpoints = []

    for r in records:
        url = r.get("url", "")
        status = r.get("status_code", 0)
        content_type = r.get("content_type", "")

        ext = extract_extension(url)
        if ext:
            ext_counter[ext] += 1

        rtype = classify_type(url, content_type)
        type_counter[rtype] += 1

        depth = extract_depth(url)
        depth_counter[depth] += 1

        if url:
            domain = urlparse(url).netloc
            if domain:
                domain_counter[domain] += 1

        if status:
            status_counter[status] += 1

        # 表单统计
        if r.get("form"):
            form_counter += 1

        # XHR 请求
        if r.get("type") == "xhr" or r.get("xhr_request"):
            xhr_counter += 1

        # 参数提取
        params = extract_params(url)
        for key in params:
            param_keys[key] += 1

        # API 端点
        if is_api_endpoint(url) and url not in api_endpoints:
            api_endpoints.append(url)

    return {
        "total": total,
        "unique_urls": len(unique_urls),
        "ext_counter": ext_counter,
        "type_counter": type_counter,
        "depth_counter": depth_counter,
        "domain_counter": domain_counter,
        "status_counter": status_counter,
        "form_counter": form_counter,
        "xhr_counter": xhr_counter,
        "param_keys": param_keys,
        "api_endpoints": api_endpoints,
        "urls": sorted(unique_urls),
    }


def print_stats(stats: dict) -> None:
    """终端打印统计摘要"""
    print(f"\n{'='*55}")
    print(f"[RESULTS] Katana Crawl Summary")
    print(f"{'='*55}")
    print(f"Total records:          {stats['total']}")
    print(f"Unique URLs:             {stats['unique_urls']}")

    # 类型分布
    print(f"\n[TYPE] Distribution:")
    for rtype, count in stats["type_counter"].most_common():
        bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
        print(f"  {rtype:<12} {count:>5}  {bar}")

    # 状态码
    if stats["status_counter"]:
        print(f"\n[STATUS] Top Status Codes:")
        for code, count in sorted(stats["status_counter"].items(), key=lambda x: -x[1])[:8]:
            bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
            print(f"  {str(code):<8} {count:>5}  {bar}")

    # 扩展名
    if stats["ext_counter"]:
        print(f"\n[EXT] Top File Extensions:")
        for ext, count in stats["ext_counter"].most_common(10):
            bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
            print(f"  {ext:<12} {count:>5}  {bar}")

    # 深度分布
    if stats["depth_counter"]:
        print(f"\n[DEPTH] Path Depth Distribution:")
        for depth, count in sorted(stats["depth_counter"].items())[:10]:
            bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
            print(f"  depth {depth:<4} {count:>5}  {bar}")

    # 表单 / XHR
    extra = []
    if stats["form_counter"]:
        extra.append(f"forms={stats['form_counter']}")
    if stats["xhr_counter"]:
        extra.append(f"xhr={stats['xhr_counter']}")
    if extra:
        print(f"\n[EXTRA] {' | '.join(extra)}")

    # API 端点
    if stats["api_endpoints"]:
        print(f"\n[API] Discovered {len(stats['api_endpoints'])} API endpoints:")
        for ep in stats["api_endpoints"][:20]:
            print(f"  {ep}")
        if len(stats["api_endpoints"]) > 20:
            print(f"  ... {len(stats['api_endpoints']) - 20} more")

    # Top 参数
    if stats["param_keys"]:
        print(f"\n[PARAMS] Top URL Parameters:")
        for key, count in stats["param_keys"].most_common(15):
            print(f"  {key}: {count}")

    # 域名 Top
    if stats["domain_counter"]:
        print(f"\n[DOMAIN] Top Domains:")
        for dom, count in stats["domain_counter"].most_common(8):
            print(f"  {dom}: {count}")

    # URL 列表（前 30）
    print(f"\n[URLS] Sample URLs (first 30):")
    for url in stats["urls"][:30]:
        print(f"  {url}")
    if len(stats["urls"]) > 30:
        print(f"  ... {len(stats['urls']) - 30} more")


def export_csv(stats: dict, out_path: Path) -> None:
    """导出 CSV（唯一 URL 列表）"""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])
        for url in stats["urls"]:
            writer.writerow([url])
    print(f"[OK] CSV saved: {out_path} ({len(stats['urls'])} rows)")


def export_markdown(stats: dict, out_path: Path) -> None:
    """导出 Markdown 报告"""
    lines = []
    lines.append("# Katana 爬取结果报告\n")

    # 基本统计
    lines.append(f"| 指标 | 数值 |\n|------|------|")
    lines.append(f"| 总记录数 | {stats['total']} |")
    lines.append(f"| 唯一 URL 数 | {stats['unique_urls']} |")
    if stats["form_counter"]:
        lines.append(f"| 表单数量 | {stats['form_counter']} |")
    if stats["xhr_counter"]:
        lines.append(f"| XHR 请求数 | {stats['xhr_counter']} |")
    lines.append(f"| API 端点数 | {len(stats['api_endpoints'])} |")

    # 类型分布
    if stats["type_counter"]:
        lines.append("\n## 类型分布\n")
        lines.append("| 类型 | 数量 | 占比 |")
        lines.append("|------|------|------|")
        for rtype, count in stats["type_counter"].most_common():
            pct = 100 * count / max(stats["total"], 1)
            lines.append(f"| {rtype} | {count} | {pct:.1f}% |")

    # 状态码
    if stats["status_counter"]:
        lines.append("\n## 状态码分布\n")
        lines.append("| 状态码 | 数量 |")
        lines.append("|--------|------|")
        for code, count in sorted(stats["status_counter"].items(), key=lambda x: -x[1]):
            lines.append(f"| {code} | {count} |")

    # 扩展名
    if stats["ext_counter"]:
        lines.append("\n## 文件扩展名 Top 20\n")
        lines.append("| 扩展名 | 数量 |")
        lines.append("|--------|------|")
        for ext, count in stats["ext_counter"].most_common(20):
            lines.append(f"| .{ext} | {count} |")

    # API 端点
    if stats["api_endpoints"]:
        lines.append("\n## API 端点列表\n")
        lines.append("| URL |")
        lines.append("|-----|")
        for ep in stats["api_endpoints"]:
            lines.append(f"| {ep} |")

    # 参数
    if stats["param_keys"]:
        lines.append("\n## URL 参数 Top 20\n")
        lines.append("| 参数名 | 出现次数 |")
        lines.append("|--------|----------|")
        for key, count in stats["param_keys"].most_common(20):
            lines.append(f"| {key} | {count} |")

    # 完整 URL 列表
    lines.append("\n## 完整 URL 列表\n")
    lines.append("| URL |")
    lines.append("|-----|")
    for url in stats["urls"]:
        lines.append(f"| {url} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Markdown saved: {out_path}")


def main():
    fix_encoding()

    parser = argparse.ArgumentParser(description="Katana JSON Lines result parser and report generator")
    parser.add_argument("input", help="Input JSON Lines file from katana -j")
    parser.add_argument("--stats", action="store_true", help="Show stats summary only")
    parser.add_argument("--out", help="Export CSV file path")
    parser.add_argument("--md", help="Export Markdown report file")
    parser.add_argument("--type", help="Filter by file extension (e.g., js, html, php)")
    parser.add_argument("--depth", type=int, help="Filter by max path depth")

    args = parser.parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Reading: {input_path}")
    records = parse_jsonl(input_path)
    print(f"[INFO] Total records: {len(records)}")

    # 应用过滤器
    if args.type:
        ext_filter = args.type.lower().lstrip('.')
        records = [r for r in records if extract_extension(r.get("url", "")) == ext_filter]
        print(f"[INFO] After filter (.{ext_filter}): {len(records)}")

    if args.depth is not None:
        records = [r for r in records if extract_depth(r.get("url", "")) <= args.depth]
        print(f"[INFO] After depth <= {args.depth}: {len(records)}")

    if not records:
        print("[WARN] No records after filtering")
        sys.exit(0)

    stats = group_stats(records)
    print_stats(stats)

    if args.out:
        export_csv(stats, Path(args.out))

    if args.md:
        export_markdown(stats, Path(args.md))

    print(f"\n[INFO] Done. {stats['unique_urls']} unique URLs from {stats['total']} records.")


if __name__ == "__main__":
    main()
