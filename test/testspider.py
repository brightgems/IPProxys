import unittest
import logging
from spider.ProxySpider import ProxySpider
from api.apiServer import WebRequestHandler

class TestSpider(unittest.TestCase):
    def test_start_spider(self):
        logging.info('Start Spider')
        spider = ProxySpider()
        spider.run()


if __name__ == '__main__':
    unittest.main()
                                        