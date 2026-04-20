# Subfinder 支持的数据源列表

## 总览

截至 Subfinder v2，共支持 **40+ 被动数据源**。以下为完整列表及说明：

| 数据源 | 是否需要 API Key | 类别 |
|--------|----------------|------|
| alienvault | ❌ 免费 | 威胁情报 |
| anubis | ❌ 免费 | DNS 被动数据库 |
| bevigil | ✅ 需要 | 移动端安全 |
| binaryedge | ✅ 需要 | 网络扫描 |
| bufferover | ❌ 免费 | DNS 汇聚 |
| c99 | ✅ 需要 | 综合 |
| censys | ✅ 需要 | 证书透明度 + 扫描 |
| certspotter | ❌ 免费（有限） | 证书透明度 |
| chaos | ✅ 需要（邀请制） | ProjectDiscovery 数据集 |
| chinaz | ❌ 免费 | 中文域名工具 |
| crtsh | ❌ 免费 | 证书透明度 |
| digitorus | ❌ 免费 | 证书 |
| dnsdumpster | ❌ 免费（有限） | DNS 搜索 |
| dnsrepo | ❌ 免费 | DNS 数据库 |
| dnsdb | ✅ 需要 | 被动 DNS |
| fofa | ✅ 需要 | 资产测绘（中国） |
| fullhunt | ✅ 需要 | 攻击面管理 |
| github | ✅ 需要（GitHub Token） | 代码搜索 |
| hackertarget | ❌ 免费（有限） | DNS 工具 |
| hunter | ✅ 需要 | 资产测绘（中国） |
| intelx | ✅ 需要 | 深网搜索 |
| leakix | ❌ 免费（有限） | 泄露数据 |
| netlas | ✅ 需要 | 互联网扫描 |
| onyphe | ✅ 需要 | 网络流量 |
| passivetotal | ✅ 需要 | 被动 DNS |
| quake360 | ✅ 需要 | 资产测绘（中国 360） |
| rapiddns | ❌ 免费 | DNS 查询 |
| recon_dev | ✅ 需要 | 综合 |
| robtex | ❌ 免费 | DNS 工具 |
| securitytrails | ✅ 需要 | DNS + WHOIS |
| shodan | ✅ 需要 | 互联网扫描 |
| sitedossier | ❌ 免费 | Web 档案 |
| spyse | ✅ 需要 | 网络情报 |
| threatbook | ✅ 需要 | 微步在线（中国） |
| urlscan | ✅ 需要（可免费） | URL 扫描 |
| virustotal | ✅ 需要 | 病毒扫描 / DNS |
| whoisxmlapi | ✅ 需要 | WHOIS 数据 |
| zoomeye | ✅ 需要 | 资产测绘（中国钟馗之眼） |
| zoomeyeapi | ✅ 需要 | ZoomEye API v2 |

## 查看可用数据源命令

```bash
# 列出所有支持的数据源
subfinder -ls

# 只使用特定数据源（逗号分隔）
subfinder -d example.com -s censys,shodan,virustotal,github

# 排除指定数据源
subfinder -d example.com -es fofa,zoomeye
```

## 中国用户推荐数据源

针对中国境内企业的子域名枚举，以下数据源效果更好：

| 数据源 | 特点 |
|--------|------|
| **fofa** | 覆盖国内 IP 较广 |
| **hunter** | 鹰图平台，国内资产丰富 |
| **quake360** | 360 网络空间测绘 |
| **zoomeye** | 钟馗之眼，老牌测绘平台 |
| **threatbook** | 微步在线，含威胁情报 |
| **chinaz** | 站长工具，适合国内域名 |

## 无需 API Key 的核心免费数据源

以下数据源无需任何配置即可使用：

- `crtsh` - 证书透明度日志（推荐，覆盖广）
- `alienvault` - OTX 威胁情报
- `anubis` - 被动 DNS 数据库
- `hackertarget` - DNS 查询工具
- `dnsdumpster` - 可视化 DNS 映射
- `rapiddns` - 快速 DNS 查询
- `robtex` - DNS 和网络工具
- `sitedossier` - 站点档案
