import unittest
import sys
import logging
logging.basicConfig()
# project improt
from validator.Validator import Validator


class TestValidator(unittest.TestCase):
    def test_getmyip(self):
        v = Validator(None)
        myIp = v.getMyIP()
        
        self.assertTrue(myIp != None,"get my IP failed! return:%s" % myIp)
        print(myIp)
        

if __name__ == '__main__':
    unittest.main()
