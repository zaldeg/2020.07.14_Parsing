from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import settings
from instagram.spiders.insta import InstaSpider


if __name__ == "__main__":
    crawler_settings = Settings() 
    crawler_settings.setmodule(settings)
    # search_list = ["orlovgorskii"]
    search_list = ["orlovgorskii", "govoruhinmax"]
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider, search=search_list)
    process.start()
