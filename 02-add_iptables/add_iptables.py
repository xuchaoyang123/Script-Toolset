# !/usr/bin/python
# -*- coding: utf-8 -*-
##############################
#Version:1.4
#脚本作用: 批量给多个服务器上添加iptables,限制多个端口,并设置多个白名单ip
#explain:
#python2.7  无需安装python
#1 无需ssh免密,可直接远程操作
##############################

import io
import os
import time

#可调整部分
Pass="123456"  #服务器的统一密码
Port=22        #服务器的统一端口
Conf='conf.txt'   #读取依赖的配置文件名


exec_ip = []             #不需要填写,通过配置文件自动渲染!
ports = []               #不需要填写,通过配置文件自动渲染!
iptables_ip = []         #不需要填写,通过配置文件自动渲染!


#无密码远程连接功能
def Ssh_Cmd(ip,Cmd):
        os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" %s  \"  " % (Pass, ip, Port,Cmd))



#实现过滤制定标签[xxx]里的内容功能
def Grep_File(Conf, Label,List):
    # 判断配置文件是否存在,不存在进行提示
    with io.open(Conf, 'r', encoding='utf-8') as f:
        for lines in f:
            if "#" not in lines.strip() and lines.strip() != '':
                if '[' in lines:
                    Wflag = False
                if Label in lines:
                    Wflag = True
                    continue
                if Wflag == True:
                # 过滤注释#内容和空格内容
                    List.append(lines.strip())



# 定义实现批量添加防火墙功能
def Add_Iptables():
    for ip in exec_ip:
          print("============> %s <============"%(ip))
          #备份iptables
          Ssh_Cmd(ip,'iptables-save > /opt/iptables_bk_%s'%(time.strftime("%Y_%m_%d",time.localtime())))

          #创建ZK_WHITELIST filter
          #   iptables -t filter -N ZK_WHITELIST
          Ssh_Cmd(ip,'iptables -t filter -N ZK_WHITELIST')
          Ssh_Cmd(ip,'iptables -t filter -I ZK_WHITELIST -j DROP')

          # iptables配置ip
          for iip in iptables_ip:
            Ssh_Cmd(ip,'iptables -t filter -I ZK_WHITELIST -s %s/32 -j RETURN'%(iip))

          #",".join(ports))将list列表转为字符串格式化内容
          Ssh_Cmd (ip,'iptables -t filter -I INPUT -p tcp -m multiport --dports %s -j ZK_WHITELIST' % (",".join(ports)))

          #打印输出当前防火墙的规则
          print(os.popen("sshpass -p %s ssh root@%s -p %s -o StrictHostKeyChecking=no \" %s  \"  " % (Pass, ip, Port,'iptables -L -n | grep -v target |  grep -v Chain | grep -v ^$')).read().strip())



if __name__ == '__main__':

    #将标签数据保存到list列表中.
    if os.path.exists(Conf):
        Grep_File(Conf, 'exec_ip',exec_ip)
        Grep_File(Conf, 'ports',ports)
        Grep_File(Conf, 'iptables_ip',iptables_ip)
    else:
        print("ERROR: File [ %s ] was not found!!!" % (Conf))

    # 实际添加防火墙功能
    Add_Iptables()





