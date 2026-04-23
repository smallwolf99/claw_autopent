# Subfinder API Key 配置指南

## 配置文件位置

| 系统 | 路径 |
|------|------|
| Linux/macOS | `~/.config/subfinder/provider-config.yaml` |
| Windows | `%USERPROFILE%\.config\subfinder\provider-config.yaml` |

若文件不存在，运行一次 `subfinder -d example.com` 会自动生成模板。

## 配置文件格式

```yaml
# ~/.config/subfinder/provider-config.yaml

binaryedge:
  - 0bf8919b-aab9-42e4-9574-d3b639324597
  - ac244e2f-b635-4581-878a-33f4e79a2c13

certspotter: []

censys:
  - ac244e2f-b635-4581-878a-33f4e79a2c13:dd510d6e-1b6e-4655-83f6-f347b363def9

chaos:
  - d23a554b-1522-4563-af1f-9c0ab97f5718

dnsdumpster: []

dnsrepo: []

fofa:
  - aaa@example.com:secret

fullhunt:
  - d23a554b-1522-4563-af1f-9c0ab97f5718

github:
  - ghp_sampletoken123456789012345678901234
  - ghp_anothersampletoken1234567890123456

hunter:
  - secret

intelx:
  - 2.intelx.io:00000000-1111-2222-3333-444444444444

passivetotal:
  - sample@email.com:sample_api_key

recon_dev:
  - secret

robtex: []

securitytrails:
  - d23a554b-1522-4563-af1f-9c0ab97f5718

shodan:
  - AAAAClHS4APCKDyFYF5AdZpGwqCcbTEe

spyse:
  - d23a554b-1522-4563-af1f-9c0ab97f5718

urlscan: []

virustotal:
  - fe244e2f-b635-4581-878a-33f4e79a2c13

whoisxmlapi:
  - at_SAMPLE_KEY

zoomeye:
  - zoomeye@example.com:password
```

## 各服务免费 API Key 申请地址

| 服务 | 申请地址 | 免费额度 |
|------|----------|----------|
| **SecurityTrails** | https://securitytrails.com/ | 50 次/月 |
| **VirusTotal** | https://www.virustotal.com/gui/my-apikey | 500 次/天 |
| **Shodan** | https://account.shodan.io/ | 有限免费 |
| **Censys** | https://censys.io/register | 250 次/月 |
| **Hunter** | https://hunter.how/ | 有免费套餐 |
| **GitHub** | https://github.com/settings/tokens | 较高限额（只需 `public_repo` 权限） |
| **Chaos** | https://chaos.projectdiscovery.io/ | 邀请制 |
| **BinaryEdge** | https://app.binaryedge.io/ | 有免费套餐 |
| **FullHunt** | https://fullhunt.io/ | 有免费套餐 |
| **IntelX** | https://intelx.io/account?tab=developer | 有免费套餐 |
| **WhoisXMLAPI** | https://user.whoisxmlapi.com/ | 500 次/月 |
| **URLScan** | https://urlscan.io/user/signup | 免费 |

## 快速配置（环境变量方式）

某些场景也可通过环境变量注入（无需修改配置文件）：

```bash
export SUBFINDER_VIRUSTOTAL_API_KEY="your-key"
export SUBFINDER_SHODAN_API_KEY="your-key"
export SUBFINDER_GITHUB_TOKEN="ghp_yourtoken"
```

## 验证 API Key 是否生效

```bash
# 查看当前加载的数据源数量
subfinder -d example.com -v 2>&1 | grep "Using source"

# 列出所有可用数据源
subfinder -ls
```

> 💡 **建议优先配置**：GitHub Token（免费且贡献最大）、SecurityTrails、VirusTotal。这三个数据源配置好后，枚举覆盖率可提升 3-5 倍。
