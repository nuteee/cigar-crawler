# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Cigar(scrapy.Item):
    country = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    amount = scrapy.Field(serializer=int)
    price = scrapy.Field(serializer=float)
    pricePerStick = scrapy.Field(serializer=float)
    pricePerStickHuf = scrapy.Field(serializer=float)
    currency = scrapy.Field()
    website = scrapy.Field()
    url = scrapy.Field()

