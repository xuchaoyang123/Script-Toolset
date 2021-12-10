#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################
#Version:2.4
#脚本作用: 批量操作多个服务器将磁盘进行UUID方式挂载。
#explain:
#python2.7  无需安装python
#1 优化执行速度,使用多进程操作.
#2 无需ssh免密,可直接远程操作
#3 磁盘格式化后,自动识别格式化的类型进行文件写入,无需人工干预
#4 需要创建依赖的配置文件默认名字为conf.txt填写信息:#为注释
#配置文件demo
# vim conf.txt
# xfs  <----- 告诉程序我要格式化以下的设备的类型
# nvme0n1 data0 <----- 挂载设备/dev/nvme0n1 挂载到/data0 下
# nvme1n1 data1
# nvme2n1 data2
# nvme3n1 data3
# 192.168.1.10  <---- 以上挂载需要在哪些机器上操作
# 192.168.1.11
##############################

import io
import os
import sys
import re
import time
from threading import Thread

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
            if "#" not in line:
                #是数字的识别为ip地址.
                if   re.findall(r'\d+.\d+.\d+.\d+',line):
                     # 过滤掉配置文件中空行内容.
                    if line != '':
                        Ip.append(line.strip())
                #是字符串的识别为挂载设备信息.   <-------------- 需要优化读取逻辑
                if  "xfs" not in line and "XFS" not in line and  "ext4" not in line and  "EXT4" not in line and re.findall(r'\D+\D+',line):
                    Mont[line.strip('@').split()[0]]=line.strip('@').split()[1]
                 #读取文件中格式化的磁盘类型
                if "xfs"  in line or "ext4"  in line or "XFS"  in line or "EXT4"  in line:
                    Types =  line.lower().split()

else:
    print("%s [ERROR]: File [ %s ] was not found!!!" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),Conf))



def Exec(ip):
    for k in Mont:

        #检查该设备没有挂载到目录上,没有挂载才能格式化,否则提示已在使用.
        Check_Dev_Dir = os.popen( "sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  lsblk | grep %s | awk '{print $7}' | awk -F '/' '{print $2}' " % ( Pass, ip, Port, k)).read().strip()
        if Check_Dev_Dir is not '':
            print("%s [Check_Warning]: %s [ %s ] already exists  [ %s ] Please check.  " % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),ip, k, Check_Dev_Dir))
            continue
        #进行磁盘格式

        if Types[0] == 'xfs':
            Mkfs_Status1 = os.system("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"  mkfs.xfs -f /dev/%s    > /dev/null 2>&1   \"   " % (Pass, ip, Port, k))
            if Mkfs_Status1 <> 0:
                print('%s [Mkfs_Error]: %s [ %s ] The device cannot be formatted. Please check.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),ip,k))
                continue

        elif Types[0] == 'ext4':
            Mkfs_Status2 = os.system("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  \"  mkfs.ext4 -F  /dev/%s  > /dev/null 2>&1  \"  " % (Pass, ip, Port, k))
            if Mkfs_Status2 <> 0:
                print('%s [Mkfs_Error]: %s [ %s ] The device cannot be formatted. Please check. ' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),ip,k))
                continue


        #自动去判断磁盘是否是ext4或者xfs
        Type=os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  blkid | grep %s  | awk -F '\"' '{print $4}'   "%(Pass,ip,Port,k)).read().strip()
        # #如果没有格式化进行输出提醒
        if Type not in {"ext4","xfs"}:
                print(ip,"%s [Warning]: The %s disk type does not meet the requirements,"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),k))
        else:
                #在远程服务器上获取磁盘的uuid进行保存变量到Temp_Uuid中
                Temp_Uuid=os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  blkid | grep %s | awk '{print $2 \" /%s %s defaults        0 0\"}' "%(Pass,ip,Port,k,Mont[k],Type)).read()

                # 创建需要挂载的目录
                os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"  mkdir -p /%s    \"  " % ( Pass, ip, Port, Mont[k]))

                # 写入内容之前将sda4磁盘相关的内容进行注释
                #sed -ri '/sda4.*data/s/(.)/#\//' /etc/fstab
             #   os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"  sed -ri '/sda4.*%s/s/(.)/#\//' %s    \"  " % (Pass, ip, Port,Mont[k],File))

                #写入内容之前将重复的内容进行删除
                #sed -ri '/^UUID.*data\b/ d' /etc/fstab
                os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"   sed -ri '/^UUID.*%s\\b/d' %s   \"  " % (Pass, ip, Port,Mont[k],File))


                #将变量远程写入到目标服务器文件中
                Remote_Uuid = os.system("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"echo '%s' >> %s\" " % (Pass,ip,Port,Temp_Uuid, File))


                #挂载前将老data目录进行卸载
                #umount /data
                # os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" umount /data  \"  " % (Pass,ip,Port))

                #进行挂载生效
                #print(os.popen("echo ok")).read()
                os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" mount -a\"  " % (Pass,ip,Port))

                #输出最新挂载信息
                #print("Mont_Info: ",ip,os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \"lsblk | grep %s \""%(Pass,ip,Port,k)).read().strip())
                Mont_Dir = os.popen( "sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no  lsblk | grep %s | awk '{print $7}' | awk -F '/' '{print $2}' " % ( Pass, ip, Port, k)).read().strip()
                print("%s [Mont_Info]: %s [ %s ]  Successfully mounted [ %s ] ." % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),ip, k, Mont_Dir))


if __name__ == '__main__':

    #进行操作远程挂载
    for ip in Ip:

        #然后在挂载
        p = Thread(target=Exec, args=(ip,))
        p.start()

