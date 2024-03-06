import scrapy
import json
from tronicsify.items import GPUItem


class GearvnSpider(scrapy.Spider):
    name = "gearvn"
    allowed_domains = ["gearvn.com"]
    start_urls = ["https://gearvn.com"]
    
    categories = ["vga-card-man-hinh"]

    def gen_url(self, category, page):
        return "https://gearvn.com/collections/" + category + "/products.json?include=metafields[product]&limit=50&page=" + str(page)
    
    def start_requests(self):
        for category in self.categories:
            url = self.gen_url(category, 1)
            yield scrapy.Request(url, self.parse, 
                                 meta={'category': category, 'page': 1})
   
    def parse(self, response):
        # Access the additional parameter in the parse function
        category = response.meta.get('category')
        page = response.meta.get('page')
        products = json.loads(response.body).get('products')
        
        for product in products:
            match category:
                case "vga-card-man-hinh": yield scrapy.Request("https://gearvn.com/products/" + product.get('handle'), self.parse_gpu)    

        if len(products) > 0:
            yield scrapy.Request(self.gen_url(category, int(page)+1), self.parse, meta={'category': category, 'page': int(page)+1} )
            

    def parse_gpu(self, response):
        gpu_item = GPUItem()
        
        gpu_item['url']= response.url,
        gpu_item['title'] = response.css('.product-name h1 ::text').get()
        gpu_item['prod_id'] = response.url
        gpu_item['warranty'] = 36
        gpu_item['availability'] = response.css('.btn-buynow ::attr(disabled)').get()
        gpu_item['num_reviews'] = response.css('.product-reviews--total span ::text').get()
        gpu_item['stars'] = response.css('.product-reviews--number span ::text').get()
        gpu_item['price'] = response.css('.pro-price.a ::text').get()
        gpu_item['short_specs'] = response.xpath('//*[@id="detail-product"]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[6]/ul').get()
        gpu_item['long_specs'] = response.xpath('//*[@id="tblGeneralAttribute"]/tbody').get()
        gpu_item['num_comments'] = response.css('.product-reviews--total span ::text').get()
        gpu_item['views'] = response.css('div.product_detail-view-counter span ::text').get()
        gpu_item['brand'] = response.xpath('//div[@class="product-desc-short prtab2"]/ul/li[contains(., "xuất")]/span/text()').get()
        gpu_item['gpu'] = response.xpath("//td[contains(span, 'Nhân đồ họa') or contains(span, 'GPU')]/following-sibling::td/span/text()").get()
        gpu_item['model'] = response.xpath("//div[@class='product-desc-short prtab2']//li[contains(., 'Mã sản phẩm')]/span/strong/text()").get()
        gpu_item['tdp'] = response.xpath("//td[contains(span, 'PSU') or contains(span, 'Nguồn')]/following-sibling::td/span/text()").get()
        gpu_item['imgs']= response.css('.swiper-wrapper').get()
        
        yield gpu_item