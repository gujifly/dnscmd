# dnscmd
将 AD域控 DNS 的操控，封装成一个通用接口，方便集成在 运维平台中。
<br>

### Python + Django + Mysql + Apache 封装windows DNS 管理接口

#### 背景：
    1. 内网 windows 服务器 是基于 AD域环境的，DNS 解析主要依靠 域控DNS 提供。
    2. 当需要变更 DNS记录时，需要运维人员登录域控 或者通过微软提供的“DNS管理工具”手工修改。
    3. 外网 DNS 管理 可以利用供应商提供的 管理接口，集成在 运维平台中。

#### 需求：
    将 AD域控 DNS 的操控，封装成一个通用接口，方便集成在 运维平台中。

#### 环境：
* Windows 2008 R2
* Python : 2.7
* Django： 1.11.4
* Mysql： 5.7
* Apache： 2.4

#### 原理：
        windows “DNS管理工具” 除了提供 GUI 管理界面外，还提供了一个名叫 “dnscmd.exe”的控制台程序，
      可以通过调用它对域控 DNS进行操控。
        Django 为快速网页开发框架，接收 HTTP 请求，通过 WSGI 模块 将请求和参数 路由到不同 APP
      （可以理解为后台程序），然后再将 APP 处理结果通过 HTTP 返回到客户端。

#### 增加、删除 逻辑图
![](https://github.com/gujifly/dnscmd/blob/master/dnscmd-img/add_del.jpg)
<br><br>
#### 查询逻辑图
![](https://github.com/gujifly/dnscmd/blob/master/dnscmd-img/query.jpg)
