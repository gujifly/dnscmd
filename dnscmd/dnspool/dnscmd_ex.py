#coding:utf8
from dnscmd import *
from updatedb_ex import *
import IPy

import sys
reload(sys)
sys.setdefaultencoding('utf8')


'''
---------------------------------------------------------------------------------------------
新增一个正向区域：dnscmd  /zoneadd 9222.com /primary
    新增一个主机 A 记录：dnscmd  /recordadd 9222.com host01 A 172.16.11.75
        新增一个二级主机 A 记录：dnscmd  /recordadd 9222.com  host02.2333  A 172.168.11.83   # host02.2333.9222.com
    新增一个正向 CNAME 记录：dnscmd  /recordadd 9222.com host03 CNAME host01.9222.com

新增一个反向区域：dnscmd  /zoneadd 11.16.172.in-addr.arpa /primary
    新增一个 PTR 记录：dnscmd  /recordadd 11.16.172.in-addr.arpa 75 PTR host01.9222.com
    新增一个反向 CNAME 记录： dnscmd /recordadd 11.16.172.in-addr.arpa 76 CNAME 75.11.16.172.in-addr.arpa

---------------------------------------------------------------------------------------------
删除一个正向域节点：dnscmd /nodedelete  9222.com 2333 /tree /f
删除一个正向域：dnscmd /zonedelete 9222.com /f

删除一条 A 记录：dnscmd /recorddelete 9222.com host01 A 172.16.11.77 /f
删除一个主机所有 A 记录：dnscmd  /recorddelete 9222.com host01 A /f

删除一个反向域：dnscmd /zonedelete 11.16.172.in-addr.arpa /f

删除一个 PTR 记录： dnscmd  /recorddelete 11.16.172.in-addr.arpa  98 PTR host06.9222.com /f
删除一个 IP 所有 PTR 记录：dnscmd /recorddelete 11.16.172.in-addr.arpa 88 PTR /f

---------------------------------------------------------------------------------------------
枚举所有正向域：dnscmd /enumzones /forward /primary
查询正向域某域所有记录：dnscmd /zoneprint 9222.com  #包括子域记录
查询正向域某节点所有 A 记录：dnscmd /enumrecords 9222.com @ /Type A
                          dnscmd /enumrecords 9222.com 2333 /Type A

枚举所有反向域：dnscmd /enumzones /reverse /primary
查询反向域某域所有记录：dnscmd /zoneprint 11.16.172.in-addr.arpa
查询反向域某域 PTR 记录：dnscmd /enumrecords 11.16.172.in-addr.arpa @ /Type PTR
'''

server_ip = "10.0.19.2"   # DNS 服务器地址

zone_switch = ('on','off')
zone_type = ('Forward','Reverse')
record_type = ('A','PTR','CNAME','MX','AAAA')


def is_ip(address):
    '''
    判断字符串是否为 IP
    '''
    try:
        IPy.IP(address)
        return True
    except Exception as  e:
        return False


def query_zone(name):
    '''
    查询区域是否存在,0 表示不存在，1 表示存在
    '''
    confirm = 0
    cmd = "dnscmd " + server_ip + " /enumzones /primary"
    tmp_result = run_cmd(cmd)  # 查询结果
    if confirm_result(name, tmp_result) == 1:  # 如果找到期望值
        confirm = 1
    return confirm


def query_record(key,zone,value):
    '''
    查询记录是否存在,0 表示不存在，1 表示存在
    '''
    confirm = 0
    cmd = "dnscmd " + server_ip + " /enumrecords " + zone + " " + key
    tmp_result = run_cmd(cmd)  # 查询结果

    if confirm_result(value,tmp_result) == 1:  # 如果找到期望值
        confirm = 1
    return {"confirm":confirm,"ttl":get_ttl(tmp_result)}



def set_zone(name,type,action="add"):
    '''
    新增/删除 一个区域, 0 表示失败, 1 表示成功, 2 表示其他
    '''
    confirm = 0
    if action == "add":
        cmd0 = "dnscmd " + server_ip + " /zoneadd " + name + " /primary"
        tmp_result0 = run_cmd(cmd0)  # 执行结果
        print tmp_result0
        if query_zone(name) == 1:
            confirm = 1
            db_add_zone(name,type)  #插入数据库

    elif action == "del":
        cmd0 = "dnscmd " + server_ip + " /zonedelete " + name + " /f"
        tmp_result0 = run_cmd(cmd0)  # 执行结果
        if query_zone(name) == 0:
            confirm = 1
            db_del_zone(name)  #数据库删除记录
    else: #其它状况
        return 2
    return confirm


