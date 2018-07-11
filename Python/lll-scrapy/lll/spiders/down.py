# -*- coding: utf-8 -*-
from lll.items import LllItem
from scrapy.http import  Request
from scrapy_redis.spiders import RedisSpider

class DownSpider(RedisSpider):
    name = 'down'
    allowed_domains = ['chouti.com']
    def start_requests(self):
        for url in self.start_urls:
            print(url)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        print('下载')
        yield LllItem(url='http://wx1.sinaimg.cn/large/8a04ef95ly1frbvy0d2opj20j00tm0vt.jpg', type='file',
                  file_name='zzzz.jpg')