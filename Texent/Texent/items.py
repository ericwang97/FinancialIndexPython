# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
class TexentItem(scrapy.Item):

    # 标题
    title = scrapy.Field()
    #关键词
    keyword = scrapy.Field()
    #摘要
    digest = scrapy.Field()
    # URL
    url = scrapy.Field()
    # 时间
    ent_time = scrapy.Field()
    # 文章
    content = scrapy.Field()
    #点赞数
    hot_degree = scrapy.Field()
    # 来源网址
    net_name = scrapy.Field()
    # 时间批次
    scan_id = scrapy.Field()

    pass
