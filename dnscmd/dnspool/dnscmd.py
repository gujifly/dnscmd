#coding:utf8

import subprocess,re,json

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


def check_result(result):
    '''
    检测执行结果
    '''
    ok_0=u"命令成功完成".encode('utf8')
    ok_1=u"已完成的区域".encode('utf8')
    fail_0=u"命令失败".encode('utf8')
    code=0  # 返回代码 0：失败  1：成功  2：未知

    if result.find(fail_0) <> -1:
        code=0
    elif result.find(ok_0) <> -1 or result.find(ok_1) <> -1:
        code=1
    else:
        code=2

    print "%d" % code
    #print "%s" % result
    return code


def get_result(result):
    '''
    获取结果数据
    '''
    all_list = result.splitlines(False)
    all_result=""
    for line in all_list:
        if len(line) <> 0:
            # 将正则表达式编译成Pattern对象
            pattern = re.compile(r'^(?![0-9]{3,10} (SOA|NS))[A-Za-z0-9].*$')
            # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
            m = pattern.match(line.lstrip())
            if m:
                # 使用Match获得分组信息
                all_result += ' '.join((re.split(r'\s+', m.group()))) +"\n" #去除重复空格
    return all_result


def get_ttl(result):
    '''
    获取 TTL 值
    '''
    ttl = "3000"
    all_list = result.splitlines(False)
    all_result = ""
    for line in all_list:
        if len(line) <> 0:
            # 将正则表达式编译成Pattern对象
            pattern = re.compile(r'^(@ [0-9]{3,10})\w.*$')
            # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
            m = pattern.match(line.lstrip())
            if m:
                # 使用Match获得分组信息
                all_result += ' '.join((re.split(r'\s+', m.group()))) + "\n"  # 去除重复空格
                ttl = all_result.split()[1]
                # print(m.group())
                ### 输出 ###
                # rlovep
                # print "%s" % ss.lstrip()
    return ttl


def confirm_result(expect,result):
    '''
    确保结果一致
    '''
    code = 0  # 返回代码 0：不一致  1：一致

    if result.find(expect.encode("utf8")) <> -1 :
        code = 1
    else:
        code = 0
    #print "%d" % code
    return code


def run_cmd(cmd):
    '''
    执行 CMD 命令
    '''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    pos = p.communicate()
    result = pos[0].decode('cp936').encode('utf-8')
    return result


