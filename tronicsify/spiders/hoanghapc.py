import scrapy
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, CaseItem, DiskItem

class HoanghapcSpider(scrapy.Spider):
    name = "hoanghapc"
    allowed_domains = ["hoanghapc.vn"]
    # start_urls = ["https://hoanghapc.vn/ram-bo-nho-trong"]
    start_urls = ["https://hoanghapc.vn/cpu-bo-vi-xu-ly","https://hoanghapc.vn/vga-card-man-hinh","https://hoanghapc.vn/main-bo-mach-chu","https://hoanghapc.vn/psu-nguon-may-tinh"
                  "https://hoanghapc.vn/ram-bo-nho-trong","https://hoanghapc.vn/tan-nhiet-nuoc-aio", "https://hoanghapc.vn/tan-nhiet-cpu","https://hoanghapc.vn/o-cung-the-ran-ssd"
                  "https://hoanghapc.vn/o-cung-hdd", "https://hoanghapc.vn/case-vo-may-tinh"]

    def parse(self, response):
        
        items = response.css('.p-container .p-item')

        for item in items:
            relative_url = item.css('a ::attr(href)').get()
            item_url = 'https://hoanghapc.vn' + relative_url
            meta={}
            if "https://hoanghapc.vn/vga-card-man-hinh" in response.url: meta={'item_type': 'gpu'}
            elif "https://hoanghapc.vn/cpu-bo-vi-xu-ly" in response.url: meta={'item_type': 'cpu'}
            elif "https://hoanghapc.vn/main-bo-mach-chu" in response.url: meta={'item_type': 'main'}
            elif "https://hoanghapc.vn/psu-nguon-may-tinh" in response.url: meta={'item_type': 'psu'}
            elif "https://hoanghapc.vn/ram-bo-nho-trong" in response.url: meta={'item_type': 'ram'}
            elif "https://hoanghapc.vn/case-vo-may-tinh" in response.url: meta={'item_type': 'case'}
            elif "https://hoanghapc.vn/tan-nhiet-nuoc-aio" in response.url: meta={'item_type': 'cooler', 'sub': 'aio'}
            elif "https://hoanghapc.vn/tan-nhiet-cpu" in response.url: meta={'item_type': 'cooler', 'sub': 'air'}
            elif "https://hoanghapc.vn/o-cung-hdd" in response.url: meta={'item_type': 'disk', 'sub': 'hdd'}
            elif "https://hoanghapc.vn/o-cung-the-ran-ssd" in response.url: meta={'item_type': 'disk', 'sub': 'ssd'}
            yield response.follow( item_url, callback=self.parse_item, meta=meta)
                                                                
        next_page = response.css('.paging .current+a ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://hoanghapc.vn' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_item(self, response):
        item_type = response.meta['item_type']
        if item_type == 'cpu':
            item = CPUItem()
        elif item_type == 'gpu':
            item = GPUItem()
        elif item_type == 'main':
            item = MainboardItem()
        elif item_type == 'ram':
            item = RAMItem()     
            # Extracting possible brand values using XPath
            capacities = [
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/text()").get(),
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/span/text()").get(),
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/p/text()").get(),
            ]

            # Stripping and filtering out empty strings
            capacities = [capacity.strip() for capacity in capacities if capacity]

            # Assigning item['brand'] based on the first non-empty string in capacities list
            item['capacity'] = next((capacity for capacity in capacities if capacity), "")
        elif item_type == 'psu':
            item = PSUItem()   
        elif item_type == 'case':
            item = CaseItem()              
        elif item_type == 'cooler':
            item = CoolerItem()
            item['sub_category'] = response.meta['sub']  
        elif item_type == 'disk':
            item = DiskItem()
            item['sub_category'] = response.meta['sub']  
           

        item['url']= response.url
        item['title'] = response.css('.pd-name ::text').get()
        item['warranty'] = response.css('.pd-warranty ::text').get()
        item['availability'] = "True"
        item['price'] = response.css('.pd-price ::text').get()
        item['short_specs'] = response.css('.pd-summary-list').get()
        item['long_specs'] = response.css('.pd-spec-holder tbody').get()
         # Extracting possible brand values using XPath
        brands = [
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/text()").get(),
            
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/text()").get(),
            
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/p/text()").get()
        ]

        # Stripping and filtering out empty strings
        brands = [brand.strip() for brand in brands if brand]

        # Assigning item['brand'] based on the first non-empty string in brands list
        item['brand'] = next((brand for brand in brands if brand), "")
        item['imgs']= response.xpath('//div[contains(@class, "pd-image-group")]//img/@data-src').extract()
        item['description']= response.css('.pd-content-holder').get()

        yield item