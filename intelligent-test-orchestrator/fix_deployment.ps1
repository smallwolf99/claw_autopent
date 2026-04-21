# 智能测试编排器 - 一键修复部署脚本
# 问题：部署后 OpenClaw 仍使用旧版本
# 解决：完全重新部署并重启 OpenClaw

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  智能测试编排器 - 一键修复部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  此脚本将：" -ForegroundColor Yellow
Write-Host "  1. 删除服务器上的旧版本" -ForegroundColor White
Write-Host "  2. 重新上传新版本" -ForegroundColor White
Write-Host "  3. 安装依赖" -ForegroundColor White
Write-Host "  4. 重启 OpenClaw" -ForegroundColor White
Write-Host ""
Write-Host "📦 目标服务器：119.45.255.144" -ForegroundColor Green
Write-Host "👤 用户：ubuntu" -ForegroundColor Green
Write-Host ""

# 确认
$confirm = Read-Host "是否继续？(y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "❌ 已取消" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📤 步骤 1/5: 删除服务器上的旧版本..." -ForegroundColor Yellow
ssh ubuntu@119.45.255.144 "rm -rf /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator"
Write-Host "✅ 旧版本已删除" -ForegroundColor Green
Write-Host ""

Write-Host "📤 步骤 2/5: 上传新版本到服务器..." -ForegroundColor Yellow
scp -r intelligent-test-orchestrator/ ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 代码上传失败" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 代码上传完成" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 步骤 3/5: 安装依赖..." -ForegroundColor Yellow
$install_commands = @'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "  • 安装 Python 依赖..."
pip3 install -r requirements.txt
echo "✅ 依赖安装完成"
'@

ssh ubuntu@119.45.255.144 $install_commands
Write-Host ""

Write-Host "🔍 步骤 4/5: 验证代码已更新..." -ForegroundColor Yellow
$verify_commands = @'
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
echo "=== 检查 SQLMap 集成 ==="
grep -n "sqlmap" adapters/phase2_adapter.py | Select-Object -First 3
echo ""
echo "=== 检查 ZAP 集成 ==="
grep -n "zap" adapters/phase2_adapter.py | Select-Object -First 3
echo ""
echo "=== 检查工具注册 ==="
grep -A 6 "self.tools = {" adapters/phase2_adapter.py
'@

ssh ubuntu@119.45.255.144 $verify_commands
Write-Host ""

Write-Host "🔄 步骤 5/5: 重启 OpenClaw..." -ForegroundColor Yellow
ssh ubuntu@119.45.255.144 "pm2 restart openclaw"
Write-Host "✅ OpenClaw 已重启" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  🎉 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏰ 请等待 2 分钟让 OpenClaw 完全重启" -ForegroundColor Yellow
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1. 在飞书中测试：帮我测试 http://demo.test.com" -ForegroundColor White
Write-Host "2. 查看日志：ssh ubuntu@119.45.255.144 'tail -f /home/ubuntu/.openclaw/logs/openclaw.log'" -ForegroundColor White
Write-Host ""
Write-Host "预期日志输出：" -ForegroundColor Cyan
Write-Host "  • Phase-2 漏洞检测适配器初始化完成（集成 ZAP-CLI + SQLMap）" -ForegroundColor White
Write-Host "  • 调用 SQLMap: http://..." -ForegroundColor White
Write-Host "  • 调用 ZAP-CLI: http://..." -ForegroundColor White
Write-Host ""
