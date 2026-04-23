#!/usr/bin/env python3
"""
auto_install.py - Katana 一键安装脚本

功能：
  1. 自动检测平台（Windows/Linux/macOS + 架构）
  2. 获取最新版号
  3. 通过国内镜像下载预编译二进制
  4. 解压到 ~/bin
  5. 调用 add_to_path.py 永久写入 PATH
  6. 验证安装

用法：
  python auto_install.py [--dry-run]

示例：
  python auto_install.py           # 完整安装
  python auto_install.py --dry-run # 预览模式
"""

import sys
import os
import re
import json
import zipfile
import platform
import subprocess
import argparse
import urllib.request
import urllib.error
from pathlib import Path


MIRRORS = [
    "https://ghfast.top/",
    "https://mirror.ghproxy.com/",
    "https://gh-proxy.com/",
]
GITHUB_BASE = "https://github.com/projectdiscovery"


def fix_encoding():
    """Fix Windows console encoding for UTF-8 output"""
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get_platform() -> dict:
    pf = platform.system().lower()
    machine = platform.machine().lower()
    arch = "amd64"
    if "arm64" in machine or "aarch64" in machine:
        arch = "arm64"
    elif "386" in machine or "x86" in machine:
        arch = "386"
    return {"system": pf, "arch": arch, "machine": machine}


def get_bin_dir() -> Path:
    return Path.home() / "bin"


def get_latest_version() -> str:
    headers = {"User-Agent": "Mozilla/5.0 (WorkBuddy)"}
    url = f"{GITHUB_BASE}/katana/releases/latest"
    for mirror in [""] + MIRRORS:
        full_url = mirror + url if mirror else url
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                m = re.search(r'/releases/tag/(v[\d.]+)', html)
                if m:
                    return m.group(1).lstrip("v")
            # Fallback: GitHub API
            api_url = "https://api.github.com/repos/projectdiscovery/katana/releases/latest"
            for m2 in [""] + MIRRORS:
                api_full = m2 + api_url if m2 else api_url
                try:
                    req2 = urllib.request.Request(api_full, headers=headers)
                    with urllib.request.urlopen(req2, timeout=15) as r2:
                        data = json.loads(r2.read())
                        tag = data.get("tag_name", "")
                        return tag.lstrip("v")
                except Exception:
                    continue
        except Exception:
            continue
    raise Exception("Could not determine latest version")


def download_file(url: str, dest: Path) -> bool:
    headers = {"User-Agent": "Mozilla/5.0 (WorkBuddy)"}
    for mirror in [""] + MIRRORS:
        full_url = mirror + url if mirror else url
        print(f"  Trying: {full_url[:80]}...")
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as out:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        out.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            print(f"\r  Downloading: {pct}% ({downloaded//1024//1024}MB)", end="", flush=True)
                print()
                size_mb = dest.stat().st_size / 1024 / 1024
                if size_mb < 0.5:
                    print(f"  [ERROR] File too small ({size_mb:.1f}MB), likely incomplete")
                    dest.unlink(missing_ok=True)
                    continue
                print(f"  Downloaded: {size_mb:.1f}MB")
                return True
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    return False


def install_katana(version: str, dry_run: bool = False) -> tuple[bool, Path]:
    info = get_platform()
    sys_name = info["system"]
    arch = info["arch"]

    if sys_name == "windows":
        zip_name = f"katana_{version}_windows_{arch}.zip"
    elif sys_name == "darwin":
        zip_name = f"katana_{version}_macos_{arch}.zip"
    else:
        zip_name = f"katana_{version}_linux_{arch}.zip"

    zip_url = f"{GITHUB_BASE}/katana/releases/download/v{version}/{zip_name}"

    tmp_zip = Path(os.environ.get("TEMP", "/tmp")) / f"katana_install_{os.getpid()}.zip"
    bin_dir = get_bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Downloading katana v{version} ({sys_name}/{arch})...")

    if dry_run:
        print(f"[DRY-RUN] Would download: {zip_url}")
        print(f"[DRY-RUN] Would install to: {bin_dir}")
        return True, bin_dir / "katana.exe" if sys_name == "windows" else bin_dir / "katana"

    success = download_file(zip_url, tmp_zip)
    if not success:
        print("[ERROR] Download failed after trying all mirrors.")
        return False, Path()

    print("[*] Extracting...")
    exe_name = "katana.exe" if sys_name == "windows" else "katana"
    exe_path = bin_dir / exe_name

    try:
        with zipfile.ZipFile(tmp_zip, "r") as zf:
            members = [m for m in zf.namelist() if exe_name in m.lower()]
            if members:
                zf.extract(members[0], bin_dir)
                extracted = bin_dir / members[0]
                if extracted != exe_path:
                    extracted.rename(exe_path)
            else:
                zf.extractall(bin_dir)
    except zipfile.BadZipFile:
        print("[ERROR] ZIP file is corrupted.")
        return False, Path()

    tmp_zip.unlink(missing_ok=True)

    if sys_name != "windows":
        os.chmod(str(exe_path), 0o755)

    print(f"[OK] Installed: {exe_path}")
    return True, exe_path


def configure_path(bin_dir: Path, dry_run: bool = False) -> None:
    print(f"\n[*] Configuring PATH for: {bin_dir}")
    if dry_run:
        print(f"[DRY-RUN] Would run: python add_to_path.py {bin_dir}")
        return

    script_dir = Path(__file__).parent.resolve()
    add_script = script_dir / "add_to_path.py"
    if add_script.exists():
        result = subprocess.run(
            [sys.executable, str(add_script), str(bin_dir)],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    else:
        print(f"[WARN] add_to_path.py not found at {add_script}")


def verify_install(bin_dir: Path) -> None:
    print("\n[*] Verifying installation...")
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    result = subprocess.run(["katana", "-version"],
                          capture_output=True, text=True,
                          env=env, encoding="utf-8", errors="replace")
    if result.stdout:
        print(result.stdout.strip())
    else:
        print(result.stderr.strip())


def main():
    fix_encoding()

    parser = argparse.ArgumentParser(description="Katana auto-install (WorkBuddy Skill)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    info = get_platform()

    print(f"=" * 55)
    print(f"  Katana Auto-Install (WorkBuddy Skill)")
    print(f"=" * 55)
    print(f"Platform: {info['system']} {info['machine']}")
    print(f"Install dir: {get_bin_dir()}")
    print(f"Dry run: {args.dry_run}")

    if args.dry_run:
        print("\n[DRY-RUN MODE] No files will be modified.\n")

    print("\n[*] Checking latest version...")
    try:
        version = get_latest_version()
        print(f"[*] Latest version: v{version}")
    except Exception as e:
        print(f"[WARN] Could not fetch version: {e}, using fallback v1.1.0")
        version = "1.1.0"

    ok, exe_path = install_katana(version, args.dry_run)
    if not ok and not args.dry_run:
        sys.exit(1)

    configure_path(get_bin_dir(), args.dry_run)

    if not args.dry_run:
        verify_install(get_bin_dir())

    print(f"\n{'=' * 55}")
    if not args.dry_run:
        print(f"  Done! Install dir: {get_bin_dir()}")
        print(f"  Restart terminal or VS Code to use 'katana' directly.")
    else:
        print("  Dry run complete.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
