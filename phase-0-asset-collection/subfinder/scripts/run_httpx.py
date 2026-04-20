#!/usr/bin/env python3
"""
run_httpx.py - httpx 存活验证与 HTTP 信息探测

功能：
  - 自动检测 httpx 是否安装，未安装则引导安装
  - 将子域名列表通过管道输入 httpx，验证 HTTP 存活状态
  - 提取标题、状态码、技术栈、WAF 检测等信息
  - 支持 JSON/CSV 输出，生成结构化报告

用法：
  # 单文件输入（subfinder txt 输出）
  python run_httpx.py subdomains.txt

  # 单文件输入（subfinder json 输出，自动提取 host）
  python run_httpx.py subdomains.json --format json

  # 管道输入
  subfinder -d example.com -silent | python run_httpx.py -

  # 完整示例（含所有选项）
  python run_httpx.py subdomains.txt -o report.json --title --status --tech --waf --cc --probe

选项：
  -i, --input    输入文件（支持 txt/json/-代表管道）
  --format      强制指定输入格式（txt/json）
  --output      输出文件路径（JSON Lines 格式）
  --title       提取页面标题
  --status      提取 HTTP 状态码
  --tech        检测技术栈
  --waf         检测 WAF
  --cc          显示国家代码
  --probe       发送 HTTP 方法探测（GET/HEAD/POST/UDP/Conn）
  --threads     并发数（默认 50）
  --timeout     超时秒数（默认 10）
  --match-regex 匹配状态码正则（如 200|301|302）
  --filter-regex 过滤状态码正则（如 404|403）
  --json        输出 JSON Lines（默认）
  --csv         输出 CSV
  --md          输出 Markdown 表格
  --stats       仅显示统计摘要
"""

import sys
import os
import re
import json
import csv
import shlex
import platform
import subprocess
import argparse
from pathlib import Path
from collections import defaultdict, Counter


# ──────────────────────────────────────────────
# httpx 检测与安装
# ──────────────────────────────────────────────

def check_httpx() -> tuple[bool, str]:
    """检测 httpx 是否在 PATH 中，返回 (是否存在, 路径)"""
    import shutil
    path = shutil.which("httpx")
    if path:
        return True, path
    return False, ""


def get_install_dir() -> Path:
    """返回工具安装目录（用户级 bin）"""
    if sys.platform.startswith("win"):
        base = Path.home() / "bin"
    else:
        base = Path.home() / "bin"
    return base.resolve()


def install_httpx() -> bool:
    """引导安装 httpx，返回是否成功"""
    print("[INFO] httpx not found. Starting installation...")

    # 优先尝试 Go 安装（ProjectDiscovery 官方推荐）
    if _try_go_install():
        return check_httpx()[0]

    # 其次尝试 pip/pip3 安装
    if _try_pip_install():
        return check_httpx()[0]

    # Docker 备用方案
    if _try_docker_install():
        return True

    print("[ERROR] All installation methods failed. Please install httpx manually.")
    return False


def _try_go_install() -> bool:
    """尝试通过 go install 安装"""
    try:
        result = subprocess.run(["go", "version"], capture_output=True, timeout=10)
        if result.returncode != 0:
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    print("[INFO] Installing httpx via 'go install'...")
    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)

    # Go 安装到用户 bin 目录
    env = os.environ.copy()
    gobin = str(install_dir)
    env["GOBIN"] = gobin
    env["GOPATH"] = str(install_dir.parent / "go")

    cmd = ["go", "install", "-v", "github.com/projectdiscovery/httpx/cmd/httpx@latest"]
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120)
        if r.returncode == 0:
            exe = install_dir / "httpx.exe" if sys.platform.startswith("win") else install_dir / "httpx"
            if exe.exists():
                print(f"[OK] httpx installed to {exe}")
                return True
    except Exception as e:
        print(f"[WARN] go install failed: {e}")
    return False


