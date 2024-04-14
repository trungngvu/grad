import scrapy
from tronicsify.items import GPUCategory
import re


class GpuNvidiaSpider(scrapy.Spider):
    name = "gpu_nvidia"
    allowed_domains = ["developer.nvidia.com", "techpowerup.com"]
    start_urls = ["https://www.techpowerup.com/gpu-specs/?ajaxsrch=rtx", 
                  "https://www.techpowerup.com/gpu-specs/?ajaxsrch=gtx%2016",
                  "https://www.techpowerup.com/gpu-specs/?ajaxsrch=gt%2010"]
    download_delay = 10
    
    def parse_item(self, response):
        lookup_url = "https://www.techpowerup.com" + response.css('a ::attr(href)').get()
        yield scrapy.Request(lookup_url, self.lookup_item, meta=response.meta)   
        
    def lookup_item(self, response):
        def strip_graphics_info(string):
            # Define patterns to match "geforce", "nvidia", "RTX", and "GTX" case insensitively
            patterns = ['geforce', 'nvidia', 'rtx', 'gtx' , 'quadro']
            
            # Construct the regular expression pattern
            pattern = '|'.join(r'\b{}\b'.format(re.escape(p)) for p in patterns)

            # Replace matched patterns with an empty string
            result = re.sub(pattern, '', string, flags=re.IGNORECASE)
            
            return " ".join(result.split())
        
        gpu_category = GPUCategory()
        
        gpu_category['brand'] = 'nvidia'
        gpu_category['gpu'] = response.meta['gpu'].strip()
        gpu_category['keyword'] = strip_graphics_info(response.meta['gpu'].strip())
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="TDP"]/dd/text()').get())
        gpu_category['tdp'] = int(number[0])
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="Memory Size"]/dd/text()').get())
        gpu_category['vram'] = int(number[0])
        
        yield gpu_category
        
    def parse(self, response):
        cards = response.xpath('//div[@class="row"]//li/text()').extract()
        cards = [card for card in cards if card != '\n']
        for item in cards:
            yield scrapy.Request("https://www.techpowerup.com/gpu-specs/?ajaxsrch=" + item, self.parse_item, meta={'gpu': item})   
            
            
            
        
        
