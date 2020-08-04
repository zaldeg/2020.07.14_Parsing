import scrapy
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=хирург&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response):
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        vacancy_links = response.xpath("//div[@class='_3mfro PlM3e _2JVkc _3LJqf']/a/@href").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacancy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response):
        vacancy_title = response.xpath("//h1/text()").extract_first()
        vacancy_salary = response.xpath(
            "//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()"
        ).extract()
        vacancy_link = response.url
        yield JobparserItem(
            vacancy_title=vacancy_title,
            vacancy_salary=[i.replace('\xa0', "") for i in vacancy_salary],
            vacancy_link=vacancy_link
        )
