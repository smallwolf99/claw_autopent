# 靶场测试说明

## 🎯 测试目标

**Altoro Mutual Bank** - `http://demo.testfire.net`

这是一个专门用于安全测试的漏洞演示站点，包含多种常见的 Web 漏洞。

---

## ⚠️ 重要声明

### ✅ 合法测试目标

- **demo.testfire.net** 是 IBM Security 提供的**官方漏洞演示站点**
- 专门用于安全工具测试和学习
- **可以合法进行安全测试**
- 无需授权即可测试

### ❌ 禁止行为

- ❌ 不要测试非授权目标
- ❌ 不要对生产环境使用真实攻击
- ❌ 不要滥用测试工具

---

## 📊 Altoro Mutual 已知漏洞

这个靶场包含以下典型漏洞：

### 高危漏洞

1. **SQL 注入**
   - 登录表单
   - 搜索功能
   - 账户查询

2. **XSS（跨站脚本）**
   - 反馈表单
   - 评论功能
   - 搜索参数

3. **命令注入**
   - 部分管理功能

### 中危漏洞

4. **路径遍历**
   - 文件下载功能

5. **CSRF**
   - 转账功能
   - 密码修改

6. **弱密码策略**
   - 默认账户：`admin/admin`

---

## 🚀 快速测试

### 在本地运行（如果已安装工具）

```bash
cd d:\TRAE\advanced-pentester-v1.2\intelligent-test-orchestrator

# 运行测试
python test/test_phase2_phase3_real.py
```

---

### 上传到服务器

```bash
# 上传测试脚本
scp test/test_phase2_phase3_real.py ubuntu@119.45.255.144:/home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator/test/

# SSH 登录服务器
ssh ubuntu@119.45.255.144

# 运行测试
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

---

## ✅ 预期结果

### Phase-2 漏洞检测

**预期发现的漏洞：**

```
📊 测试结果:
  • 发现漏洞数：10-30
  • 耗时：2-5 分钟

📋 漏洞详情:

  [1] SQL Injection in Login
      严重程度：HIGH
      检测工具：sqlmap
      置信度：95%
      位置：/do/login

  [2] XSS in Feedback Form
      严重程度：MEDIUM
      检测工具：nuclei
      置信度：90%
      位置：/do/feedback

  [3] Path Traversal
      严重程度：HIGH
      检测工具：nikto
      置信度：88%
      位置：/download?file=...

  [4] CSRF in Transfer
      严重程度：MEDIUM
      检测工具：zap
      置信度：85%
      位置：/do/transfer

  ...

✅ 验证结果:
  ✅ 使用的工具：nuclei, nikto, zap, sqlmap
  ✅ 检测到 15 个漏洞
```

---

### Phase-3 漏洞验证

```
📊 验证结果:
  • 验证漏洞数：15
  • 已确认：12
  • 误报：3
  • 耗时：1-3 分钟

✅ 验证总结:
  • 验证通过率：12/15 (80.0%)
  ✅ 成功验证 12 个真实漏洞
```

---

## 🔍 验证方法

### 手动验证（推荐）

测试完成后，可以手动验证发现的漏洞：

#### 1. SQL 注入验证

```
访问：http://demo.testfire.net/
尝试登录：
用户名：admin' OR '1'='1
密码：anything

如果成功登录，说明存在 SQL 注入
```

---

#### 2. XSS 验证

```
访问：http://demo.testfire.net/do/feedback
提交反馈：
内容：<script>alert('XSS')</script>

如果弹出 alert，说明存在 XSS
```

---

#### 3. 路径遍历验证

```
访问：http://demo.testfire.net/download?file=../../../../etc/passwd

如果显示 /etc/passwd 内容，说明存在路径遍历
```

---

## 📊 性能基准

### 不同工具的预期时间

| 工具 | 预期时间 | 说明 |
|------|---------|------|
| **Nuclei** | 1-3 分钟 | 模板扫描 |
| **Nikto** | 2-5 分钟 | Web 漏洞扫描 |
| **ZAP-CLI** | 3-10 分钟 | 全栈扫描 |
| **SQLMap** | 2-5 分钟 | SQL 注入检测 |
| **Afrog** | 1-2 分钟 | PoC 验证 |

**总耗时：** 5-15 分钟（并发执行）

---

## 🛠️ 故障排查

### 问题 1: 目标不可达

**症状：**
```
❌ 连接超时
```

**解决：**
```bash
# 检查网络连通性
ping demo.testfire.net
curl -I http://demo.testfire.net

