import scrapy
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, CaseItem, DiskItem

class HacomSpider(scrapy.Spider):
    name = "hacom"
    allowed_domains = ["hacom.vn"]
    # start_urls = []
   
    start_urls = ["https://hacom.vn/cpu-bo-vi-xu-ly","https://hacom.vn/vga-card-man-hinh", "https://hacom.vn/mainboard-bo-mach-chu", "https://hacom.vn/ram-bo-nho-trong","https://hacom.vn/nguon-may-tinh"
                  "https://hacom.vn/o-cung-hdd-desktop", "https://hacom.vn/o-cung-ssd", "https://hacom.vn/vo-case", "https://hacom.vn/tan-nhiet-khi","https://hacom.vn/tan-nhiet-nuoc-all-in-one"]

    def parse(self, response):
        
        items = response.css('.p-component')

        for item in items:
            relative_url = item.css('a ::attr(href)').get()
            item_url = 'https://hacom.vn' + relative_url
            if "https://hacom.vn/vga-card-man-hinh" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'gpu'})
            elif "https://hacom.vn/cpu-bo-vi-xu-ly" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'cpu'})
            elif "https://hacom.vn/mainboard-bo-mach-chu" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'main'})
            elif "https://hacom.vn/ram-bo-nho-trong" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'ram'})
            elif "https://hacom.vn/nguon-may-tinh" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'psu'})
            elif "https://hacom.vn/vo-case" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'case'})    
            elif "https://hacom.vn/tan-nhiet-khi" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'cooler', 'sub': 'air'})
            elif "https://hacom.vn/tan-nhiet-nuoc-all-in-one" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'cooler', 'sub': 'aio'})          
            elif "https://hacom.vn/o-cung-ssd" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'disk', 'sub': 'ssd'})
            elif "https://hacom.vn/o-cung-hdd-desktop" in response.url:
                yield response.follow( item_url, callback=self.parse_item, meta={'item_type': 'disk', 'sub': 'hdd'})              
                
                
                                                                
        next_page = response.css('.paging .current+a ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://hacom.vn' + next_page
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
        item['title'] = response.css('.product_detail-title h1 ::text').get()
        item['warranty'] = response.css('.product-summary-item.ribbons div:nth-child(2) ::text').get()
        item['availability'] = response.css('.mua-ngay span ::text').get()
        item['price'] = response.css('#js-pd-price ::attr(data-price)').get()
        item['short_specs'] = response.css('.product-summary-item-ul').get()
        item['long_specs'] = response.css('.bang-tskt tbody').get()
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
        item['imgs']=  response.xpath('//div[contains(@class, "container-icon")]//img/@src').extract()
        item['description']= response.css('#js-product-description').get()

        yield item