# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import hashlib
from scrapy.utils.python import to_bytes
from pymongo import MongoClient


class LeroymerlinPipeline:
    """
    Класс обработки и сохранения полученных данных
    """
    def __init__(self):
        """
        Инициализация класса и базы данных
        """
        client = MongoClient('localhost', 27017)
        self.mongobase = client['Leroymerlin']

    def process_item(self, item, spider):
        """
        Метод сохранения в базу данных
        :param item:
        :param spider:
        :return:
        """
        collections = self.mongobase[f"{spider.name}_{item['name_base']}"]
        collections.update_one({'_id': {'$eq': item['_id']}}, {'$set': item}, upsert=True)
        return item


class LeroymerlinImgPipeline(ImagesPipeline):
    """
    Класс для сохранения скаченных картинок и корректного сохранения
    """
    def get_media_requests(self, item, info):
        """
        Метод скачивающий и сохраняющий картинки
        :param item:
        :param info:
        :return:
        """
        if item['img']:
            for img in item['img']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)
        return item

    def item_completed(self, results, item, info):
        """
        Метод создающий полную информацию о картинках
        :param results:
        :param item:
        :param info:
        :return:
        """
        if results:
            item['img'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        """
        Метод создающий название папки и картинки
        :param request:
        :param response:
        :param info:
        :param item:
        :return:
        """
        image_name = hashlib.sha1(to_bytes(request.url)).hexdigest()
        if item:
            return f'{item["_id"]}/{image_name}.jpg'
        else:
            return f'full/{image_name}.jpg'