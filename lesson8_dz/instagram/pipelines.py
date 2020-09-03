# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient


class InstagramPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram_users

    def process_item(self, item, spider):
        users = self.mongo_base[spider.name]
        relations = self.mongo_base['relations']
        if 'follower_id' in item:
            relations.insert_one({
                'follower' : int(item['follower_id']),
                'followed' : int(item['_id'])
            })
            item['_id'] = int(item['follower_id'])
            item.pop('follower_id')
        if 'followed_id' in item:
            relations.insert_one({
                'follower' : int(item['_id']),
                'followed' : int(item['followed_id'])
            })
            item['_id'] = int(item['followed_id'])
            item.pop('followed_id')
        try:
            users.insert_one(item)
        except:
            pass

        return item
