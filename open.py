#coding=utf-8
#!/usr/bin/python


import os, sys
import win32api
import win32process
import win32event
import win32con
import subprocess
from psutil import process_iter
from signal import SIGTERM # or SIGKILL
import zipfile
import shutil
import requests
import time
import json
from download_oss import oss

webhook ='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9af0d737-7e82-4e90-8adc-6215e3feb844'
def kill_port(port):
    try:
        for proc in process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == int(port):
                    print(proc)
                    proc.kill() 
    except Exception as e:
        print(e)
 

def create_process(filename):
    hInstance, exe_filename = win32api.FindExecutable (filename)
    print(exe_filename + ' '+ filename)

    hProcess, hThread, pid, tid = win32process.CreateProcess (
    None,
    '"%s" "%s2' % (exe_filename, filename),
    None, # process attributes
    None, # process attributes
    0, # inherit handles
    0, # creation flags
    None, # new environment
    None, # current directory
    win32process.STARTUPINFO ())
    print(pid)
    return win32api.OpenProcess (win32con.PROCESS_ALL_ACCESS, True, pid)

def send_to_robot(webhook, data):
    r = requests.post(webhook, json=data)
    print(r.text)

def create_data(text):
    return {
        "msgtype": "markdown",
        "markdown": {
            "content": text,
            "mentioned_list": ["@all"],
            "mentioned_mobile_list": ["@all"]
        }
    }

def unzip_zip(zip_file, file_folder):
    zFile = zipfile.ZipFile(zip_file, "r")
    zFile.extractall(file_folder)
    zFile.close()

def move_file(origin_folder,dest_folder):
    files= os.listdir(origin_folder) 
    for file in files:
        if file == "designer":
            pass
        else:
            shutil.copy(os.path.join(origin_folder, file), dest_folder)

def read_json_file(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def start_tomcat(tomcat_path):
    print(tomcat_path)
    os.putenv('CATALINA_HOME',tomcat_path)
    popen = subprocess.Popen(tomcat_path + '\\bin\\startup.bat', shell=True)
    popen.wait()


#finebi/5.1.2/release/backup/2020-01-03/BI5.1_spider_jar_jdk1.8.zip
#finebi/5.1.2/release/BI5.1_spider_jar_jdk1.8.zip
#finereport/10.0/release/finereport10.0_jar_openjdk1.8.zip
#finereport/10.0/stable/backup/2019-12-08/finereport10.0_jar_openjdk1.8.zip
def get_oss_download_url(server_type, server_branch, backup, server_version):
    download_url = ''
    if server_type == 'bi':
        download_url = 'finebi/' + server_version + "/" +server_branch
        if backup.strip() != "":
            download_url = download_url + "/backup/" + backup + "/BI5.1_spider_jar_jdk1.8.zip"
        else:
            download_url = download_url + "/BI5.1_spider_jar_jdk1.8.zip"
    elif server_type == 'fr':
        download_url = 'finereport/' + server_version + "/"
        if server_branch == "persist" and backup.strip() != "":
            download_url = download_url + "stable/backup/" + backup
        elif server_branch == "persist":
            download_url = download_url + "stable"
        else:    
            download_url = download_url + server_branch 
        download_url = download_url + "/finereport11.0_jar_openjdk1.8.zip"
    else:
        pass
    print(download_url)
    return download_url
   

if __name__ == '__main__':
     jsonpath = sys.argv[1]
     only_start_server = False
     if len(sys.argv) >= 3:
        only_start_server = sys.argv[2] == 'only_start_server'
     print('读取json配置中...\n')
     j = read_json_file(jsonpath)
     result = -1
     print(j)
     if j == None:
        print("请输入正确的json配置文件地址")
        sys.exit(0)
     try:
        server_name = j["服务器名字"]
        server_port = j["服务器端口号"]
        jar_download_path = j["jar下载目录"]
        jar_unzip_path = j["jar解压目录"]    
        server_webroot_path = j["服务器webroot地址"]
        server_exe_path=j["BIexe文件路径"]
        server_backup_time = j["jar日期(默认下载最新)"]
        server_branch = j["jar分支(默认release)"]
        server_version = j["服务器版本号"]
        only_download_jar = j["只下载jar(默认否)"]
        server_type = j["工程类型(bi或fr)"].strip().lower()
        tomcat_path = j["FRtomcat路径"]
        if only_start_server == False:
            only_start_server = j["只重启工程(默认否)"] == "是"
     except Exception as e:
         print('读取json配置失败:'+e)
         sys.exit(0)
     if only_start_server == False:
        try:
            print('开始下载jar包...\n')
            oss_download_url = get_oss_download_url(server_type ,server_branch,server_backup_time, server_version)
            oss=oss(oss_download_url,jar_download_path +'temp.zip')
            result = oss.download_file()
        except Exception as e:
            print('jar下载失败:'+e)
            sys.exit(0)
     if only_download_jar == '是':
        sys.exit(0)
     is_bi = server_type == 'bi'
     if result == 1 or only_start_server:
            print('开始关闭之前的工程...\n')
            kill_port(server_port)
            if result == 1:
                send_to_robot(webhook, create_data(server_name + '换jar'))
                print('开始解压zip包...\n')
                unzip_zip(jar_download_path +'temp.zip', jar_unzip_path)
                print('开始将jar移动到对应文件夹下\n')
                move_file(jar_unzip_path, server_webroot_path +'\\WEB-INF\\lib')
            if is_bi:
                try:
                    print('开始启动BI工程...\n')
                    handle = create_process(server_exe_path)
                    if handle != None:
                        print('create process success')
                        time.sleep(90)
                        send_to_robot(webhook, create_data(server_name +'重启成功'))
                        print('换jar并重启完成...\n')
                except Exception as e:
                    print(e)
                    send_to_robot(webhook, create_data(server_name + '重启失败: ```' + e + '```'))
            else:
                print('开始启动tomcat工程')
                start_tomcat(tomcat_path)
                time.sleep(90)
                send_to_robot(webhook, create_data(server_name +'重启成功'))
                print('换jar并重启完成...\n')
     sys.exit(0)







   