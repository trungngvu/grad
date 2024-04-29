import scrapy
import json
import re
from tronicsify.items import CPUCategory

class CpuAmdSpider(scrapy.Spider):
    name = "cpu_amd"
    allowed_domains = ["amd.com"]
    start_urls = ["https://amd.com/en/products/specifications/processors"]
    download_delay = 0.5

    def parse(self, response):   
        data = json.loads(response.css('#product-specs-table-1d8ba6a7da ::attr(data-json)').get())
        rows = data.get('items')
        for row in rows:
            link = row.get('productPages').get('en')
            if link and 'desktops' in link: 
                yield scrapy.Request(link, callback=self.parse_item)

    def parse_item(self, response):       
        CPU_category = CPUCategory()
        
        def extract_word_with_numbers(text):
            pattern = r'\b\w*\d{3,}\w*\b'  # Regular expression pattern to match words with 3 or more digits
            match = re.search(pattern, text)
            if match:
                return match.group()
            else:
                return None

        data = json.loads(response.css('.col-12.product-specs-container ::attr(data-product-specs)').get())
        elements = data.get('elements')

        CPU_category['brand'] = 'amd'
        CPU_category['core'] = elements.get('numOfCpuCores').get('value')
        CPU_category['thread'] = elements.get('numOfThreads').get('value')
        CPU_category['cpu'] = data.get('title')
        CPU_category['tdp'] = elements.get("defaultTdp").get('value')
        CPU_category['boost_clock'] = elements.get("maxBoostClock").get("formatValue")
        CPU_category['base_clock'] = elements.get("baseClock").get("formatValue")
        CPU_category['socket'] =  elements.get("cpuSocket").get("formatValue")
        CPU_category['keyword'] = extract_word_with_numbers(data.get('title'))
        CPU_category['iGPU'] = elements.get("graphicsModel").get("value")

        yield CPU_category        
    
        
        
