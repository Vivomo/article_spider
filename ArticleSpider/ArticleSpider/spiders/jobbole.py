# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.get articles and parse
        2.get next page's url and download by scrapy
        :param response:
        :return:
        """
        post_urls = response.css('.archive-title::attr(href)').extract()
        for url in post_urls:
            yield Request(url=parse.urljoin(response.url, url), callback=self.parse_detail)
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        get detail of article
        :param response:
        :return:
        """
        title = response.css('.entry-header h1::text').extract()
        content = response.css('.entry').extract()[0]
        print(title, content)
