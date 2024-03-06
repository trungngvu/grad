import scrapy
from tronicsify.items import GPUItem

class HacomSpider(scrapy.Spider):
    name = "hacom"
    allowed_domains = ["hacom.vn"]
    # start_urls = ["https://hacom.vn/cpu-bo-vi-xu-ly","https://hacom.vn/mainboard-bo-mach-chu","https://hacom.vn/ram-bo-nho-trong","https://hacom.vn/vga-card-man-hinh",
    #               "https://hacom.vn/o-cung-ssd","https://hacom.vn/odd-o-dia-quang","https://hacom.vn/card-am-thanh","https://hacom.vn/vo-case","https://hacom.vn/nguon-may-tinh",
    #               "https://hacom.vn/tan-nhiet-khi","https://hacom.vn/tan-nhiet-nuoc-all-in-one","https://hacom.vn/quat-tan-nhiet","https://hacom.vn/keo-tan-nhiet","https://hacom.vn/man-hinh-may-tinh-theo-hang"]
    start_urls = ["https://hacom.vn/vga-card-man-hinh"]

    def parse(self, response):
        
        items = response.css('.p-component')

        for item in items:
            relative_url = item.css('a ::attr(href)').get()
            item_url = 'https://hacom.vn' + relative_url
            if "https://hacom.vn/vga-card-man-hinh" in response.url:
                yield response.follow( item_url, callback=self.parse_gpu_page)

        next_page = response.css('.paging .current+a ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://hacom.vn' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_gpu_page(self, response):
        gpu_item = GPUItem()

        gpu_item['url']= response.url,
        gpu_item['title'] = response.css('.product_detail-title h1 ::text').get()
        gpu_item['prod_id'] = response.css('.sku ::text').get()
        gpu_item['warranty'] = response.css('.product-summary-item.ribbons div:nth-child(2) ::text').get()
        gpu_item['availability'] = response.css('.mua-ngay span ::text').get()
        gpu_item['num_reviews'] = response.css('.count-rate ::text').get()
        gpu_item['stars'] = response.css('.avgRate span ::text').get()
        gpu_item['price'] = response.css('#js-pd-price ::attr(data-price)').get()
        gpu_item['short_specs'] = response.css('.product-summary-item-ul').get()
        gpu_item['long_specs'] = response.css('.bang-tskt tbody').get()
        gpu_item['num_comments'] = response.css('.counter-number ::text').get()
        gpu_item['views'] = response.css('div.product_detail-view-counter span ::text').get()
        gpu_item['brand'] = response.xpath('//*[@id="tab2"]/div/div[1]/table/tbody/tr[2]/td[2]/text()').get()
        gpu_item['gpu'] = response.xpath('//*[@id="tab2"]/div/div[1]/table/tbody/tr[4]/td[2]/text()').get()
        gpu_item['model'] = response.xpath('//*[@id="tab2"]/div/div[1]/table/tbody/tr[3]/td[2]/text()').get()
        gpu_item['tdp'] = response.xpath('//tr[td[contains(text(), "Công suất nguồn yêu cầu")]]/td[2]/text()').get()
        gpu_item['imgs']= response.css('.owl-carousel').get()

        yield gpu_item