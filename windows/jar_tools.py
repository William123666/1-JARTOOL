# coding=utf-8
import os
import requests
import shutil
import zipfile

# 定义常量存储JAR文件的URL
JAR_URLS = {
    'FR':
        {
            '11.0':
                {
                    'feature': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/nightly/finereport11'
                               '.0_jar_openjdk1.8.zip',
                    'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/release/finereport11'
                               '.0_jar_openjdk1.8.zip',
                    'final': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/final/finereport11'
                             '.0_jar_openjdk1.8.zip',
                    'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/stable/finereport11'
                               '.0_jar_openjdk1.8.zip',
                    'XC': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/XC/finereport11'
                          '.0_jar_openjdk1.8.zip '
                },
            '10.0':
                {
                    'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/release/finereport10'
                               '.0_jar_openjdk1.8.zip',
                    'final': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/final/finereport10'
                             '.0_jar_openjdk1.8.zip',
                    'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/10.0/stable/finereport10'
                               '.0_jar_openjdk1.8.zip',
                }
        },
    'BI': {
        '11.0':
            {
                'feature': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finereport/11.0/nightly/finereport11'
                           '.0_jar_openjdk1.8.zip',
                'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x/release/BI5'
                           '.1_spider_jar_jdk1.8 '
                           '.zip',
                'final': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x/final/BI5.1_spider_jar_jdk1.8'
                         '.zip '
            },
        '10.0':
            {
                'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/release/BI5'
                           '.1_spider_jar_jdk1.8.zip',
                'final': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/final/BI5'
                         '.1_spider_jar_jdk1.8.zip',
                'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/5.1.x-fr10/stable/BI5'
                           '.1_spider_jar_jdk1.8.zip',
            },
        '6.0':
            {
                'release': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/release/BI6.0_spider_jar_jdk1'
                           '.8.zip',
                'final': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/final/BI6.0_spider_jar_jdk1.8.zip',
                'persist': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/stable/BI6.0_spider_jar_jdk1.8'
                           '.zip',
                'XC': 'https://fine-build.oss-cn-shanghai.aliyuncs.com/finebi/6.0/XC/BI6.0_spider_jar_jdk1.8.zip'
                      '.0_jar_openjdk1.8.zip '
            }
    }
}


def choose_option(options, message):
    while True:
        print(message)
        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")
        choice = input("请输入对应序号: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        else:
            print('输入有误，请重新输入有效的序号')


def download_jar(url):
    print("正在下载JAR包，请稍等...")
    response = requests.get(url)
    with open("file.zip", "wb") as f:
        f.write(response.content)


def replace_jar():
    jar_path = os.path.abspath('file.zip')
    lib_path = input("请输入工程lib绝对路径:")
    print("工程lib路径为%s" % lib_path)
    if os.path.exists(os.path.join(lib_path, 'file.zip')):
        os.remove(os.path.join(lib_path, 'file.zip'))
    shutil.move(jar_path, lib_path)
    zip_path = os.path.join(lib_path, "file.zip")
    with zipfile.ZipFile(zip_path, 'r') as f:
        f.extractall(lib_path)
    designer_lib = os.path.abspath(os.path.join(lib_path, "../../../../lib"))
    jar_designer_path = os.path.join(lib_path, "designer", "fine-report-designer-11.0.jar")
    print("预期的设计器路径为：%s" % designer_lib)

    lib_list = os.listdir(designer_lib)
    for i in lib_list:
        if i == "fine-report-designer-11.0.jar":
            shutil.copy(jar_designer_path, designer_lib)
    print("JAR包替换成功！")


def main():
    project = choose_option(['FR', 'BI'], '请选择需要下载的项目：')

    if project == 'FR':
        versions = ['11.0', '10.0']
    elif project == 'BI':
        versions = ['11.0', '10.0', '6.0']
    else:
        print("无效的项目选择")
        return

    version = choose_option(versions, '请选择需要下载的版本：')
    branch = choose_option(['feature', 'release', 'final', 'persist', 'XC'], '请选择需要下载的分支：')

    jar_url = JAR_URLS[project][version][branch]

    download_jar(jar_url)  # 下载文件

    replace_jar()  # 替换JAR文件
    input("按 Enter 键退出…")


if __name__ == "__main__":
    main()