def _try_pip_install() -> bool:
    """尝试通过 pip 安装 httpx"""
    pip_cmd = "pip3" if not sys.platform.startswith("win") else "pip"
    try:
        print(f"[INFO] Installing httpx via '{pip_cmd} install httpx'...")
        r = subprocess.run([pip_cmd, "install", "-q", "httpx"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
        if r.returncode == 0:
            if check_httpx()[0]:
                print("[OK] httpx installed via pip")
                return True
    except Exception as e:
        print(f"[WARN] pip install failed: {e}")
    return False


def _try_docker_install() -> bool:
    """尝试 Docker 运行 httpx（不安装到主机）"""
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        if r.returncode != 0:
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    print("[INFO] Using httpx via Docker (docker must be running)")
    return True


# ──────────────────────────────────────────────
# 输入解析
# ──────────────────────────────────────────────

def load_hosts(input_path: str, fmt: str) -> list[str]:
    """从文件加载子域名列表"""
    if input_path == "-":
        # stdin
        hosts = [line.strip() for line in sys.stdin if line.strip()]
        return hosts

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    hosts = []
    if path.suffix.lower() == ".json" or fmt == "json":
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    host = obj.get("host", "")
                    if host:
                        hosts.append(host)
                except json.JSONDecodeError:
                    if line:
                        hosts.append(line)
    else:
        with open(path, encoding="utf-8") as f:
            hosts = [line.strip() for line in f if line.strip()]

    return hosts


# ──────────────────────────────────────────────
# httpx 命令构建与执行
# ──────────────────────────────────────────────

def build_httpx_cmd(hosts: list[str], args) -> list[str]:
    """构建 httpx 命令行参数列表"""
    cmd = ["httpx"]
    subdomains_file = Path("C:/Users/mic1860/AppData/Local/Temp/httpx_input.txt")
    if sys.platform.startswith("win"):
        subdomains_file = Path(os.environ.get("TEMP", "/tmp")) / "httpx_input.txt"
    else:
        subdomains_file = Path("/tmp/httpx_input.txt")

    subdomains_file.parent.mkdir(parents=True, exist_ok=True)
    subdomains_file.write_text("\n".join(hosts), encoding="utf-8")
    cmd.extend(["-l", str(subdomains_file)])

    # 输出选项
    if args.output:
        cmd.extend(["-json", "-o", str(args.output)])

    # 信息提取选项
    extract_opts = []
    if args.title:
        extract_opts.append("title")
    if args.status:
        extract_opts.append("status-code")
    if args.tech:
        extract_opts.append("tech-detect")
    if args.waf:
        extract_opts.append("waf")
    if args.cc:
        extract_opts.append("country")

    if extract_opts:
        cmd.extend(["-td", ",".join(extract_opts)])

    # 探测选项
    if args.probe:
        cmd.append("-probe")

    # 过滤选项
    if args.match_regex:
        cmd.extend(["-match-regex", args.match_regex])
    if args.filter_regex:
        cmd.extend(["-filter-regex", args.filter_regex])

    # 性能选项
    if args.threads:
        cmd.extend(["-t", str(args.threads)])
    if args.timeout:
        cmd.extend(["-timeout", f"{args.timeout}s"])

    # 静默模式
    cmd.append("-silent")

    return cmd


def run_httpx(hosts: list[str], args) -> tuple[list[dict], Path]:
    """执行 httpx 并返回结果"""
    httpx_ok, httpx_path = check_httpx()
    if not httpx_ok:
        if not install_httpx():
            raise RuntimeError("httpx installation failed")
        httpx_ok, httpx_path = check_httpx()

    # 设置 PATH
    install_dir = get_install_dir()
    env = os.environ.copy()
    if httpx_path:
        bin_dir = str(Path(httpx_path).parent)
    else:
        bin_dir = str(install_dir)
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")

    cmd = build_httpx_cmd(hosts, args)
    output_file = Path(args.output) if args.output else None

    if output_file is None:
        # 临时输出文件
        import tempfile
        if sys.platform.startswith("win"):
            output_file = Path(os.environ.get("TEMP", ".")) / "httpx_output.jsonl"
        else:
            output_file = Path("/tmp/httpx_output.jsonl")
        cmd.extend(["-json", "-o", str(output_file)])

    print(f"[INFO] Running: {' '.join(shlex.quote(c) for c in cmd)}")
    print(f"[INFO] Target hosts: {len(hosts)}")

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("[WARN] httpx timed out", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] httpx execution failed: {e}", file=sys.stderr)

    # 解析结果
    results = []
    if output_file and output_file.exists():
        with open(output_file, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    return results, output_file


# ──────────────────────────────────────────────
# 结果解析与报告
# ──────────────────────────────────────────────

def parse_results(results: list[dict]) -> dict:
    """解析 httpx 结果，生成统计摘要"""
    total = len(results)

    status_counter: Counter = Counter()
    tech_counter: Counter = Counter()
    waf_counter: Counter = Counter()
    cc_counter: Counter = Counter()
    live_hosts = []

    for r in results:
        url = r.get("url", r.get("host", ""))
        status = r.get("status_code", 0)
        techs = r.get("tech", [])
        wafs = r.get("waf", [])
        cc = r.get("country_code", r.get("country", ""))

        if status and status < 500:
            live_hosts.append(url)

        if status:
            status_counter[status] += 1
        if isinstance(techs, list):
            for t in techs:
                tech_counter[t] += 1
        elif techs:
            tech_counter[techs] += 1
        if isinstance(wafs, list):
            for w in wafs:
                waf_counter[w] += 1
        elif wafs:
            waf_counter[wafs] += 1
        if cc:
            cc_counter[cc] += 1

    return {
        "total": total,
        "live": len(live_hosts),
        "status_counter": status_counter,
        "tech_counter": tech_counter,
        "waf_counter": waf_counter,
        "cc_counter": cc_counter,
        "live_hosts": live_hosts,
    }


def print_summary(stats: dict) -> None:
    """终端打印统计摘要"""
    print(f"\n{'='*55}")
    print(f"[RESULTS] httpx Live Verification Summary")
    print(f"{'='*55}")
    print(f"Total targets scanned:  {stats['total']}")
    print(f"Live (status < 500):    {stats['live']}  ({100*stats['live']/max(stats['total'],1):.1f}%)")

    # 状态码分布
    print(f"\n[STATUS] Status Code Distribution:")
    for code, count in sorted(stats["status_counter"].items(), key=lambda x: -x[1])[:10]:
        bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
        print(f"  {str(code):<8} {count:>5}  {bar}")

    # 技术栈 Top 10
    if stats["tech_counter"]:
        print(f"\n[TECH] Top 10 Technologies:")
        for tech, count in stats["tech_counter"].most_common(10):
            bar = "#" * min(int(count * 30 / max(stats["total"], 1)), 30)
            print(f"  {tech:<30} {count:>5}  {bar}")

    # WAF 检测
    if stats["waf_counter"]:
        print(f"\n[WAF] WAF Detected:")
        for waf, count in stats["waf_counter"].most_common():
            print(f"  {waf}: {count}")

    # 存活主机列表
    print(f"\n[LIVE] Live Hosts ({len(stats['live_hosts'])}):")
    for url in sorted(stats["live_hosts"])[:30]:
        print(f"  {url}")
    if len(stats["live_hosts"]) > 30:
        print(f"  ... {len(stats['live_hosts']) - 30} more")


def export_csv(results: list[dict], out_path: Path) -> None:
    """导出 CSV"""
    if not results:
        return
    fields = ["url", "host", "status_code", "title", "tech", "waf", "content_length",
              "favicon", "input", "a"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            row = dict(r)
            if isinstance(row.get("tech"), list):
                row["tech"] = ", ".join(row["tech"])
            if isinstance(row.get("waf"), list):
                row["waf"] = ", ".join(row["waf"])
            writer.writerow(row)
    print(f"[OK] CSV saved: {out_path}")


def export_markdown(stats: dict, out_path: Path) -> None:
    """导出 Markdown 报告"""
    lines = []
    lines.append("# httpx 存活验证报告\n")

    total = stats["total"]
    live = stats["live"]
    lines.append(f"| 指标 | 数值 |\n|------|------|")
    lines.append(f"| 扫描总数 | {total} |")
    lines.append(f"| 存活数量 | {live} |")
    lines.append(f"| 存活率 | {100*live/max(total,1):.1f}% |")

    # 状态码
    if stats["status_counter"]:
        lines.append("\n## 状态码分布\n")
        lines.append("| 状态码 | 数量 |")
        lines.append("|--------|------|")
        for code, count in sorted(stats["status_counter"].items(), key=lambda x: -x[1]):
            lines.append(f"| {code} | {count} |")

    # 技术栈
    if stats["tech_counter"]:
        lines.append("\n## 技术栈 Top 10\n")
        lines.append("| 技术 | 数量 |")
        lines.append("|------|------|")
        for tech, count in stats["tech_counter"].most_common(10):
            lines.append(f"| {tech} | {count} |")

    # WAF
    if stats["waf_counter"]:
        lines.append("\n## WAF 检测\n")
        lines.append("| WAF | 数量 |")
        lines.append("|-----|------|")
        for waf, count in stats["waf_counter"].most_common():
            lines.append(f"| {waf} | {count} |")

    # 存活主机
    if stats["live_hosts"]:
        lines.append("\n## 存活主机列表\n")
        lines.append("| URL |")
        lines.append("|-----|")
        for url in sorted(stats["live_hosts"]):
            lines.append(f"| {url} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Markdown saved: {out_path}")


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    # Fix Windows console encoding
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="httpx live verification - check HTTP accessibility of subdomains",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", help="Input file (txt/json) or '-' for stdin")
    parser.add_argument("--format", choices=["txt", "json"], help="Force input format")
    parser.add_argument("--output", help="Output file (JSON Lines)")
    parser.add_argument("--title", action="store_true", help="Extract page title")
    parser.add_argument("--status", action="store_true", help="Extract status code")
    parser.add_argument("--tech", action="store_true", help="Detect technology stack")
    parser.add_argument("--waf", action="store_true", help="Detect WAF")
    parser.add_argument("--cc", action="store_true", help="Show country code")
    parser.add_argument("--probe", action="store_true", help="Enable HTTP probe")
    parser.add_argument("--threads", type=int, default=50, help="Concurrency (default: 50)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout seconds (default: 10)")
    parser.add_argument("--match-regex", help="Match URLs by status code regex")
    parser.add_argument("--filter-regex", help="Filter out URLs by status code regex")
    parser.add_argument("--csv", help="Export CSV file")
    parser.add_argument("--md", help="Export Markdown report file")
    parser.add_argument("--stats", action="store_true", help="Only show summary (no detail output)")

    args = parser.parse_args()

    # 默认开启常见选项
    if not any([args.title, args.status, args.tech, args.waf, args.cc]):
        args.title = True
        args.status = True
        args.tech = True

    print(f"[INFO] Loading hosts from: {args.input}")
    try:
        hosts = load_hosts(args.input, args.format or "")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Loaded {len(hosts)} hosts")

    if not hosts:
        print("[WARN] No hosts to scan")
        sys.exit(0)

    print(f"[INFO] Starting httpx scan...")
    results, raw_output = run_httpx(hosts, args)
    stats = parse_results(results)
    print_summary(stats)

    if args.csv:
        export_csv(results, Path(args.csv))

    if args.md:
        export_markdown(stats, Path(args.md))

    # 清理临时输入文件
    tmp_input = Path("C:/Users/mic1860/AppData/Local/Temp/httpx_input.txt")
    if sys.platform.startswith("win"):
        tmp_input = Path(os.environ.get("TEMP", "/tmp")) / "httpx_input.txt"
    else:
        tmp_input = Path("/tmp/httpx_input.txt")
    try:
        tmp_input.unlink(missing_ok=True)
    except Exception:
        pass

    print(f"\n[INFO] Done. {stats['live']}/{stats['total']} hosts are live.")


if __name__ == "__main__":
    main()
