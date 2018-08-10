# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import news_spider.spiders.similarity as similarity
import json
from scrapy import Request
from news_spider.items import NewsItem
import time
import datetime
import configparser


# 爬取新浪网
class sina_news_Spider(scrapy.Spider):
    name = 'sina_news'
    allowed_domains = ['news.sina.com.cn']
    start_urls = ['http://news.sina.com.cn/roll/']

    def __init__(self):
        cf = load_config()
        self.threshold = float(cf.get('Section', 'threshold'))
        self.days = int(cf.get('Section', 'days'))
        self.maxPage = int(cf.get('Section', 'maxPage'))
        target_path = cf.get('Section', 'target_path')
        stopwords_path = cf.get('Section', 'stopwords_path')
        self.s = similarity.TextSimilarity(target_path, stopwords_path)
        # 扫描的批次
        self.scan_id = str(time.time())
        self.category_urls = []

    # 将请求转换成splashRequest
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_category, args={'wait': 1}, dont_filter=True)

    # 解析获取新闻类别
    def parse_category(self, response):
        soup = BeautifulSoup(response.body)
        soup.prettify()
        # category_list = soup.find_all('a', attrs={'s_type': 'col'})
        # 获取主页的所有类别URL
        # for item in category_list:
        #     self.category_urls.append(
        #         'http://news.sina.com.cn/roll/#pageid={}&lid={}&page={}'.format(str(item['pageid']), str(item['s_id']),
        #                                                                         str(1)))
        self.category_urls.append('http://news.sina.com.cn/roll/#pageid=153&lid=2515&page=1')
        self.category_urls.append('http://news.sina.com.cn/roll/#pageid=153&lid=2516&page=1')
        # 解析各类别新闻URL
        for url in self.category_urls:
            yield SplashRequest(url, self.parse_page,
                                args={'wait': 1}, dont_filter=True)

    # 解析每个类别的新闻列表
    def parse_page(self, response):
        soup = BeautifulSoup(response.body)
        soup.prettify()

        for item in soup.find_all('li'):
            yield SplashRequest(item.a['href'], self.parse_detail, args={'wait': 1}, dont_filter=True)

        url = response.url
        # 获取page
        page = int(str(url)[-1])
        page += 1
        if page < self.maxPage:
            next_url = str(url)[:-1] + str(page)
            yield SplashRequest(next_url, self.parse_page, args={'wait': 1}, dont_filter=True)

    # 解析新闻内容
    def parse_detail(self, response):
        soup = BeautifulSoup(response.body)
        soup.prettify()
        # 获取新闻标题
        title = soup.select('h1[class="main-title"]')[0].get_text()
        # 获取新闻发布时间
        date = soup.select('span[class="date"]')[0].get_text()
        # 获取新闻内容
        article = soup.select('div[class="article"]')[0]
        # 获取新闻关键词
        keywords = []
        try:
            a_list = soup.find_all('div', attrs={'class': 'keywords'})[0].find_all('a')
            for item in a_list:
                keywords.append(item.get_text())
        except:
            pass
        # 获取新闻URL
        url = response.url
        # 删除图片和JS
        try:
            article.style.decompose()
        except:
            pass
        try:
            for i in article.find_all('script'):
                i.decompose()
            for i in article.find_all('div'):
                i.decompose()
            article.find('p', attrs={'class': 'article-editor'}).decompose()
        except AttributeError:
            article = article.get_text().strip()  # 去除空格
        else:
            article = article.get_text().strip()  # 去除空格
        temp_keywords, abstract = sina_keyword_abstract(article, 3, 3)
        if len(keywords) == 0:
            keywords = temp_keywords
        keywords = ' '.join(keywords)
        print('-----------------------------------------------')
        print('标题:', title)
        #print(article)
        print('关键词:', keywords)
        print('摘要:', end='\n')
        print(abstract)
        print('时间:', date)
        print('新闻URL:', url)
        print('相似度:', self.s.cal_similarities(article))
        print('-----------------------------------------------')

        # 封装成item
        similar_list = self.s.cal_similarities(article)
        if max(similar_list) > self.threshold:
            print('存在相似，保存入数据库')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            item = NewsItem()
            item['title'] = title.strip()
            item['url'] = url.strip()
            item['net_name'] = '新浪网'
            item['ent_time'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime(time.mktime(time.strptime(date, '%Y年%m月%d日 %H:%M'))))

            item['keyword'] = keywords.strip()
            item['digest'] = abstract.strip()
            item['content'] = article.strip()
            item['hot_degree'] = '0'
            item['scan_id'] = str(self.scan_id)
            return item
        else:
            print('没超过阈值，pass')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            pass


