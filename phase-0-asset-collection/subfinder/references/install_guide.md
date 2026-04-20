# Subfinder 安装指南

## 方式一：预编译二进制（推荐，最快）

### Linux / macOS

```bash
# 下载最新版本（以 Linux amd64 为例）
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip
unzip subfinder_linux_amd64.zip
sudo mv subfinder /usr/local/bin/
subfinder -version
```

```bash
# macOS（Intel）
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_macos_amd64.zip
unzip subfinder_macos_amd64.zip
sudo mv subfinder /usr/local/bin/
```

```bash
# macOS（Apple Silicon M1/M2）
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_macos_arm64.zip
unzip subfinder_macos_arm64.zip
sudo mv subfinder /usr/local/bin/
```

### Windows

1. 访问 [Releases 页面](https://github.com/projectdiscovery/subfinder/releases/latest)
2. 下载 `subfinder_windows_amd64.zip`
3. 解压后将 `subfinder.exe` 放入系统 PATH（例如 `C:\Users\<用户名>\bin\` 或 `C:\Windows\System32\`）
4. 打开新终端验证：`subfinder -version`

### 国内镜像加速下载（无法直连 GitHub 时使用）

```powershell
# Windows PowerShell - 通过 ghfast.top 镜像
$version = "v2.13.0"
$url = "https://ghfast.top/https://github.com/projectdiscovery/subfinder/releases/download/$version/subfinder_2.13.0_windows_amd64.zip"
$out = "$env:TEMP\subfinder.zip"
$installDir = "C:\Users\$env:USERNAME\bin"
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
(New-Object System.Net.WebClient).DownloadFile($url, $out)
Expand-Archive -Path $out -DestinationPath $installDir -Force
# 将 $installDir 加入 PATH（当前会话）
$env:PATH = "$installDir;" + $env:PATH
subfinder -version
```

```bash
# Linux/macOS - 通过 ghfast.top 镜像
VERSION="v2.13.0"
wget "https://ghfast.top/https://github.com/projectdiscovery/subfinder/releases/download/${VERSION}/subfinder_linux_amd64.zip"
unzip subfinder_linux_amd64.zip
sudo mv subfinder /usr/local/bin/
```



## 方式二：Go 安装（需要 Go 1.21+）

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

> Go 安装后二进制位于 `$GOPATH/bin/subfinder`，确保该目录在 PATH 中。

## 方式三：Homebrew（macOS）

```bash
brew install subfinder
```

## 方式四：Docker

```bash
# 拉取镜像
docker pull projectdiscovery/subfinder:latest

# 运行（挂载当前目录）
docker run --rm -it -v $(pwd):/tmp projectdiscovery/subfinder:latest -d example.com -o /tmp/output.txt
```

## 方式五：pdtm（ProjectDiscovery 工具管理器）

```bash
# 安装 pdtm
go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest

# 通过 pdtm 安装 subfinder
pdtm -install subfinder
```

## 验证安装

```bash
subfinder -version
# 预期输出：subfinder v2.x.x
```

## 配置文件位置

Subfinder 的配置文件（含 API Key）默认位于：

| 系统 | 路径 |
|------|------|
| Linux/macOS | `~/.config/subfinder/provider-config.yaml` |
| Windows | `%USERPROFILE%\.config\subfinder\provider-config.yaml` |

详见 `api_keys_setup.md`。
