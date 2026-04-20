#!/usr/bin/env pwsh
# 设置 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# 调用 main.py
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptPath\main.py" $args
