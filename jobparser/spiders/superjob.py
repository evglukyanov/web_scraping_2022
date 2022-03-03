import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://mo.superjob.ru/vacancy/search/?keywords=SAP']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").get()

        if next_page:
            next_page = response.url + next_page
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='jNMYr GPKTZ _1tH7S']/span/a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//span[@class='_2Wp8I _3a-0Y _3DjcL _3fXVo']//text()").getall()
        url = response.url
        yield JobparserItem(l_name=name, l_salary=salary, l_url=url)
