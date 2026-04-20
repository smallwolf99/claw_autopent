# 智能测试编排器 - 部署到 OpenClaw 服务器 (PowerShell 版本)
# 服务器：119.45.255.144
# 用户：ubuntu
# 路径：/home/ubuntu/.openclaw/workspace/skills

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  智能测试编排器 - 部署脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 目标服务器：119.45.255.144" -ForegroundColor Green
Write-Host "👤 用户：ubuntu" -ForegroundColor Green
Write-Host "📁 部署路径：/home/ubuntu/.openclaw/workspace/skills" -ForegroundColor Green
Write-Host ""

# 步骤 1: 上传代码
Write-Host "📤 步骤 1/4: 上传代码到服务器..." -ForegroundColor Yellow
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 代码上传失败" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 代码上传完成" -ForegroundColor Green
Write-Host ""

# 步骤 2: SSH 连接并安装依赖
Write-Host "🔧 步骤 2/4: 安装依赖..." -ForegroundColor Yellow
$ssh_commands = @'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 安装 Python 依赖..."
pip3 install -r requirements.txt
echo "✅ 依赖安装完成"
'@

ssh ubuntu@119.45.255.144 $ssh_commands
Write-Host ""

# 步骤 3: 验证部署
Write-Host "🔍 步骤 3/4: 验证部署..." -ForegroundColor Yellow
$verify_commands = @'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 检查文件完整性..."
ls -la manifest.json main.py SKILL.md
echo "  • 检查目录结构..."
ls -d core/ adapters/
echo "✅ 文件结构验证完成"
'@

ssh ubuntu@119.45.255.144 $verify_commands
Write-Host ""

# 步骤 4: 测试运行
Write-Host "🧪 步骤 4/4: 测试运行..." -ForegroundColor Yellow
$test_commands = @'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 运行简单测试..."
python3 test_simple.py
echo "✅ 测试完成"
'@

ssh ubuntu@119.45.255.144 $test_commands
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  🎉 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 在飞书中测试：帮我测试 http://demo.test.com" -ForegroundColor White
Write-Host "2. 查看 OpenClaw 日志：ssh ubuntu@119.45.255.144 'tail -f /home/ubuntu/.openclaw/logs/openclaw.log'" -ForegroundColor White
Write-Host ""