# 如果确实不可达，更换测试目标
# 编辑 test_phase2_phase3_real.py
```

---

### 问题 2: 工具执行失败

**症状：**
```
❌ Nuclei 调用失败
```

**解决：**
```bash
# 检查工具是否安装
which nuclei nikto zap-cli sqlmap

# 安装缺失的工具
sudo apt install nikto
pip3 install zap-cli
```

---

### 问题 3: 扫描结果为空

**症状：**
```
ℹ️  未检测到漏洞
```

**解决：**
```bash
# 1. 检查目标是否可达
curl http://demo.testfire.net

# 2. 手动测试工具
nuclei -u http://demo.testfire.net
nikto -h http://demo.testfire.net

# 3. 增加扫描时间
# 编辑 phase2_adapter_real.py，增加 timeout 参数
```

---

## 🎯 测试建议

### 1. 使用代理（可选）

```bash
# 如果需要代理
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080

# 运行测试
python3 test/test_phase2_phase3_real.py
```

---

### 2. 限制扫描范围

```python
# 在测试脚本中指定工具
test_strategy = {
    'tools': ['nuclei', 'nikto'],  # 只使用部分工具
    'timeout': 300
}

vulnerabilities = await adapter.detect(test_assets, test_strategy)
```

---

### 3. 保存测试记录

```bash
# 保存完整输出
python3 test/test_phase2_phase3_real.py 2>&1 | tee testfire_test.log

# 分析结果
grep -E "✅|❌|⚠️" testfire_test.log
```

---

## 📚 相关资源

### Altoro Mutual 文档

- 📖 [官方介绍](https://github.com/Altoro/AltoroJ)
- 📖 [漏洞列表](https://github.com/Altoro/AltoroJ#vulnerabilities)
- 📖 [使用指南](http://demo.testfire.net/)

---

### 其他测试靶场

如果 demo.testfire.net 不可用，可以测试：

1. **OWASP Juice Shop**
   - URL: https://juice-shop.herokuapp.com/
   - 类型：现代 Web 应用漏洞

2. **bWAPP**
   - URL: 需要本地部署
   - 类型：PHP 漏洞应用

3. **DVWA**
   - URL: 需要本地部署
   - 类型：PHP 漏洞应用

---

## 🔧 自定义测试目标

### 修改测试脚本

```python
# 编辑 test/test_phase2_phase3_real.py

# 修改 test_assets
test_assets = [
    {
        "type": "web",
        "url": "http://your-target.com",  # 你的目标
        "host": "your-target.com",
        "description": "自定义测试目标"
    }
]
```

---

### 注意事项

- ✅ 确保有合法授权
- ✅ 使用自己的测试环境
- ✅ 遵守法律法规
- ✅ 不要测试未授权目标

---

## 📊 测试结果分析

### 成功标志

- ✅ 检测到 10+ 个漏洞
- ✅ 包含 SQL 注入、XSS 等高危漏洞
- ✅ 多个工具都有发现
- ✅ 验证通过率 > 60%
- ✅ 耗时 5-15 分钟

---

### 改进建议

如果结果不理想：

1. **增加扫描时间**
   ```python
   # phase2_adapter_real.py
   timeout=600  # 增加到 10 分钟
   ```

2. **调整工具参数**
   ```python
   # 使用更激进的扫描模式
   cmd = f"nuclei -u {target} -json -silent -timeout 30"
   ```

3. **添加更多工具**
   ```python
   tools = ['nuclei', 'nikto', 'zap', 'sqlmap', 'afrog']
   ```

---

## 🎓 学习资源

### 漏洞详解

- 📖 [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- 📖 [SQL 注入详解](https://owasp.org/www-community/attacks/SQL_Injection)
- 📖 [XSS 详解](https://owasp.org/www-community/attacks/xss/)

---

### 工具文档

- 📖 [Nuclei 文档](https://nuclei.projectdiscovery.io/)
- 📖 [Nikto 文档](https://github.com/sullo/nikto)
- 📖 [ZAP 文档](https://www.zaproxy.org/docs/)
- 📖 [SQLMap 文档](https://sqlmap.org/)

---

**开始测试吧！** 🚀

```bash
cd /home/ubuntu/.openclaw/workspace/skills/intelligent-test-orchestrator
python3 test/test_phase2_phase3_real.py
```

**预期：** 发现 10-30 个漏洞，耗时 5-15 分钟
