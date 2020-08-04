# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    _id = scrapy.Field()
    vacancy_title = scrapy.Field()
    vacancy_salary = scrapy.Field()
    vacancy_link = scrapy.Field()
    vacancy_site = scrapy.Field()
    vacancy_salary_min = scrapy.Field()
    vacancy_salary_max = scrapy.Field()
    vacancy_salary_cur = scrapy.Field()
    site = scrapy.Field()
    
