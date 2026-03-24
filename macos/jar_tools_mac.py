# coding=utf-8
import os
import sys
import requests
import shutil
import zipfile

# 定义常量存储JAR文件的URL
JAR_URLS = {
    'FR': {
        '11.0': {
            'feature': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/nightly/finereport11.0_jar_openjdk1.8.zip',
            'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/release/finereport11.0_jar_openjdk1.8.zip',
            'final':   'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/final/finereport11.0_jar_openjdk1.8.zip',
            'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/stable/finereport11.0_jar_openjdk1.8.zip',
            'XC':      'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/XC/finereport11.0_jar_openjdk1.8.zip',
        },
        '10.0': {
            'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/release/finereport10.0_jar_openjdk1.8.zip',
            'final':   'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/final/finereport10.0_jar_openjdk1.8.zip',
            'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/stable/finereport10.0_jar_openjdk1.8.zip',
        }
    },
    'BI': {
        '11.0': {
            'feature': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/nightly/finereport11.0_jar_openjdk1.8.zip',
            'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x/release/BI5.1_spider_jar_jdk1.8.zip',
            'final':   'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x/final/BI5.1_spider_jar_jdk1.8.zip',
        },
        '10.0': {
            'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/release/BI5.1_spider_jar_jdk1.8.zip',
            'final':   'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/final/BI5.1_spider_jar_jdk1.8.zip',
            'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/stable/BI5.1_spider_jar_jdk1.8.zip',
        },
        '6.0': {
            'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/release/BI6.0_spider_jar_jdk1.8.zip',
            'final':   'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/final/BI6.0_spider_jar_jdk1.8.zip',
            'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/stable/BI6.0_spider_jar_jdk1.8.zip',
            'XC':      'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/XC/BI6.0_spider_jar_jdk1.8.zip',
        }
    }
}

# 各产品可用版本与分支映射
VERSION_MAP = {
    'FR': ['11.0', '10.0'],
    'BI': ['11.0', '10.0', '6.0'],
}

BRANCH_MAP = {
    ('FR', '11.0'): ['feature', 'release', 'final', 'persist', 'XC'],
    ('FR', '10.0'): ['release', 'final', 'persist'],
    ('BI', '11.0'): ['feature', 'release', 'final'],
    ('BI', '10.0'): ['release', 'final', 'persist'],
    ('BI', '6.0'):  ['release', 'final', 'persist', 'XC'],
}


def choose_option(options, message):
    """通用选项选择，支持序号输入"""
    while True:
        print(f"\n{message}")
        for idx, opt in enumerate(options, 1):
            print(f"  {idx}. {opt}")
        choice = input("请输入对应序号: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("输入有误，请重新输入有效的序号")


def download_jar(url, save_path="file.zip"):
    """下载 JAR 包（带进度显示）"""
    print(f"\n正在下载 JAR 包，请稍等...")
    print(f"URL: {url}")
    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        bar = '#' * (pct // 2) + '-' * (50 - pct // 2)
                        print(f"\r[{bar}] {pct}%", end='', flush=True)
        print(f"\n下载完成：{save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"\n下载失败：{e}")
        sys.exit(1)


def replace_jar(zip_path="file.zip"):
    """解压并替换 lib 目录中的 JAR 文件"""
    lib_path = input("\n请输入工程 lib 绝对路径: ").strip()
    if not os.path.isdir(lib_path):
        print(f"路径不存在：{lib_path}")
        sys.exit(1)

    print(f"工程 lib 路径：{lib_path}")

    dest_zip = os.path.join(lib_path, "file.zip")
    if os.path.exists(dest_zip):
        os.remove(dest_zip)
    shutil.move(zip_path, dest_zip)

    print("正在解压...")
    with zipfile.ZipFile(dest_zip, 'r') as zf:
        zf.extractall(lib_path)

    # 尝试复制 designer JAR（若存在）
    designer_jar_src = os.path.join(lib_path, "designer", "fine-report-designer-11.0.jar")
    designer_lib = os.path.abspath(os.path.join(lib_path, "../../../../lib"))
    if os.path.isfile(designer_jar_src) and os.path.isdir(designer_lib):
        for fname in os.listdir(designer_lib):
            if fname == "fine-report-designer-11.0.jar":
                shutil.copy(designer_jar_src, designer_lib)
                print(f"Designer JAR 已复制到：{designer_lib}")
                break

    print("JAR 包替换成功！")


def main():
    print("=" * 50)
    print("       JAR Tools for macOS")
    print("=" * 50)

    # 1. 选产品
    project = choose_option(['FR', 'BI'], '请选择需要下载的项目：')

    # 2. 选版本
    versions = VERSION_MAP[project]
    version = choose_option(versions, '请选择需要下载的版本：')

    # 3. 选分支（仅显示该 产品+版本 组合实际存在的分支）
    branches = BRANCH_MAP.get((project, version), ['release', 'final'])
    branch = choose_option(branches, '请选择需要下载的分支：')

    # 4. 获取 URL
    try:
        jar_url = JAR_URLS[project][version][branch]
    except KeyError:
        print(f"不支持的组合：{project} {version} {branch}")
        sys.exit(1)

    # 5. 下载
    zip_path = download_jar(jar_url)

    # 6. 替换
    replace_jar(zip_path)

    input("\n按 Enter 键退出...")


if __name__ == "__main__":
    main()
