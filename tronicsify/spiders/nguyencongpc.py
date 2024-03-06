import scrapy
from tronicsify.items import GPUItem

class NguyencongpcSpider(scrapy.Spider):
    name = "nguyencongpc"
    allowed_domains = ["nguyencongpc.vn"]
    start_urls = ["https://nguyencongpc.vn/vga-card-man-hinh"]

    def parse(self, response):
        
        items = response.css('.list-product-category .product-item')

        for item in items:
            relative_url = item.css('a ::attr(href)').get()
            item_url = 'https://nguyencongpc.vn' + relative_url
            if "https://nguyencongpc.vn/vga-card-man-hinh" in response.url:
                yield response.follow( item_url, callback=self.parse_gpu_page)

        next_page = response.css('.paging .current+a ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://nguyencongpc.vn' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_gpu_page(self, response):
        gpu_item = GPUItem()

        gpu_item['url']= response.url,
        gpu_item['title'] = response.css('.product-name ::text').get()
        gpu_item['prod_id'] = response.xpath("/html/body/section/div[1]/div[1]/div[2]/div[1]/div[1]/span/text()").get()
        gpu_item['warranty'] = response.xpath("/html/body/section/div[1]/div[1]/div[2]/div[2]/div[1]/span/text()").get()
        gpu_item['availability'] = response.css('.color-green ::text').get()
        gpu_item['num_reviews'] = response.xpath("/html/body/section/div[1]/div[1]/div[2]/div[1]/div[2]/span/text()").get()
        gpu_item['stars'] = response.xpath("/html/body/section/div[1]/div[3]/div[1]/div[2]/div[1]/form/div[1]/div[1]/span/text()").get()
        gpu_item['price'] = response.css('.price-detail ::text').get()
        gpu_item['short_specs'] = response.css('.list-product-summary').get()
        gpu_item['long_specs'] = response.css('.content-spec tbody').get()
        gpu_item['num_comments'] = response.xpath("/html/body/section/div[1]/div[1]/div[2]/div[1]/div[3]/span/text()").get()
        gpu_item['views'] = response.xpath("/html/body/section/div[1]/div[1]/div[2]/div[1]/div[4]/span/text()").get()
        gpu_item['brand'] = response.xpath("(//td[starts-with(normalize-space(), 'Hãng sản xuất')]/following-sibling::td[1]/text() | //td[starts-with(normalize-space(), 'Hãng sản xuất')]/following-sibling::td[1]/span/text())[1]").get()
        gpu_item['gpu'] = response.xpath("(//td[starts-with(normalize-space(), 'Nhân đồ họa')]/following-sibling::td[1]/text() | //td[starts-with(normalize-space(), 'Nhân đồ họa')]/following-sibling::td[1]/span/text())[1]").get()
        gpu_item['model'] = response.xpath("(//td[starts-with(normalize-space(), 'Model')]/following-sibling::td[1]/text() | //td[starts-with(normalize-space(), 'Model')]/following-sibling::td[1]/span/text())[1]").get()
        gpu_item['tdp'] = response.xpath("//td[contains(text(), 'TDP')]/following-sibling::td/text()").get()
        gpu_item['imgs']= response.css('.swiper-wrapper').get()

        yield gpu_item