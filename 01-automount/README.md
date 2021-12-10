
### 一、介绍:
```
    该脚本主要是针对工作中
       需要批量将多个服务器的多个设备采用uuid方式进行磁盘挂载(已实现 自动格式化磁盘+自动挂载模式)
     ansible进行uuid的挂载方式比较难实现,所以才写出了该脚本,解决此问题.
     如果直接写设备名挂载的话,也可以实现,但是没有uuid方式更加可靠和安全.
     

     
 ```  



### 二、使用方法展示:

```
  #1. 在脚本同级目录下编辑conf.txt文件制定你要挂载的机器列表和设备列表
     配置文件中空格随意添加不受影响
     配置文件中设备信息和ip列表那个在上那个在下都没关系,程序不受顺序影响.
     vim conf.txt
     ![image](01-automount/Photo/1.png)

#2.执行脚本进行挂载.
    python  automount.py 
    ![image](https://github.com/xuchaoyang123/Script-Toolset/blob/main/01-automouns/Photo/2.png)
    
    
    重复执行的话,因为检查到磁盘已经挂载到设备上了,所以会提示 已经存在.
    ![image](https://github.com/xuchaoyang123/Script-Toolset/blob/main/01-automouns/Photo/3.png)
    
```