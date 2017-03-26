import unittest
import sys
import logging
logging.basicConfig()
import requests

class TestWebServer(unittest.TestCase):
    def test_api_china(self):
        rsp =requests.get("http://localhost:5000/api/proxy/china",auth=('eyJhbGciOiJIUzI1NiJ9.eyJpZCI6MX0._6jmLfy5i96Ux_fLqIXwTHySY8rdSjvHGJw5VedbZ1I',''))
        self.assertEqual(rsp.status_code, 200)
        print(rsp.text)
        

if __name__ == '__main__':
    unittest.main()
