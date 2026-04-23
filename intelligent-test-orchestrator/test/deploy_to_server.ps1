# ==========================================
# 阶段 3 优化代码 - 一键部署脚本 (PowerShell)
# ==========================================
# 用途：将优化后的代码部署到 OpenClaw 服务器
# 使用：.\deploy_to_server.ps1 -ServerIP "192.168.1.100"
# ==========================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [string]$ServerUser = "ubuntu",
    
    [string]$ProjectDir = "~/.openclaw/workspace/skills/intelligent-test-orchestrator"
)

# 颜色函数
function Write-Header {
    param([string]$Message)
    Write-Host "==========================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "==========================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# 获取脚本所在目录
$LocalDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalDir = Split-Path -Parent $LocalDir  # 返回到项目根目录

Write-Header "开始部署到 $ServerUser@$ServerIP"

# 步骤 1: 检查本地文件
Write-Header "步骤 1: 检查本地文件"
$RequiredFiles = @(
    "utils\cache.py",
    "utils\performance_monitor.py",
    "utils\health_checker.py",
    "utils\memory_optimizer.py",
    "utils\logger.py",
    "adapters\base_tool_adapter.py",
    "core\config_optimized.py",
    "core\config_validation.py"
)

$MissingFiles = @()
foreach ($file in $RequiredFiles) {
    $filePath = Join-Path $LocalDir $file
    if (Test-Path $filePath) {
        Write-Success "$file 存在"
    } else {
        Write-Error-Custom "$file 不存在"
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Error-Custom "缺少 $($MissingFiles.Count) 个文件，请检查本地目录"
    exit 1
}

Write-Success "所有必需文件检查通过"

# 步骤 2: 测试 SSH 连接
Write-Header "步骤 2: 测试 SSH 连接"
try {
    $testConnection = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "echo '连接成功'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH 连接正常"
    } else {
        throw "SSH 连接失败"
    }
} catch {
    Write-Error-Custom "无法连接到服务器 $ServerUser@$ServerIP"
    Write-Warning-Custom "请检查："
    Write-Warning-Custom "  1. 服务器 IP 是否正确"
    Write-Warning-Custom "  2. SSH 密钥是否配置"
    Write-Warning-Custom "  3. 服务器是否在线"
    exit 1
}

# 步骤 3: 创建备份
Write-Header "步骤 3: 创建服务器备份"
$BackupDir = "backup_" + (Get-Date -Format "yyyyMMdd_HHmmss")
$BackupCommand = @"
cd $ProjectDir

# 创建备份目录
mkdir -p $BackupDir/utils $BackupDir/adapters $BackupDir/core

# 备份现有文件
cp utils/*.py $BackupDir/utils/ 2>/dev/null || echo "ℹ️  utils 目录为空或不存在"
cp adapters/*.py $BackupDir/adapters/ 2>/dev/null || echo "ℹ️  adapters 目录为空或不存在"
cp core/*.py $BackupDir/core/ 2>/dev/null || echo "ℹ️  core 目录为空或不存在"

echo "✅ 备份已创建：$BackupDir"
"@

ssh "$ServerUser@$ServerIP" $BackupCommand

# 步骤 4: 上传文件
Write-Header "步骤 4: 上传优化文件"

# 创建远程目录
ssh "$ServerUser@$ServerIP" "mkdir -p $ProjectDir/utils $ProjectDir/adapters $ProjectDir/core"

$FilesToUpload = @(
    "utils\cache.py",
    "utils\performance_monitor.py",
    "utils\health_checker.py",
    "utils\memory_optimizer.py",
    "utils\logger.py",
    "adapters\base_tool_adapter.py",
    "core\config_optimized.py",
    "core\config_validation.py"
)

foreach ($file in $FilesToUpload) {
    $filePath = Join-Path $LocalDir $file
    $remotePath = "$ProjectDir/$file".Replace('\', '/')
    Write-Host "上传 $file ... " -NoNewline
    
    scp "$filePath" "$ServerUser@$ServerIP:$remotePath"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "已上传"
    } else {
        Write-Error-Custom "上传失败"
        exit 1
    }
}

Write-Success "所有文件上传完成"

# 步骤 5: 验证文件
Write-Header "步骤 5: 验证文件完整性"
$VerifyCommand = @"
cd $ProjectDir

echo "检查文件:"
ls -lh utils/cache.py
ls -lh utils/performance_monitor.py
ls -lh utils/health_checker.py
ls -lh utils/memory_optimizer.py
ls -lh adapters/base_tool_adapter.py
ls -lh core/config_optimized.py
ls -lh core/config_validation.py

echo ""
echo "统计行数:"
wc -l utils/*.py adapters/*.py core/*.py | tail -1
"@

ssh "$ServerUser@$ServerIP" $VerifyCommand

# 步骤 6: 测试导入
Write-Header "步骤 6: 测试 Python 导入"
$ImportTestCommand = @"
cd $ProjectDir

# 设置 Python 路径
export PYTHONPATH="$ProjectDir:`$PYTHONPATH"

echo "测试导入..."
python3 -c "from utils.cache import MemoryCache; print('✅ 缓存系统导入成功')"
python3 -c "from utils.performance_monitor import PerformanceMonitor; print('✅ 性能监控导入成功')"
python3 -c "from utils.health_checker import HealthChecker; print('✅ 健康检查导入成功')"
python3 -c "from utils.memory_optimizer import VulnerabilityStream; print('✅ 内存优化导入成功')"
python3 -c "from adapters.base_tool_adapter import BaseToolAdapter; print('✅ 基类适配器导入成功')"

echo ""
echo "所有导入测试通过！"
"@

ssh "$ServerUser@$ServerIP" $ImportTestCommand

# 步骤 7: 运行功能测试
Write-Header "步骤 7: 运行功能测试"
$FunctionTestCommand = @"
cd $ProjectDir
export PYTHONPATH="$ProjectDir:`$PYTHONPATH"

echo "运行缓存测试..."
python3 -c "
from utils.cache import MemoryCache
cache = MemoryCache()
cache.set('test', 'value')
assert cache.get('test') == 'value'
print('✅ 缓存功能测试通过')
"

echo "运行性能监控测试..."
python3 -c "
from utils.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor()
report = monitor.get_report()
assert 'metrics' in report
print('✅ 性能监控测试通过')
"

echo ""
echo "所有功能测试通过！"
"@

ssh "$ServerUser@$ServerIP" $FunctionTestCommand

# 步骤 8: 清理 Python 缓存
Write-Header "步骤 8: 清理 Python 缓存"
$CleanCommand = @"
cd $ProjectDir

echo "清理 .pyc 文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Python 缓存已清理"
"@

ssh "$ServerUser@$ServerIP" $CleanCommand

# 步骤 9: 提供重启说明
Write-Header "部署完成！"
Write-Host ""
Write-Success "所有文件已成功部署到 $ServerUser@$ServerIP"
Write-Host ""
Write-Host "📝 下一步操作：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 重启 OpenClaw（如果需要）:"
Write-Host "   ssh $ServerUser@$ServerIP"
Write-Host "   # 找到 OpenClaw 进程并重启"
Write-Host ""
Write-Host "2. 验证智能编排功能:"
Write-Host "   在 OpenClaw 中调用智能测试编排技能"
Write-Host ""
Write-Host "3. 检查日志:"
Write-Host "   tail -f ~/.openclaw/logs/openclaw.log"
Write-Host ""
Write-Host "4. 运行完整测试（可选）:"
Write-Host "   ssh $ServerUser@$ServerIP"
Write-Host "   cd $ProjectDir"
Write-Host "   python3 test/test_phase3_optimization.py"
Write-Host ""
Write-Host "📊 备份位置:" -ForegroundColor Cyan
Write-Host "   $ProjectDir/$BackupDir"
Write-Host ""
Write-Host "🔄 如需回滚:" -ForegroundColor Yellow
Write-Host "   ssh $ServerUser@$ServerIP"
Write-Host "   cd $ProjectDir"
Write-Host "   cp $BackupDir/utils/*.py utils/"
Write-Host "   cp $BackupDir/adapters/*.py adapters/"
Write-Host "   cp $BackupDir/core/*.py core/"
Write-Host ""
Write-Success "部署成功！"
