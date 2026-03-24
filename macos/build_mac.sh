#!/bin/bash
# build_mac.sh —— macOS 打包脚本
# 用法：bash build_mac.sh

set -e
cd "$(dirname "$0")"

echo "=============================="
echo "  JAR Tools macOS 打包脚本"
echo "=============================="

# 1. 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "错误：未找到 python3，请先安装 Python 3.8+"
    exit 1
fi
echo "Python 版本：$(python3 --version)"

# 2. 安装依赖
echo ""
echo "安装依赖..."
pip3 install --quiet requests pyinstaller

# 3. 打包
echo ""
echo "开始打包..."
pyinstaller Jar_Tools_mac.spec --clean --noconfirm --distpath .

echo ""
echo "=============================="
echo "打包完成！"
echo "  可执行文件：Jar_Tools"
echo "  应用程序包：Jar_Tools.app"
echo "=============================="
