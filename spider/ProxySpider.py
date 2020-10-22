#coding:utf-8
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from gevent.queue import Queue,Empty
import gevent

import requests
import time
from config import THREADNUM, parserList, MINNUM, UPDATE_TIME,COLLECT_HISTORY,HISTORY_KEEP_DAYS
from db.DataStore import sqlHelper
from spider.HtmlDownLoader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from validator.Validator import Validator
from util.bloomfilter import BloomFilter
from datetime import datetime,timedelta
from db.SqlHelper import SqlHelper
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
        self.repo = None # init inside run
        
    def init_repo(self,ls_valid):
        '''
            init repository that port:ip has validated when db validation finished
        '''
        self.repo = BloomFilter()
        if type(ls_valid) != list:
            logger.warn('wrong ls_valid:'+str(ls_valid))
            return
        for each in ls_valid:
            ip = "%s:%s" % (each.ip, each.port)
            self.repo.add(ip)

    def run(self):
        lastdeltm = datetime.now()
        while True:
            if COLLECT_HISTORY and lastdeltm + timedelta(days=1) >datetime.now():
                sqlHelper.delete_history(HISTORY_KEEP_DAYS)
                lastdeltm = datetime.now()    
            logger.info("Start to run spider...")
            t1 = time.time()
            validator = Validator(sqlHelper)
            ls_valid = validator.detect_db_proxys()
            valid_cnt = len(ls_valid) if ls_valid else 0
            self.init_repo(ls_valid)
            logger.info('Finished to validate db proxy, count=%s' % valid_cnt)
            if valid_cnt < MINNUM:
                self.crawl_tasks = [gevent.spawn(self.crawl,each_site,self.queue) for each_site in parserList]
                self.validate_tasks = [gevent.spawn_later(5,self.validate,self.queue) for i in range(THREADNUM)]
                gevent.joinall(self.crawl_tasks + self.validate_tasks)
                proxys = sqlHelper.select()
                logger.info('success ip: %d' % len(proxys))
            # 保存历史记录
            if COLLECT_HISTORY:
                sqlHelper.copy_history()
            logger.info('Finished to run spider')


            t2 = time.time()
            logger.info("Finish run spider in %fs",t2 - t1)
            time.sleep(UPDATE_TIME)


    def crawl(self,parser,queue):
        html_parser = Html_Parser()
        urls =parser['urls']
        if type(urls) is not list:
            urls = [urls]
        for url in urls:
            response = Html_Downloader.download(url)
            import pdb; pdb.set_trace()
            if response != None:
                proxylist = html_parser.parse(response,parser)
                if proxylist != None:
                    for each in proxylist:
                        
                        ip = "%s:%s" % (each['ip'], each['port'])
                        if not ip in self.repo:
                            self.repo.add(ip)
                            queue.put_nowait(each)
                            logger.debug("duplicate ip:%s" % ip)

    def validate(self,queue):
        coroutine_sqlhelper = SqlHelper()
        validator = Validator(coroutine_sqlhelper)
        try:
            while True:
                proxy = queue.get(timeout=15) # decrements queue size by 1
                proxy_validated = validator.detect_proxy(proxy)
                if proxy_validated:
                    coroutine_sqlhelper.insert(proxy_validated)
                gevent.sleep(0.1)
        except Empty:
            print('Quitting time!') 

def start_spider():
    spider = ProxySpider()
    spider.run()