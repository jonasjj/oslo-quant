# -*- coding: utf-8 -*-
import scrapy


class NetfondsSpider(scrapy.Spider):
    name = 'netfonds'
    allowed_domains = ['netfonds.no']
    start_urls = ['http://netfonds.no/']

    def parse(self, response):
        pass
