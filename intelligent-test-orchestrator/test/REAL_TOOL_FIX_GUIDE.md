# 🔧 真实工具调用修复指南

## 📋 问题诊断

### 问题现象
- ⚠️ 12 秒完成完整扫描（应该需要 5-30 分钟）
- ⚠️ Nmap 扫描仅用 0.3 秒（正常需要 1-5 分钟）
- ⚠️ 漏洞验证每个 400 毫秒（正常需要 2-30 秒）
- ⚠️ 8 个工具并发但总时间异常短

### 根本原因
**所有工具适配器都在使用模拟数据！**

```python
# ❌ 当前代码（模拟）
async def _call_nmap(self, target: str):
    await asyncio.sleep(0.3)  # 假装在扫描
    return [{"type": "port", "ports": [...]}]  # 返回假数据

# ✅ 应该的代码（真实调用）
async def _call_nmap(self, target: str):
    process = await asyncio.create_subprocess_shell(
        f"nmap -sV -sC {target}",
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    return self._parse_nmap_output(stdout)
```

---

## 🔍 受影响的文件

### Phase-0 资产收集适配器
- 📄 [`adapters/phase0_adapter.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase0_adapter.py)
- ❌ 问题：所有工具调用都是模拟的
- 🔧 修复：创建 `phase0_adapter_real.py`（已创建）

### Phase-2 漏洞检测适配器
- 📄 [`adapters/phase2_adapter.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase2_adapter.py)
- ❌ 问题：Nuclei、Afrog、Nikto、ZAP、SQLMap 都是模拟的
- 🔧 需要创建 `phase2_adapter_real.py`

