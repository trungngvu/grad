import scrapy
import re
from tronicsify.items import CPUCategory

class CpuAmdSpider(scrapy.Spider):
    name = "cpu_amd"
    allowed_domains = ["amd.com"]
    start_urls = ["https://amd.com/en/products/specifications/processors"]
    download_delay = 0.5

    def parse(self, response):   
        def get_number_following(string, term):
        # Check if the string is not None and contains the term
            if string is not None and term in string:
                # Use regular expression to find the number following the term
                match = re.search(rf"{term}-\s*(\d+)", string)
                if match:
                    return int(match.group(1))
            return None
            
        rows = response.xpath('//tr')
        
        for row in rows:
            platform = row.xpath('.//td[@headers="view-platform-table-column"]/text()').get()
            if platform and ("Boxed Processor" in platform or "Desktop" in platform) and (not "Laptop" in platform):
                term_class = row.xpath('.//td[@headers="view-name-table-column" and contains(text(), "Ryzen") or contains(text(), "Athlon")]/@class').get()
                num = get_number_following(term_class, "entity")
                if num != None: yield scrapy.Request("https://www.amd.com/en/product/"+str(num), callback=self.parse_item)

    def parse_item(self, response):       
        CPU_category = CPUCategory()
        
        def extract_word_with_numbers(text):
            pattern = r'\b\w*\d{3,}\w*\b'  # Regular expression pattern to match words with 3 or more digits
            match = re.search(pattern, text)
            if match:
                return match.group()
            else:
                return None

        CPU_category['brand'] = 'amd'
        CPU_category['core'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'CPU Cores')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()
        CPU_category['thread'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'Threads')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()
        CPU_category['cpu'] = response.css('#block-amd-page-title h2 ::text').get()
        CPU_category['tdp'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'TDP')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()
        CPU_category['boost_clock'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'Boost')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()
        CPU_category['base_clock'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'Base')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()
        CPU_category['socket'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'Socket')]/following-sibling::div/div[@class= 'field__item']/text()").get()
        CPU_category['keyword'] = extract_word_with_numbers(response.css('#block-amd-page-title h2 ::text').get())
        CPU_category['iGPU'] = response.xpath("//div[contains(@class, 'field__label') and contains(text(), 'Integrated Graphics')]/following-sibling::div[contains(@class, 'field__item')]/text()").get()

        yield CPU_category        
    
        
        
