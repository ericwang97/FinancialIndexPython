# -*- coding: utf-8 -*-
"""
科技新闻爬虫

Created on Wes Aug 8, 2018

@author: Huachong Peng & Liwei Wang
"""
from scrapy import cmdline

#cmdline.execute("scrapy crawl leiphone_news".split())
#cmdline.execute("scrapy crawl _36kr_news".split())
cmdline.execute("scrapy crawl sina_news".split())