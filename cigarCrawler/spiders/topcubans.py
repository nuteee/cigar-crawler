# -*- coding: utf-8 -*-
import re
import logging
import scrapy

from scrapy import Request
from scrapy.loader import ItemLoader
from cigarCrawler.items import Cigar


class TopCubansSpider(scrapy.Spider):
    name = 'topcubans'
    allowed_domains = ['www.topcubans.com']
    start_urls = ['https://www.topcubans.com/cuban-cigars']

    def parse(self, response):

        items = response.xpath('//div[@id="content"]/section/div')

        for item in items:
            url = item.xpath('a/@href').get()
            brand = item.xpath('a/@title').get()

            request = Request(url, callback=self.parseBrand)
            request.meta['country'] = 'Cuba'
            request.meta['brand'] = brand

            # logging.warn('Parsing [' + brand + ']')

            yield request

    def parseBrand(self, response):

        items = response.xpath(
            '//section[2]/div')

        for item in items:

            name = item.xpath('article/div[1]/h1/a/@title').get().strip()
            url = item.xpath('article/div[1]/h1/a/@href').get().strip()

            # logging.warn('Checking [' + name + ']')

            if self.isItemAvailable(item):
                cigar_type = self.getActualAmount(
                    item.xpath('article/div[2]/text()').get().strip())

                # logging.warn('Amount: [' + str(cigar_type) + ']')

                try:
                    price = float(item.xpath(
                        'article/div[3]/span/text()').extract()[-1].strip().replace('\'', ''))
                    currency = item.xpath(
                        'article/div[3]/span/meta/@content').get().strip()
                except Exception:
                    try:
                        price = float(item.xpath(
                            'article/div[3]/span[@class="price-discounted"]/text()').extract()[-2].strip().replace('\'', ''))
                    except Exception:
                        price = float(item.xpath(
                            'article/div[3]/span[@class="price-discounted"]/text()').extract()[-1].strip().replace('\'', ''))
                    currency = item.xpath(
                        'article/div[3]/span[@class="price-discounted"]/meta/@content').get().strip()

                if price is not 0:
                    yield Cigar({'url': url, 'name': name, 'amount': cigar_type, 'price': price, 'currency': currency, 'country': response.meta['country'],
                                 'brand': response.meta['brand'], 'website': 'TopCubans'})

    def isItemAvailable(self, item):
        try:
            # logging.warn('Item is available? [' + len(item.xpath(
            #     'article/div[4]/i[@class="is-out-of-stock"]').get()) == 0 + ']')
            return len(item.xpath('article/div[4]/i[@class="is-out-of-stock"]').get()) == 0
        except:
            return True

    def getActualAmount(self, amt):
        try:
            return int(re.findall(r'\d+', amt)[-1])
        except Exception:
            return 1