################################################################################
# 爬取雷锋网
class leiphone_Spider(scrapy.Spider):
    name = 'leiphone_news'
    allowed_domains = ['www.leiphone.com']
    start_urls = ['https://www.leiphone.com/site/AjaxLoad/page/1']

    def __init__(self):
        cf = load_config()
        self.threshold = float(cf.get('Section', 'threshold'))
        self.days = int(cf.get('Section', 'days'))
        self.maxPage = int(cf.get('Section', 'maxPage'))
        target_path = cf.get('Section', 'target_path')
        stopwords_path = cf.get('Section', 'stopwords_path')
        self.s = similarity.TextSimilarity(target_path, stopwords_path)
        # 扫描的批次
        self.scan_id = str(time.time())

    def parse(self, response):
        html = json.loads(response.body)['html']
        soup = BeautifulSoup(html)
        news_list = soup.find_all('a', attrs={'class': 'headTit'})
        for item in news_list:
            yield scrapy.Request(item['href'], self.parse_content)

        url = response.url
        # 获取page
        page = int(str(url)[-1])
        page += 1
        if page < self.maxPage:
            yield scrapy.Request('https://www.leiphone.com/site/AjaxLoad/page/' + str(page))

    def parse_content(self, response):
        soup = BeautifulSoup(response.body)
        # 获取新闻发布时间
        date = soup.select('td[class="time"]')[0].get_text().strip()
        date = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M'))))
        # 终止条件
        interval = time_cmp(float(self.scan_id), date)
        if interval > self.days:
            print('新闻过时')
            return

        # 获取新闻标题
        title = soup.select('h1[class="headTit"]')[0].get_text().strip()
        # 获取新闻导语
        leadword = soup.select('div[class="article-lead"]')[0].get_text().strip()
        # 获取新闻URL
        url = response.url
        # 获取新闻内容
        article = soup.select('div[class="lph-article-comView"]')[0]
        keywords = []
        try:
            for i in soup.find('div', attrs={'class': 'related-link clr'}).children:
                keywords.append(i.string.strip())
        except:
            pass
        # 删除模版和JS
        try:
            [s.extract() for s in article(['script', 'strong'])]
        except AttributeError:
            article = fix_content(article.get_text())  # 去除空格
        else:
            article = fix_content(article.get_text())  # 去除空格
        temp_keywords, abstract = leiphone_keyword_abstract(article, 3, 3)
        if len(keywords) == 0:
            keywords = temp_keywords
        keywords = ' '.join(keywords)
        print('-----------------------------------------------')
        print('标题:', title)
        print(leadword) #导语
        #print(article)
        print('关键词:', keywords)
        print('摘要:', end='')
        print(abstract)
        print('时间:', date)
        print('新闻URL:', url)
        print('相似度:', self.s.cal_similarities(article))
        print('-----------------------------------------------')

        # 封装成item
        similar_list = self.s.cal_similarities(article)
        if max(similar_list) > self.threshold:
            print('存在相似，保存入数据库')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            item = NewsItem()
            item['ent_time'] = date
            item['title'] = title.strip()
            item['url'] = url.strip()
            item['net_name'] = '雷锋网'
            item['keyword'] = keywords.strip()
            item['digest'] = abstract.strip()
            item['content'] = article.strip()
            item['hot_degree'] = '0'
            item['scan_id'] = self.scan_id
            return item
        else:
            print('没超过阈值，pass')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            pass


