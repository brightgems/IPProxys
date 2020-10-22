#coding:utf-8

import random
import config
import json
__author__ = 'Xaxdus'

import requests
import logging
from db.DataStore import sqlHelper

logger = logging.getLogger('download')

class Html_Downloader(object):

    @classmethod
    def download(self,url):
        count = 0#重试次数
        r = ''
        logger.info("downloading url: %s",url)
        ls_p = sqlHelper.select(count=10,conditions= {'protocol':1, 'score':1})
        while count < config.RETRY_TIME:
            if r == '' or (not r.ok) or len(r.content) < 500 :
                if count==config.RETRY_TIME-1 :
                    choose = random.choice(ls_p)
                    proxies = {"https": "http://%s:%s" % (choose.ip,choose.port)}
                else:
                    proxies = {}
                try:
                    r = requests.get(url=url,headers=config.get_header(),timeout=config.TIMEOUT,proxies=proxies)
                    r.encoding = 'gbk'
                    count += 1
                except Exception,e:
                    import pdb; pdb.set_trace()
                    count += 1

            else:
                return r.text

        return None










