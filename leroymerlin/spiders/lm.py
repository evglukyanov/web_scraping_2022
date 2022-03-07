import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader
import hashlib


class LmSpider(scrapy.Spider):
    """
    Класс паука для парсинга 'leroymerlin.ru'
    """
    name = 'lm'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        """
        инициализация класса
        """
        super(LmSpider, self).__init__()
        self.name_base = search # Название паука
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&family=linoleum-201709&suggest=true'] # Домен для работы

    def parse(self, response, **kwargs):
        """
        Метод сбора данных и перехода на другую страницу
        """
        ads_links = response.xpath("//div[@class='phytpj4_plp largeCard']/a/@href").getall()
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        for link in ads_links:
            # Переход на страницу товара
            yield response.follow(f'https://leroymerlin.ru{link}', callback=self.ads_parse)

        if next_page:
            # Переход на следующую страницу
            yield response.follow(f'https://leroymerlin.ru{next_page}', callback=self.parse)

    def ads_parse(self, response: HtmlResponse):
        """
        Метод сбора данных со страницы товара
        """
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_value('name_base', self.name_base)
        loader.add_value('_id', hashlib.sha1(str(response.url).encode()).hexdigest())
        loader.add_value('link', response.url)
        loader.add_xpath('name', '//h1[@slot="title"]/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('img', '//picture[@slot="pictures"]//img[@alt="product image"]/@src')
        parameters = response.xpath('//div[@class="def-list__group"]')
        parameter_list = dict()
        for param in parameters:
            parameter_list[param.xpath('.//dt[@class="def-list__term"]/text()').get()] \
                                                    = param.xpath('.//dd[@class="def-list__definition"]/text()').get()
        loader.add_value('parameters', parameter_list)
        yield loader.load_item() # Отправка необработанных данных о товаре в Item
 11  lesson_7/scrapy.cfg
@@ -0,0 +1,11 @@
# Automatically created by: scrapy startproject
#
# For more information about the [deploy] section see:
# https://scrapyd.readthedocs.io/en/latest/deploy.html

[settings]
default = leroymerlin.settings

[deploy]
#url = http://localhost:6800/
project = leroymerlin