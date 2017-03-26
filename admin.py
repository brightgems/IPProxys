import unittest
import logging
from db.DataStore import sqlHelper
from db.SqlHelper import User
import argparse

'''
usage: 
    python admin.py -u mars.yu@omnicommediagroup.com 1qz@WSX
    python admin.py -t mars.yu@omnicommediagroup.com
    python admin.py -a eyJhbGciOiJIUzI1NiJ9.eyJpZCI6MX0._6jmLfy5i96Ux_fLqIXwTHySY8rdSjvHGJw5VedbZ1I
'''

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Jimu Box Utility command')
    parser.add_argument('-r','--register',nargs=2, help='register user')
    parser.add_argument('-t','--tokenize', help='generate auth token')
    parser.add_argument('-a','--authorize', help='authorize token')
    args = parser.parse_args()
    if args.register:
        sqlHelper.createUser(args.register[0],args.register[1])
    elif args.tokenize:
        u = sqlHelper.find_user(args.tokenize)
        if u:
            t = u.generate_auth_token()
            print(t)
    elif args.authorize:
            u = User.verify_auth_token(args.authorize)
            if u:
                print('OK')