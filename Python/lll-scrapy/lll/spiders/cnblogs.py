from bs4 import BeautifulSoup
from scrapy.spiders import Request
import scrapy
import re
class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    start_urls = ['http://www.cnblogs.com/post/prevnext?postId=9078770&blogId=133379&dateCreated=2018%2F5%2F23+20%3A28%3A00&postType=1']

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        a = soup.find(name='a',attrs={'class': 'p_n_p_prefix'})
        print(a.get('href'))
        pattern = re.compile(r'\d+')
        post_id = pattern.findall(a.get('href'))[0]
        print(post_id)
        next_url = 'http://www.cnblogs.com/post/prevnext?postId={0}&blogId=133379&dateCreated=2018%2F5%2F23+20%3A28%3A00&postType=1'.format(post_id)
        print(next_url)
        yield Request(url=next_url, callback=self.parse)