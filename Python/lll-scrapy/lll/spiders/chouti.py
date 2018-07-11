# -*- coding: utf-8 -*-

from scrapy.http import  Request
from scrapy_redis.spiders import RedisSpider
import os


class ChoutiSpider(RedisSpider):
    name = 'chouti'
    allowed_domains = ['chouti.com']

    def start_requests(self):
        # 设置代理
        os.environ['HTTP_PROXY'] = "http://192.168.11.11"

        for url in self.start_urls:
            print(url)
            # 自动设置cookiejar
            yield Request(url=url, callback=self.login,meta={'cookiejar':True})

    def login(self,response):
        print('调用这个参数',response.text)
        req = Request(
            url='http://dig.chouti.com/login',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            body='phone=8618672994167&password=123456&oneMonth=1',
            callback=self.vote,
            meta={'cookiejar': True}
        )
        yield req

    # 点赞
    def vote(self,response):
        print('=======')
        yield Request(
            url='https://dig.chouti.com/link/vote?linksId=20695571',
            method='POST',
            callback=self.voteresult,
            meta={'cookiejar': True}
        )

    def voteresult(self,response):
        print(response.text)

    def parse(self, response):
        yield Request(url='https://dig.chouti.com', callback=self.login, meta={'cookiejar': True})