import oss2
import sys
import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog


def _set_env_persistent(key, value):
    """将环境变量写入系统（当前进程 + 持久化）"""
    os.environ[key] = value
    system = platform.system()
    if system == 'Windows':
        subprocess.run(['setx', key, value], check=True, capture_output=True)
    elif system in ('Darwin', 'Linux'):
        shell_rc = os.path.expanduser('~/.zshrc' if system == 'Darwin' else '~/.bashrc')
        export_line = f'\nexport {key}="{value}"\n'
        with open(shell_rc, 'a') as f:
            f.write(export_line)


def _gui_config_keys():
    """弹窗引导用户输入并保存环境变量，返回 (key_id, key_secret) 或 None"""
    root = tk.Tk()
    root.withdraw()

    messagebox.showwarning(
        '缺少阿里云 OSS 密钥',
        '未检测到阿里云 OSS 认证信息。\n\n'
        '请在接下来的对话框中输入 AccessKey ID 和 AccessKey Secret。\n'
        '密钥将以系统环境变量的形式保存：\n'
        '  OSS_KEY_ID\n'
        '  OSS_KEY_SECRET'
    )

    key_id = simpledialog.askstring(
        '配置 OSS_KEY_ID',
        '请输入 Alibaba Cloud AccessKey ID：',
        parent=root
    )
    if not key_id or not key_id.strip():
        messagebox.showerror('配置取消', '未输入 AccessKey ID，程序退出。')
        root.destroy()
        return None

    key_secret = simpledialog.askstring(
        '配置 OSS_KEY_SECRET',
        '请输入 Alibaba Cloud AccessKey Secret：',
        show='*',
        parent=root
    )
    if not key_secret or not key_secret.strip():
        messagebox.showerror('配置取消', '未输入 AccessKey Secret，程序退出。')
        root.destroy()
        return None

    try:
        _set_env_persistent('OSS_KEY_ID', key_id.strip())
        _set_env_persistent('OSS_KEY_SECRET', key_secret.strip())
        messagebox.showinfo(
            '配置成功',
            '密钥已保存为系统环境变量。\n'
            '首次配置后重启终端/应用使其全局生效。'
        )
    except Exception as e:
        messagebox.showerror('保存失败', f'写入环境变量时出错：{e}\n本次运行仍将使用已输入的值。')

    root.destroy()
    return key_id.strip(), key_secret.strip()


def get_oss_credentials():
    """获取 OSS 密钥，缺失时弹窗引导配置"""
    key_id = os.environ.get('OSS_KEY_ID', '').strip()
    key_secret = os.environ.get('OSS_KEY_SECRET', '').strip()

    if key_id and key_secret:
        return key_id, key_secret

    result = _gui_config_keys()
    if result is None:
        sys.exit(1)
    return result


class oss(object):
    def __init__(self, ossPath, localPath):
        self.ossPath = ossPath
        self.localPath = localPath

    def download_file(self):
        KeyId, KeySecret = get_oss_credentials()
        try:
            print('download start')
            auth = oss2.Auth(KeyId, KeySecret)
            bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'fine-build')  # waiwang
            # bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai-internal.aliyuncs.com', 'fine-build')  # neiwang
            bucket.get_object_to_file(self.ossPath, self.localPath)
            print('download %s success' % self.ossPath)
            return 1
        except Exception as e:
            print('download_file filed : ', e)
            return -1


if __name__ == '__main__':
    ossPath = sys.argv[1]
    localPath = sys.argv[2]
    oss = oss(ossPath, localPath)
    oss.download_file()
