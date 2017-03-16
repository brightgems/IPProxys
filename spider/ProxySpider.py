#coding:utf-8
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from gevent.queue import Queue,Empty
import gevent

import requests
import time
from config import THREADNUM, parserList, MINNUM, UPDATE_TIME
from db.DataStore import store_data, sqlHelper
from spider.HtmlDownLoader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from validator.Validator import Validator
import logging
logger = logging.getLogger('spider')


'''
这个类的作用是描述爬虫的逻辑
'''

class ProxySpider(object):

    def __init__(self):
        self.crawl_tasks = []
        self.validate_tasks = []
        self.queue = Queue()

    def run(self):
        while True:
            logger.info("Start to run spider...")
            t1 = time.time()
            validator = Validator()
            count = validator.detect_db_proxys()
            logger.info('Finished to validate db proxy, count=%s' % count)
            if count < MINNUM:
                self.crawl_tasks = [gevent.spawn(self.crawl,each_site,self.queue) for each_site in parserList]
                self.validate_tasks = [gevent.spawn_later(5,self.validate,self.queue) for i in range(THREADNUM)]
                gevent.joinall(self.crawl_tasks + self.validate_tasks)
                proxys = sqlHelper.select()
                logger.info('success ip: %d' % len(proxys))
                sqlHelper.close()
            logger.info('Finished to run spider')
            t2=time.time()
            logger.info("Finish run spider in %fs",t2-t1)
            time.sleep(UPDATE_TIME)


    def crawl(self,parser,queue):
        html_parser = Html_Parser()
        for url in parser['urls']:
            response = Html_Downloader.download(url)
            if response != None:
                proxylist = html_parser.parse(response,parser)
                if proxylist != None:
                    for each in proxylist:
                        queue.put_nowait(each)

    def validate(self,queue):
        validator = Validator()
        try:
            while True:
                proxy = queue.get(timeout=15) # decrements queue size by 1
                proxy_validated = validator.detect_proxy(proxy)
                if proxy_validated:
                    sqlHelper.insert(proxy_validated)
                gevent.sleep(0)
        except Empty:
            print('Quitting time!') 

def start_spider():
    spider = ProxySpider()
    spider.run()