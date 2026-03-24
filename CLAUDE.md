# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

JAR Tools 是一个用于帮助 FineReport (FR) / FineBI (BI) 开发人员下载和替换 JAR 包的工具集。支持从阿里云 OSS 下载指定版本的 JAR 包，并自动替换到本地工程目录。

## 运行方式

### 直接运行脚本（无需打包）

```bash
# Windows（交互式）
python Jar_Tools.py

# macOS（交互式）
python3 Jar_Tools_mac.py

# macOS（自动化，通过 JSON 配置）
python3 open_mac.py <config.json> [only_start_server]

# Windows（自动化，通过 JSON 配置）
python open.py <config.json> [only_start_server]

# 通过 oss2 SDK 下载单个文件
python download_oss.py <oss路径> <本地路径>
```

### 安装依赖

```bash
pip3 install requests pyinstaller   # macOS
pip install requests oss2 pywin32 psutil   # Windows（open.py 需要）
```

### 打包成可执行文件

```bash
# macOS 打包
bash build_mac.sh
# 或手动执行
pyinstaller Jar_Tools_mac.spec --clean --noconfirm

# Windows 打包
pyinstaller Jar_Tools.spec --clean --noconfirm
```

打包产物在 `dist/` 目录下。

## 架构说明

项目包含两套脚本，分别针对 Windows 和 macOS：

| 文件 | 平台 | 用途 |
|------|------|------|
| `Jar_Tools.py` | Windows | 交互式命令行：选择产品/版本/分支，下载并替换 JAR |
| `Jar_Tools_mac.py` | macOS | 同上，macOS 版，增加了下载进度显示和 BRANCH_MAP 精细控制 |
| `open.py` | Windows | 自动化：读取 JSON 配置，下载 JAR，停服/解压/替换/重启 |
| `open_mac.py` | macOS | 同上，macOS 版，用 HTTP 直接下载代替 oss2 SDK |
| `download_oss.py` | Windows | 通过 oss2 SDK 下载单个 OSS 文件，GUI 引导配置 AccessKey |
| `Jar_Tools.spec` | Windows | PyInstaller 打包配置 |
| `Jar_Tools_mac.spec` | macOS | PyInstaller 打包配置，生成 .app bundle |

### 核心数据结构

JAR URL 以 `JAR_URLS[product][version][branch]` 三层嵌套字典存储，产品为 `FR`/`BI`，版本为 `11.0`/`10.0`/`6.0`，分支为 `feature`/`release`/`final`/`persist`/`XC`。

`Jar_Tools_mac.py` 还额外维护了 `BRANCH_MAP`（按 `(product, version)` 元组限制可用分支列表），避免用户选择不存在的组合。

### Windows vs macOS 差异

- `open.py` 依赖 `win32api`/`win32process`（pywin32）启动进程，macOS 版 `open_mac.py` 改用 `subprocess.Popen`
- `open.py` 通过 oss2 SDK 鉴权下载，`open_mac.py` 直接用 HTTP 公网地址下载
- `download_oss.py` 使用 tkinter GUI 引导配置 OSS AccessKey（环境变量 `OSS_KEY_ID` / `OSS_KEY_SECRET`）

### open.py / open_mac.py 的 JSON 配置字段

关键字段：`服务器名字`、`服务器端口号`、`jar下载目录`、`jar解压目录`、`服务器webroot地址`、`BIexe文件路径`、`jar日期(默认下载最新)`、`jar分支(默认release)`、`服务器版本号`、`只下载jar(默认否)`、`工程类型(bi或fr)`、`FRtomcat路径`、`只重启工程(默认否)`、`微信webhook`（仅 mac 版支持该字段）。
