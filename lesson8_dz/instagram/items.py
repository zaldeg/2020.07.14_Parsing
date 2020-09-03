# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id =  scrapy.Field()
    user_id = scrapy.Field()
    follower_id = scrapy.Field()
    username = scrapy.Field()
    name = scrapy.Field()
    picture = scrapy.Field()
    followed_id = scrapy.Field()
