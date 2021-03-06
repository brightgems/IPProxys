# coding:utf-8
import sys
from util.exception import Con_DB_Fail


try:
    from db.SqlHelper import SqlHelper as SqlHelper
    sqlHelper = SqlHelper()
    sqlHelper.init_db()
except Exception as e:
    print(str(e))
    raise Con_DB_Fail



def store_data(queue2, db_proxy_num):

    successNum = 0
    failNum = 0
    while True:
        try:
            proxy = queue2.get(timeout=300)
            if proxy:

                sqlHelper.insert(proxy)
                successNum += 1
            else:
                failNum += 1
            str = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
            sys.stdout.write(str + "\r")
            sys.stdout.flush()
        except BaseException as e:

            if db_proxy_num.value != 0:
                successNum += db_proxy_num.value
                db_proxy_num.value = 0
                str = 'IPProxyPool----->>>>>>>>Success ip num :%d,Fail ip num:%d' % (successNum, failNum)
                sys.stdout.write(str + "\r")
                sys.stdout.flush()
                successNum = 0
                failNum = 0
