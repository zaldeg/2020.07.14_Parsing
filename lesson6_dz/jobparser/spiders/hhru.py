import scrapy
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://spb.hh.ru/vacancies/yuvelir']

    def parse(self, response):
        next_page = response.xpath("//a[contains(@class, 'HH-Pager-Controls-Next')]/@href").extract_first()
        vacancy_links = response.xpath("//a[@class='bloko-link HH-LinkModifier']/@href").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacancy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response):
        vacancy_title = response.xpath("//h1/text()").extract_first()
        vacancy_salary = response.xpath(
            "//p[@class='vacancy-salary']/span/text()"
        ).extract()
        vacancy_link = response.url
        yield JobparserItem(
            vacancy_title=vacancy_title,
            vacancy_salary=[i.replace('\xa0', "") for i in vacancy_salary],
            vacancy_link=vacancy_link
        )