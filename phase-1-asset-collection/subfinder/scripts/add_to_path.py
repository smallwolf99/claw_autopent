#!/usr/bin/env python3
"""
add_to_path.py - 跨平台永久 PATH 环境变量配置工具

功能：
  - 自动检测当前操作系统
  - 将指定目录永久添加到用户 PATH 环境变量
  - Windows: 使用 setx 写入注册表（当前用户级别）
  - Linux/macOS: 追加到 ~/.bashrc / ~/.zshrc

用法：
  python add_to_path.py <目录路径> [--dry-run]
  python add_to_path.py "C:\Users\<用户名>\bin"
  python add_to_path.py "~/bin" --dry-run

注意：
  - 默认不覆盖已有 PATH，仅追加（去重）
  - --dry-run 仅显示将执行的操作，不实际修改
"""

import sys
import os
import re
import argparse
import subprocess
from pathlib import Path


def normalize_path(path_str: str) -> str:
    """展开 ~ 和环境变量，返回绝对路径字符串"""
    return str(Path(path_str).expanduser().resolve())


def get_shell_configs() -> list[Path]:
    """获取当前用户的所有 shell 配置文件"""
    home = Path.home()
    candidates = [
        home / ".bashrc",
        home / ".zshrc",
        home / ".profile",
        home / ".bash_profile",
    ]
    return [p for p in candidates if p.exists()]


def add_to_unix_path(dir_path: str, dry_run: bool = False) -> bool:
    """Linux/macOS: 追加目录到 shell 配置文件的 PATH"""
    dir_abs = normalize_path(dir_path)

    if not Path(dir_abs).exists():
        print(f"[ERROR] Directory does not exist: {dir_abs}")
        return False

    # 检查是否已在任一配置文件中
    for cfg in get_shell_configs():
        try:
            content = cfg.read_text()
            if f'PATH="{dir_abs}"' in content or f"PATH='{dir_abs}'" in content or f"{dir_abs}" in content.split("PATH=")[-1].split("\n")[0]:
                # 简单检查
                for line in content.splitlines():
                    if "PATH=" in line and dir_abs in line and not line.strip().startswith("#"):
                        print(f"[SKIP] {dir_abs} already in PATH via {cfg}")
                        return True
        except Exception:
            pass

    # 选择目标配置文件
    bashrc = Path.home() / ".bashrc"
    zshrc = Path.home() / ".zshrc"
    target = zshrc if zshrc.exists() else bashrc

    export_line = f'\n# Added by subfinder skill\nexport PATH="{dir_abs}:$PATH"\n'

    if dry_run:
        print(f"[DRY-RUN] Would append to {target}:")
        print(f"  {export_line.strip()}")
        return True

    try:
        with open(target, "a", encoding="utf-8") as f:
            f.write(export_line)
        print(f"[OK] Added {dir_abs} to PATH via {target}")
        print(f"    Run 'source {target}' or restart terminal to apply.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write to {target}: {e}")
        return False


def add_to_windows_path(dir_path: str, dry_run: bool = False) -> bool:
    """Windows: 使用 setx 将目录添加到用户 PATH（永久）"""
    dir_abs = normalize_path(dir_path)

    if not Path(dir_abs).exists():
        print(f"[ERROR] Directory does not exist: {dir_abs}")
        return False

    try:
        # 读取当前用户 PATH（从注册表）
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "[Environment]::GetEnvironmentVariable('Path', 'User')"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        current_path = result.stdout.strip()
    except Exception as e:
        print(f"[WARN] Could not read current PATH: {e}, proceeding anyway")
        current_path = ""

    # 解析现有 PATH
    existing = [p.strip().rstrip('\\') for p in current_path.split(';') if p.strip()]

    # 去重检查（不区分大小写）
    dir_abs_lower = dir_abs.lower()
    if any(p.lower().rstrip('\\') == dir_abs_lower for p in existing):
        print(f"[SKIP] {dir_abs} already in user PATH")
        return True

    # 构建新 PATH
    new_path = ";".join(existing + [dir_abs])
    escaped_new_path = new_path.replace('"', '\\"')

    if dry_run:
        print(f"[DRY-RUN] Would set user PATH to:")
        print(f"  {new_path}")
        return True

    try:
        # 使用 setx 写入注册表（用户级别，永久生效）
        # 注意：setx 需要重启新的命令窗口才能看到变化
        result = subprocess.run(
            ['setx', 'PATH', new_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print(f"[OK] Added {dir_abs} to user PATH (permanent)")
            print(f"    Note: Restart terminal / VS Code to see changes.")
            print(f"    Or run: $env:PATH = \"{dir_abs};\" + $env:PATH")
            return True
        else:
            print(f"[ERROR] setx failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    # Fix Windows console encoding
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() in ("gbk", "cp936", "gb2312"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Add a directory to system PATH permanently (cross-platform)"
    )
    parser.add_argument("dir", help="Directory path to add to PATH")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")

    args = parser.parse_args()
    dir_path = args.dir

    print(f"[INFO] Target directory: {normalize_path(dir_path)}")

    if sys.platform.startswith("win"):
        success = add_to_windows_path(dir_path, args.dry_run)
    else:
        success = add_to_unix_path(dir_path, args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
