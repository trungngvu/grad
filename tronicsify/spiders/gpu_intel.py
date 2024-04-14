import scrapy
from tronicsify.items import GPUCategory
from scrapy import Selector
import re
import json


class GpuIntelSpider(scrapy.Spider):
    name = "gpu_intel"
    allowed_domains = ["techpowerup.com"]
    start_urls = ["https://www.techpowerup.com/gpu-specs/?mfgr=Intel&mobile=No&workstation=No&memtype=GDDR6&sort=name&ajax=1"]
    download_delay = 10
    

    def parse(self, response):
        html = Selector(text=json.loads(response.body).get('list'))
        for row in html.css('tr')[2:]:
            product_name = row.css('td a ::text')[0].get()
            product_link = row.css('td a ::attr(href)')[0].get()
            released_date = row.css('td')[2].css('::text').get() 
            if product_name and "m" not in product_name.lower() and released_date.lower() != "never released":
                yield response.follow("https://www.techpowerup.com" + product_link, callback=self.parse_product)    
                
    def parse_product(self, response):            
        gpu_category =  GPUCategory()
        
        gpu_category['brand'] = 'intel'
        gpu_category['gpu'] = response.css('.gpudb-name ::text').get().strip()  
        gpu_category['keyword'] = response.css('.gpudb-name ::text').get().strip()  
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="TDP"]/dd/text()').get())
        gpu_category['tdp'] = int(number[0])
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="Memory Size"]/dd/text()').get())
        gpu_category['vram'] = int(number[0])
        
        yield gpu_category
        