# 1-JARTOOL

JAR 包管理工具，用于 FineReport (FR) / FineBI (BI) 开发人员下载和替换 JAR 包。
支持从阿里云 OSS 下载指定版本的 JAR 包，并自动替换到本地工程目录。

## 目录结构

```
1-JARTOOL/
├── windows/
│   ├── jar_tools.py          # Windows 交互式 JAR 下载替换工具
│   ├── open.py               # Windows 自动化脚本（读取 JSON 配置）
│   ├── download_oss.py       # 通过 oss2 SDK 下载单个 OSS 文件
│   ├── Jar_Tools.spec        # Windows PyInstaller 打包配置
│   ├── Jar_Tools.exe         # Windows 可执行文件（打包产物）
│   └── requirements.txt      # Windows 依赖
├── macos/
│   ├── jar_tools_mac.py      # macOS 交互式 JAR 下载替换工具
│   ├── open_mac.py           # macOS 自动化脚本（读取 JSON 配置）
│   ├── Jar_Tools_mac.spec    # macOS PyInstaller 打包配置
│   ├── build_mac.sh          # macOS 一键打包脚本
│   └── requirements.txt      # macOS 依赖
└── README.md
```

## 使用方式

### Windows（交互式）

```bash
cd windows
pip install -r requirements.txt
python jar_tools.py
```

### macOS（交互式）

```bash
cd macos
pip3 install -r requirements.txt
python3 jar_tools_mac.py
```

### Windows（自动化，通过 JSON 配置）

```bash
cd windows
python open.py <config.json> [only_start_server]
```

### macOS（自动化，通过 JSON 配置）

```bash
cd macos
python3 open_mac.py <config.json> [only_start_server]
```

### OSS 单文件下载（Windows 专用）

```bash
cd windows
python download_oss.py <oss路径> <本地路径>
```

首次运行会弹出 GUI 引导配置阿里云 AccessKey（保存为环境变量 `OSS_KEY_ID` / `OSS_KEY_SECRET`）。

## 打包

### macOS

```bash
bash macos/build_mac.sh
# 产物：macos/Jar_Tools 和 macos/Jar_Tools.app
```

### Windows

```bash
cd windows
pyinstaller Jar_Tools.spec --clean --noconfirm --distpath .
# 产物：windows/Jar_Tools.exe
```

## 依赖安装

```bash
# macOS
pip3 install -r macos/requirements.txt

# Windows
pip install -r windows/requirements.txt
```
