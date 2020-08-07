import scrapy
from scrapy.loader import ItemLoader
from leroyMerlin.items import LeroymerlinItem


class LeroyruSpider(scrapy.Spider):
    
    
    name = 'leroyru'
    allowed_domains = ['leroymerlin.ru']
    
    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://spb.leroymerlin.ru/search/?q={search}']

    def parse(self, response):
        next_button_link = response.xpath("//a[@class='paginator-button next-paginator-button']/@href").extract_first()
        product_links = response.xpath("//a[@slot='name']/@href")
        for link in product_links:
            yield response.follow(link, callback=self.parse_pages)
        yield response.follow(next_button_link, callback=self.parse)
        
    def parse_pages(self, response):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('photos', '//uc-pdp-media-carousel//img[@slot]/@src')
        loader.add_xpath('title', "//h1[@class='header-2']/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//uc-pdp-price-view[@slot="primary-price"]/span/text()')
        loader.add_xpath('characteristics_dt', '//dl/div/dt/text()')
        loader.add_xpath('characteristics_dd', '//dl/div/dd/text()')

        yield loader.load_item()


        