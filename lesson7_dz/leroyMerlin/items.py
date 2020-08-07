# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def make_int(value):
    if value.isdigit():
        return int(value)


class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field()
    characteristics_dt = scrapy.Field()
    characteristics_dd = scrapy.Field(input_processor=MapCompose(str.strip))
    price = scrapy.Field(input_processor=MapCompose(make_int),output_processor=TakeFirst())
    photos = scrapy.Field()
    characteristics = scrapy.Field()

