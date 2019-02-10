# -*- coding: utf-8 -*-
import logging
import re

import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader

from cigarCrawler.items import Cigar


class DanpipeSpider(scrapy.Spider):
    name = 'danpipe'
    allowed_domains = ['www.danpipe.de']
    start_urls = ['https://www.danpipe.de/Zigarren/Herkunftsland']

    def parse(self, response):

        items = response.xpath('//td[@class="categoriesPreviewContent"]')

        for item in items:
            url = item.xpath('h2/a/@href').get()
            country = item.xpath('h2/a/@title').get()

            request = Request(url, callback=self.parseCountry)
            request.meta['country'] = country

            yield request

    def parseCountry(self, response):
        country = response.meta['country']
        logging.warn("Parsing country: [" + country + "]")
        items = response.xpath('//td[@class="categoriesPreviewContent"]')

        for item in items:
            url = item.xpath('h2/a/@href').get()
            brand = item.xpath('h2/a/@title').get()
            request = Request(url, callback=self.parseBrands)
            request.meta['country'] = country
            request.meta['brand'] = brand
            yield request

    def parseBrands(self, response):
        country = response.meta['country']
        brand = response.meta['brand']

        tmp = response.xpath(
            '//div[@id="content"]/table[@class="productPreview"]')
        if len(tmp) is 0:
            raise Exception("WTF")

        for row in tmp:
            name = row.xpath(
                'tr/td[@class="productPreviewContent"]/h2/a/text()').get().strip()
            url = row.xpath(
                'tr/td[@class="productPreviewContent"]/h2/a/@href').get()

            request = Request(url, callback=self.parseItem)
            request.meta['country'] = country
            request.meta['brand'] = brand
            request.meta['name'] = name

            yield request

    def parseItem(self, response):
        country = response.meta['country']
        brand = response.meta['brand'].strip()
        name = response.meta['name'].strip().replace(
            "»", '').replace('«', '').split(',')[0]

        if name.split(' ')[-1] == 'Kiste' or name.split(' ')[-1] == 'Schachtel':
            name = " ".join(name.split(' ')[:-2])

        if self.isItemAvailable(response):

            cigar_type = self.getActualAmount(
                response.xpath('//h1[@itemprop="name"]/text()').get().strip())

            if self.shouldParseAgain(response):
                request = Request(response.url, callback=self.parseBrands)
                request.meta['country'] = country
                request.meta['brand'] = brand

                yield request
            else:
                try:
                    price = float(response.xpath(
                        '//div[@id="productinfoprice"]/p[@class="productprice"]/span[@itemprop="price"]/text()').get())
                except TypeError:
                    price = float(response.xpath(
                        '//div[@id="productinfoprice"]/span[@itemprop="price"]/text()').get())

                logging.warn("Found price: [" + str(price) + "]")
                isAvailable = self.isItemAvailable(response)

                if isAvailable:
                    yield Cigar({'url': response.url, 'name': name, 'amount': cigar_type, 'price': price, 'currency': 'EUR', 'country': response.meta['country'],
                                 'brand': response.meta['brand'], 'website': 'DanPipe'})

    def shouldParseAgain(self, item):
        tmp = item.xpath(
            '//div[@id="productlist"]/div/table/tr')

        return len(tmp) > 0

    def isItemAvailable(self, item):
        tmp = item.xpath('//p[@class="stockimagetext"]/text()').get().strip()
        # logging.warn("Item available: " + str(tmp))
        return "Derzeit nicht vorrätig" is not tmp

    def getActualAmount(self, amt):
        try:
            return int(re.findall(r'\d+', amt)[-1])
        except Exception:
            return 1
