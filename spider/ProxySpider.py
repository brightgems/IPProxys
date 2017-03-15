#coding:utf-8
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
import requests
import time
from config import THREADNUM, parserList, MINNUM, UPDATE_TIME
from db.DataStore import store_data, sqlHelper
from spider.HtmlDownLoader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from validator.Validator import Validator
import pandas as pd
import logging
logger = logging.getLogger('parser')


'''
这个类的作用是描述爬虫的逻辑
'''

class ProxySpider(object):

    def __init__(self):
        self.crawl_pool = Pool(THREADNUM)

    def run(self):
        while True:
            logger.info("Start to run spider...")
            validator = Validator()
            count = validator.detect_db_proxys()
            logger.info('Finished to run validator, count=%s' % count)
            if count < MINNUM:
                proxys = self.crawl_pool.map(self.crawl,parserList)
                #这个时候proxys的格式是[[{},{},{}],[{},{},{}]]
                proxys_tmp = []
                for proxy in proxys:
                    proxys_tmp.extend(proxy)
                #这个时候应该去重:
                df_proxys = pd.DataFrame.from_records(proxys_tmp)
                logger.info('first_proxys: %s' % len(proxys_tmp))
                #这个时候proxys的格式是[{},{},{},{},{},{}]
                
                #这个时候开始去重:
                df_proxys = df_proxys.drop_duplicates('ip')
                proxys = df_proxys.to_dict(orient='records')
                #proxys = df_proxys
                logger.info('end_proxy: %s' % len(proxys))
                
                proxys = validator.run_list(proxys)#这个是检测后的ip地址

                sqlHelper.batch_insert(proxys)
                proxys = sqlHelper.select()
                logger.info('success ip: %d' % len(proxys))
                sqlHelper.close()
            logger.info('Finished to run spider')
            time.sleep(UPDATE_TIME)


    def crawl(self,parser):
        proxys = []
        html_parser = Html_Parser()
        for url in parser['urls']:
            response = Html_Downloader.download(url)
            if response != None:
                proxylist = html_parser.parse(response,parser)
                if proxylist != None:
                    proxys.extend(proxylist)
        return proxys


def start_spider():
    spider = ProxySpider()
    spider.run()