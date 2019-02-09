# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

import pymongo
from forex_python.converter import CurrencyRates


class CigarcrawlerPipeline(object):
    eurToHufRate = CurrencyRates().get_rate('EUR', 'HUF')

    def process_item(self, item, spider):
        item['pricePerStick'] = item.get('price') / item.get('amount')
        item['pricePerStickHuf'] = item['pricePerStick'] * self.eurToHufRate

        return item


class MongoPipeline(object):

    collection_name = 'cigar_items'

    def __init__(self, mongo_uri, mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.db[self.collection_name].ensure_index([('country', 'text'), ('brand', 'text'),('name', 'text')], name="search_index", weights={ 'name': 100, 'brand': 25, 'country': 17})
        # logging.info("[MongoDB] Dropping")
        # logging.info(self.db[self.collection_name])
        # self.db[self.collection_name].drop()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'cigars')
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        logging.debug("Inserted:")
        logging.debug(item)
        # return item
