# coding:utf-8
'''
定义规则 urls:url列表
         type：解析方式,取值 regular(正则表达式),xpath(xpath解析),module(自定义第三方模块解析)
         patten：可以是正则表达式,可以是xpath语句不过要和上面的相对应
'''
from multiprocessing import Value
import os
import random

'''
ip，端口，类型(0高匿名，1透明)，protocol(0 http,1 https),country(国家),area(省市),updatetime(更新时间)
 speed(连接速度)
'''
parserList = [
    {
        'urls': ['http://www.66ip.cn/%s.html' % n for n in ['index'] + list(range(1, 5))],
        'type': 'xpath',
        'pattern': ".//*[@id='main']/div/div[1]/table//tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]', 'protocol': ''}
    },
    {
        'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (m, n) for m in range(1, 35) for n in range(1, 10)],
        'type': 'xpath',
        'pattern': ".//*[@id='footer']/div/table//tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]', 'protocol': ''}
    },
    {
        'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in ['inha', 'intr'] for n in
                 range(1, 11)],
        'type': 'xpath',
        'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]', 'protocol': './td[4]'}
    },
    {
        'urls': ['http://www.freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0'],
        'type': 'xpath',
        'pattern': "//table[@class='DataGrid']//tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]', 'protocol': './td[3]'}
    },
    {
        'urls': ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)],
        'type': 'module',
        'moduleName': 'parser_listPraser',
        'parser':'html'
    },
    {'urls': ['https://ip.ihuan.me/'],
        'type': 'module', 'moduleName': 'parser_ihuan','parser':'lxml'},
    {'urls': ['http://www.ip3366.net/free/?stype=%s' % n for n in range(
        1, 3)], 'type': 'module', 'moduleName': 'parser_3366','parser':'lxml'},
    {'urls': ['http://www.goubanjia.com/'], 'type': 'module',
        'moduleName': 'parser_goubanjia', 'parser':'bs4'},
    {'urls': 'http://www.kxdaili.com/dailiip.html',
        'type': 'module', 'moduleName': 'parser_kaixin','parser':'lxml'},
    {'urls': 'http://www.kxdaili.com/dailiip/2/1.html',
        'type': 'module', 'moduleName': 'parser_kaixin','parser':'lxml'},
    {'urls': 'http://www.nimadaili.com/gaoni/',
        'type': 'module', 'moduleName': 'parser_nima','parser':'lxml'},
    {'urls': 'http://www.nimadaili.com/http/',
        'type': 'module', 'moduleName': 'parser_nima','parser':'lxml'},
    {'urls': 'http://www.nimadaili.com/https/',
        'type': 'module', 'moduleName': 'parser_nima','parser':'lxml'},
    {'urls': 'http://www.data5u.com/', 'type': 'module', 'moduleName': 'parser_da5u','parser':'lxml'},
    
    {'urls': 'http://www.xsdaili.com/', 'type': 'module',
        'moduleName': 'parser_xsdaili','parser':'lxml'},  # 需要爬取二级网页，已解决
    
    {'urls': 'http://www.66ip.cn/mo.php?tqsl=2048', 'type': 'module',
        'moduleName': 'parser_66ip', 'parser': 'bs4'},  # 需要js解密，已解决
    {'urls': 'https://proxy.seofangfa.com/',
        'type': 'module', 'moduleName': 'parser_sff','parser':'lxml'},
    {'urls': 'http://cool-proxy.net/proxies.json',
        'type': 'module', 'moduleName': 'parser_cool','parser':'html'},
    {'urls': ['http://www.proxylists.net/%s' % p for p in ['http_highanon.txt',
                                                           'https_highanon.txt']], 
                                                           'parser':'html', 'type': 'module', 'moduleName': 'parser_proxyls'},
    {'urls': 'http://www.mrhinkydink.com/proxies.htm',
        'type': 'module', 'moduleName': 'parser_mrhin','parser':'lxml'},
    
    # {'urls': ['https://proxy.mimvp.com/%s' % p for p in ['freeopen', 'freesole',
    #                                                      'freesecret']], 'type': 'module', 'moduleName': 'parser_mipu','parser':'lxml'},  # 需要图片识别端口，已解决
    # {'urls': 'https://ip.jiangxianli.com/blog.html',
    #     'type': 'module', 'moduleName': 'parser_jxl','parser':'lxml'},  # 需要爬取二级网页，有问题
]


