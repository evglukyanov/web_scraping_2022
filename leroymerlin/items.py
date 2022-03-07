# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import MapCompose, TakeFirst
import scrapy


def get_price(value: str) -> int:
    """
    Функция преобразования цены из str в int
    :param value: str
    :return: int
    """
    value = ''.join(value.split(" "))
    try:
        return int(value)
    except:
        return value


def get_parameter(parameter_list: dict) -> dict:
    """
    Функция обработки строк параметров товара
    :param parameter_list: dict
    :return: dict
    """
    for key, value in parameter_list.items():
        parameter_list[key] = value.strip()
    return parameter_list


class LeroymerlinItem(scrapy.Item):
    """
    Класс обработки данных о товаре
    """
    name_base = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    parameters = scrapy.Field(input_processor=MapCompose(get_parameter), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(get_price), output_processor=TakeFirst())
    img = scrapy.Field()
