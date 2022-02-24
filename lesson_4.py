# 1. Написать приложение(используя lxml, нельзя использовать BeautifulSoup),
# которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex news Для парсинга использовать xpath.
# Структура данных должна содержать:
# 2. название источника(mail и яндекс не источники, а аггрегаторы, см. страницу новости),
# 3. наименование новости,
# 4. ссылку на новость,
# 5. дата публикации
# 6. Сложить все новости в БД, новости должны обновляться, т.е. используйте update

from pprint import pprint
from lxml import html
from pymongo import MongoClient
import datetime, time
import unicodedata
import json
import pandas as pd
import requests

yandex_link = 'https://yandex.ru/news/'
mailru_link = 'https://news.mail.ru/'
lenta_link = 'https://lenta.ru/'

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'}
yandex_request = requests.get(yandex_link, headers=header).text
mailru_request = requests.get(mailru_link, headers=header).text
lenta_request = requests.get(lenta_link, headers=header).text

yandex_html = html.fromstring(yandex_request)
mailru_html = html.fromstring(mailru_request)
lenta_html = html.fromstring(lenta_request)

# YANDEX NEWS

news_link_yandex = yandex_html.xpath('//h2/a[contains(@class, link_theme_black)]/@href')
news_header_yandex = yandex_html.xpath('//h2/a[contains(@class, link_theme_black)]/text()')
news_origin_date_yandex = yandex_html.xpath('//div[@class="story__date"]/text()')

news_origin_date_yandex1 = news_origin_date_yandex.copy()

for k, i in enumerate(news_link_yandex):
    news_link_yandex[k] = i.replace('/news/', yandex_link)

for k, i in enumerate(news_origin_date_yandex):
    news_origin_date_yandex[k] = unicodedata.normalize('NFKD', i).split(' ')
    news_origin_date_yandex[k][0] = ' '.join(news_origin_date_yandex[k][:-1])
    if str('вчера в') in news_origin_date_yandex[k][0]:
        news_origin_date_yandex[k][0] = news_origin_date_yandex[k][0].replace('вчера в','')
        news_origin_date_yandex[k][-1] = 'вчера в ' + news_origin_date_yandex[k][-1]

for z, k in enumerate([i[-1] for i in news_origin_date_yandex]):
    if len(k) == 5:
        news_origin_date_yandex[z][-1] = str(datetime.date.today())
    elif 'вчера' in str.lower(k):
        news_origin_date_yandex[z][-1] = str(datetime.date.today()-datetime.timedelta(days=1))

for i in zip(news_header_yandex, news_link_yandex, [i[0] for i in news_origin_date_yandex], [i[-1] for i in news_origin_date_yandex]):
    #print(i)
    pass

# LENTA NEWS

news_link_lenta = lenta_html.xpath('//div[@class="topnews"]//a[@class="card-mini _topnews"]/@href')
news_header_lenta = lenta_html.xpath('//div[@class="card-mini__text"]/span[@class="card-mini__title"]/text()')

for k, i in enumerate(news_header_lenta):
    news_header_lenta[k] = unicodedata.normalize('NFKD', i)
    news_date_lenta = []
    for i in news_link_lenta:
        if len(i.split('.htm')) > 1:
            news_date_lenta.append('https://lenta.ru' + '/'.join(''.join(list(i.split('.htm')[0])[-10:]).split('-')[::-1]))
        else:
            news_date_lenta.append('/'.join(i.split('/')[2:5]))
    news_origin_lenta = []
    for k, i in enumerate(news_link_lenta):
        if str(i)[0] == '/':
            news_origin_lenta.append('Lenta.Ru')
        else:
            news_origin_lenta.append(i.replace('https://','').split('/')[0].title())

    for i in zip(news_header_lenta, news_link_lenta, news_origin_lenta, news_date_lenta):
        #print(i)
        pass

# MAIL.RU NEWS

news_link_mailru = mailru_html.xpath('//div[contains(@class,"daynews__item")]//a/@href|//a[@class="list__text"]/@href|//a[@class="link link_flex"]/@href|//a[@class="newsitem__title link-holder"]/@href')
news_header_mailru = mailru_html.xpath('//div[contains(@class,"daynews__item")]//a//span[contains(@class,\"photo__title_new\")]/text()|//a[@class=\"list__text\"]/text()|//a[@class="link link_flex"]/span/text()|//a[@class="newsitem__title link-holder"]/span/text()')

for k, i in enumerate(news_header_mailru):
    news_header_mailru[k]=unicodedata.normalize('NFKD',i)
for k, i in enumerate(news_link_mailru):
    if str(i)[0] == '/':
        news_link_mailru[k] = mailru_link + str(i)[1:]
    else:
        continue
# если - вдруг - источник не найдется (или не указан, как в lenta.ru), примем, что источником является mail.ru",
news_origin_mailru = []
for i in news_link_mailru:
    news_origin_mailru.append(i.replace('https://','').split('/')[0].title())

news_date_mailru = []
for k, i in enumerate(news_link_mailru):
    time.sleep(1)
    news_date_request = html.fromstring(requests.get(i, headers=header).text)
    news_date = news_date_request.xpath('//span[contains(@class, "note__text breadcrumbs__text js-ago")]/@datetime')
    try:
        news_origin_mailru[k] = news_date_request.xpath('//span[@class="breadcrumbs__item"]//span[@class="link__text"]/text()')[0]
    except:
        pass
    if news_date:
        news_date_mailru.append(str(news_date[0]).split('T')[0])
    else:
        news_date = news_date_request.xpath('//span[contains(@class, "breadcrumbs__item js-ago")]/@datetime')
        if news_date:
            news_date_mailru.append(str(news_date[0]).split('T')[0])
        else:
            news_date = news_date_request.xpath('//time[contains(@class, "breadcrumbs__text js-ago")]/@datetime')
            if news_date:
                news_date_mailru.append(str(news_date[0]).split('T')[0])
            else:
                news_date = json.loads(news_date_request.xpath('//script[@type="application/ld+json"]/text()')[0])['datePublished']
                news_date_mailru.append(news_date)

for i in zip(news_header_mailru, news_link_mailru, news_origin_mailru, news_date_mailru):
    #print(i)
    pass

client = MongoClient('localhost', 27017)

db = client['db_of_news']

yandex_db = db.yandex_news
mailru_db = db.mailru
lenta_db = db.lenta

