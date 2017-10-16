#coding:utf8

from models import zones,records,logs
import datetime,IPy
import django
django.setup()


zone_switch = ('on','off')
zone_type = ('Forward','Reverse')
record_type = ('A','PTR','CNAME','MX','AAAA')
object_type = ('record','zone')
operation_type = ('add','del')

def is_ip(address):
    '''
    判断字符串是否为 IP
    '''
    try:
        IPy.IP(address)
        return True
    except Exception as  e:
        return False


def db_add_log(object,operation,detail):
    '''
    日志记录
    '''
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.objects.create(Time=now,Object=object,Operation=operation,Detail=detail)


def db_add_zone(name,type,switch="on"):
    '''
    新增 zone 记录
    '''
    zones.objects.get_or_create(Name=name,Type=type,Switch=switch)
    db_add_log(object_type[1], operation_type[0],"REPLACE INTO zones VALUES(" + name + "," + type + "," + switch + ");")


def db_add_record(zone,key,ttl,type,value):  #此处 zone 为对象，而非字符串
    '''
    新增 record 记录
    '''
    records.objects.get_or_create(ZoneName=zone,Key=key,TTL=ttl,Type=type,Value=value)
    db_add_log(object_type[0], operation_type[0],"REPLACE INTO records VALUES(" + zone.Name + "," + key + "," + ttl + "," + type + "," + value + ");")

def db_del_zone(name):
    '''
    删除 zone 记录
    '''
    zones.objects.filter(Name=name).delete()
    db_add_log(object_type[1], operation_type[1], "DELETE FROM zones WHERE `Name`=" + name + ";")


def db_del_record(zone,key,type,value):  #此处 zone 为对象，而非字符串
    '''
    删除 record 记录
    '''
    records.objects.filter(ZoneName=zone,Key=key,Type=type,Value=value).delete()
    db_add_log(object_type[0], operation_type[1],"DELETE FROM records WHERE `ZoneName`=" + zone.Name + " AND `Key`=" + key + " AND `Type`=" + type + " AND `Value`=" + value + ";")


def db_get_zones():
    '''
    返回所有 zone
    '''
    return  zones.objects.all()


def db_get_records(name):
    '''
    获取指定 zone 的所有 records
    '''
    zone = zones.objects.get(Name=name)
    return  records.objects.filter(ZoneName=zone)


def db_get_record(key,zone="none"):
    '''
    获取指定 zone 的单条 record
    '''
    if is_ip(key): #如果输入的是IP地址
        ip_addr = IPy.IP(key)
        ip_rever = ip_addr.reverseNames()[0]  # 完整反向解析字符串
        ip_spilit = ip_rever.find(".")  # 查找分割点
        key = ip_rever[0:ip_spilit]  # %D
        zone = ip_rever[ip_spilit + 1:-1]  # zone name
    if zone == "none" or zone == "":
        return records.objects.filter(Key=key)  #返回所有符合的 record

    return  records.objects.filter(ZoneName=zone,Key=key)
