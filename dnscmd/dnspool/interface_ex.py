#coding:utf8
from dnscmd_ex import *
from django.core import serializers
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
import simplejson

action_result = ("success", "part", "fail", "error")  # 操作结果：succes：全部成功，part：部分成功，fail：操作失败，error：发生错误
action = ("add", "del", "query","all","sync")  # 操作类型： 增、删、查、获取所有 zone 名称,同步MySQL和DNS数据库
object = ("zone", "record")  # 操作对象：zone、record
zone_type = ("Forward", "Reverse")
record_type = ("A", "PTR", "CNAME", "MX", "AAAA")

def log_in(request):
    '''
    用户验证函数
    '''
    dict = {}
    req = {}
    action_result_send = ""
    action_msg_send = ""

    if request.method == 'POST':
        try:
            req = simplejson.loads(request.body)  # 从 POST 接收 JSON数据
        except ValueError:
            action_result_send = action_result[3]
            action_msg_send = u"传入格式有误，请确认传入数据为 JSON 格式！"
            dict['action_result'] = action_result_send
            dict['action_msg'] = action_msg_send
            resp_json = simplejson.dumps(dict)
            return HttpResponse(resp_json)
        username = req['username']
        password = req['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                action_result_send = action_result[0]
                action_msg_send = u"登录成功！"
            else:
                # Return a 'disabled account' error message
                action_result_send = action_result[2]
                action_msg_send = u"当前用户被禁用！"
        else:
            # Return an 'invalid login' error message.
            action_result_send = action_result[2]
            action_msg_send = u"账户或密码不正确！"
    else:
        action_result_send = action_result[3]
        action_msg_send = u"请通过 POST 方式传递登录参数！"

    dict['action_result'] = action_result_send
    dict['action_msg'] = action_msg_send
    resp_json = simplejson.dumps(dict)
    return HttpResponse(resp_json)

def gate(request):
    '''
    入口函数，接收 json 格式数据，调用对应处理函数，返回 json 格式数据
    '''
    if not request.user.is_authenticated(): #如果用户未登录
        dict = {}
        action_result_send = action_result[2]
        action_msg_send = u"请先用账户、密码登录本系统！"
        dict['action_result'] = action_result_send
        dict['action_msg'] = action_msg_send
        resp_json = simplejson.dumps(dict)
        return HttpResponse(resp_json)

    req = {}
    dict = {}
    success_list = []        #操作成功列表
    fail_list = []           #操作失败列表
    query_list = []          #查询结果列表
    action_result_send = ""
    action_msg_send = ""
    action_send = ""
    object_send = ""

    try:
        if request.method == 'POST':
            try:
                req = simplejson.loads(request.body)  #从 POST 接收 JSON数据
            except ValueError:
                action_result_send = action_result[3]
                action_msg_send = u"传入格式有误，请确认传入数据为 JSON 格式！"
                dict['action_result'] = action_result_send
                dict['action_msg'] = action_msg_send
                resp_json = simplejson.dumps(dict)
                return HttpResponse(resp_json)

            action_send = ""
            object_send = ""
            object_req = ""
            datas_req = {}
            datas_req_num = 0

            check_result = check_rec(req) #检测参数是否合法
            if check_result[0] == 0: #如果参数非法
                action_result_send = action_result[3]
                action_msg_send = check_result[1]
            else:
                action_req = req['action'].strip()
                if action_req <> action[3] and action_req <> action[4]:
                    object_req = req['object'].strip()

                action_send = action_req
                object_send = object_req

                if action_req <> action[3] and action_req <> action[4]:
                    datas_req = req['datas']
                    datas_req_num = len(datas_req)

                if datas_req_num > 0 and action_req <> action[3] and action_req <> action[4]:
                    for each in datas_req:
                        if action_req == action[0] or action_req == action[1]:  #增、删
                            if single_set(object_req,each,action_req) == 1:
                                success_list.append(each)
                            else:
                                fail_list.append(each)
                        elif action_req == action[2]:  #查
                            tmp_query = single_query(object_req,each)
                            if tmp_query[0] == 1:  #查询成功
                                success_list.append(each)
                                for i in range(len(tmp_query[1])): #查询的数据添加到 query 列表中
                                    query_list.append(tmp_query[1][i])
                            else:
                                fail_list.append(each)
                    if len(success_list) == datas_req_num:
                        action_result_send = action_result[0]
                        action_msg_send = u"全部记录操作成功！"
                    elif len(success_list) == 0:
                        action_result_send = action_result[2]
                        action_msg_send = u"全部记录操作失败！"
                    else:
                        action_result_send = action_result[1]
                        action_msg_send = u"部分记录操作成功！"
                elif action_req == action[3]:  #获取所有 zone
                    tmp_query = get_zones()
                    if tmp_query[0] == 1:  #查询成功
                        action_result_send = action_result[0]
                        action_msg_send = u"zone名单获取成功！"
                        for i in range(len(tmp_query[1])):  #查询的数据添加到 query 列表中
                            query_list.append(tmp_query[1][i])
                    else:
                        action_result_send = action_result[2]
                        action_msg_send = u"zone名单获取失败！"
                else: # MySQL 与 DNS 数据库同步
                    if sync_db() == 1:  #同步成功
                        action_result_send = action_result[0]
                        action_msg_send = u"MySQL与 DNS 数据库同步成功！"
                    else:
                        action_result_send = action_result[2]
                        action_msg_send = u"MySQL与 DNS 数据库同步失败！"
        else:
            action_result_send = action_result[3]
            action_msg_send = u"请通过 POST 方式，传入 JSON 格式参数！"
    except Exception as  e:
        action_result_send = action_result[3]
        action_msg_send = u"发生未知错误，请查看服务器日志！"

    dict['action_result'] = action_result_send
    dict['action_msg'] = action_msg_send
    dict['action'] = action_send
    dict['object'] = object_send
    dict['success'] = success_list
    dict['fail'] = fail_list
    dict['query'] = query_list
    resp_json=simplejson.dumps(dict)
    return HttpResponse(resp_json)


def single_set(object_req,data,action_req):
    '''
    add、del 处理函数， 0：失败，1：成功
    '''
    zone_name = ""
    if object_req == object[0]: #如果操作对象是 zone
        return set_zone(data["zone_name"].strip(), data["zone_type"].strip(), action_req)
    else:
        if "record_value" not in data.keys():
            return 0
        elif data["record_value"].strip() == "":
            return 0

        if "zone_name" in data.keys():
            zone_name = data["zone_name"].strip()

        return set_record(data["record_name"].strip(), data["record_type"].strip(), data["record_value"].strip(), zone_name, action_req)


def single_query(object_req,data):
    '''
    query 处理函数， 0：失败，1：成功，query_list：数据
    '''
    zone_name = ""
    query_list = []
    if object_req == object[0]: #如果操作对象是 zone
        tmp_list = simplejson.loads(serializers.serialize("json",db_get_records(data["zone_name"].strip())))
    else:
        if "zone_name" in data.keys():
            zone_name = data["zone_name"].strip()
        tmp_list = simplejson.loads(serializers.serialize("json",db_get_record(data["record_name"].strip(),zone_name)))

    if tmp_list is None:
        return [0,u"查询失败"]
    else:
        for each in tmp_list:
            query_list.append(each["fields"])
        return [1,query_list]

def get_zones():
    '''
    获取所有 zone 信息，0：失败，1：成功，query_list：数据
    '''
    query_list = []
    tmp_list = simplejson.loads(serializers.serialize("json",db_get_zones()))
    if tmp_list is None:
        return [0,u"查询失败"]
    else:
        for each in tmp_list:
            query_list.append(each["fields"])
        return [1, query_list]


def check_rec(req):
    '''
    检测接收到的所有参数是否合法， 0：非法，1：合法， msg：详细信息
    '''

    action_req = ""
    object_req = ""
    datas_req_num = 0
    datas_req = {}

    if "action" not in req.keys():
        msg = u"action 参数不能为空"
        return [0,msg]

    action_req = req['action'].strip()

    if action_req <> action[3] and action_req <> action[4] and "object" not in req.keys():
        msg = u"object 参数不能为空"
        return [0, msg]
    elif action_req <> action[3] and action_req <> action[4] and "object" in req.keys():
        object_req = req['object'].strip()
    else:
        return [1, u"参数合法"]

    if action_req <> action[3] and action_req <> action[4]  and "datas" not in req.keys():
        msg = u"zone 或 record 数据不能为空"
        return [0,msg]
    elif action_req <> action[3] and action_req <> action[4]  and "datas" in req.keys():
        datas_req = req['datas']
        datas_req_num = len(datas_req)
    else:
        return [1,u"参数合法"]

    if action_req == "" or object_req == "":
        msg = u"action 或 object 参数不能为空"
        return [0,msg]

    if action_req not in action or object_req not in object_type:
        msg = u"action 或 object 参数不合法"
        return [0,msg]

    if datas_req_num == 0:
        msg = u"zone 或 record 数据不能为空"
        return [0,msg]
    else:  # datas 有数据
        for each in datas_req:
            if object_req == object[0]:  #对象为 zone
                msg = ""
                if "zone_name" not in each.keys():
                    msg = u"zone_name 不存在"
                    return [0, msg]
                elif each["zone_name"].strip() == "":
                    msg = u"zone_name 不能为空"
                    return [0,msg]

                if "zone_type" not in each.keys():
                    msg = u"zone_type 不存在"
                    return [0, msg]
                elif each["zone_type"].strip() not in zone_type:
                    msg = u"zone_type 参数不合法"
                    return [0,msg]
            if object_req == object[1]:  #对象为 record
                msg = ""
                if "record_name" not in each.keys():
                    msg = u"record_name 不存在"
                    return [0, msg]
                elif each["record_name"].strip() == "":
                    msg = u"record_name 不能为空"
                    return [0, msg]
            if object_req == object[1] and action_req <> action[2]: #非记录查询
                msg = ""
                if "record_type" not in each.keys():
                    msg = u"record_type 不存在"
                    return [0, msg]
                elif each["record_type"].strip() not in record_type:
                    msg = u"record_type 参数不合法"
                    return [0,msg]
            if object_req == object[1] and ( action_req == action[0] or action_req == action[1] ): #增、删记录
                msg = ""
                if "record_value" not in each.keys():
                    msg = u"record_value 不存在"
                    return [0, msg]
                elif each["record_value"].strip() == "":
                    msg = u"record_value 不能为空"
                    return [0, msg]

    return [1,u"参数合法"]


def sync_db():
    '''
    #重新校对 dnsdb 数据库（与 DNS 数据库进行校对） 0：失败，1：成功
    '''
    try:
        enum_zones()
        for zone in db_get_zones():
            zone_print(zone)
    except:
        return 0
    return 1