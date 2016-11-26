import unittest
import sys
sys.path.append('..')
import logging
logging.basicConfig()
# project improt
from validator.Validator import Validator


class Test_testvalidator(unittest.TestCase):
    def test_getmyip(self):
        v = Validator(None)
        myIp = v.getMyIP()
        self.assertIsNotNone(myIp,"get my IP failed! return:%s" % myIp)
        

if __name__ == '__main__':
    unittest.main()
