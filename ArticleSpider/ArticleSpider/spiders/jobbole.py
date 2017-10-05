# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import ArticleItem
from ArticleSpider.utils.common import get_md5


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
        thumb_nodes = response.css('#archive .post-thumb a')
        for node in thumb_nodes:
            url = node.css('::attr(href)').extract_first('')
            cover = node.css('img::attr(src)').extract_first('')
            yield Request(url=parse.urljoin(response.url, url), meta={'cover': cover}, callback=self.parse_detail)
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        get detail of article
        :param response:
        :return:
        """
        article_item = ArticleItem()
        title = response.css('.entry-header h1::text').extract()
        content = response.css('.entry').extract()[0]
        create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].replace("·", "").strip()

        article_item['url_object_id'] = get_md5(response.url)
        article_item['url'] = response.url
        article_item['cover'] = [response.meta.get('cover', '')]
        article_item['title'] = title
        article_item['content'] = content
        article_item['create_date'] = create_date
        yield article_item
