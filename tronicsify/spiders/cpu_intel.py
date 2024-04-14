import scrapy
from tronicsify.items import CPUCategory
import re

class CpuIntelSpider(scrapy.Spider):
    name = "cpu_intel"
    allowed_domains = ["ark.intel.com"]
    start_urls = ["https://ark.intel.com/content/www/us/en/ark/products/series/122139/intel-core-processors.html#@Desktop",
                  "https://ark.intel.com/content/www/us/en/ark/products/series/29862/intel-pentium-processor.html#@Desktop"
                  ]

    header = {
        'host': 'ark.intel.com'
    }
    
    def start_requests(self):
        for url in self.start_urls:  
            yield scrapy.Request(url, self.parse, headers=self.header)

    def parse(self, response):
        links = response.css('.add-compare-wrap a ::attr(href)')
        for link in links:
            yield scrapy.Request("https://ark.intel.com" + link.get() , self.parse_item, headers=self.header)

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # Override middleware settings
            'tronicsify.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': None,
        },
    }
                 
    def parse_item(self, response):
        def strip_cpu_info(string):
            # Define patterns to match "geforce", "nvidia", "RTX", and "GTX" case insensitively
            patterns = ['intel', 'core', 'i9', 'i7' , 'i5' , "i3", '-']
            
            # Construct the regular expression pattern
            pattern = '|'.join(r'\b{}\b'.format(re.escape(p)) for p in patterns)

            # Replace matched patterns with an empty string
            result = re.sub(pattern, '', string, flags=re.IGNORECASE)
            
            return " ".join(result.split())
        
        CPU_category = CPUCategory()

        CPU_category['brand'] = 'intel'
        CPU_category['core'] = response.xpath('//span[@data-key="CoreCount" ]/text()').get()
        CPU_category['thread'] = response.xpath('//span[@data-key="ThreadCount" ]/text()').get()
        CPU_category['cpu'] = response.xpath('//span[@data-key="ProcessorNumber" ]/text()').get()
        CPU_category['tdp'] = response.xpath('//span[@data-key="MaxTDP" ]/text() |  //span[@data-key="MaxTurboPower"]/text()').get()
        CPU_category['boost_clock'] = response.xpath('//span[@data-key="TurboBoostMaxTechMaxFreq" ]/text() |  //span[@data-key="ClockSpeedMax"]/text()').get()
        CPU_category['base_clock'] = response.xpath('//span[@data-key="ECoreBaseFreq" ]/text() |  //span[@data-key="ClockSpeed"]/text() |  //span[@data-key="ECoreTurboFreq"]/text()').get()
        CPU_category['socket'] = response.xpath('//span[@data-key="SocketsSupported" ]/text()').get()
        CPU_category['keyword'] = strip_cpu_info(response.xpath('//span[@data-key="ProcessorNumber" ]/text()').get())
        CPU_category['iGPU'] = response.xpath('//span[@data-key="ProcessorGraphicsModelId" ]/text()').get()
        
        yield CPU_category