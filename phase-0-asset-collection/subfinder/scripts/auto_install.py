#!/usr/bin/env python3
"""
auto_install.py - Subfinder + httpx 一键安装脚本

功能：
  1. 自动检测系统平台（Windows/Linux/macOS）
  2. 下载最新版 subfinder 预编译二进制
  3. 安装到用户级 bin 目录
  4. 调用 add_to_path.py 永久配置 PATH
  5. 可选安装 httpx

用法：
  python auto_install.py [--with-httpx] [--dry-run]

示例：
  python auto_install.py              # 仅安装 subfinder
  python auto_install.py --with-httpx # 安装 subfinder + httpx
  python auto_install.py --dry-run     # 预览模式（不实际下载）
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


# ──────────────────────────────────────────────
# 平台与路径
# ──────────────────────────────────────────────

def get_platform() -> dict:
    """返回平台信息字典"""
    pf = platform.system().lower()
    machine = platform.machine().lower()
    
    # 修正架构检测逻辑：优先64位，再32位
    if "x86_64" in machine or "amd64" in machine:
        arch = "amd64"
    elif "arm64" in machine or "aarch64" in machine:
        arch = "arm64"
    elif "386" in machine or "i386" in machine or "x86" in machine:
        arch = "386"
    else:
        arch = "amd64"  # 默认假定amd64
    
    return {"system": pf, "arch": arch}


def get_bin_dir() -> Path:
    """返回用户级工具安装目录"""
    if sys.platform.startswith("win"):
        return Path.home() / "bin"
    else:
        return Path.home() / "bin"


# ──────────────────────────────────────────────
# 下载工具
# ──────────────────────────────────────────────

MIRRORS = [
    "https://ghfast.top",           # 国内可用，速度快
    "https://mirror.ghproxy.com",   # 备选镜像
    "https://gh-proxy.com",         # 备选镜像
    "https://ghproxy.com",          # 常用镜像
    "https://kgithub.com",          # GitHub镜像
    "https://github.moeyy.xyz",     # 备用镜像
    "https://download.fastgit.org", # FastGit镜像
]

GITHUB_BASE = "https://github.com/projectdiscovery"


def fetch_json(url: str) -> dict:
    """带超时和镜像回退的 GET 请求"""
    headers = {"User-Agent": "Mozilla/5.0 (WorkBuddy auto-install)"}
    for mirror in [""] + MIRRORS:
        full_url = mirror + url if mirror else url
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue
    raise Exception(f"Failed to fetch: {url}")


def get_latest_version() -> str:
    """获取 subfinder 最新版本号"""
    data = fetch_json(f"{GITHUB_BASE}/subfinder/releases/latest")
    tag = data.get("tag_name", "")
    return tag.lstrip("v")


def download_file(url: str, dest: Path, max_size_mb: int = 200) -> bool:
    """下载文件，支持镜像回退，显示进度"""
    headers = {"User-Agent": "Mozilla/5.0 (WorkBuddy auto-install)"}
    for mirror in [""] + MIRRORS:
        full_url = mirror + url if mirror else url
        print(f"  Trying: {full_url}")
        try:
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, timeout=180) as resp:
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
                            print(f"\r  Progress: {pct}% ({downloaded//1024//1024}MB)", end="", flush=True)
                print()
                size_mb = dest.stat().st_size / 1024 / 1024
                if size_mb < 0.5:
                    print(f"  [ERROR] Downloaded file too small: {size_mb:.1f}MB, likely incomplete")
                    dest.unlink()
                    continue
                print(f"  Downloaded: {size_mb:.1f}MB -> {dest}")
                return True
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    return False


# ──────────────────────────────────────────────
# 安装 subfinder
# ──────────────────────────────────────────────

def install_subfinder(version: str, dry_run: bool = False) -> tuple[bool, Path]:
    """下载并解压 subfinder，返回 (成功, 可执行文件路径)"""
    info = get_platform()
    sys_name = info["system"]
    arch = info["arch"]

    # 构建下载 URL
    if sys_name == "windows":
        zip_name = f"subfinder_{version}_windows_{arch}.zip"
    elif sys_name == "darwin":
        zip_name = f"subfinder_{version}_macos_{arch}.zip"
    else:
        zip_name = f"subfinder_{version}_linux_{arch}.zip"

    zip_url = f"{GITHUB_BASE}/subfinder/releases/download/v{version}/{zip_name}"

    tmp_zip = Path("C:/Users/mic1860/AppData/Local/Temp/subfinder_install.zip")
    if sys.platform.startswith("win"):
        tmp_zip = Path(os.environ.get("TEMP", "/tmp")) / "subfinder_install.zip"
    else:
        tmp_zip = Path("/tmp/subfinder_install.zip")

    bin_dir = get_bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Downloading subfinder v{version} ({sys_name}/{arch})...")

    if dry_run:
        print(f"[DRY-RUN] Would download: {zip_url}")
        print(f"[DRY-RUN] Would install to: {bin_dir}")
        return True, bin_dir / "subfinder.exe" if sys_name == "windows" else bin_dir / "subfinder"

    success = download_file(zip_url, tmp_zip)
    if not success:
        print("[ERROR] Download failed after trying all mirrors.")
        return False, Path()

    # 解压
    print("[*] Extracting...")
    exe_name = "subfinder.exe" if sys_name == "windows" else "subfinder"
    exe_path = bin_dir / exe_name

    try:
        with zipfile.ZipFile(tmp_zip, "r") as zf:
            members = [m for m in zf.namelist() if exe_name in m or m.endswith(exe_name)]
            if members:
                zf.extract(members[0], bin_dir)
                extracted = bin_dir / members[0]
                if extracted != exe_path:
                    extracted.rename(exe_path)
            else:
                zf.extractall(bin_dir)
    except zipfile.BadZipFile:
        print("[ERROR] ZIP file is corrupted. Try running again.")
        return False, Path()

    tmp_zip.unlink(missing_ok=True)

    # 设置可执行权限（Linux/macOS）
    if sys_name != "windows":
        os.chmod(str(exe_path), 0o755)

    print(f"[OK] Installed: {exe_path}")
    return True, exe_path


# ──────────────────────────────────────────────
# 安装 httpx
# ──────────────────────────────────────────────

def install_httpx(dry_run: bool = False) -> bool:
    """安装 httpx"""
    bin_dir = get_bin_dir()
    bin_dir.mkdir(parents=True, exist_ok=True)

    # 优先 go install
    print("[*] Installing httpx...")
    try:
        result = subprocess.run(["go", "version"], capture_output=True, timeout=10)
        if result.returncode == 0:
            if dry_run:
                print("[DRY-RUN] Would run: go install httpx@latest")
                return True
            env = os.environ.copy()
            env["GOBIN"] = str(bin_dir)
            env["GOPATH"] = str(bin_dir.parent / "go")
            print("[*] Installing via go install...")
            r = subprocess.run(
                ["go", "install", "-v", "github.com/projectdiscovery/httpx/cmd/httpx@latest"],
                env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=180
            )
            if r.returncode == 0:
                exe = bin_dir / "httpx.exe" if sys.platform.startswith("win") else bin_dir / "httpx"
                print(f"[OK] httpx installed: {exe}")
                return True
    except Exception as e:
        print(f"[WARN] go install failed: {e}")

    # pip 备用
    pip_cmd = "pip3" if not sys.platform.startswith("win") else "pip"
    try:
        if dry_run:
            print(f"[DRY-RUN] Would run: {pip_cmd} install httpx")
            return True
        print(f"[*] Installing via pip...")
        r = subprocess.run([pip_cmd, "install", "-q", "httpx"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            print("[OK] httpx installed via pip")
            return True
    except Exception as e:
        print(f"[WARN] pip install failed: {e}")

    print("[ERROR] All httpx install methods failed.")
    return False


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    # Fix Windows console encoding
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Subfinder + httpx auto-install")
    parser.add_argument("--with-httpx", action="store_true", help="Also install httpx")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    args = parser.parse_args()

    print(f"=" * 55)
    print(f"  Subfinder Auto-Install (WorkBuddy Skill)")
    print(f"=" * 55)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Install dir: {get_bin_dir()}")
    print(f"Dry run: {args.dry_run}")

    if args.dry_run:
        print("\n[DRY-RUN MODE] No files will be modified.\n")

    # 获取版本
    print("\n[*] Checking latest version...")
    try:
        version = get_latest_version()
        print(f"[*] Latest version: v{version}")
    except Exception as e:
        print(f"[ERROR] Could not fetch latest version: {e}")
        version = "2.13.0"  # fallback

    # 安装 subfinder
    ok, exe_path = install_subfinder(version, args.dry_run)
    if not ok and not args.dry_run:
        sys.exit(1)

    # 配置 PATH
    bin_dir = get_bin_dir()
    print(f"\n[*] Configuring PATH...")
    if args.dry_run:
        print(f"[DRY-RUN] Would call: python add_to_path.py {bin_dir}")
    else:
        script_dir = Path(__file__).parent.resolve()
        add_to_path_script = script_dir / "add_to_path.py"
        if add_to_path_script.exists():
            result = subprocess.run(
                [sys.executable, str(add_to_path_script), str(bin_dir)],
                capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            print(result.stdout)
        else:
            print(f"[WARN] add_to_path.py not found at {add_to_path_script}")

    # 验证
    if not args.dry_run:
        print("\n[*] Verifying installation...")
        env = os.environ.copy()
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        result = subprocess.run(["subfinder", "-version"],
                                capture_output=True, text=True,
                                env=env, encoding="utf-8", errors="replace")
        print(result.stdout.strip() if result.stdout else result.stderr.strip())

    # 安装 httpx
    if args.with_httpx:
        install_httpx(args.dry_run)

    print(f"\n{'=' * 55}")
    if not args.dry_run:
        print(f"  Done! Install dir: {bin_dir}")
        print(f"  Restart terminal or VS Code to use 'subfinder' directly.")
        print(f"  Or run: $env:PATH = \"{bin_dir};\" + $env:PATH  (PowerShell)")
    else:
        print("  Dry run complete. No changes made.")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
