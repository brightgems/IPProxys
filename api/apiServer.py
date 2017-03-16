# coding:utf-8
'''
定义几个关键字，count type,protocol,country,area,
'''
import json
import sys
from flask import Flask, session, redirect, url_for, escape, request
import config
from db.DataStore import sqlHelper

import logging
logger = logging.getLogger('api')

app = Flask(__name__)


@app.route("/api")
def index():
    inputs = request.args
    json_result = json.dumps(sqlHelper.select(inputs.get('count', None), inputs))
    return json_result

@app.route("/api/delete")
def delete():
    inputs = request.args
    json_result = json.dumps(sqlHelper.delete(inputs))
    return json_result


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.run(port=config.API_PORT)