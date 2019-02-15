from scrapy.cmdline import execute

try:
    execute(
        [
            'scrapy',
            'crawl',
            'topcubans',
        ]
    )
except SystemExit:
    pass