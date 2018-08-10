# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from Texent.settings import PROXIES

#-*- coding:utf-8 -*-
from selenium import webdriver
import time
from scrapy.http import HtmlResponse

'''
class SeleniumMiddleware(object):
    def process_request(self, request, spider):

        click_url_list = [
            'https://new.qq.com/ch/tech/',      #爬取网页，这里是腾讯科技
            'https://new.qq.com/ch2/ai',        #AI新闻
            'https://new.qq.com/ch2/internet',  #互联网
            'https://new.qq.com/ch2/bt',        #前沿科技
            'https://new.qq.com/ch2/tcctit',    #通信/传统IT
            'https://new.qq.com/tag/276813',     #区块链
            'https://new.qq.com/ch2/tech_cycx'  #创业创新
        ]

        #true_page = ''

        if request.url in click_url_list:
            try:
                driver = webdriver.Chrome()
                driver.get(request.url)
                driver.implicitly_wait(3)
                time.sleep(5)
                h = 2   ##################### 翻页长度！！！！！！！！！
                print('正在解析%s' % request.url)

                # 将页面滚动条拖到底部
                for i in range(0, h):
                    js = "var q=document.documentElement.scrollTop=100000"
                    driver.execute_script(js)
                    print('已完成%s次'%(i+1))
                    time.sleep(3)

                print('翻页结束，共有%s页'%(h))

                true_page =  driver.page_source

                print('网址{}已经翻页储存完毕'.format(request.url))

                driver.close()

                return HtmlResponse(request.url, body = true_page, encoding='utf-8', request=request)

            except:
                print("get news data failed")

        else:
            print("news data is not in the list")
            #return None
'''
##############################################


class RandomUserAgent(object):

    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))

##############################################

class ProxyMiddleware(object):

    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        if proxy['user_pass'] is None:
            print("**************ProxyMiddleware no pass************" + proxy['ip_port'])
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
        else:
            pass

        #if proxy['user_pass'] is not None:
        #    request.meta['proxy'] = "http://%s" % proxy['ip_port']
        #    encoded_user_pass = base64.b64encode(proxy['user_pass'].encode(encoding='utf-8'))
        #    request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        #    print("**************ProxyMiddleware have pass************" + proxy['ip_port'])

##############################################

class TexentSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

##############################################

class TexentDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


##################################################

class PhantomJSMiddleware(object):

    @classmethod
    def process_request(self, request, spider):

        h = 3 ############################################################################## 翻页长度！！！！！！！！！

        click_url_list = [
            'https://new.qq.com/ch/tech/',  # 爬取网页，这里是腾讯科技
            'https://new.qq.com/ch2/ai',  # AI新闻
            'https://new.qq.com/ch2/internet',  # 互联网
            'https://new.qq.com/ch2/bt',  # 前沿科技
            'https://new.qq.com/ch2/tcctit',  # 通信/传统IT
            'https://new.qq.com/tag/276813',  # 区块链
            'https://new.qq.com/ch2/tech_cycx'  # 创业创新
        ]

        js = """
        
        function scrollToBottom() {        
            var Height = document.body.clientHeight,  //文本高度
                screenHeight = window.innerHeight,  //屏幕高度
                INTERVAL = 10,  // 滚动动作之间的间隔时间
                delta = 5000,  //每次滚动距离
                curScrollTop = 0;    //当前window.scrollTop 值
        
            var scroll = function () {
                curScrollTop = document.body.scrollTop;
                window.scrollTo(0,curScrollTop + delta);
            };
        
            var timer = setInterval(function () {
                var curHeight = curScrollTop + screenHeight;
                if (curHeight >= Height){   //滚动到页面底部时，结束滚动
                    clearInterval(timer);
                }
                scroll();
            }, INTERVAL)
        }
        scrollToBottom()
        """

        if 'PhantomJS' in request.meta:

            service_args = []
            service_args.append('--load-images=no')  ##关闭图片加载
            service_args.append('--disk-cache=yes')  ##开启缓存
            service_args.append('--ignore-ssl-errors=true')  ##忽略https错误

            if request.url in click_url_list:
                try:
                    driver = webdriver.PhantomJS(service_args=service_args,
                                                 executable_path=r"D:\phantomjs\bin\phantomjs.exe")
                    driver.set_page_load_timeout(10)
                    driver.get(request.url)
                    driver.implicitly_wait(3)
                    time.sleep(3)
                    print('Using PhantomJS Now')
                    print('正在翻页解析%s' % request.url)

                    # 将页面滚动条拖到底部
                    for i in range(0, h):
                        driver.execute_script(js)
                            #"window.scrollTo(0, document.body.scrollHeight);")  # 执行JavaScript实现网页下拉倒底部
                        time.sleep(8)
                        print('已完成%s次' % (i + 1))


                    print('翻页结束，共有%s页' % h)
                    print('-' * 100)

                    true_page = driver.page_source.encode('utf-8')
                    time.sleep(10)
                    print('网址{}已经翻页储存完毕'.format(request.url))

                    driver.quit()

                    return HtmlResponse(request.url, body=true_page, encoding='utf-8', request=request)

                except:
                    print("get news data failed")

            else:
                print("news data is not in the list")

        if 'GoogleChrome' in request.meta:

            if request.url in click_url_list:
                try:
                    driver = webdriver.Chrome()
                    driver.get(request.url)
                    driver.implicitly_wait(3)
                    time.sleep(5)
                    print('Using Chrome Driver Now')
                    print('正在翻页解析%s' % request.url)

                    # 将页面滚动条拖到底部
                    for i in range(0, h):
                        js = "var q=document.documentElement.scrollTop=100000"
                        driver.execute_script(js)
                        print('已完成%s次' % (i + 1))
                        time.sleep(3)

                    print('翻页结束，共有%s页' % (h))

                    true_page = driver.page_source

                    print('网址{}已经翻页储存完毕'.format(request.url))

                    driver.close()

                    return HtmlResponse(request.url, body=true_page, encoding='utf-8', request=request)

                except:
                    print("get news data failed")

            else:
                print("news data is not in the list")

        if 'PhantomJS' and 'GoogleChrome' not in request.meta:
            pass



