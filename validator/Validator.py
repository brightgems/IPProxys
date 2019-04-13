#coding:utf-8
from gevent import monkey
monkey.patch_all()
import datetime
import json    
from lxml import etree
from gevent.pool import Pool
import requests
import urllib2
import time
from config import TEST_URL
import config
from db.SqlHelper import SqlHelper
from requests.exceptions import HTTPError
import math
import logging
logger = logging.getLogger("validator")

from util.exception import Test_URL_Fail

class Validator(object):

    def __init__(self, coroutine_sqlhelper):
        self.sqlHelper = coroutine_sqlhelper
        self.selfip = self.getMyIP()
        self.detect_pool = Pool(config.THREADNUM)

    def detect_db_proxys(self):
        '''
        从数据库中检测
        :return: validated Proxy objects
        '''
        try:
            #删除重复ip
            self.sqlHelper.del_duplicate_ip()
            #接着检测剩余的ip,是否可用
            results = self.sqlHelper.select()
            self.detect_pool.map(self.detect_db_each,results)
            results = self.sqlHelper.select()
            return results #返回最终的数量
        except Exception,e:
            logger.warning(str(e))
            return 0

    def detect_db_each(self,proxy):
        '''
        :param result: 从数据库中检测
        :return:
        '''
        proxy_dict = {'ip': proxy.ip, 'port': proxy.port}
        result = self.detect_proxy(proxy_dict)
        if result:
            result['updatetime']=datetime.datetime.today()
            result.pop('ip')
            result.pop('port')
            ret = self.sqlHelper.update(conditions= proxy_dict,value= result)
        else:
            self.sqlHelper.delete(proxy_dict)


    def detect_proxy(self,proxy):
        '''
        :param proxy: ip字典
        :return:
        '''
        proxy = proxy.copy()
        ip = proxy['ip']
        port = proxy['port']
        proxies = {"http": "http://%s:%s" % (ip,port),"https": "http://%s:%s" % (ip,port)}
        protocol, proxyType, speed = self.checkProxyType(proxies)
        if protocol >= 0:
            proxy['protocol'] = protocol
            proxy['type'] = proxyType
            proxy['speed'] = speed
            proxy['score'] = 1 if speed <= 2 else 0
            logger.info('succeed %s:%s' % (ip,port))
        else:
            logger.debug('failed %s:%s' % (ip,port))
            proxy = None
        
        return proxy


    def checkProxyType(self,proxies):
        '''
        用来检测代理的类型，突然发现，免费网站写的信息不靠谱，还是要自己检测代理的类型
        :param proxies: 代理(0 高匿，1 匿名，2 透明 3 无效代理
        :return:
        '''

        protocol = -1
        types = -1
        speed = -1
        http, http_types, http_speed = self._checkHttpProxy(self.selfip, proxies)
        https, https_types, https_speed = self._checkHttpProxy(self.selfip, proxies, False)
        if http and https:
            protocol = 2
            types = http_types
            speed = http_speed
        elif http:
            types = http_types
            protocol = 0
            speed = http_speed
        elif https:
            types = https_types
            protocol = 1
            speed = https_speed
        else:
            types = -1
            protocol = -1
            speed = -1
        return protocol, types, speed

    def _checkHttpProxy(self,selfip, proxies, isHttp=True):
        types = -1
        speed = -1
        if isHttp:
            test_url = config.TEST_HTTP_HEADER
        else:
            test_url = config.TEST_HTTPS_HEADER
        try:
            start = time.time()
            r = requests.get(url=test_url, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
            if r.ok:
                speed = round(time.time() - start, 2)
                content = json.loads(r.text)
                headers = content['headers']
                ip = content['origin']
                x_forwarded_for = headers.get('X-Forwarded-For', None)
                x_real_ip = headers.get('X-Real-Ip', None)
                if selfip in ip:
                    return False, types, speed
                elif x_forwarded_for is None and x_real_ip is None:
                    types = 0
                elif selfip not in x_forwarded_for and selfip not in x_real_ip:
                    types = 1
                else:
                    types = 2
                return True, types, speed
            else:
                return False, types, speed
        except Exception, e:
            return False, types, speed
            logger.warning(str(e))



    def getMyIP(self):
        try:
            r = requests.get(url=config.TEST_IP, headers=config.get_header(), timeout=10)
            ip = json.loads(r.text)
            return ip['origin'].split(',')[0]
        except HTTPError as e:
            raise Test_URL_Fail

if __name__ == '__main__':
    v = Validator()
    v.getMyIP()
    v.selfip
