#!/usr/bin/env python3
import subprocess
import sys
import shlex
import os

def get_whatweb_path():
    return os.environ.get("WHATWEB_PATH", "whatweb")

def run_whatweb(targets, opts="", output_format="text"):
    base_cmd = [get_whatweb_path()]
    # 智能单个、批量文本或文件
    if isinstance(targets, str):
        targets = targets.strip()
        if targets.startswith("http"):
            base_cmd.append(targets)
        elif os.path.isfile(targets):
            base_cmd += ["-i", targets]
        elif any(sep in targets for sep in [',',';','\n']):
            tlist = [t.strip() for t in re.split('[,;\n]+', targets) if t.strip()]
            with open(".tmp_whatweb_targets.txt","w") as f: f.write("\n".join(tlist))
            base_cmd += ["-i", ".tmp_whatweb_targets.txt"]
        else: # 默认为单目标
            base_cmd.append(targets)
    if opts:
        base_cmd += shlex.split(opts)
    # 支持结构化json
    if output_format == "json":
        base_cmd += ["--log-json", ".tmp_whatweb_out.json"]
    try:
        res = subprocess.run(base_cmd, capture_output=True, text=True, timeout=300)
        out = res.stdout
        # 提取结构化输出（json模式）
        if output_format == "json" and os.path.exists(".tmp_whatweb_out.json"):
            with open(".tmp_whatweb_out.json") as f:
                out = f.read()
            os.remove(".tmp_whatweb_out.json")
        if os.path.exists(".tmp_whatweb_targets.txt"): os.remove(".tmp_whatweb_targets.txt")
        if res.returncode != 0:
            raise Exception(res.stderr or "whatweb退出异常")
        return out
    except Exception as e:
        err_info = {
            "status": "error",
            "cmd": " ".join(base_cmd),
            "reason": str(e)
        }
        return str(err_info)

if __name__ == '__main__':
    import argparse
    import re
    parser = argparse.ArgumentParser(description="OpenClaw whatweb skill入口")
    parser.add_argument("--targets", type=str, help="目标URL/批量文件/逗号拼接", required=False)
    parser.add_argument("--opts", nargs='?', default='', help="附加参数，可选")
    parser.add_argument("--format", type=str, default="text", choices=["text","json"])
    args = parser.parse_args()
    if args.targets:
        out = run_whatweb(args.targets, args.opts, args.format)
        print(out)
    else:
        parser.print_help()
