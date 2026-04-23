#!/usr/bin/env python3
import subprocess
import sys
import shlex
import os
import json

def get_httpx_path():
    # 优先使用环境变量指定路径
    env_path = os.environ.get("HTTPX_PATH")
    if env_path:
        return env_path
    
    # 检查常见的 httpx 安全工具安装路径
    possible_paths = [
        "/usr/local/bin/httpx-security",    # 重命名版本（避免冲突）
        "/usr/local/go/bin/httpx",          # Go 安装路径
        os.path.expanduser("~/go/bin/httpx"), # 用户 Go 安装
        "httpx"                             # 最后尝试 PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果找不到，检查是否有 HTTP 客户端的 httpx
    http_client_path = subprocess.run(["which", "httpx"], capture_output=True, text=True)
    if http_client_path.returncode == 0:
        client_path = http_client_path.stdout.strip()
        print(f"警告: 找到 HTTP 客户端 httpx 在 {client_path}，不是安全工具 httpx")
        print(f"请手动安装: go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
        print(f"或设置环境变量: export HTTPX_PATH=/path/to/httpx-security")
    
    return "httpx"  # 回退

def run_httpx(targets, opts="", output_format="text"):
    base_cmd = [get_httpx_path()]
    # 智能判断是单url、url列表或文件
    if isinstance(targets, str):
        targets = targets.strip()
        if targets.startswith("http"):  # 单个
            base_cmd += ["-u", targets]
        elif os.path.isfile(targets):    # 文件
            base_cmd += ["-l", targets]
        elif "," in targets:
            tls = [t.strip() for t in targets.split(",") if t.strip()]
            with open(".tmp_httpx_list.txt","w") as f:f.write("\n".join(tls))
            base_cmd += ["-l", ".tmp_httpx_list.txt"]
        else:
            base_cmd += ["-u", targets]
    # 附加参数
    if opts:
        base_cmd += shlex.split(opts)
    # 标准输出格式
    if output_format=="json":
        base_cmd += ["-json"]
    try:
        res = subprocess.run(base_cmd, capture_output=True, text=True, timeout=300)
        out = res.stdout
        # 自动清理临时文件
        if os.path.exists(".tmp_httpx_list.txt"): os.remove(".tmp_httpx_list.txt")
        if res.returncode != 0:
            raise Exception(res.stderr or "httpx退出异常")
        return out
    except Exception as e:
        err_info = {
            "status": "error",
            "cmd": " ".join(base_cmd),
            "reason": str(e)
        }
        return json.dumps(err_info, ensure_ascii=False)

def parse_httpx_json(content):
    """将多行httpx -json输出转list"""
    try:
        result = [json.loads(line) for line in content.strip().splitlines() if line.strip().startswith("{")]
        return result
    except Exception as e:
        return {"status": "parse_error", "reason": str(e)}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw httpx skill入口")
    parser.add_argument("--targets", type=str, help="目标URL/文件/逗号拼接", required=False)
    parser.add_argument("--opts", type=str, help="httpx附加参数，可选", default="-status-code -title -web-server")
    parser.add_argument("--format", type=str, default="text", choices=["text","json"], help="输出格式")
    parser.add_argument("--parse", action="store_true", help="二次结构化json输出")
    args = parser.parse_args()
    if args.targets:
        out = run_httpx(args.targets, args.opts, args.format)
        if args.parse and args.format=="json":
            print(json.dumps(parse_httpx_json(out), indent=2, ensure_ascii=False))
        else:
            print(out)
    else:
        parser.print_help()
