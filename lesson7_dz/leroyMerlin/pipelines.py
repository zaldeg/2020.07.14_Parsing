# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
import os
from urllib.parse import urlparse


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlen

    def process_item(self, item, spider):
        if item['characteristics_dt']:
            item['characteristics'] = dict(zip(item['characteristics_dt'],item['characteristics_dd']))
        item.pop('characteristics_dt')
        item.pop('characteristics_dd')
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

class LMPhotosPipeline(ImagesPipeline):
    # def file_path(self, request, response=None, info=None):
    #     print(1)
    #     return 'files/' + os.path.basename(urlparse(request.url).path)
    #     # return 'files/' + "1"
        
    def get_media_requests(self, item, info):     
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img.replace('w_82,h_82', 'w_1200,h_1200'))
                except Exception as ex:
                    print(ex)

    def item_completed(self, results, item, info):
        print(1)
        if results:
            item['photos'] = [i[1] for i in results if i[0]]   
        return item

    # def item_completed(self, results, item, info):
    #     if results:
    #         item['photos'] = [i[1] for i in results if i[0]]
    #     for result in [x for ok, x in results if ok]:
    #         path = result['path']
    #         target_path = os.path.join((item['session_path'], os.path.basename(path)))
    #         try:
    #             os.rename(path, target_path)
    #         except:
    #             print("Could not move image to target folder")
    #         if self.IMAGES_RESULT_FIELD in item.fields:
    #             result['path'] = target_path
    #             item[self.IMAGES_RESULT_FIELD].append(result)

    #     return item
