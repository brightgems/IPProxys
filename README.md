# IPProxys
IPProxys代理池项目，提供代理ip。使用python2.7.x开发

> 本项目在qiyeboy/IPProxyPool项目的分支

## 使用方式
分别启动爬虫和API服务
```
python api/apiServer.py
python IPProxys.py
```

## 支持自动抓取的代理网站

https://free-proxy-list.net/
https://github.com/Eeyhan/IPproxy/blob/master/proxy.py


## 项目依赖
### ubuntu,debian下
<br/>
安装sqlite数据库(一般系统内置):
apt-get install sqlite3
<br/>
安装requests库:
pip install requests
<br/>
安装chardet库:
pip install chardet
<br/>
安装lxml:
apt-get install python-lxml
<br/>
安装gevent库:
pip install gevent
######(有时候使用的gevent版本过低会出现自动退出情况，请使用pip install gevent --upgrade更新)
<br/>
####windows下
下载[sqlite](http://www.sqlite.org/download.html),路径添加到环境变量
<br/>
安装requests库:
pip install requests
<br/>
安装chardet库:
pip install chardet
<br/>
安装lxml:
pip install lxml或者下载[lxml windows版](https://pypi.python.org/pypi/lxml/)
<br/>
安装gevent库:
pip install gevent
######(有时候使用的gevent版本过低会出现自动退出情况，请使用pip install gevent --upgrade更新)

## API 使用方法

#### 模式
```
GET /api
```

####参数 


| Name | Type | Description |
| ----| ---- | ---- |
| types | int | 0: 高匿代理, 1 透明 |
| protocol | int | 0: http, 1 https |
| count | int | 数量 |
| country | str | 国家 |
| area | str | 地区 |



#### 例子
#####IPProxys默认端口为8000
#####如果是在本机上测试：
1.获取5个ip地址在中国的高匿代理：http://127.0.0.1:5000/?types=0&count=5&country=中国
<br/>
2.响应为JSON格式，按照响应速度由高到低，返回数据：
<br/>
[{"ip": "220.160.22.115", "port": 80}, {"ip": "183.129.151.130", "port": 80}, {"ip": "59.52.243.88", "port": 80}, {"ip": "112.228.35.24", "port": 8888}, {"ip": "106.75.176.4", "port": 80}]
<br/>
```
import requests
import json
r = requests.get('http://127.0.0.1:8000/?types=0&count=5&country=中国')
ip_ports = json.loads(r.text)
print ip_ports
ip = ip_ports[0]['ip']
port = ip_ports[0]['port']
proxies={
    'http':'http://%s:%s'%(ip,port),
    'https':'http://%s:%s'%(ip,port)
}
r = requests.get('http://ip.chinaz.com/',proxies=proxies)
r.encoding='utf-8'
print r.text
```
## TODO:
1. API接口增加OAuth认证
2. 简单的查询页面
    
## 更新进度
-----------------------------2017-3-16----------------------------

1. ApiServer使用Flask框架代码重构
2. 在Crawl和Validator两个步骤间采用非阻塞式编程

-----------------------------2016-11-24----------------------------
<br/>
1.增加chardet识别网页编码
<br/>
2.突破66ip.cn反爬限制
<br/>
-----------------------------2016-10-27----------------------------
<br/>
1.增加对代理的检测，测试是否能真正访问到网址，实现代理
<br/>
2.添加通过正则表达式和加载插件解析网页的方式
<br/>
3.又增加一个新的代理网站
<br/>

-----------------------------2017-3-20----------------------------
<br/>
1.增加web API访问接口
<br/>

-----------------------------2018-12-31----------------------------
<br/>
1.更新代理网站配置，删除不能访问的网站
<br/>
-----------------------------2019-04-13----------------------------
<br/>
1.修复存储重复的IP地址问题
2.优化网页性能，只显示30条IP地址
3.升级到python2.7.11，使用sqlite3最新版本以支持sql2标准语法
```
conda update python
```
<br/>
