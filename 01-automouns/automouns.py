#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################
#Version:2.1
#脚本作用: 批量操作多个服务器将磁盘进行UUID方式挂载。
#explain:
#python2.7  无需安装python
#1 优化执行速度,使用多进程操作.
#2 无需ssh免密,可直接远程操作
#3 磁盘格式化后,自动识别格式化的类型进行文件写入,无需人工干预
#4 需要创建依赖的配置文件默认名字为conf.txt填写信息:#为注释
#配置文件demo
# vim conf.txt
# nvme0n1 data0
# nvme1n1 data1
# nvme2n1 data2
# nvme3n1 data3
# 192.168.1.10
# 192.168.1.11
##############################

import io
import os
import sys
import re
import time
from multiprocessing import Process

# 可调整部分
File = "/etc/fstab"  # 写入的配置文件位置
Pass = "123456"  # 服务器的统一密码
Port = 22  # 服务器的统一端口
Conf = 'conf.txt'  # 读取依赖的配置文件名

Ip = []  # 不需要填写,通过配置文件自动渲染!
Mont = {}  # 不需要填写,通过配置文件自动渲染!



#定义处理配置文件数据功能
#判断配置文件是否存在,不存在进行提示
if os.path.exists(Conf):
    ##通过读取指定的conf文件内容,将ip和挂载信息追加到Ip和Mount中.
    with  io.open(Conf,encoding='utf-8') as f:
        for line in f:
            #如果该行内包含#则代表是注释
            #是数字的识别为ip地址.
            if  "#" not in line and re.findall(r'\d+.\d+.\d+.\d+',line):
                #过滤掉配置文件中空行内容.
                if line != '':
                    Ip.append(line.strip())
            #是字符串的识别为挂载设备信息.
            if "#" not in line and re.findall(r'\D+\D+',line):
                Mont[line.strip('@').split()[0]]=line.strip('@').split()[1]
else:
    print("ERROR: File [ %s ] was not found!!!" % (Conf))


def Exec(k):
    for ip in Ip:
        #自动去判断磁盘是否是ext4或者xfs
                Type=os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  blkid | grep %s  | awk -F '\"' '{print $4}'   "%(Pass,ip,Port,k)).read().strip()
                # #如果没有格式化进行输出提醒
                if Type not in {"ext4","xfs"}:
                        print("[Warning]: The %s disk type does not meet the requirements,"%(k))
                else:
                        #在远程服务器上获取磁盘的uuid进行保存变量到Temp_Uuid中
                        Temp_Uuid=os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  blkid | grep %s | awk '{print $2 \" /%s %s defaults        0 0\"}' "%(Pass,ip,Port,k,Mont[k],Type)).read()

                        # 写入内容之前将sda4磁盘相关的内容进行注释
                        #sed -ri '/sda4.*data/s/(.)/#\//' /etc/fstab
                        os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"  sed -ri '/sda4.*%s/s/(.)/#\//' %s    \"  " % (Pass, ip, Port,Mont[k],File))

                        #写入内容之前将重复的内容进行删除
                        #sed -ri '/^UUID.*data\b/ d' /etc/fstab
                        os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"   sed -ri '/^UUID.*%s\\b/d' %s   \"  " % (Pass, ip, Port,Mont[k],File))


                        #将变量远程写入到目标服务器文件中
                        Remote_Uuid = os.system("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"echo '%s' >> %s\" " % (Pass,ip,Port,Temp_Uuid, File))


                        #挂载前将老data目录进行卸载
                        #umount /data
                        os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" umount /data  \"  " % (Pass,ip,Port))

                        #进行挂载生效
                        #print(os.popen("echo ok")).read()
                        os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" mount -a\"  " % (Pass,ip,Port))

                        #输出最新挂载信息
                        print(ip,os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"lsblk | grep %s \""%(Pass,ip,Port,k)).read().strip())


if __name__ == '__main__':

    #进行操作远程挂载
    for k in Mont:
        p = Process(target=Exec, args=(k,))
        p.start()
