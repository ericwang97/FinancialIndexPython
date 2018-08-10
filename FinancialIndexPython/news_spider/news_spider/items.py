# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    scan_id = scrapy.Field()
    net_name = scrapy.Field()
    status = scrapy.Field()
    ent_time = scrapy.Field()
    fail_result = scrapy.Field()
    pass


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    net_name = scrapy.Field()
    ent_time = scrapy.Field()
    keyword = scrapy.Field()
    digest = scrapy.Field()
    content = scrapy.Field()
    hot_degree = scrapy.Field()
    scan_id = scrapy.Field()
    pass

