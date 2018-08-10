# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from imp import reload
from scrapy_splash import SplashRequest
from scrapy.http import Request
from scrapy.selector import Selector
from Texent.items import TexentItem
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import sys
import time
import Texent.spiders.similarity as similarity
reload(sys)

def text_keyword_abstract(article, keywords_len, sentences_len):

    tr4w = TextRank4Keyword()
    tr4w.analyze(text=article, lower=True, window=2)
    keywords = []
    for item in tr4w.get_keywords(keywords_len, word_min_len=2):
        keywords.append(item.word)
    keywords = ' '.join(keywords)

    sentences = article.split('。')
    first_sentence = sentences[0]
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source='all_filters')
    abstract = []
    for item in tr4s.get_key_sentences(num=sentences_len):
        if item.sentence != first_sentence:
            abstract.append(item.sentence+ '。')
    abstract = '\n'.join(abstract)
    return keywords,abstract

class SplashSpider(Spider):

    name = 'scrapy_splash'
    allowed_domains = ['https://new.qq.com/']
    start_urls = [
        'https://new.qq.com/ch/tech/',      #爬取网页，这里是腾讯科技
        'https://new.qq.com/ch2/ai',        #AI新闻
        #'https://new.qq.com/ch2/internet',  #互联网
        #'https://new.qq.com/ch2/bt',        #前沿科技
       # 'https://new.qq.com/ch2/tcctit',    #通信/传统IT
        #'https://new.qq.com/tag/276813',     #区块链
       # 'https://new.qq.com/ch2/tech_cycx'   #创业创新
    ]

    scan_id = str(round(time.time()))
    s = similarity.TextSimilarity('F:\工行实习\代码部分\爬虫\Texent\Texent\spiders\Target',
                                  'F:\工行实习\代码部分\爬虫\Texent\Texent\spiders\stopwords.txt')  # 语料库路径   停用词路径  这里是自己写的包了相当于！！！！！！！！！

    thres = 0.2  ################################## 主题筛选阈值

    # request需要封装成SplashRequest
    def start_requests(self):
        # splash lua script
        script = """
                    function main(splash,args)
                        
                        splash.resource_timeout = 1
                        splash:set_viewport_size(1028, 10000)
                        splash.images_enabled = true
                        splash:go(args.url)
                        splash.scroll_position={0,5000}
                        splash:wait(7)
                        return {
                            html = splash:html()
                        }
                    end
                    """

        for url in self.start_urls:
            print('---------------------------------------------------------------------------爬虫开始解析%s-------------------------------------------------------------------------------'% url)

            '''
            yield Request(url, callback=self.parse_URL, dont_filter=True, meta={
                'PhantomJS':True, 'dont_redirect': True,
                'splash': {
                    'args': {'wait': '0.5'}
                   , 'endpoint': 'execute'}
            })
           '''
            ###########################################################使用chrome还是无头！

            #'''
            yield Request(url, callback=self.parse_URL,  dont_filter=True,meta={
                'GoogleChrome': True, 'dont_redirect': True,
                'splash': {
                    'args': {'wait': '0.5', 'lua_source': script, 'images': 0}
                    , 'endpoint': 'execute'}
            })
           # '''

    def parse_URL(self, response):

        site = Selector(response)
        time.sleep(10)############################这里设置长一点停顿，否则经常会输出混乱

        #keywords = site.xpath('//div[@class="tags"]/a[@class="tag"]/text()').extract()
        URL_site =  site.xpath('//h3[@class]/a[@target="_blank"]/@href').extract()
        url_title = site.xpath('//h3[@class]/a[@target="_blank"]/text()').extract()
        print('-' * 100)
        print('目前解析网址：',response.url)
        print('新闻个数：', len(URL_site))
        strurl = []
        raw_strkeywords =[]
        print('-' * 100)

        for j in range(0, len(URL_site)):

            strtitle = url_title[j]
            strurl = URL_site[j]
            #raw_strkeywords = keywords[(3 * j):(3 * j + 3)]
            #strkeywords = str(raw_strkeywords[0]+','+raw_strkeywords[1]+','+raw_strkeywords[2])
            print('''index：{},标题：{},  URL：{},来源于：{}'''.format((j+1),strtitle,strurl,response.url))

            #item = TexentItem()
            #item['keyword'] = strkeywords

            yield SplashRequest(strurl,self.parse_article, #meta={'dont_redirect': True},
                                args={'wait': '0.5'},dont_filter=True)

    def parse_article(self, response):
        try:
            site = Selector(response)
            #标题
            title = site.xpath('//div[@class="LEFT"]/h1/text()').extract()
            url = response.url

            # 时间
            year = site.xpath('//div[@class="year through"]/span/text()').extract()
            md = site.xpath('//div[@class="md"]/text()').extract()
            hm = site.xpath('//div[@class="time"]/text()').extract()
            ent_time = str(year[0])+'/'+str(md[0])+'/'+str(md[2])+' '+str(hm[0])+':'+str(hm[2])
            hot_degree = site.xpath('//div[@class="text"]/i[@id="cmtNum"]/text()').extract()

            # 文章
            raw_article =site.xpath('//p[@class="one-p"]/text()').extract()
            content =''
            print('-----------------------------------------------------------------------------------------------------------------')
            print('标题:%s ' % title[0])
            print('URL:%s ' % url)
            print('时间:%s ' % ent_time)
            print('评论数:%s ' % hot_degree[0])

            for va in raw_article[0:-2]:
                content += va

            # 摘要与关键词
            keywords,raw_abstract = text_keyword_abstract(content, 3, 3)  ######## 关键词和摘要的个数

            simi = self.s.cal_similarities(content)  # 输入文章 范围相似度列表

            digest = ''
            for va in raw_abstract:
                digest += va

            print('关键词:%s ' % keywords)

            print('摘要:%s ' % digest)
            #print('文章:%s ' % content)
            print('相似度:', simi)


        ########################################################


            if max(simi) > self.thres:
                print('存在相似，保存入数据库')
                print('-----------------------------------------------------------------------------------------------------------------')

                item = TexentItem()
                #item = response.meta['item']
                item['title'] = title[0]
                item['hot_degree'] = '0'
                item['net_name'] = net_name = '腾讯科技'
                item['digest'] = digest
                item['keyword'] = keywords
                item['url'] = url
                item['ent_time'] = ent_time
                item['scan_id'] = self.scan_id
                item['content'] = content
                yield item

            else:
                print('没超过阈值，pass')
                print('-----------------------------------------------------------------------------------------------------------------')
                pass
        except:
            print('-----------------------------------------------------------------------------------------------------------------')
            print('页面获取失败，爬取下一页')
            print('-----------------------------------------------------------------------------------------------------------------')
            pass

##################################################################################





