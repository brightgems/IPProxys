import unittest
import logging
from db.DataStore import sqlHelper

class TestSqlHelper(unittest.TestCase):
    def test_update_proxy(self):
        sqlHelper.update({'ip':'42.81.58.199','port':80},{'score':1})


if __name__ == '__main__':
    unittest.main()
                                        