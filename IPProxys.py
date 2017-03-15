#coding:utf-8
import BaseHTTPServer
import threading
import logging
import logging.config

from api.apiServer import start_api_server
from config import API_PORT
from spider.ProxySpider import start_spider


import sys
reload(sys)
sys.setdefaultencoding('utf8')

logging.config.fileConfig('logging.conf')


if __name__ == "__main__":


    apiServer = threading.Thread(target=start_api_server)
    
    apiServer.start()
    start_spider()


