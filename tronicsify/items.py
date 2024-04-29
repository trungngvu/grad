# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Item(scrapy.Item):
    _id = scrapy.Field()
class Product(Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    warranty = scrapy.Field()
    short_specs = scrapy.Field()
    long_specs = scrapy.Field()
    brand= scrapy.Field()
    imgs = scrapy.Field()
    slug = scrapy.Field()
    price = scrapy.Field()
    reviews = scrapy.Field()
    availability = scrapy.Field()
    updatedAt = scrapy.Field()
    category = scrapy.Field()
    embedding = scrapy.Field()
class GPUCategory(Item):
    brand = scrapy.Field()
    gpu = scrapy.Field()
    tdp = scrapy.Field()  
    vram = scrapy.Field()  
    keyword = scrapy.Field()      
class CPUCategory(Item):
    brand = scrapy.Field()
    core = scrapy.Field()
    thread = scrapy.Field()
    cpu = scrapy.Field()
    tdp = scrapy.Field()  
    boost_clock = scrapy.Field()  
    base_clock = scrapy.Field()  
    socket = scrapy.Field()  
    keyword = scrapy.Field()  
    iGPU = scrapy.Field() 
class GPUItem(Product):
    manufacturer = scrapy.Field()
class CPUItem(Product):
    pass
class MainboardItem(Product):
    socket = scrapy.Field() 
    size = scrapy.Field() 
    ram = scrapy.Field()         
class RAMItem(Product):
    capacity = scrapy.Field()
    ram = scrapy.Field()
class PSUItem(Product):
    wattage = scrapy.Field() 
class CoolerItem(Product):
    sub_category = scrapy.Field()
class DiskItem(Product):
    sub_category = scrapy.Field()
    connector = scrapy.Field()
    capacity = scrapy.Field()
class CaseItem(Product):
    size = scrapy.Field()