### Phase-3 漏洞验证适配器
- 📄 [`adapters/phase3_validator.py`](file://d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator\adapters\phase3_validator.py)
- ❌ 问题：漏洞验证是模拟的
- 🔧 需要创建 `phase3_validator_real.py`

---

## 🚀 修复方案

### 方案 1：渐进式替换（推荐）

**优点：**
- ✅ 不影响现有功能
- ✅ 可以逐步验证
- ✅ 出现问题容易回滚

**步骤：**

#### 步骤 1: 创建真实工具调用版本

```bash
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# Phase-0 已创建
# adapters/phase0_adapter_real.py ✅

# 接下来创建 Phase-2 和 Phase-3 的真实版本
```

#### 步骤 2: 修改 main.py 使用真实适配器

```python
# main.py 中修改导入
# from adapters.phase0_adapter import Phase0Adapter  # 旧（模拟）
from adapters.phase0_adapter_real import Phase0Adapter  # 新（真实）
```

#### 步骤 3: 测试真实工具调用

```bash
# 运行测试
python test_simple.py

# 观察日志
# - Nmap 应该运行 1-5 分钟
# - WhatWeb 应该调用真实命令
# - 总时间应该在合理范围（5-30 分钟）
```

---

### 方案 2：混合模式（开发/生产切换）

在配置中添加开关：

```json
{
    "target": "http://example.com",
    "test_mode": "full",
    "use_real_tools": true  // 新增配置项
}
```

修改适配器支持模式切换：

```python
class Phase0Adapter:
    def __init__(self, use_real_tools: bool = False):
        self.use_real_tools = use_real_tools
        
    async def _call_nmap(self, target: str):
        if self.use_real_tools:
            return await self._call_nmap_real(target)
        else:
            return await self._call_nmap_mock(target)
```

---

## 📝 真实工具调用实现

### Phase-0 资产收集（已完成 ✅）

**工具调用示例：**

```python
async def _call_nmap(self, target: str):
    """真实调用 Nmap"""
    cmd = f"nmap -sV -sC -T4 --open -oX - {target}"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    # 解析 XML 输出
    ports = self._parse_nmap_xml(stdout.decode())
    
    return [{"type": "port", "host": target, "ports": ports}]
```

**预期时间：**
- Nmap 快速扫描：1-3 分钟
- WhatWeb 识别：10-30 秒
- Subfinder 子域名：30 秒 -2 分钟
- Httpx 探测：5-15 秒

**总计：** 2-7 分钟（取决于目标）

---

### Phase-2 漏洞检测（待实现）

**需要实现的真实调用：**

#### 1. Nuclei

```python
async def _call_nuclei(self, target: str):
    """真实调用 Nuclei"""
    cmd = f"nuclei -u {target} -json -silent"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await process.communicate()
    
    # 解析 JSON 输出（每行一个漏洞）
    vulnerabilities = []
    for line in stdout.decode().split('\n'):
        if line.strip():
            vuln = json.loads(line)
            vulnerabilities.append(self._normalize_nuclei_vuln(vuln))
    
    return vulnerabilities
```

**预期时间：** 2-10 分钟

---

#### 2. Afrog

```python
async def _call_afrog(self, target: str):
    """真实调用 Afrog"""
    cmd = f"afrog -t {target} -json -silent"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await process.communicate()
    
    # 解析 JSON 输出
    vulnerabilities = self._parse_afrog_output(stdout)
    
    return vulnerabilities
```

**预期时间：** 1-5 分钟

---

#### 3. Nikto

```python
async def _call_nikto(self, target: str):
    """真实调用 Nikto"""
    cmd = f"nikto -h {target} -Format json -output -"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await process.communicate()
    
    # 解析 JSON 输出
    vulnerabilities = self._parse_nikto_output(stdout)
    
    return vulnerabilities
```

**预期时间：** 3-10 分钟

---

#### 4. ZAP-CLI

```python
async def _call_zap(self, target: str):
    """真实调用 ZAP"""
    domain = target.split('//')[-1].split('/')[0]
    
    # 1. 启动 ZAP 扫描
    start_cmd = f"zap-cli quick-scan -s all -o results.json {target}"
    
    process = await asyncio.create_subprocess_shell(
        start_cmd,
        stdout=asyncio.subprocess.PIPE
    )
    
    await process.communicate()
    
    # 2. 读取结果
    if os.path.exists('results.json'):
        with open('results.json', 'r') as f:
            results = json.load(f)
        
        vulnerabilities = self._parse_zap_results(results)
        return vulnerabilities
    
    return []
```

**预期时间：** 5-15 分钟

---

#### 5. SQLMap

```python
async def _call_sqlmap(self, target: str):
    """真实调用 SQLMap"""
    # 初步探测
    cmd = f"sqlmap -u \"{target}\" --batch --level=2 --risk=2 --output-dir=/tmp/sqlmap"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    # 读取结果
    vulnerabilities = self._parse_sqlmap_results('/tmp/sqlmap')
    
    return vulnerabilities
```

**预期时间：** 5-30 分钟（取决于目标）

---

### Phase-3 漏洞验证（待实现）

**真实验证逻辑：**

```python
async def verify_vulnerability(self, vuln: Dict) -> bool:
    """真实验证漏洞"""
    
    if vuln.get('type') == 'sql_injection':
        return await self._verify_sqli(vuln)
    elif vuln.get('type') == 'xss':
        return await self._verify_xss(vuln)
    # ...
    
async def _verify_sqli(self, vuln: Dict) -> bool:
    """验证 SQL 注入"""
    url = vuln.get('url')
    payload = vuln.get('payload')
    
    # 发送真实请求
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}{payload}") as response:
            content = await response.text()
            
            # 检查 SQL 错误信息
            sql_errors = ['SQL syntax', 'MySQL', 'ORA-', 'PostgreSQL']
            for error in sql_errors:
                if error in content:
                    return True
    
    return False
```

**预期时间：** 每个漏洞 2-30 秒

---

## ⚠️ 注意事项

### 1. 工具依赖

确保服务器上安装了所有工具：

```bash
# 检查工具是否安装
which nmap whatweb httpx subfinder nuclei afrog nikto zap-cli sqlmap

# 安装缺失的工具
sudo apt install nmap whatweb
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
# ...
```

### 2. 权限要求

某些工具需要 root 权限：

```bash
# Nmap SYN 扫描需要 root
sudo nmap -sS target

# 或者使用普通用户友好的选项
nmap -sT target  # TCP 连接扫描（不需要 root）
```

### 3. 超时设置

真实扫描可能很慢，需要设置合理超时：

```python
# 设置工具超时
process = await asyncio.wait_for(
    asyncio.create_subprocess_shell(cmd),
    timeout=300  # 5 分钟
)
```

### 4. 资源限制

并发工具会消耗大量资源：

```bash
# 限制并发数
ulimit -u 100  # 限制进程数
ulimit -n 1024  # 限制文件描述符
```

---

## 🧪 测试验证

### 测试步骤

#### 1. 本地快速测试

```bash
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 使用小目标测试
python -c "
import asyncio
from adapters.phase0_adapter_real import Phase0Adapter

async def test():
    adapter = Phase0Adapter()
    assets = await adapter.collect('http://example.com')
    print(f'发现 {len(assets)} 个资产')
    for asset in assets:
        print(f'  - {asset}')

asyncio.run(test())
"
```

**预期输出：**
```
2026-04-21 13:00:00 - Phase-0 资产收集适配器初始化完成（真实工具调用）
2026-04-21 13:00:00 - 开始资产收集：http://example.com
2026-04-21 13:00:00 - 调用 Nmap: http://example.com
2026-04-21 13:00:00 - 执行命令：nmap -sV -sC -T4 --open -oX - http://example.com
...
资产收集完成：发现 3 个资产
```

**预期时间：** 1-3 分钟

---

#### 2. 服务器测试

```bash
# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 进入目录
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator

# 运行完整测试
python test_simple.py

# 观察日志
tail -f /home/ubuntu/.openclaw/logs/openclaw.log
```

**预期日志：**
```
Phase-0 资产收集适配器初始化完成（真实工具调用）
调用 Nmap: http://demo.test.com
执行命令：nmap -sV -sC -T4 --open -oX - http://demo.test.com
...
（等待 2-5 分钟）
...
资产收集完成：发现 6 个资产
```

---

## 📊 预期时间对比

| 阶段 | 模拟模式 | 真实模式 | 说明 |
|------|---------|---------|------|
| **Phase-0 资产收集** | 1-2 秒 | 2-7 分钟 | Nmap 占主要时间 |
| **Phase-1 风险画像** | <1 秒 | <1 秒 | 纯计算，无工具调用 |
| **Phase-2 漏洞检测** | 2-3 秒 | 10-40 分钟 | 5 个工具并发执行 |
| **Phase-3 漏洞验证** | 1-2 秒 | 1-10 分钟 | 取决于漏洞数量 |
| **Phase-4 报告生成** | <1 秒 | <1 秒 | 纯计算 |
| **总计** | **5-10 秒** | **15-60 分钟** | - |

---

## 🎯 下一步行动

### 立即执行（推荐）

1. **测试 Phase-0 真实版本**
   ```bash
   cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator
   python -c "from adapters.phase0_adapter_real import Phase0Adapter; import asyncio; print(asyncio.run(Phase0Adapter().collect('http://example.com')))"
   ```

2. **创建 Phase-2 真实版本**
   - 需要我帮你创建 `phase2_adapter_real.py` 吗？

3. **创建 Phase-3 真实版本**
   - 需要我帮你创建 `phase3_validator_real.py` 吗？

### 可选配置

4. **添加模式切换开关**
   - 在配置中添加 `use_real_tools: true/false`
   - 适配器根据配置选择真实/模拟模式

5. **添加超时和重试机制**
   - 防止工具卡死
   - 失败自动重试

---

## 📞 需要帮助吗？

我可以帮你：

1. ✅ 创建 `phase2_adapter_real.py`（Phase-2 真实工具调用）
2. ✅ 创建 `phase3_validator_real.py`（Phase-3 真实漏洞验证）
3. ✅ 修改 `main.py` 支持模式切换
4. ✅ 添加工具依赖检查脚本
5. ✅ 添加超时和错误处理

请告诉我你想要：
- **立即全部实现**（创建所有真实版本）
- **渐进式实现**（先测试 Phase-0，再逐步实现其他）
- **混合模式**（支持模拟/真实切换）

---

**重要提醒：** 真实工具扫描会产生网络流量，可能对目标系统造成影响。请确保：
- ✅ 你有合法的测试授权
- ✅ 在测试环境中使用
- ✅ 遵守法律法规和公司政策
