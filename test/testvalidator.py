import unittest
import sys
import logging
logging.basicConfig()
# project improt
from validator.Validator import Validator


class TestValidator(unittest.TestCase):
    def test_getmyip(self):
        v = Validator()
        myIp = v.getMyIP()
        
        self.assertTrue(myIp != None,"get my IP failed! return:%s" % myIp)
        print(myIp)

    def test_detect_proxy(self):
        v = Validator()
        p=v.detect_proxy({'ip':'42.81.58.199','port':80})      
        self.assertTrue('score' in p.keys())

if __name__ == '__main__':
    unittest.main()
