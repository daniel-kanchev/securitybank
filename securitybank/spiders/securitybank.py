import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from securitybank.items import Article


class securitybankSpider(scrapy.Spider):
    name = 'securitybank'
    start_urls = ['https://www.securitybank.com/blog/featured/']

    def parse(self, response):
        links = response.xpath('//div[@class="col-md-4"]//a[@class="btn btn-primary"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@data-action="load-next-page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="entry financial-blog-entry"]//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('(//div[@class="col-md-8"])[1]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
