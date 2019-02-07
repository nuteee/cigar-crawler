# -*- coding: utf-8 -*-

import scrapy
from scrapy.crawler import CrawlerProcess
from cigarCrawler.spiders.hacico import HacicoSpider
from cigarCrawler.spiders.danpipe import DanpipeSpider

process = CrawlerProcess()
process.crawl(HacicoSpider)
process.crawl(DanpipeSpider)
process.start() # the script will block here until all crawling jobs are finished