#!/usr/bin/env python3
"""
parse_results.py - Subfinder 结果解析与统计工具

用法：
  python parse_results.py <输入文件> [选项]

选项：
  --format  txt|json     输入文件格式（默认自动检测）
  --out     <文件路径>   输出 CSV 文件路径（可选）
  --md      <文件路径>   输出 Markdown 表格路径（可选）
  --stats                仅显示统计信息

示例：
  python parse_results.py output.txt --stats
  python parse_results.py output.json --out result.csv --md result.md
"""

import sys
import json
import argparse
import csv
from pathlib import Path
from collections import defaultdict, Counter


def parse_txt(filepath: Path) -> list[dict]:
    """解析纯文本格式（每行一个子域名）"""
    results = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            subdomain = line.strip()
            if subdomain:
                results.append({"host": subdomain, "source": "unknown", "input": ""})
    return results


def parse_json(filepath: Path) -> list[dict]:
    """解析 subfinder -oJ 输出的 JSON（每行一个 JSON 对象）"""
    results = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                results.append(
                    {
                        "host": obj.get("host", ""),
                        "source": obj.get("source", "unknown"),
                        "input": obj.get("input", ""),
                    }
                )
            except json.JSONDecodeError:
                # 可能是普通文本行，当作 txt 处理
                results.append({"host": line, "source": "unknown", "input": ""})
    return results


def auto_detect_format(filepath: Path) -> str:
    """根据扩展名和内容自动检测格式"""
    if filepath.suffix.lower() == ".json":
        return "json"
    # 尝试读第一行判断
    with open(filepath, encoding="utf-8") as f:
        first_line = f.readline().strip()
    try:
        json.loads(first_line)
        return "json"
    except json.JSONDecodeError:
        return "txt"


def deduplicate(results: list[dict]) -> list[dict]:
    """按 host 去重，保留所有来源"""
    seen: dict[str, set] = defaultdict(set)
    for r in results:
        seen[r["host"]].add(r["source"])
    deduped = []
    for host, sources in seen.items():
        deduped.append({"host": host, "sources": ", ".join(sorted(sources))})
    return sorted(deduped, key=lambda x: x["host"])


def group_by_root_domain(records: list[dict]) -> dict[str, list[str]]:
    """按一级根域名分组"""
    groups: dict[str, list[str]] = defaultdict(list)
    for r in records:
        host = r["host"]
        parts = host.split(".")
        if len(parts) >= 2:
            root = ".".join(parts[-2:])
        else:
            root = host
        groups[root].append(host)
    return dict(groups)


def source_stats(results: list[dict]) -> Counter:
    """统计各数据源贡献数量"""
    counter: Counter = Counter()
    for r in results:
        for src in r.get("source", "unknown").split(", "):
            counter[src.strip()] += 1
    return counter


def export_csv(records: list[dict], out_path: Path) -> None:
    """Export to CSV"""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["host", "sources"])
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] CSV saved: {out_path}")


def export_markdown(records: list[dict], groups: dict, stats: Counter, out_path: Path) -> None:
    """导出 Markdown 表格"""
    lines = []
    lines.append("# Subfinder 枚举结果报告\n")
    lines.append(f"**总计子域名数量**: {len(records)}\n")

    # 数据源统计
    lines.append("\n## 数据源贡献统计\n")
    lines.append("| 数据源 | 发现数量 |")
    lines.append("|--------|----------|")
    for src, count in stats.most_common():
        lines.append(f"| {src} | {count} |")

    # 按根域名分组
    lines.append("\n## 子域名列表（按根域名分组）\n")
    for root, hosts in sorted(groups.items()):
        lines.append(f"\n### {root} ({len(hosts)} 个)\n")
        lines.append("| 子域名 | 数据来源 |")
        lines.append("|--------|----------|")
        host_map = {r["host"]: r["sources"] for r in records}
        for h in sorted(hosts):
            lines.append(f"| {h} | {host_map.get(h, '-')} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Markdown saved: {out_path}")


def print_stats(records: list[dict], groups: dict, stats: Counter) -> None:
    """Print summary statistics to terminal"""
    print(f"\n{'='*50}")
    print(f"[STATS] Subfinder Results")
    print(f"{'='*50}")
    print(f"Total subdomains (deduped): {len(records)}")
    print(f"Root domains:               {len(groups)}")

    print(f"\n[SOURCES] Top 10 contributors:")
    for src, count in stats.most_common(10):
        bar = "#" * min(count, 30)
        print(f"  {src:<25} {count:>5}  {bar}")

    print(f"\n[GROUPS] By root domain:")
    for root, hosts in sorted(groups.items(), key=lambda x: -len(x[1])):
        print(f"  {root}: {len(hosts)}")

    print(f"\n[LIST] Subdomains (first 50):")
    for r in records[:50]:
        print(f"  {r['host']}")
    if len(records) > 50:
        print(f"  ... {len(records) - 50} more (use --out to export full list)")


def main():
    # Fix Windows console encoding for non-ASCII output
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Subfinder result parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input file path (txt or json)")
    parser.add_argument("--format", choices=["txt", "json"], help="Force format")
    parser.add_argument("--out", help="Export CSV file path")
    parser.add_argument("--md", help="Export Markdown file path")
    parser.add_argument("--stats", action="store_true", help="Show stats only")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 检测并解析
    fmt = args.format or auto_detect_format(input_path)
    print(f"[INFO] Reading: {input_path} (format: {fmt})")

    if fmt == "json":
        raw = parse_json(input_path)
    else:
        raw = parse_txt(input_path)

    print(f"[INFO] Raw records: {len(raw)}")

    # 去重
    records = deduplicate(raw)
    print(f"[INFO] After dedup: {len(records)}")

    # 分组 & 统计
    groups = group_by_root_domain(records)
    stats = source_stats(raw)

    # 输出
    print_stats(records, groups, stats)

    if args.out:
        export_csv(records, Path(args.out))

    if args.md:
        export_markdown(records, groups, stats, Path(args.md))


if __name__ == "__main__":
    main()
