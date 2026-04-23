#!/bin/bash
# 测试 httpx skill
python3 ../main.py --targets "http://127.0.0.1:4280" --opts "-status-code -title" --format text
