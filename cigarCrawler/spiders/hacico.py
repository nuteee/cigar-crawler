# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import Request


class HacicoSpider(scrapy.Spider):
    name = 'hacico'
    allowed_domains = ['www.hacico.de']
    start_urls = ['https://www.hacico.de/en/Cigars']

    def parse(self, response):

        items = response.xpath('//div[@class="meineListe"]')

        for item in items:
            url = item.xpath('div/a/@href').get()
            country = item.xpath('div/a/@title').get()

            request = Request(url, callback=self.parseCountry)
            request.meta['country'] = country

            yield request

    def parseCountry(self, response):

        country = response.meta['country']

        items = response.xpath('//div[@class="list_left"]')

        if(len(items) is 0):
            request = Request(response.url, callback=self.parseBrands)
            request.meta['country'] = country
            request.meta['brand'] = 'TODO'
            yield request
        else:
            for item in items:
                url = item.xpath('div/div/strong/a/@href').get()
                brand = item.xpath('div/div/strong/a/@title').get()
                try:
                    request = Request(url, callback=self.parseBrands)
                    request.meta['country'] = country
                    request.meta['brand'] = brand
                    yield request
                except TypeError as e:
                    url = item.xpath('div/strong/a/@href').get()
                    brand = item.xpath('div/strong/a/@title').get()
                    request = Request(url, callback=self.parseBrands)
                    request.meta['country'] = country
                    request.meta['brand'] = brand
                    yield request

    def parseBrands(self, response):

        items = response.xpath('//div[@class="product_listing_box"]')
        for item in items:

            try:
                name = item.xpath('div[1]/a/text()').get().strip()
            except AttributeError:
                return
            
            for row in item.xpath('div[2]/table/tr[1]/td[4]/table/tr'):
                if self.isItemAvailable(row):
                    cigar_type = self.getActualAmount(row.xpath(
                        'td[1]/form/text()').get().strip())

                    tmp = row.xpath('td[3]/text()').get().strip().split(' ')
                    currency = tmp[0]

                    try:
                        price = float(tmp[1].replace(',', '.'))
                    except Exception as e:
                        return

                    if price is not 0:
                        yield {'Name': name, 'Amount': cigar_type, 'Price': price, 'Currency': currency, 'Price / stick': price / cigar_type, 'Country': response.meta['country'], 'Brand': response.meta['brand']}

        try:
            next_page = response.xpath(
                '//a[@class="pageResults" and @title=" next page "]/@href').get()

            yield Request(next_page, callback=self.parseBrands)
        except Exception as e:
            print e

    def isItemAvailable(self, item):
        return len(item.xpath('td[5]/input').extract()) != 0

    def getActualAmount(self, amt):
        try:
            return int(re.search(r'\d+', amt).group())
        except AttributeError:
            return 1
