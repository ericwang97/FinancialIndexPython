import pymysql
import json
import random
import requests
import re
import time
from bs4 import BeautifulSoup

from download import Download
from cookie_generator import Generator

from textrank4zh import TextRank4Keyword, TextRank4Sentence
from similarity import TextSimilarity

"""
@Author: Lee & Liwei Wang
@Date: 2018-8-5
此爬虫用作对微信公众号文章的爬取，v1只是用作关键词搜索，请将search_type设置为True

"""

def text_keyword_abstract(article, keywords_len, sentences_len):

    tr4w = TextRank4Keyword()
    tr4w.analyze(text=article, lower=True, window=2)
    keywords = []
    for item in tr4w.get_keywords(keywords_len, word_min_len=2):
        keywords.append(item.word)
    keywords = ' '.join(keywords)

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source='all_filters')
    abstract = []
    for item in tr4s.get_key_sentences(num=sentences_len):
        abstract.append(item.sentence)
    return keywords,abstract
# -*- coding: utf-8 -*-


class WeChatCrawler(Download):
    s = TextSimilarity('F:\工行实习\代码部分\爬虫\Texent\Texent\spiders\Target',
                       'F:\工行实习\代码部分\爬虫\Texent\Texent\spiders\stopwords.txt')  # 语料库路径   停用词路径  这里是自己写的包了相当于！！！！！！！！！

    scan_id = str(round(time.time()))
    print('scan_id:', scan_id)

    def __init__(self, keyword, hostname, username, password, schema, tablename, search_type=True):
        """
        initializing the WeChat crawler(mainly setup the local db) and input some key params
        :param keyword: the searching words
        :param search_type: the searching method: by_type: True or by_author: False
        """
        Download.__init__(self)
        self.query = keyword
        self.search_type = search_type
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

        #数据库
        self.db = pymysql.connect(str(hostname), str(username), str(password), str(schema))
        self.tablename = tablename
        cursor = self.db.cursor()
        print('已连接上数据库')

        #登录
        account = input("pls enter ur wechat account: ")
        pwd = input("pls enter ur wechat password: ")
        generator = Generator(account=account, password=pwd)
        generator.generate()
        print('扫码成功，数据生成结束')

        #sql = """CREATE TABLE IF NOT EXISTS scrapy (
        #               id INT NOT NULL AUTO_INCREMENT,
        #                article_type TINYTEXT NOT NULL,
        #                article_title TINYTEXT NOT NULL,
        #                wechat_author TINYTEXT NOT NULL,
        #                wechat_nickname TINYTEXT NOT NULL,
        #                fetch_date DATETIME NOT NULL,
        #                url TINYTEXT NOT NULL,
        #                Content TEXT NOT NULL,
        #                PRIMARY KEY (id)
        #                )  ENGINE=INNODB
        #                default character set utf8Mb4"""
        #cursor.execute(sql)

    def Openspider(self):

        source_scanInsert = '''insert into netfin_scanlog(id,net_name,status,ent_time,fail_result)
                               values('{scan_id}','{net_name}','{status}','{ent_time}','{fail_result}')'''
        cursor = self.db.cursor()
        print('已连接上数据库')

        print('-' * 200)
        print(self.scan_id)
        sqltext = source_scanInsert.format(scan_id=pymysql.escape_string(self.scan_id),
                                           net_name=pymysql.escape_string('Wechat.scrapy'),
                                           status=pymysql.escape_string('1'),
                                           ent_time=pymysql.escape_string(
                                               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))),
                                           fail_result=pymysql.escape_string('started')
                                           )
        cursor.execute(sqltext)
        self.db.commit()
        print('已生成start scan_log')
        print('-'*200)

    def crawling(self, thres,max_article=10000):
        """
        Main function, it will calling request to fetch data and analyzer to store specific data into db
        :param max_article: limit for max article number
        :return:
        """


        if self.search_type:
            search_url = 'https://mp.weixin.qq.com/cgi-bin/operate_appmsg?sub=check_appmsg_copyright_stat'
            headers = {
                'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
                'Referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&share=1&token=738037669&lang=zh_CN',
                'Host': 'mp.weixin.qq.com'
            }
            with open('cookies.txt', 'r') as file:
                cookie = file.read()
            cookies = json.loads(cookie)
            response = requests.get(url='https://mp.weixin.qq.com/', headers=headers, cookies=cookies)
            token = re.findall(r'token=(\d+)', str(response.url))[0]
            print('token:',token)
            data = {
                'token': token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1',
                'random': random.random(),
                'url': self.query,
                'begin': '0',
                'count': '20',
            }
            response = self.request(search_url=search_url, cookies=cookies, data=data, headers=headers, proxy=None, num_retries=6)#这里都是模仿网站post的数据！！！
            print('已成功解析')
            #print('json:',response.json())

            ########################然后开始解析json，爬取数据#####################

            max_num = response.json().get('total')################这条很容易拿不到
            print('max_num:',max_num)
            if max_num > max_article:
                print("the total number of articles({}) exceeds the limit, crawler will fetching {} articles only, "
                      "if u wanna fetch more articles, pls turns up the limit".format(max_num, max_article))
                max_num = max_article
                time.sleep(2)
            else:
                print("the total number of articles({}) is below the limit, it is enough?".format(max_num))
                time.sleep(2)

            begin = 0  #  each post will start from the position of begin
            index = 0

            ########################然后开始解析json，爬取数据#####################

            while max_num > begin-int(data['count']):
                data['begin']='{}'.format(begin)
                response = self.request(search_url=search_url, cookies=cookies, data=data, headers=headers, proxy=None,
                                        num_retries=6)
                if response is not None:
                    article_list = response.json().get("list")
                    if article_list is not None:
                        print('-----------------------------------------------------------------New pages, article_list is not NONE----------------------------------------------------------------')
                        former_index = index
                        for article in article_list:#############################真正的大大循环
                            cursor = self.db.cursor()
                            #sql = """
                            #        SELECT
                            #            id
                            #        FROM
                            #            financial.netfin_source_message
                            #        WHERE
                            #            url='{}'
                            #""".format(article.get('url')) #进行了一个简单的URL 去重！！！
                            sql = """
                                    SELECT 
                                        id
                                    FROM
                                        {}
                                    WHERE
                                        url='{}'
                             """.format(self.tablename,article.get('url')) #进行了一个简单的URL 去重！！！
                            try:
                                cursor.execute(sql)
                                res = cursor.fetchone()
                                if res:
                                    print('index:',index)
                                    print("This article is already analyzed!")
                                    index +=1################################################这里为何又加了一次
                                    print('-' * 50)
                                    continue
                            except pymysql.Error as e:
                                print("error occurred in Deduplication operation ! ")
                                print('-' * 50)
                                self.db.rollback()
                                continue

            ########################然后开始真正写入不重复的东西#####################

                            print('index:',index)
                            print('scan_id:',self.scan_id)
                            print("Title: "+article.get("title"))
                            print(article['title'])
                            print(article['url'])
                            print(article['article_type'])
                            #print("Author: "+article.get("author"))
                            content = self.analyzer(article['content'])
                            #print(content)

                            hot_degree = 0 #######阅读量和公众号发布时间的问题需要解决！！！！！！！！！！！！！！！！！！！！！！！！
                            simi = self.s.cal_similarities(content)  # 输入文章 范围相似度列表
                            print('相似度:',simi)
                            keyword, raw_abstract = text_keyword_abstract(content, 3, 3)  ######## 关键词和摘要的个数
                            print('keyword:',keyword)
                            digest = ''
                            for va in raw_abstract:
                                digest += va
                            print('digest:',digest)
                            ent_time = '0000-00-00 00:00:00'
                            net_name = '微信公众号'


                            #记住，总共有9大字段
                            #thres = 0.2  ################################## 主题筛选阈值
                            if max(simi) > thres:
                                print('存在相似，保存入数据库')

                                sql = '''
                                insert into {}(title,url,net_name,ent_time,keyword,digest,content,hot_degree,scan_id)
                                                            values('{}','{}','{}','{}','{}', '{}','{}','{}','{}')
                                '''.format(self.tablename,article['title'], article['url'],net_name,ent_time,keyword ,digest,content,hot_degree,self.scan_id)

                                try:
                                    cursor.execute(sql)
                                    self.db.commit()
                                    print("INSERTION SUCCESS!")
                                    print('-' * 50)
                                except pymysql.Error as e:
                                    print(repr(e))
                                    print("Error occurred in INSERT operation !")
                                    print('-' * 50)
                                    self.db.rollback()
                                    continue
                            else:
                                print('没超过阈值，pass')
                                print('-' * 50)
                                pass

                            index += 1
                        begin += index-former_index
                    else:
                        print(response.text)
                        print("Bad Response, try to regain the data after 2s...")
                        time.sleep(2)
                else:
                    print("requesting error!")
                    time.sleep(10)

        else:
            print("Next version coming soon...")

    def analyzer(self, html):
        soup = BeautifulSoup(html, 'lxml')
        return soup.get_text()

    def Closespider(self):

        source_scanInsert = '''insert into netfin_scanlog(id,net_name,status,ent_time,fail_result)
                                                        values('{scan_id}','{net_name}','{status}','{ent_time}','{fail_result}')'''
        cursor = self.db.cursor()
        print('已连接上数据库')
        print('-' * 200)
        print(self.scan_id)
        sqltext = source_scanInsert.format(scan_id=pymysql.escape_string(self.scan_id),
                                           net_name=pymysql.escape_string('Wechat.scrapy'),
                                           status=pymysql.escape_string('2'),
                                           ent_time=pymysql.escape_string(
                                               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))),
                                           fail_result=pymysql.escape_string('finished')
                                           )
        cursor.execute(sqltext)
        self.db.commit()
        cursor.close()
        print('已生成finished scan_log')
        print('-' * 200)
        #connect.close()


############################################################


crawler = WeChatCrawler(keyword="互联网科技前沿",hostname="10.2.17.208", username="root", password="mysql", schema="financial", tablename="netfin_source_message", search_type=True)
#crawler = WeChatCrawler(keyword="互联网技术", hostname="127.0.0.1", username="root", password="889", schema="test", tablename="netfin_source_message", search_type=True)

crawler.Openspider()
crawler.crawling(max_article=500,thres = 0.1)
crawler.Closespider()

