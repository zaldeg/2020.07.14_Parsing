# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        item['vacancy_salary_max'], item['vacancy_salary_min'], item['vacancy_salary_cur'] = self.process_salary(
                                            item['vacancy_salary'],
                                            spider.name
                                        )
        item['site'] = spider.name
        item.pop('vacancy_salary')
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary(self, vacancy_salary, site):
        length = len(vacancy_salary)
        if site == 'hhru':
            if length == 1:
                vs_max = None
                vs_min = None
                vs_cur = None
            elif length == 7:
                vs_max = vacancy_salary[3]
                vs_min = vacancy_salary[1]
                vs_cur = vacancy_salary[5]
            elif length == 5 and vacancy_salary[0] == 'от':
                vs_max = None
                vs_min = vacancy_salary[1]
                vs_cur = vacancy_salary[3]
            else:
                vs_max = vacancy_salary[1]
                vs_min = None
                vs_cur = vacancy_salary[3]
        elif site == 'sjru':
            if length == 1:
                vs_max = None
                vs_min = None
                vs_cur = None
            elif length == 4:
                vs_max = vacancy_salary[1]
                vs_min = vacancy_salary[0]
                vs_cur = vacancy_salary[3]
            elif length == 3 and vacancy_salary[0] == 'от':
                vs_max = None
                vs_min = "".join([i for i in vacancy_salary[2] if i.isdigit()])
                vs_cur = "".join([i for i in vacancy_salary[2] if i.isalpha()])
            elif length == 3 and vacancy_salary[0] == 'до':
                vs_max = "".join([i for i in vacancy_salary[2] if i.isdigit()])
                vs_min = None
                vs_cur = "".join([i for i in vacancy_salary[2] if i.isalpha()])
            else:
                vs_max = "".join([i for i in vacancy_salary[0] if i.isdigit()])
                vs_min = "".join([i for i in vacancy_salary[0] if i.isdigit()])
                vs_cur = "".join([i for i in vacancy_salary[2] if i.isalpha()])

        return vs_max, vs_min, vs_cur

