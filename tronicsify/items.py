# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TronicsifyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GPUItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    prod_id = scrapy.Field()
    warranty = scrapy.Field()
    availability = scrapy.Field()
    num_reviews = scrapy.Field()
    stars = scrapy.Field()
    price = scrapy.Field()
    short_specs = scrapy.Field()
    long_specs = scrapy.Field()
    num_comments = scrapy.Field()
    views = scrapy.Field()
    brand= scrapy.Field()
    gpu = scrapy.Field()
    model =scrapy.Field()
    tdp = scrapy.Field()
    imgs = scrapy.Field()
