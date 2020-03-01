# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JPMItem
from ArticleSpider.utils.common import extract_num

site_name = 'ji' + 'npin' + 'gmei'


class JPMSpider(scrapy.Spider):
    name = 'jpm'
    allowed_domains = ['www.' + site_name + '.org']
    start_urls = ['http://www.' + site_name + '.org/category/' + site_name + 'cihua/']

    def parse(self, response):
        """
        1.get articles and parse
        2.get next page's url and download by scrapy
        :param response:
        :return:
        """
        thumb_nodes = response.css('article')
        for node in thumb_nodes:
            url = node.css('::attr(href)').extract_first('')
            # cover = node.css('img::attr(src)').extract_first('')
            index = extract_num(url)
            yield Request(url=parse.urljoin(response.url, url),
                          meta={
                              # 'cover': cover,
                              'index': index
                          },
                          callback=self.parse_detail)
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        get detail of article
        :param response:
        :return:
        """
        article_item = JPMItem()
        title = response.css('.entry-header h1::text').extract()[0]
        content = response.css('.single-content').extract()[0]

        # article_item['cover'] = [response.meta.get('cover', '')]
        article_item['index'] = [response.meta.get('index', '')]
        article_item['title'] = title
        article_item['content'] = content
        yield article_item
