#coding:utf-8
import BaseHTTPServer
import threading
import logging
import logging.config

from config import API_PORT
from spider.ProxySpider import start_spider
from multiprocessing import Process

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
BASE_DIR = os.path.dirname(__file__)
logging.config.fileConfig(os.path.join(BASE_DIR,'logging.conf'))


if __name__ == "__main__":

    start_spider()
    

