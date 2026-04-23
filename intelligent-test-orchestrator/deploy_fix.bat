@echo off
REM 快速部署 phase2_adapter_real.py 到服务器
REM 用法：deploy_fix.bat [服务器 IP]

set SERVER_IP=%1
if "%SERVER_IP%"=="" set SERVER_IP=你的服务器 IP

echo ============================================================
echo 部署 phase2_adapter_real.py 到服务器
echo ============================================================
echo.
echo 服务器：%SERVER_IP%
echo.
echo 请按提示操作：
echo.
echo 1. 复制以下命令并在 PowerShell 中执行：
echo ============================================================

echo scp -i your_key.pem adapters/phase2_adapter_real.py ubuntu@%SERVER_IP%:~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator/adapters/

echo ============================================================
echo.
echo 2. SSH 登录服务器并清除缓存：
echo ssh ubuntu@%SERVER_IP%
echo cd ~/.openclaw/workspace/skills/advanced-pentester-v2/intelligent-test-orchestrator
echo find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo find . -name "*.pyc" -delete
echo.
echo 3. 验证修复：
echo grep -n "def normalize_vulnerabilities" adapters/phase2_adapter_real.py
echo python3 -c "from adapters.phase2_adapter_real import Phase2Adapter; adapter = Phase2Adapter(); print('OK' if hasattr(adapter, 'normalize_vulnerabilities') else 'FAIL')"
echo.
echo ============================================================
pause
