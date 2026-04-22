# PowerShell 一键部署脚本
# 用法：.\deploy_to_server.ps1 -ServerIP "your_server_ip" -Username "ubuntu"

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "ubuntu",
    
    [Parameter(Mandatory=$false)]
    [string]$RemotePath = "~/.openclaw/workspace/skills/intelligent-test-orchestrator"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  部署优化后的代码到服务器" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 设置本地路径
$LocalPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$UtilsPath = Join-Path $LocalPath "utils"
$AdaptersPath = Join-Path $LocalPath "adapters"

# 临时目录
$TempUploadPath = Join-Path $env:TEMP "intelligent-test-orchestrator-upload"
if (Test-Path $TempUploadPath) {
    Remove-Item $TempUploadPath -Recurse -Force
}
New-Item -ItemType Directory -Path $TempUploadPath | Out-Null
New-Item -ItemType Directory -Path (Join-Path $TempUploadPath "utils") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $TempUploadPath "adapters") | Out-Null

Write-Host "[1/6] 检查本地文件..." -ForegroundColor Yellow

# 检查必需文件
$RequiredFiles = @(
    (Join-Path $UtilsPath "logger.py"),
    (Join-Path $AdaptersPath "base_tool_adapter.py"),
    (Join-Path $AdaptersPath "phase0_adapter_real.py"),
    (Join-Path $AdaptersPath "phase2_adapter_real.py")
)

$AllFilesExist = $true
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $([System.IO.Path]::GetFileName($file))" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $([System.IO.Path]::GetFileName($file)) 不存在" -ForegroundColor Red
        $AllFilesExist = $false
    }
}

if (-not $AllFilesExist) {
    Write-Host "`n❌ 错误：缺少必需文件，请确保在正确的项目目录中运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/6] 准备上传文件..." -ForegroundColor Yellow

# 复制文件到临时目录
Copy-Item (Join-Path $UtilsPath "logger.py") (Join-Path $TempUploadPath "utils\")
Copy-Item (Join-Path $AdaptersPath "base_tool_adapter.py") (Join-Path $TempUploadPath "adapters\")
Copy-Item (Join-Path $AdaptersPath "phase0_adapter_real.py") (Join-Path $TempUploadPath "adapters\")
Copy-Item (Join-Path $AdaptersPath "phase2_adapter_real.py") (Join-Path $TempUploadPath "adapters\")

Write-Host "  ✅ 文件已准备就绪" -ForegroundColor Green

Write-Host "`n[3/6] 检查服务器连接..." -ForegroundColor Yellow

# 测试 SSH 连接
try {
    $TestConnection = ssh -o ConnectTimeout=5 -o BatchMode=yes "$Username@$ServerIP" "exit" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ 服务器连接成功" -ForegroundColor Green
    } else {
        throw "SSH 连接失败"
    }
} catch {
    Write-Host "  ❌ 无法连接到服务器，请检查：" -ForegroundColor Red
    Write-Host "     - 服务器 IP 地址是否正确" -ForegroundColor Yellow
    Write-Host "     - SSH 密钥是否配置" -ForegroundColor Yellow
    Write-Host "     - 防火墙设置" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[4/6] 上传文件到服务器..." -ForegroundColor Yellow

# 在服务器上创建临时目录
ssh "$Username@$ServerIP" "mkdir -p ~/intelligent-test-orchestrator/utils ~/intelligent-test-orchestrator/adapters"

# 上传文件
$UploadFiles = @(
    "utils/logger.py",
    "adapters/base_tool_adapter.py",
    "adapters/phase0_adapter_real.py",
    "adapters/phase2_adapter_real.py"
)

foreach ($file in $UploadFiles) {
    $LocalFile = Join-Path $TempUploadPath $file
    $RemoteDir = "$Username@$ServerIP:~/intelligent-test-orchestrator/$([System.IO.Path]::GetDirectoryName($file))"
    
    Write-Host "  - 上传 $([System.IO.Path]::GetFileName($file))..." -NoNewline
    try {
        scp "$LocalFile" "$RemoteDir" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✅" -ForegroundColor Green
        } else {
            Write-Host " ❌" -ForegroundColor Red
        }
    } catch {
        Write-Host " ❌" -ForegroundColor Red
    }
}

Write-Host "`n[5/6] 在服务器上部署文件..." -ForegroundColor Yellow

# 执行部署命令
$DeployScript = @'
cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator

# 备份旧文件
echo "  - 备份旧版本..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp adapters/phase0_adapter_real.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp adapters/phase2_adapter_real.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# 复制新文件
echo "  - 复制新文件..."
cp ~/intelligent-test-orchestrator/utils/logger.py utils/
cp ~/intelligent-test-orchestrator/adapters/base_tool_adapter.py adapters/
cp ~/intelligent-test-orchestrator/adapters/phase0_adapter_real.py adapters/
cp ~/intelligent-test-orchestrator/adapters/phase2_adapter_real.py adapters/

# 清理临时文件
rm -rf ~/intelligent-test-orchestrator

# 清除 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ 文件部署完成"
'@

ssh "$Username@$ServerIP" $DeployScript

Write-Host "`n[6/6] 重启 OpenClaw..." -ForegroundColor Yellow

# 重启 OpenClaw
ssh "$Username@$ServerIP" "openclaw restart" 2>&1 | Out-Null
Write-Host "  ✅ OpenClaw 已重启" -ForegroundColor Green

# 清理临时文件
Remove-Item $TempUploadPath -Recurse -Force

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 等待 OpenClaw 重启完成（约 30 秒）" -ForegroundColor White
Write-Host "  2. 运行测试验证功能" -ForegroundColor White
Write-Host "  3. 检查日志确认优化效果" -ForegroundColor White
Write-Host ""
Write-Host "测试命令（在服务器上执行）：" -ForegroundColor Yellow
Write-Host "  cd ~/.openclaw/workspace/skills/intelligent-test-orchestrator/test" -ForegroundColor White
Write-Host "  python3 test_phase2_phase3_real.py" -ForegroundColor White
Write-Host ""
Write-Host "查看日志：" -ForegroundColor Yellow
Write-Host "  tail -f ~/.openclaw/workspace/skills/intelligent-test-orchestrator/logs/latest_run.log" -ForegroundColor White
Write-Host ""
