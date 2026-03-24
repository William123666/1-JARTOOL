# coding=utf-8
#!/usr/bin/env python3
"""
open_mac.py —— macOS 版自动换 JAR + 重启服务脚本
用法：python3 open_mac.py <config.json> [only_start_server]

JSON 配置示例：
{
    "服务器名字": "测试BI",
    "服务器端口号": "37799",
    "jar下载目录": "/tmp/",
    "jar解压目录": "/tmp/jar_unzip/",
    "服务器webroot地址": "/opt/finebi/webapps/webroot",
    "BIexe文件路径": "/opt/finebi/bin/start.sh",
    "jar日期(默认下载最新)": "",
    "jar分支(默认release)": "release",
    "服务器版本号": "5.1.x",
    "只下载jar(默认否)": "否",
    "工程类型(bi或fr)": "bi",
    "FRtomcat路径": "/opt/tomcat",
    "只重启工程(默认否)": "否",
    "微信webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
}
"""

import os
import sys
import json
import time
import shutil
import signal
import zipfile
import subprocess
import requests


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def read_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"读取 JSON 失败：{e}")
        return None


def kill_port(port):
    """杀掉占用指定端口的进程（macOS/Linux）"""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGKILL)
                print(f"已终止进程 PID {pid}（端口 {port}）")
    except Exception as e:
        print(f"kill_port 异常：{e}")


def unzip_zip(zip_file, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.extractall(dest_folder)
    print(f"解压完成：{zip_file} → {dest_folder}")


def move_file(src_folder, dest_folder):
    """将 src_folder 下的文件（跳过 designer 子目录）复制到 dest_folder"""
    os.makedirs(dest_folder, exist_ok=True)
    for fname in os.listdir(src_folder):
        if fname == "designer":
            continue
        src = os.path.join(src_folder, fname)
        if os.path.isfile(src):
            shutil.copy(src, dest_folder)
    print(f"JAR 文件已移动到：{dest_folder}")


def send_to_robot(webhook, text):
    if not webhook:
        return
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": text,
            "mentioned_list": ["@all"],
            "mentioned_mobile_list": ["@all"]
        }
    }
    try:
        r = requests.post(webhook, json=data, timeout=10)
        print(f"通知发送结果：{r.text}")
    except Exception as e:
        print(f"通知发送失败：{e}")


def start_bi(exe_path):
    """启动 BI（macOS/Linux：执行 shell 脚本）"""
    if not os.path.isfile(exe_path):
        print(f"BI 启动脚本不存在：{exe_path}")
        return
    os.chmod(exe_path, 0o755)
    popen = subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"BI 进程已启动，PID：{popen.pid}")


