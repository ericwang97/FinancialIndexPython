# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from Texent import settings
import logging
import time

class TexentPipeline(object):
    source_urlselect = '''select url from {}'''.format(settings.TABLE_NAME)
    url_list = []

    scrapyInsert = '''insert into {}(title,url,net_name,ent_time,keyword,digest,content,hot_degree,scan_id)
                            values('{title}','{url}','{net_name}','{ent_time}','{keyword}','{digest}','{content}','{hot_degree}','{scan_id}')'''

    source_scanInsert = '''insert into netfin_scanlog(id,net_name,status,ent_time,fail_result)
                                        values('{scan_id}','{net_name}','{status}','{ent_time}','{fail_result}')'''


    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            port=settings.MYSQL_PORT,
            charset='utf8',
            use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

        # 获取数据库的URL
        self.cursor.execute(self.source_urlselect)
        for r in self.cursor:
            self.url_list.append(r[0])

    def process_item(self, item, spider):
        try:
            if item['url'] in self.url_list:
                print('--------------------------------------------------------------重复新闻-----------------------------------------------------------------------------')
                return

            else:
                sqltext = self.scrapyInsert.format(
                    settings.TABLE_NAME,
                    title=pymysql.escape_string(item['title']),
                    url=pymysql.escape_string(item['url']),
                    net_name=pymysql.escape_string(item['net_name']),
                    ent_time=pymysql.escape_string(item['ent_time']),
                    keyword=pymysql.escape_string(item['keyword']),
                    digest=pymysql.escape_string(item['digest']),
                    content=pymysql.escape_string(item['content']),
                    hot_degree=pymysql.escape_string(item['hot_degree']),
                    scan_id = pymysql.escape_string(item['scan_id']))
                self.cursor.execute(sqltext)
                self.connect.commit()

        except Exception as error:
            logging.log(error)
            #pass

        return item

    #def close_spider(self, spider):
    #    self.cursor.close()
    #    self.connect.close()


    def open_spider(self, spider):
        sqltext = self.source_scanInsert.format(scan_id=pymysql.escape_string(spider.scan_id),
                                                net_name=pymysql.escape_string('Tencent.scrapy'),
                                                status=pymysql.escape_string('1'),
                                                ent_time=pymysql.escape_string(
                                                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))),
                                                fail_result=pymysql.escape_string('started')
                                                )
        # spider.log(sqltext)
        self.cursor.execute(sqltext)

    def close_spider(self, spider):
        sqltext = self.source_scanInsert.format(scan_id=pymysql.escape_string(spider.scan_id),
                                                net_name=pymysql.escape_string('Tencent.scrapy'),
                                                status=pymysql.escape_string('2'),
                                                ent_time=pymysql.escape_string(
                                                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))),
                                                fail_result=pymysql.escape_string('finished')
                                                )
        self.cursor.execute(sqltext)
        self.cursor.close()
        self.connect.close()








    '''
     def __init__(self):
        self.file = open('data.json', 'wb')
        self.file = codecs.open(
            'spider.txt', 'w', encoding='utf-8')

        self.file = codecs.open(
             'spider.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()

    '''
