# coding:utf-8
import config


class Test_URL_Fail(Exception):
    def __str__(self):
        str = "IP test failed:" % config.TEST_IP
        return str


class Con_DB_Fail(Exception):
    def __str__(self):
        str = "db connection failed: `DB_CONNECT_STRING` " % config.DB_CONNECT_STRING
        return str