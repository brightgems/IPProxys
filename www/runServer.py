# coding:utf-8
'''
定义几个关键字，count type,protocol,country,area,

API TEST:
    
'''
import json

from flask import Flask,abort,jsonify, globals,Blueprint, url_for, request,render_template,make_response
from flask_httpauth import HTTPBasicAuth
import config
from db.DataStore import sqlHelper
from filters import pretty_date
from db.SqlHelper import AlchemyEncoder,User
import pandas as pd
import chartkick
import logging
logger = logging.getLogger('api')

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route('/api/register', methods = ['POST'])
def regiser():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if sqlHelper.find_user(username) is not None:
        abort(400) # existing user
    sqlHelper.createUser(username,password)
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    ''' 产生授权码 '''
    token = globals.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@auth.verify_password
def verify_password(username_or_token, password):
    ''' replacement to http_auth verify password'''
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = sqlHelper.find_user(username_or_token)
        if not user or not user.verify_password(password):
            return False
    globals.user = user
    return True

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/")
def index():
    def get_summary_data(proxys):
        json_result = json.dumps(proxys,cls=AlchemyEncoder)
        # load all data
        df = pd.read_json(json_result)
        df['score'] = df['score'].map({0:u'普通',1:u'高速'})
        df['protocol'] = df['protocol'].map({0:u'HTTP',1:u'HTTPS',2:u'Both'})
        # score
        df_score = df.groupby(by='score')['ip'].count()
        proxy_stats_by_score = df_score.to_json()
        # country
        df_country = df.groupby(by='country')['ip'].count()
        proxy_stats_by_country = df_country.to_json()
        # protocol
        df_score = df.groupby(by='protocol')['ip'].count()
        proxy_stats_by_protocol = df_score.to_json()
        # 7 days trend
        ret = sqlHelper.get_stats_7days_history()
        df = pd.DataFrame(ret,columns=('updatetime','score','cnt'))
        df['score'] = df['score'].map({0:u'普通',1:u'高速'})
        df['updt'] = df['updatetime'].map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        json_dict = []
        
        for cat,cat_data in df.groupby('score'):
            grp_dict = {}
            grp_dict['name'] = cat
            grp_dict['data'] = cat_data[['updt','cnt']].values.tolist()
            json_dict.append(grp_dict)
        
        proxy_his_stats = json.dumps(json_dict)
        return proxy_stats_by_score,proxy_stats_by_country,proxy_stats_by_protocol,proxy_his_stats

    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), inputs)
    proxy_stats_by_score,proxy_stats_by_country,proxy_stats_by_protocol,proxy_his_stats = get_summary_data(proxys)
    return render_template("index.html" ,proxys = proxys,
        proxy_stats_by_score=proxy_stats_by_score,
        proxy_stats_by_country = proxy_stats_by_country,
        proxy_stats_by_protocol = proxy_stats_by_protocol,
        proxy_his_stats=proxy_his_stats)

@app.route("/api/proxy/normal")
@auth.login_required
def api_normal_proxys():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), {'score':0})
    proxys_obj = ["%s:%d" % (p.ip, p.port) for p in proxys]
    json_result = json.dumps(proxys_obj)
    return json_result

@app.route("/api/proxy/fast")
@auth.login_required
def api_fast_proxys():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None),{'score':1})
    proxys_obj = ["%s:%d" % (p.ip, p.port) for p in proxys]
    json_result = json.dumps(proxys_obj)
    return json_result

@app.route("/api/proxy/public")
@auth.login_required
def api_public_proxys():
    inputs = request.args
    proxys = sqlHelper.select(count=50,conditions= {'score':0})
    json_result = json.dumps(proxys,cls=AlchemyEncoder)
    return json_result

@app.route("/api/proxy/vip")
@auth.login_required
def api_vip_proxys():
    '''
        vip 方法可以返回全部对象信息，并可指定查询参数
    '''
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), inputs)
    
    json_result = json.dumps(proxys,cls=AlchemyEncoder)
    return json_result

@app.route("/api/proxy/china")
@auth.login_required
def api_china_proxys():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', None), {'country':u'国内','socre':1})
    proxys_obj = ["%s:%d" % (p.ip, p.port) for p in proxys]
    json_result = json.dumps(proxys_obj)
    return json_result

@app.route("/api/proxy/oversee")
@auth.login_required
def api_oversee_proxys():
    inputs = request.args
    proxys = sqlHelper.select(inputs.get('count', 10), {'country':u'国外','socre':1,'protocol':1})
    proxys_obj = ["%s:%d" % (p.ip, p.port) for p in proxys]
    json_result = json.dumps(proxys_obj)
    return json_result

@app.route("/api/delete")
def delete():
    inputs = request.args
    json_result = json.dumps(sqlHelper.delete(inputs),cls=AlchemyEncoder)
    return json_result


# set the secret key.  keep this really secret:
app.secret_key = config.APP_SECRET_KEY
app.static_folder = "static"
app.jinja_env.filters['pretty_date'] = pretty_date
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")
app.run(port=config.API_PORT,debug=True)