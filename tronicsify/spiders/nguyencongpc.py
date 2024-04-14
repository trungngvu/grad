import scrapy
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, CaseItem, DiskItem

class NguyencongpcSpider(scrapy.Spider):
    name = "nguyencongpc"
    allowed_domains = ["nguyencongpc.vn"]
    # start_urls = [
    #     "https://nguyencongpc.vn/ram",
    # ]
    start_urls = [
        "https://nguyencongpc.vn/cpu-bo-vi-xu-ly",
        "https://nguyencongpc.vn/vga-card-man-hinh",
        "https://nguyencongpc.vn/mainboard-bo-mach-chu",
        "https://nguyencongpc.vn/ram",
        "https://nguyencongpc.vn/psu-nguon-may-tinh",
        "https://nguyencongpc.vn/tan-nhiet-nuoc-aio",
        "https://nguyencongpc.vn/tan-nhiet-khi",
        "https://nguyencongpc.vn/case-vo-may-tinh",
        "https://nguyencongpc.vn/o-cung-ssd",
        "https://nguyencongpc.vn/o-cung-hdd"
    ]

    def parse(self, response):
        items = response.css('.list-product-category .product-item')

        for item in items:
            relative_url = item.css('a ::attr(href)').get()
            item_url = response.urljoin(relative_url)
            meta={}
            if "cpu" in response.url: meta={'item_type': 'cpu'}
            elif "vga" in response.url: meta={'item_type': 'gpu'}
            elif "mainboard" in response.url: meta={'item_type': 'main'}
            elif "ram" in response.url: meta={'item_type': 'ram'}
            elif "psu" in response.url: meta={'item_type': 'psu'}
            elif "case" in response.url: meta={'item_type': 'case'}
            elif "ssd" in response.url: meta={'item_type': 'disk', 'sub': 'ssd'}
            elif "hdd" in response.url: meta={'item_type': 'disk', 'sub': 'hdd'}
            elif "tan-nhiet-khi" in response.url: meta={'item_type': 'cooler', 'sub': 'air'}
            elif "aio" in response.url: meta={'item_type': 'cooler', 'sub': 'aio'}
            yield response.follow( item_url, callback=self.parse_item, meta=meta)

        next_page = response.css('.paging .current+a ::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

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
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/span/span/text()").get(),
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/span/span/text()").get(),
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/p/text()").get(),
                response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/p/span/text()").get(),
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
            
        item['url'] = response.url
        item['title'] = response.css('.product-name ::text').get()
        item['warranty'] = response.css('.warranty ::text').get()
        item['availability'] = response.css('.color-green ::text').get()
        item['price'] = response.css('.price-detail ::text').get()
        item['short_specs'] = response.css('.list-product-summary').get()
        item['long_specs'] = response.css('.content-spec tbody').get()
        # Extracting possible brand values using XPath
        brands = [
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/span/text()").get(),
            
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/span/span/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/text()").get(),
            response.xpath("//td[contains(., 'Hãng')]/following-sibling::td[1]/p/span/text()").get(),
            
            
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/span/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/span/span/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/p/text()").get(),
            response.xpath("//td[contains(., 'Thương hiệu')]/following-sibling::td[1]/p/span/text()").get(),
        ]

        # Stripping and filtering out empty strings
        brands = [brand.strip() for brand in brands if brand]

        # Assigning item['brand'] based on the first non-empty string in brands list
        item['brand'] = next((brand for brand in brands if brand), "")
        item['description'] = response.css('.content-descreption-detail').get()
        item['imgs'] = [response.urljoin(img) for img in response.css('.product-images-slider .swiper-wrapper img::attr(data-src)').getall()]

        yield item