'''
数据库的配置
'''
DB_CONFIG = {

    'DB_CONNECT_TYPE': 'sqlalchemy',  # 'pymongo'sqlalchemy;redis
    # 'DB_CONNECT_STRING':'mongodb://localhost:27017/'
    'DB_CONNECT_STRING': 'sqlite:///' + os.path.dirname(__file__) + '/data/proxy.db'
    # 'DB_CONNECT_STRING' : 'mysql+mysqldb://ipxyz:1qaz!QAZ2wsx@45.76.159.146/proxy?charset=utf8'
    # 'DB_CONNECT_TYPE': 'redis',  # 'pymongo'sqlalchemy;redis
    # 'DB_CONNECT_STRING': 'redis://localhost:6379/8',
}

CHINA_AREA = ['河北', '山东', '辽宁', '黑龙江', '吉林', '甘肃', '青海', '河南', '江苏', '湖北', '湖南',
              '江西', '浙江', '广东', '云南', '福建',
              '台湾', '海南', '山西', '四川', '陕西',
              '贵州', '安徽', '重庆', '北京', '上海', '天津', '广西', '内蒙', '西藏', '新疆', '宁夏', '香港', '澳门']
QQWRY_PATH = os.path.dirname(__file__) + "/data/qqwry.dat"

THREADNUM = 1
API_PORT = 5000
'''
爬虫爬取和检测ip的设置条件
不需要检测ip是否已经存在，因为会定时清理
'''
UPDATE_TIME = 60 * 60  # 每一个小时检测一次是否有代理ip失效
MINNUM = 300  # 当有效的ip值小于一个时 需要启动爬虫进行爬取
HISTORY_KEEP_DAYS = 7  # IP代理历史保存的天数，如果超过这个时间，都删除

TIMEOUT = 15  # socket延时

'''
反爬虫的设置
'''
'''
重试次数
'''
RETRY_TIME = 3

'''
收集历史数据到HISTORY表
'''
COLLECT_HISTORY = True

'''
USER_AGENTS 随机头信息
'''
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


def get_header():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }


TEST_PROXY_URLS = [

    # 下面的是主流搜索引擎搜ip的网址，相对比较开放，而且查询结果比较准确
    {'url': 'https://www.baidu.com/s?wd=ip', 'type': 'baidu'},
    {'url': 'https://www.sogou.com/web?query=ip', 'type': 'sogou'},
    {'url': 'https://www.so.com/s?q=ip&src=srp&fr=none&psid=2d511001ad6e91af893e0d7e561f1bba', 'type': 'so'},
    {'url': 'https://mijisou.com/?q=ip&category_general=on&time_range=&language=zh-CN&pageno=1', 'type': 'miji'},

    # 下面的是专门查询本机公网ip的网址，请求不能过于频繁
    {'url': 'http://pv.sohu.com/cityjson', 'type': 'sohu'},
    {'url': 'http://ip.taobao.com/ipSearch.html', 'type': 'taobao'},
    {'url': 'https://myip.ipip.net/', 'type': 'myip'},
    {'url': 'http://httpbin.org/ip', 'type': 'httpbin'},
    {'url': 'http://ip.chinaz.com/', 'type': 'chinaz'},
    {'url': 'https://www.ipip.net/ip.html', 'type': 'ipip'},
    {'url': 'https://ip.cn/', 'type': 'ipcn'},
    {'url': 'https://tool.lu/ip/', 'type': 'luip'},
    {'url': 'http://api.online-service.vip/ip/me', 'type': 'onlineservice'},
    {'url': 'https://ip.ttt.sh/', 'type': 'ttt'},
]

TEST_IP = 'http://httpbin.org/ip'
TEST_HTTP_HEADER = 'http://httpbin.org/get'
TEST_HTTPS_HEADER = 'https://httpbin.org/get'

APP_SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
