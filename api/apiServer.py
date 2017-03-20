# coding:utf-8
'''
定义几个关键字，count type,protocol,country,area,
'''
import json
import sys

from flask import Flask, session, redirect, url_for, escape, request,render_template
import config
from db.DataStore import sqlHelper
from filters import pretty_date
from db.SqlHelper import AlchemyEncoder

import logging
logger = logging.getLogger('api')

app = Flask(__name__)

@app.route("/")
def index():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), inputs)
    return render_template("index.html" ,proxys = proxys)

@app.route("/api")
def api():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), inputs)
    proxys_obj = [{'ip':p.ip,'port':p.port} for p in proxys]
    json_result = json.dumps(proxys_obj)
    return json_result

@app.route("/api/delete")
def delete():
    inputs = request.args
    json_result = json.dumps(sqlHelper.delete(inputs),cls=AlchemyEncoder)
    return json_result


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.static_folder = "static"
app.jinja_env.filters['pretty_date'] = pretty_date
app.run(port=config.API_PORT,debug=True)