from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings
from leroymerlin.spiders.lm import LmSpider

if __name__ == '__main__':

    crawler_settings = Settings()  # создание класса для парсинга настроек
    crawler_settings.setmodule(settings)  # передача файла настроек

    process = CrawlerProcess(settings=crawler_settings)  # создание класса для парсинга сайта
    process.crawl(LmSpider, search='ламинат дуб')  # создание паука

    process.start()  # старт парсинга