# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JobparserItem(scrapy.Item):
    l_name = scrapy.Field()
    l_salary = scrapy.Field()
    l_url = scrapy.Field()
    #for pipe
    l_min = scrapy.Field()
    l_max = scrapy.Field()
    l_cur = scrapy.Field()
    _id = scrapy.Field()

