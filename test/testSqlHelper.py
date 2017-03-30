# coding: utf8

import unittest
import logging
from db.DataStore import sqlHelper
from db.SqlHelper import AlchemyEncoder,ProxyHistory
import json
import pandas as pd
import itertools

class TestSqlHelper(unittest.TestCase):
    def test_update_proxy(self):
        sqlHelper.update({'ip':'42.81.58.199','port':80},{'score':1})

    def test_get_summary(self):
        proxys = sqlHelper.select(None, None)
        json_result = json.dumps(proxys,cls=AlchemyEncoder)
        
        df = pd.read_json(json_result)
        score_map = {0:u'普通',1:u'高速'}
        df['score'] = df['score'].map(score_map)
        df_score = df.groupby(by='score')['ip'].count()
        proxy_stats_by_socre = df_score.to_json()
        print(proxy_stats_by_socre)
        
    def test_get_hist_trends(self):
        ret= sqlHelper.get_stats_7days_history()
        df=pd.DataFrame(ret,columns=('updatetime','score','cnt'))
        df['score'] = df['score'].map({0:u'普通',1:u'高速'})
        df['updt'] = df['updatetime'].map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        json_dict = []
        
        for cat,cat_data in df.groupby('score'):
            grp_dict = {}
            grp_dict['name'] = cat
            grp_dict['data'] =cat_data[['updt','cnt']].values.tolist()
            json_dict.append(grp_dict)
        
        print(json.dumps(json_dict))

    def test_delete_history(self):
        sqlHelper.delete_history()

if __name__ == '__main__':
    unittest.main()
                                        