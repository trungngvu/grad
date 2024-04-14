import scrapy
from tronicsify.items import GPUCategory
import re

class GpuCategorySpider(scrapy.Spider):
    name = "gpu_category"
    allowed_domains = ["techpowerup.com"]
    start_urls = ["https://www.techpowerup.com/gpu-specs/?ajaxsrch=rx",
                  "https://www.techpowerup.com/gpu-specs/?ajaxsrch=rtx", 
                  "https://www.techpowerup.com/gpu-specs/?ajaxsrch=gtx%2016",
                  "https://www.techpowerup.com/gpu-specs/?ajaxsrch=gt%2010",]
    download_delay = 10
    

    def parse(self, response):
        for row in response.css('tr')[1:]:
            product_name = row.css('td a ::text')[0].get()
            product_link = row.css('td a ::attr(href)')[0].get()
            released_date = row.css('td')[2].css('::text').get()
            if product_name and "m" not in product_name.lower() and released_date.lower() != "never released":
                yield response.follow("https://www.techpowerup.com" + product_link, callback=self.parse_product)    
                
    def parse_product(self, response):   
        
        def strip_graphics_info(string):
            # Define patterns to match "geforce", "nvidia", "RTX", and "GTX" case insensitively
            patterns = ['radeon', 'rx' , 'amd', 'geforce', 'nvidia', 'rtx', 'gtx' , 'quadro', "ada", "generation"]
            
            # Construct the regular expression pattern
            pattern = '|'.join(r'\b{}\b'.format(re.escape(p)) for p in patterns)

            # Replace matched patterns with an empty string
            result = re.sub(pattern, '', string, flags=re.IGNORECASE)
            
            return " ".join(result.split())
               
        gpu_category =  GPUCategory()
        
        gpu_category['gpu'] = response.css('.gpudb-name ::text').get().strip()  
        gpu_category['brand'] = 'amd' if 'amd' in response.css('.gpudb-name ::text').get().strip().lower() else "nvidia"
        gpu_category['keyword'] = strip_graphics_info(response.css('.gpudb-name ::text').get().strip())
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="TDP"]/dd/text()').get())
        gpu_category['tdp'] = int(number[0])
        number = re.findall(r'\d+', response.xpath('//section[@class="details"]//dl[dt="Memory Size"]/dd/text()').get())
        gpu_category['vram'] = int(number[0])
        
        yield gpu_category
        