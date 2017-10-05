# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        for success, value in results:
            image_path = value['path']
        item['cover_path'] = image_path
        return item