def start_tomcat(tomcat_path):
    """启动 Tomcat（macOS/Linux：startup.sh）"""
    startup = os.path.join(tomcat_path, "bin", "startup.sh")
    if not os.path.isfile(startup):
        print(f"Tomcat 启动脚本不存在：{startup}")
        return
    os.chmod(startup, 0o755)
    os.environ['CATALINA_HOME'] = tomcat_path
    popen = subprocess.Popen([startup], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    popen.wait()
    print(f"Tomcat 启动命令已执行")


# ──────────────────────────────────────────────
# OSS 路径拼接（与 open.py 保持一致）
# ──────────────────────────────────────────────

def get_oss_download_url(server_type, server_branch, backup, server_version):
    backup = backup.strip()
    if server_type == 'bi':
        base = f"finebi/{server_version}/{server_branch}"
        if backup:
            return base + f"/backup/{backup}/BI5.1_spider_jar_jdk1.8.zip"
        return base + "/BI5.1_spider_jar_jdk1.8.zip"
    elif server_type == 'fr':
        base = f"finereport/{server_version}/"
        if server_branch == "persist" and backup:
            base += f"stable/backup/{backup}"
        elif server_branch == "persist":
            base += "stable"
        else:
            base += server_branch
        return base + "/finereport11.0_jar_openjdk1.8.zip"
    else:
        raise ValueError(f"未知工程类型：{server_type}")


def download_from_oss(oss_path, local_path):
    """
    通过公网 HTTP 下载（替换 Windows 版的 oss2 SDK）
    OSS bucket：fine-build，Region：oss-cn-shanghai
    """
    url = f"https://fine-build.oss-cn-shanghai.aliyuncs.com/{oss_path}"
    print(f"下载地址：{url}")
    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        downloaded = 0
        os.makedirs(os.path.dirname(local_path) or '.', exist_ok=True)
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        bar = '#' * (pct // 2) + '-' * (50 - pct // 2)
                        print(f"\r[{bar}] {pct}%", end='', flush=True)
        print(f"\n下载完成：{local_path}")
        return True
    except Exception as e:
        print(f"\n下载失败：{e}")
        return False


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法：python3 open_mac.py <config.json> [only_start_server]")
        sys.exit(1)

    jsonpath = sys.argv[1]
    only_start_server = len(sys.argv) >= 3 and sys.argv[2] == 'only_start_server'

    print("读取 JSON 配置中...\n")
    j = read_json_file(jsonpath)
    if j is None:
        print("请输入正确的 JSON 配置文件地址")
        sys.exit(1)

    print(j)

    try:
        server_name       = j["服务器名字"]
        server_port       = j["服务器端口号"]
        jar_download_path = j["jar下载目录"]
        jar_unzip_path    = j["jar解压目录"]
        server_webroot    = j["服务器webroot地址"]
        server_exe_path   = j["BIexe文件路径"]
        server_backup     = j["jar日期(默认下载最新)"]
        server_branch     = j["jar分支(默认release)"]
        server_version    = j["服务器版本号"]
        only_download_jar = j["只下载jar(默认否)"]
        server_type       = j["工程类型(bi或fr)"].strip().lower()
        tomcat_path       = j["FRtomcat路径"]
        webhook           = j.get("微信webhook", "")
        if not only_start_server:
            only_start_server = j.get("只重启工程(默认否)", "否") == "是"
    except KeyError as e:
        print(f"读取 JSON 配置失败，缺少字段：{e}")
        sys.exit(1)

    download_ok = False

    # ── 1. 下载 JAR ──
    if not only_start_server:
        print("开始下载 JAR 包...\n")
        try:
            oss_path   = get_oss_download_url(server_type, server_branch, server_backup, server_version)
            local_zip  = os.path.join(jar_download_path, "temp.zip")
            download_ok = download_from_oss(oss_path, local_zip)
        except Exception as e:
            print(f"JAR 下载失败：{e}")
            sys.exit(1)

    if only_download_jar == "是":
        print("仅下载模式，退出。")
        sys.exit(0)

    is_bi = (server_type == 'bi')

    # ── 2. 停服、解压、替换、重启 ──
    if download_ok or only_start_server:
        print("开始关闭之前的工程...\n")
        kill_port(server_port)

        if download_ok:
            send_to_robot(webhook, f"{server_name} 换 JAR 中")
            print("开始解压 zip 包...\n")
            unzip_zip(local_zip, jar_unzip_path)
            print("开始将 JAR 移动到对应文件夹...\n")
            lib_dest = os.path.join(server_webroot, "WEB-INF", "lib")
            move_file(jar_unzip_path, lib_dest)

        if is_bi:
            try:
                print("开始启动 BI 工程...\n")
                start_bi(server_exe_path)
                time.sleep(90)
                send_to_robot(webhook, f"{server_name} 重启成功")
                print("换 JAR 并重启完成\n")
            except Exception as e:
                print(e)
                send_to_robot(webhook, f"{server_name} 重启失败：{e}")
        else:
            print("开始启动 Tomcat 工程...\n")
            start_tomcat(tomcat_path)
            time.sleep(90)
            send_to_robot(webhook, f"{server_name} 重启成功")
            print("换 JAR 并重启完成\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