################################################################################
# 爬取36kr
class _36_kr_Spider(scrapy.Spider):
    name = '_36kr_news'
    page = 1
    start_urls = ['http://36kr.com/api/search-column/mainsite?per_page=20&page=' + str(page)]

    def __init__(self):
        cf = load_config()
        self.threshold = float(cf.get('Section', 'threshold'))
        self.days = int(cf.get('Section', 'days'))
        self.maxPage = int(cf.get('Section', 'maxPage'))
        target_path = cf.get('Section', 'target_path')
        stopwords_path = cf.get('Section', 'stopwords_path')
        self.s = similarity.TextSimilarity(target_path, stopwords_path)
        # 扫描的批次
        self.scan_id = str(time.time())

    def parse(self, response):
        data = json.loads(response.body)['data']
        news_list = data['items']
        for item in news_list:
            id = item['id']
            date = item['published_at']
            if id > 50000:
                yield SplashRequest('http://36kr.com/p/' + str(id) + '.html', callback=self.parse_content,
                                    args={'wait': 1.5}, meta={'date': date})
            else:
                yield SplashRequest('http://36kr.com/video/' + str(id), self.parse_video, args={'wait': 1},
                                    meta={'date': date})
        url = response.url
        # 获取page
        page = int(str(url)[-1])
        page += 1
        if page < self.maxPage:
            next_url = str(url)[:-1] + str(page)
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_content(self, response):
        soup = BeautifulSoup(response.body)
        # 获取时间
        date = response.meta['date']
        # 终止条件
        interval = time_cmp(float(self.scan_id), time.strftime("%Y-%m-%d %H:%M:%S",
                                                               time.localtime(time.mktime(
                                                                   time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00")))))
        if interval > self.days:
            print('过时')
            return
        # 获取标题
        title = soup.find('div', attrs={'class': 'mobile_article'}).find('h1').get_text()
        # 获取文章
        article = soup.find('section', attrs={'class': 'textblock'})
        try:
            if article.find('p').get_text().strip().startswith('编者'):
                article.find('p').decompose()
        except:
            pass
        article = article.get_text().strip()
        # 获取总结
        summary = soup.find('section', attrs={'class': 'summary'}).get_text().strip()
        # 获取关键词和摘要
        keywords, abstract = _36r_keyword_abstract(article, 3, 3)
        raw_keywords = []
        for item in soup.find_all('a', attrs={'class': 'kr-tag-gray'}):
            raw_keywords.append(item.get_text())
        if len(raw_keywords) != 0:
            keywords = raw_keywords
        keywords = ' '.join(keywords)
        print('-----------------------------------------------')
        print('标题:', title)
        print('总结:', summary)
        print('关键词:', keywords)
        #print(article)
        print('摘要:', end='')
        print(abstract)
        print('url:', response.url)
        print('时间:', time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.localtime(time.mktime(time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00")))))
        print('相似度', self.s.cal_similarities(article))
        print('-----------------------------------------------')

        # 封装成item
        similar_list = self.s.cal_similarities(article)
        if max(similar_list) > self.threshold:
            print('存在相似，保存入数据库')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            item = NewsItem()
            item['title'] = title.strip()
            item['url'] = response.url.strip()
            item['net_name'] = '36氪'
            item['ent_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
                time.mktime(time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00"))))
            item['keyword'] = keywords.strip()
            item['digest'] = abstract.strip()
            item['content'] = article.strip()
            item['hot_degree'] = '0'
            item['scan_id'] = str(self.scan_id)
            return item
        else:
            print('没超过阈值，pass')
            print(
                '-----------------------------------------------------------------------------------------------------------------')
            pass

    def parse_video(self, response):
        try:
            soup = BeautifulSoup(response.body)
            # 获取标题
            title = soup.find('div', attrs={'class': 'content-wrapper'}).find('h1').get_text()
            # 获取介绍
            desc = soup.find('section', attrs={'class': 'single-post-desc'}).get_text().strip()
            # 获取时间
            date = response.meta['date']
            # 获取关键词和摘要
            keywords, abstract = _36r_keyword_abstract(desc, 3, 1)
            raw_keywords = []
            for item in soup.find_all('a', attrs={'class': 'kr-tag-gray'}):
                raw_keywords.append(item.get_text())
            if len(raw_keywords) != 0:
                keywords = raw_keywords
            keywords = ' '.join(keywords)
            print('-----------------------------------------------')
            print('标题:', title)
            print('关键词:', keywords)
            print(desc)
            print('url:', response.url)
            print('时间:', time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.localtime(time.mktime(time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00")))))
            print('-----------------------------------------------')
        except:
            pass


################################################################################
# 爬取微信公众号
class wechat_Spider(scrapy.Spider):
    name = 'wechat_news'
    allowed_domains = ['http://weixin.sogou.com']
    keyword = '互联网新技术新应用动态'
    start_urls = ['http://weixin.sogou.com/weixin?type=1&s_from=input&query=' + keyword]

    def parse(self, response):
        soup = BeautifulSoup(response.body)
        request = Request(soup.find_all('p', attrs={'class': 'tit'})[0].a['href'], self.parse_list,
                          dont_filter=True)
        request.meta['PhantomJS'] = True
        yield request

    def parse_list(self, response):
        soup = BeautifulSoup(response.body)
        for item in soup.find_all('h4', attrs={'class': 'weui_media_title'}):
            request = Request('https://mp.weixin.qq.com' + item['hrefs'], self.parse_content,
                              dont_filter=True)
            request.meta['PhantomJS'] = True
            yield request

    def parse_content(self, response):
        soup = BeautifulSoup(response.body)
        try:
            title = soup.select('h2[class="rich_media_title"]')[0].get_text().strip()
            content = soup.select('div[class="rich_media_content "]')[0].get_text().strip()
            print('-----------------------------------------------')
            print('标题：', title)
            print(content)
            print('-----------------------------------------------')
        except:
            pass


# 去掉文章的空格
def fix_content(s):
    return re.sub('\s', '', s)


# 根据文章抽取关键词和摘要
def leiphone_keyword_abstract(article, keywords_len, sentences_len):
    # 抽取关键词
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=article, lower=True, window=2)
    keywords = []
    for item in tr4w.get_keywords(keywords_len, word_min_len=1):
        keywords.append(item.word)
    # 抽取摘要
    sentences = article.split('。')
    first_sentence = sentences[0]
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source='all_filters')
    abstract = []
    abstract.append(first_sentence + '。')
    for item in tr4s.get_key_sentences(num=sentences_len):
        if item.sentence != first_sentence:
            abstract.append(item.sentence + '。')
    abstract = '\n'.join(abstract)
    return keywords, abstract


# 根据文章抽取关键词和摘要
def sina_keyword_abstract(article, keywords_len, sentences_len):
    # 抽取关键词
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=article, lower=True, window=2)
    keywords = []
    for item in tr4w.get_keywords(keywords_len, word_min_len=1):
        keywords.append(item.word)
    # 抽取摘要
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source='all_filters')
    abstract = []
    for item in tr4s.get_key_sentences(num=sentences_len):
        if str(item.sentence).startswith('原标题') or str(item.sentence).startswith('责任编辑') or str(
                item.sentence).startswith('来源'):
            continue
        abstract.append(item.sentence + '。')
    abstract = '\n'.join(abstract)
    return keywords, abstract


# 根据文章抽取关键词和摘要
def _36r_keyword_abstract(article, keywords_len, sentences_len):
    # 抽取关键词
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=article, lower=True, window=2)
    keywords = []
    for item in tr4w.get_keywords(keywords_len, word_min_len=1):
        keywords.append(item.word)
    # 抽取摘要
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source='all_filters')
    abstract = []
    for item in tr4s.get_key_sentences(num=sentences_len):
        abstract.append(item.sentence + '。')
    abstract = '\n'.join(abstract)
    return keywords, abstract


# 比较时间的大小
def time_cmp(now_date, article_date):
    now_date = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(now_date))
    d1 = datetime.datetime.strptime(now_date, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(article_date, '%Y-%m-%d %H:%M:%S')
    return (d1 - d2).days


# 读取配置文件
def load_config():
    cf = configparser.ConfigParser()
    cf.read('news_spider/spiders/config.cfg')
    return cf
