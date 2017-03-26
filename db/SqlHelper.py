# coding:utf-8
import datetime
from sqlalchemy import text,Column,Index, Integer, String, DateTime, Numeric, create_engine, VARCHAR,NVARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_CONFIG
from sqlalchemy.ext.declarative import DeclarativeMeta
from db.ISqlHelper import ISqlHelper
import sqlalchemy as db
import json
from passlib.apps import custom_app_context as pwd_context
from util.singleton import SingletonMetaClass
from itsdangerous import JSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from config import APP_SECRET_KEY
import logging

'''
sql操作的基类
包括ip，端口，types类型(0高匿名，1透明)，protocol(0 http,1 https http),country(国家),area(省市),updatetime(更新时间)
 speed(连接速度)
'''

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key = True)
    username = db.Column(String(32), index = True)
    password_hash = db.Column(String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        s = Serializer(APP_SECRET_KEY)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(APP_SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        sqlhelper = SqlHelper()
        user = sqlhelper.find_user_by_id(data['id'])
        return user 

class Proxy(BaseModel):
    __tablename__ = 'proxys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    types = Column(Integer, nullable=False)
    protocol = Column(Integer, nullable=False, default=0)
    country = Column(NVARCHAR(100), nullable=False)
    area = Column(NVARCHAR(100), nullable=False)
    createtime = Column(DateTime(), default=datetime.datetime.now)
    updatetime = Column(DateTime(), default=datetime.datetime.now)
    speed = Column(Numeric(5, 2), nullable=False)
    score = Column(Integer, nullable=False, default=0) # 0:normal(speed>2s) 1:good(speed<=2s)
Index('idx_proxy_ip_port',Proxy.ip,Proxy.port)

class ProxyHistory(BaseModel):
    __tablename__ = 'proxy_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    types = Column(Integer, nullable=False)
    protocol = Column(Integer, nullable=False, default=0)
    country = Column(NVARCHAR(100), nullable=False)
    area = Column(NVARCHAR(100), nullable=False)
    updatetime = Column(DateTime())
    speed = Column(Numeric(5, 2), nullable=False)
    score = Column(Integer, nullable=False, default=0)
Index('idx_proxyhis_ip_port',ProxyHistory.ip,ProxyHistory.port)    

def with_session(fn):
    def go(self,*args, **kw):
        try:
            ret = fn(self,*args, **kw)
            
            self.session.commit()
            return ret
        except Exception, ex:
            self.session.rollback()
            raise
    return go

class SqlHelper(ISqlHelper):

    __metaclass__ = SingletonMetaClass

    params = {'ip': Proxy.ip, 'port': Proxy.port, 'types': Proxy.types, 'protocol': Proxy.protocol,'speed':Proxy.speed,
              'country': Proxy.country, 'area': Proxy.area, 'score': Proxy.score,'updatetime':Proxy.updatetime}

    def __init__(self):
        if 'sqlite' in DB_CONFIG['DB_CONNECT_STRING']:
            connect_args = {'check_same_thread': False}
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False, connect_args=connect_args)
        else:
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False)
        DB_Session = sessionmaker(bind=self.engine)

        self.session = DB_Session()
        self.logger = logging.getLogger("db")

    def init_db(self):
        BaseModel.metadata.create_all(self.engine)

    def drop_db(self):
        BaseModel.metadata.drop_all(self.engine)

    def find_user(self,username):
        u = self.session.query(User).filter(User.username == username).first()
        return u

    def find_user_by_id(self,id):
        u = self.session.query(User).filter(User.id == id).first()
        return u

    @with_session
    def createUser(self,username,password):
        '''
        create new user
        '''
        user = User(username = username)
        user.hash_password(password)
        self.session.add(user)
        self.session.commit()

    @with_session
    def insert(self, value):
        """
            create or replace proxy
        """
        p_ = self.session.query(Proxy).filter(Proxy.id == value['ip'], Proxy.port == value['port']).first()
        if p_:
            print(p_)
            p_.speed = value['speed']
            p_.score = value['score']
            p_.updatetime = datetime.datetime.now()
        else:
            proxy = Proxy(ip=value['ip'], port=value['port'], types=value['types'], protocol=value['protocol'],
                            country=value['country'],area=value['area'], 
                            speed=value['speed'],score=value['score'])
            self.session.add(proxy)
        self.session.commit()

    @with_session
    def batch_insert(self,values):
        objects = [Proxy(ip=value['ip'], port=value['port'], types=value['types'], protocol=value['protocol'],
                        country=value['country'],score = value['score'],
                        area=value['area'], speed=value['speed']) for value in values]
        self.session.bulk_save_objects(objects)
        self.session.commit()
    
    @with_session
    def delete(self, conditions=None):
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            deleteNum = query.delete()
            self.session.commit()
        else:
            deleteNum = 0
        return ('deleteNum', deleteNum)

    def delete_all(self, values):
        
        self.session.commit()

    @with_session
    def update(self, conditions=None, value=None):
        '''
        conditions的格式是个字典。类似self.params
        :param conditions:
        :param value:也是个字典：{'ip':192.168.0.1}
        :return:
        '''
        if conditions and value:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
            query = self.session.query(Proxy)
            for condition in conditions:
                query = query.filter(condition)
            updatevalue = {}

            for key in list(value.keys()):
                if self.params.get(key, None):
                    updatevalue[self.params.get(key, None)] = value.get(key)
            
            updateNum = query.update(updatevalue)
            self.session.commit()            
        else:
            updateNum = 0
        return {'updateNum': updateNum}

    @with_session
    def copy_history(self):
        '''
        Copy Proxy to ProxyHistory    
        '''
        
        sql = text("insert into proxy_history(ip,port,types,protocol,country,area,updatetime,speed,score)" + "\nselect ip,port,types,protocol,country,area,'%s',speed,score from proxys" % datetime.datetime.today().isoformat())
        self.session.execute(sql)

    def select(self, count=None, conditions=None):
        '''
        conditions的格式是个字典。类似self.params
        :param count:
        :param conditions:
        :return:
        '''
        if conditions:
            conditon_list = []
            for key in list(conditions.keys()):
                if self.params.get(key, None):
                    conditon_list.append(self.params.get(key) == conditions.get(key))
            conditions = conditon_list
        else:
            conditions = []

        query = self.session.query(Proxy)
        if len(conditions) > 0 and count:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc(), Proxy.speed).limit(count).all()
        elif count:
            return query.order_by(Proxy.score.desc(), Proxy.speed).limit(count).all()
        elif len(conditions) > 0:
            for condition in conditions:
                query = query.filter(condition)
            return query.order_by(Proxy.score.desc(), Proxy.speed).all()
        else:
            return query.order_by(Proxy.score.desc(), Proxy.speed).all()


    def close(self):
        pass


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
    sqlhelper = SqlHelper()
    sqlhelper.init_db()
    proxy = {'ip': '192.168.1.1', 'port': 80, 'type': 0, 'protocol': 0, 'country': '中国', 'area': '广州', 'speed': 11.123, 'types': ''}
    sqlhelper.insert(proxy)
    sqlhelper.update({'ip': '192.168.1.1', 'port': 80}, {'score': 10})
    print(sqlhelper.select(1))
