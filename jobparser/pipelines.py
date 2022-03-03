# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.scrapy_jobs

    def process_item(self, item, spider):
        item['l_min'], item['l_max'], item['l_cur'] = self.process_salary_hh(item['l_salary'], spider.name)

        #del item['salary']
        collections = self.mongobase[spider.name]
        collections.insert_one(item)
        return item

    def process_salary_hh(self, salary:dict, spider_name):
        money_min = None
        money_max = None
        money_type = None
        if spider_name == 'superjob':
            if len(salary) == 3 and salary[0] == 'от':
                lst = salary[2].split('\xa0')
                money_min = salary[2].replace('\xa0','').replace(lst[-1],'')
                money_type = lst[-1]
            elif len(salary) == 3 and salary[0] == 'до':
                lst = salary[2].split('\xa0')
                money_max = salary[2].replace('\xa0','').replace(lst[-1],'')
                money_type = lst[-1]
            elif len(salary) == 7:
                money_min = salary[0].replace('\xa0','')
                money_max = salary[4].replace('\xa0','')
                money_type = salary[6]
            elif len(salary) == 1:
                pass
        elif spider_name == 'hhru':
            if len(salary) == 1:
                pass
            elif len(salary) == 7:
                money_min = salary[1].replace(' ', '')
                money_max = salary[3].replace(' ', '')
                money_type = salary[5]
            elif len(salary) == 5:
                if salary[0].replace(' ','') == 'от':
                    money_min = salary[1].replace(' ', '')
                    money_type = salary[3]
                elif salary[0].replace(' ','') == 'до':
                    money_max = salary[1].replace(' ', '')
                    money_type = salary[3]

        return money_min, money_max, money_type
