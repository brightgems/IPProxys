# coding:utf-8
import re
import json
import base64
import requests
import js2py
from lxml import etree
from bs4 import BeautifulSoup

from config import QQWRY_PATH, CHINA_AREA, get_header
from util.IPAddress import IPAddresss
from util.compatibility import text_

__author__ = 'qiye'
from lxml import etree

class Html_Parser(object):
    def __init__(self):
        self.ips = IPAddresss(QQWRY_PATH)

    def parse(self, response, parser):
        '''
        :param response: 响应
        :param type: 解析方式
        :return:
        '''
        if parser['type'] == 'xpath':
            return self.XpathPraser(response, parser)
        elif parser['type'] == 'regular':
            return self.RegularPraser(response, parser)
        elif parser['type'] == 'module':
            if parser.get('parser') == 'bs4':
                html = BeautifulSoup(response, "lxml")
                return getattr(self, parser['moduleName'], None)(html)
            if parser.get('parser') == 'lxml':
                html = etree.HTML(response)
                return getattr(self, parser['moduleName'], None)(html)
            else:
                return getattr(self, parser['moduleName'], None)(response)
        else:
            return None

    def AuthCountry(self, addr):
        '''
        用来判断地址是哪个国家的
        :param addr:
        :return:
        '''
        for area in CHINA_AREA:
            if text_(area) in addr:
                return True
        return False

    
    def collect_ip_info(self, ip, port):
        type = 0
        protocol = 0
        addr = self.ips.getIpAddr(self.ips.str2ip(ip))
        country = text_('')
        area = text_('')
        # print(ip,port)
        if text_('省') in addr or self.AuthCountry(addr):
            country = text_('国内')
            area = addr
        else:
            country = text_('国外')
            area = addr
        proxy = {'ip': ip, 'port': int(port), 'types': type, 'protocol': protocol, 'country': country,
                    'area': area, 'speed': 100}
        return proxy

    def XpathPraser(self, response, parser):
        '''
        针对xpath方式进行解析
        :param response:
        :param parser:
        :return:
        '''
        proxylist = []
        root = etree.HTML(response)
        proxys = root.xpath(parser['pattern'])
        for proxy in proxys:
            try:
                ip = proxy.xpath(parser['position']['ip'])[0].text
                port = proxy.xpath(parser['position']['port'])[0].text
                proxy = self.collect_ip_info(ip,port)
                proxylist.append(proxy)
            except Exception as e:
                continue
        return proxylist

    def RegularPraser(self, response, parser):
        '''
        针对正则表达式进行解析
        :param response:
        :param parser:
        :return:
        '''
        proxylist = []
        pattern = re.compile(parser['pattern'])
        matchs = pattern.findall(response)
        if matchs != None:
            for match in matchs:
                try:
                    ip = match[parser['position']['ip']]
                    port = match[parser['position']['port']]
                    # 网站的类型一直不靠谱所以还是默认，之后会检测
                    proxy = self.collect_ip_info(ip,port)
                    proxylist.append(proxy)
                except Exception as e:
                    continue
            return proxylist


    def parser_listPraser(self, response):
        proxylist = []
        pattern = re.compile(r'Proxy\(.+\)')
        matchs = pattern.findall(response)
        if matchs:
            for match in matchs:
                try:
                    ip_port = base64.b64decode(match.replace("Proxy('", "").replace("')", ""))
                    ip,port = ip_port.split(':')
                    proxy = self.collect_ip_info(ip,port)
                except Exception as e:
                    continue

                proxylist.append(proxy)
            return proxylist

    def solve_66ip(self, response):
        """
        处理66ip的js加密
        :param response: 第一次请求返回的js数据
        :return: 返回解密好的网页数据
        """

        cookie = response.headers["Set-Cookie"]
        js = response.text.encode("utf8").decode("utf8")

        js = js.replace("<script>", "").replace("</script>", "").replace("{eval(", "{var data1 = (").replace(chr(0),
                                                                                                             chr(32))

        # 使用js2py处理js
        context = js2py.EvalJs()
        context.execute(js)
        js_temp = context.data1
        index1 = js_temp.find("document.")
        index2 = js_temp.find("};if((")
        # print('11', js_temp[index1:index2])
        js_temp = js_temp[index1:index2].replace("document.cookie", "data2")
        # print('22', js_temp)
        try:
            context.execute(js_temp)
        except:
            # time.sleep(2)
            # context.execute(js_temp)
            pass

        data = context.data2

        # 合并cookie，重新请求网站。
        cookie += ";" + data
        response = requests.get("http://www.66ip.cn/mo.php?tqsl=1024", headers={
            "User-Agent": get_header(),
            "cookie": cookie
        }, timeout=(3, 7))
        return response

    def parser_66ip(self, html):
        """
        解析66ip的代理
        :param html: beautifulsoup对象
        :return:
        """
        proxylist = []
        res = html.find('p').stripped_strings
        for item in res:
            if '$' in item or '}' in item:
                continue
            ip, port = item.split(':')
            proxy = self.collect_ip_info(ip,port)
            proxylist.append(proxy)
        return proxylist

    def parser_ihuan(self, etree_html):
        """小幻代理，访问过于频繁的话会限流"""
        proxylist = []
        res = etree_html.xpath('//div[@class="table-responsive"]/table/tbody/tr')
        for item in res:
            ip = item.xpath('string(./td)')
            xpath_data = item.xpath('./td/text()')
            port = xpath_data[0]
            proxy = self.collect_ip_info(ip,port)
            proxylist.append(proxy)
        return proxylist

    
    def parser_3366(self, etree_html):
        """
        3366代理解析
        :param etree_html: etree对象
        :return:
        """
        proxylist = []
        res = etree_html.xpath('//*[@id="list"]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0]
            port = xpath_data[1]
            proxy = self.collect_ip_info(ip,port)
            proxylist.append(proxy)
        return proxylist

    def parser_goubanjia(self, html):
        """
        解析goubanjia代理
        :param html: 网站源码
        :return:
        """
        proxylist = []
        soup = html.select('.table.table-hover tbody tr')
        for item in soup:
            td_list = item.select('td[class="ip"]')
            for td in td_list:
                child_list = td.find_all()
                text = ""
                for child in child_list:
                    if 'style' in child.attrs.keys():
                        if child.attrs['style'].replace(' ', '') == "display:inline-block;":
                            if child.string is not None:
                                text = text + child.string
                    # 过滤出端口号
                    elif 'class' in child.attrs.keys():
                        class_list = child.attrs['class']
                        if 'port' in class_list:
                            port = self.decrypt_port(class_list[1])
                            # 拼接端口
                            text = text + ":" + str(port)
                    else:
                        if child.string != None:
                            text = text + child.string
                ip,port=text.split(":")
                proxy = self.collect_ip_info(ip, port)
                proxylist.append(proxy)
        return proxylist

    def parser_kaixin(self, html):
        """
        开心代理解析
        :param html: etree对象
        :return:
        """
        proxylist=[]
        res = html.xpath('//div[@class="hot-product-content"]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip, port = xpath_data[0] , xpath_data[1]
            proxy = self.collect_ip_info(ip, port)
            proxylist.append(proxy)
        return proxylist

    def parser_jisu(self, html):
        """
        极速代理解析
        :param html: etree对象
        :return:
        """
        proxylist=[]
        res = html.xpath('//tr')[5:]
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip, port = xpath_data[0] , xpath_data[1]
            proxy = self.collect_ip_info(ip, port)
            proxylist.append(proxy)
        return proxylist

    def parser_nima(self, html):
        """
        尼玛代理解析
        :param html: etree对象
        :return:
        """
        proxylist=[]
        res = html.xpath('//table/tbody/tr')
        # print(len(res))
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip, port = xpath_data[0].split(':')
            proxy = self.collect_ip_info(ip, port)
            proxylist.append(proxy)
        return proxylist

    def decrypt_port(self, port_word):
        """
        解密被加密的真实端口号，该字段放在标签的属性里
        :param port_word: 加密字段
        :return:
        """
        word = list(port_word)
        num_list = []
        for item in word:
            num = 'ABCDEFGHIZ'.find(item)
            num_list.append(str(num))
        port = int("".join(num_list)) >> 0x3
        return port

    def parser_da5u(self, html):
        """
        da5u代理解析
        :param html:
        :return:
        """

        ports = html.xpath('//li[contains(@class,"port")]')
        port_list = []
        proxylist=[]
        for port in ports:
            encryption_port = port.values()[0].split(' ')[1]
            port = self.decrypt_port(encryption_port)
            port_list.append(port)

        items = html.xpath('//ul[@class="l2"]')
        temp_data = []
        for item in items:
            xpath_data = item.xpath('./span/li/text()')
            ip = xpath_data[0]
            protocal = xpath_data[3]
            temp_data.append([ip, protocal])

        res = zip(temp_data, port_list)
        for item in res:
            ip, port = item[0][0], str(item[1])
            proxy = self.collect_ip_info(ip, port)
            proxylist.append(proxy)
        return proxylist

    def parser_mipu(self, html):
        """
        米扑代理解析 该方法未完善，后续补充
        :param html: etree对象
        :return:
        """
        proxylist=[]
        res = html.xpath('//table[@class="free-proxylist-tbl"]/tbody/tr')

        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip, port = xpath_data[0], xpath_data[1]
            proxy = self.collect_ip_info(ip, port)
            proxylist.append(proxy)
        return proxylist

    
    def parser_xsdaili(self, html):
        """
        小舒代理网站解析
        :param html:
        :return:
        """
        # 爬取每天的最新的
        res = html.xpath('//div[contains(@class,"ips")][position()<3]')
        url_start = 'http://www.xsdaili.com'
        proxylist=[]
        for item in res:
            second_url = url_start + item.xpath('./div[@class="title"]/a/@href')[0]
            result = self.get_xsdaili_result(second_url)
            proxylist.extend(result)

        return proxylist

    def get_xsdaili_result(self, url):
        """
        小舒代理二层网页爬取
        :param url:
        :return:
        """
        headers = get_header()
        response = requests.get(url, headers=headers, timeout=(3, 7), verify=False).content
        try:
            content = response.decode('utf-8')
        except Exception as e:
            # print(e)
            content = response.decode('gb2312')
        etree_html = etree.HTML(content)
        items = etree_html.xpath('//div[@class="cont"]/text()')[:-1]
        proxies = []
        for item in items:
            ip_port, protocal = item.strip().split('@')
            ip, port = ip_port.split(':')
            proxy = self.collect_ip_info(ip, port)
            proxies.append(proxy)
        return proxies

    def parser_jxl(self, html):
        """
        jxl代理网站解析
        :param html:
        :return:
        """
        # 爬取每天的最新的
        proxies = []
        res = html.xpath('//div[@class="contar-wrap"]/div[@class="item"]')
        for item in res:
            second_url = item.xpath('./div/h3/a/@href')[0]
            result = self.get_jxl_result(second_url)
            proxies.extend(result)
        return proxies

    def get_jxl_result(self, url):
        """
        jxl代理二层网页爬取
        :param url:
        :return:
        """
        headers = get_header()
        response = requests.get(url, headers=headers, timeout=(3, 7), verify=False).content
        try:
            content = response.decode('utf-8')
        except Exception as e:
            # print(e)
            content = response.decode('gb2312')
        etree_html = etree.HTML(content)
        items = etree_html.xpath('//div[contains(@class,"item-box")]/p/text()')
        proxies = []
        for item in items:
            ip_port, protocal = item.strip().split('@')
            ip, port = ip_port.split(':')
            proxy = self.collect_ip_info(ip, port)
            proxies.append(proxy)
        return proxies

    def parser_sff(self, html):
        """
        解析seofangfang的代理
        :param html: etree对象
        :return:
        """
        res = html.xpath('//div[@class="table-responsive"]/table/tbody/tr')
        proxies=[]
        for item in res:
            ip = item.xpath('./td[1]/text()')
            ip = ip[0] if ip else ''
            port = item.xpath('./td[2]/text()')
            port = port[0] if port else ''
            if ip and port:
                proxy = self.collect_ip_info(ip, port)
                proxies.append(proxy)
        return proxies


    def parser_cool(self, html):
        """
        解析cool代理
        :param html: etree对象
        :return:
        """
        proxies=[]
        if html:
            data = json.loads(html)
            for item in data:
                if item:
                    ip = item.get("ip")
                    port = item.get("port")
                    if ip and port:
                        proxy = self.collect_ip_info(ip, port)
                        proxies.append(proxy)
        return proxies


    def parser_proxyls(self, html):
        """
        解析proxylist的https代理
        :param html: etree对象
        :return:
        """
        proxies=[]
        res = html.split('\r\n')
        for item in res:
            if item:
                ip, port=item.split(':')
                proxy = self.collect_ip_info(ip, port)
                proxies.append(proxy)
        return proxies


    def parser_mrhin(self, html):
        """
        解析mrhin的https代理
        :param html: etree对象
        :return:
        """
        proxies=[]
        res = html.xpath('//table[@cellpadding="3"]/tr[position()>2]')
        for item in res:
            ip = item.xpath('./td[1]/text()')
            ip = ip[0] if ip else ''
            port = item.xpath('./td[2]/text()')
            port = port[0] if port else ''
            if ip and port:
                proxy = self.collect_ip_info(ip, port)
                proxies.append(proxy)
        return proxies