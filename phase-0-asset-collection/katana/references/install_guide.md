# Katana 安装指南

## 快速一键安装（推荐）

```bash
# 在 skill 目录下执行
python scripts/auto_install.py
```

该脚本自动完成：下载 → 解压 → PATH 配置 → 验证版本。

---

## 方式一：预编译二进制（手动）

### Linux / macOS

```bash
# 获取最新版本号
VERSION=$(curl -s https://api.github.com/repos/projectdiscovery/katana/releases/latest | grep tag_name | cut -d '"' -f4)
# 下载（amd64 示例）
wget "https://github.com/projectdiscovery/katana/releases/download/${VERSION}/katana_${VERSION#v}_linux_amd64.zip"
unzip katana_*.zip
chmod +x katana
mv katana /usr/local/bin/
katana -version
```

### Windows

1. 访问 https://github.com/projectdiscovery/katana/releases/latest
2. 下载 `katana_<版本>_windows_amd64.zip`
3. 解压，将 `katana.exe` 放入 `C:\Users\<用户名>\bin\` 或 `C:\Windows\System32\`
4. 验证：`katana -version`

---

## 方式二：Go 安装（需要 Go 1.21+）

```bash
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
```

> 二进制位于 `$GOPATH/bin/katana`，确保该目录在 PATH 中。

---

## 方式三：Homebrew（macOS）

```bash
brew install katana
```

---

## 方式四：Docker

```bash
# 拉取镜像
docker pull projectdiscovery/katana:latest

# 运行（挂载当前目录）
docker run --rm -it -v $(pwd):/tmp projectdiscovery/katana:latest \
  -u https://example.com -silent -o /tmp/results.jsonl
```

---

## 方式五：pdtm（ProjectDiscovery 工具管理器）

```bash
go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest
pdtm -install katana
```

---

## 国内镜像加速下载（无法直连 GitHub 时）

### Windows PowerShell

```powershell
$version = "v1.1.0"
$base = "https://ghfast.top/https://github.com/projectdiscovery/katana/releases/download"
$url = "$base/$version/katana_${version#v}_windows_amd64.zip"
$out = "$env:TEMP\katana.zip"
$installDir = "$env:USERPROFILE\bin"
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
(New-Object System.Net.WebClient).DownloadFile($url, $out)
Expand-Archive -Path $out -DestinationPath $installDir -Force
# 验证
& "$installDir\katana.exe" -version
```

### Linux / macOS

```bash
VERSION="v1.1.0"
MIRROR="https://ghfast.top"
wget "${MIRROR}/https://github.com/projectdiscovery/katana/releases/download/${VERSION}/katana_${VERSION#v}_linux_amd64.zip"
unzip katana_*.zip
chmod +x katana
sudo mv katana /usr/local/bin/
```

---

## 验证安装

```bash
katana -version
# 预期输出：katana v1.x.x
```

## 配置 PATH

安装后确保 katana 在 PATH 中（见 `scripts/add_to_path.py`）。

## 依赖说明

- **非无头模式**：仅依赖网络，无需额外依赖
- **无头模式（`hl`）**：建议安装 Chrome，Katana 自带无头 Chromium（无需手动安装）
  - 若需要本地 Chrome：安装 Google Chrome 后使用 `-sc` / `-scp` 参数指向 Chrome 可执行文件