def set_record(key,type,value,zone_name="none",action="add"):
    '''
    插入|删除 一条记录, 0 表示失败，1 表示成功, 2 表示其他
    '''
    confirm = 0
    zone_type = "Forward"

    if is_ip(key): #如果输入的是IP地址
        ip_addr = IPy.IP(key)
        ip_rever = ip_addr.reverseNames()[0]  # 完整反向解析字符串
        ip_spilit = ip_rever.find(".") # 查找分割点
        key = ip_rever[0:ip_spilit]  # %D
        zone_name = ip_rever[ip_spilit+1:-1]  # zone name
        zone_type = "Reverse"
    if zone_name.strip() == "none" or zone_name.strip() == "":
        if not is_ip(key):
            return 0  #返回失败

    if action == "add": #插入新纪录
        if query_zone(zone_name) == 0:  #如果 zone 不存在
            if set_zone(zone_name,zone_type,"add") == 0: #如果新增 zone 失败
                return 0
            else:
                db_add_zone(zone_name,zone_type) #插入数据库


        cmd0 = "dnscmd " + server_ip + " /recordadd "+ zone_name + " " + key + " " + type + " " + value   #添加记录
        tmp_result0 = run_cmd(cmd0)  # 执行结果

        query_result = query_record(key,zone_name,value)
        if query_result['confirm'] == 1:
            confirm = 1
            zone = {}
            try:
                zone = zones.objects.get(Name=zone_name)
            except Exception as e:
                print e

            db_add_record(zone,key,query_result['ttl'],type,value) #插入数据库


    elif action == "del":  #删除记录
        cmd0 = "dnscmd " + server_ip + " /recorddelete " + zone_name + " " + key + " " + type + " " + value + " /f"   #删除记录
        tmp_result0 = run_cmd(cmd0)  # 执行结果

        query_result = query_record(key, zone_name, value)
        if query_result['confirm'] == 0:
            confirm = 1
            zone = zones.objects.get(Name=zone_name)
            db_del_record(zone,key,type,value)  #数据库删除记录
    else: #其它状况
        return 2

    return confirm


def enum_zones():  # DNS数据存储路径不一样，显示结果格式也不一样，这里存储在 AD数据库中，而非 file
    '''
    刷新数据库 zones 表记录（获取所有区域名称）
    '''
    cmd = "dnscmd " + server_ip + " /enumzones /primary"
    tmp_result = run_cmd(cmd)  # 查询结果
    result = get_result(tmp_result) #获取提取后的数据
    all_list = result.splitlines(False) #按行分割
    for line in all_list:
        tmp_list = line.split()
        if len(tmp_list) >= 5:
            if tmp_list[4].strip() == "Rev":
                db_add_zone(tmp_list[0],"Reverse")  #插入数据库
            else:
                db_add_zone(tmp_list[0],"Forward")  #插入数据库
        elif len(tmp_list) == 3 or len(tmp_list) == 4:
            db_add_zone(tmp_list[0],"Forward")  #插入数据库
        else:
            break


def zone_print(zone):  #此处 zone 为 对象，而非字符串
    '''
    刷新数据库 records 表记录（获取某区域的所有子记录（正向、反向））
    '''
    name = zone.Name
    cmd = "dnscmd " + server_ip + " /zoneprint " + name
    tmp_result = run_cmd(cmd)  # 查询结果
    result = get_result(tmp_result) #获取提取后的数据
    all_list = result.splitlines(False) #按行分割
    current_host = "" #保存上条记录 host名，以便处理 同机多记录情况
    for line in all_list:
        tmp_list = line.split()
        if len(tmp_list) == 5:  #包含"[老化:xxxxxx]" 一栏
            current_host = tmp_list[0]
            db_add_record(zone, current_host, tmp_list[2], tmp_list[3], tmp_list[4])  # 插入数据库
        elif len(tmp_list) == 4:
            if tmp_list[0].find(u"老化") == -1:
                current_host = tmp_list[0]
            db_add_record(zone,current_host,tmp_list[1],tmp_list[2],tmp_list[3])  #插入数据库
        elif len(tmp_list) == 3:  #与上条记录同名
            db_add_record(zone,current_host,tmp_list[0],tmp_list[1],tmp_list[2])  #插入数据库
        else:
            break

