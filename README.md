# cigar-crawler
This is a basic web-crawler project based on python and scrapy to get the prices of the cigars.

# How to run:

- `pip install scrapy forex-python`
- `scrapy crawl danpipe && scrapy crawl hacico && scrapy crawl topcubans`

# Heroku:

- `heroku run:detached data_load`
- `heroku scale discord=1`