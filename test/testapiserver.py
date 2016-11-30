import unittest
import logging
from api.apiServer import WebRequestHandler
import BaseHTTPServer
from config import API_PORT


class TestApiServer(unittest.TestCase):

    def test_start_api_server(self):
        logging.info('Start server @ %s:%s' %('0.0.0.0',API_PORT))
        server = BaseHTTPServer.HTTPServer(('0.0.0.0',API_PORT), WebRequestHandler)
        server.serve_forever()

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
                                        