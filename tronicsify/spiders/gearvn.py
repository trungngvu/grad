import scrapy
import json
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, DiskItem, CaseItem

class GearvnSpider(scrapy.Spider):
    name = "gearvn"
    allowed_domains = ["gearvn.com"]
    
    categories = []
    # categories = ["cpu-bo-vi-xu-ly","vga-card-man-hinh", "mainboard-bo-mach-chu", "psu-nguon-may-tinh", "ram-pc", "tan-nhiet-nuoc-240mm" , "tan-nhiet-nuoc-280mm"
    #               , "tan-nhiet-nuoc-360mm", "tan-nhiet-nuoc-420mm", "tan-nhiet-khi", 'hdd-o-cung-pc', 'ssd-o-cung-the-ran', 'case-thung-may-tinh']

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
            meta={}
            if category == "vga-card-man-hinh":
                meta = {'item_type': 'gpu'}
            elif category == "cpu-bo-vi-xu-ly":
                meta = {'item_type': 'cpu'}
            elif category == "mainboard-bo-mach-chu":
                meta = {'item_type': 'main'}
            elif category == "psu-nguon-may-tinh":
                meta = {'item_type': 'psu'} 
            elif category == "ram-pc":
                meta = {'item_type': 'ram'}
            elif category == "hdd-o-cung-pc":
                meta = {'item_type': 'disk', 'sub': 'hdd'}
            elif category == "ssd-o-cung-the-ran":
                meta = {'item_type': 'disk', 'sub': 'ssd'}
            elif category == "case-thung-may-tinh":
                meta = {'item_type': 'case'}
            else:
                if "tan-nhiet-nuoc" in category:
                    meta = {'item_type': 'cooler', 'sub': 'aio'}
                elif "tan-nhiet-khi" in category:
                    meta = {'item_type': 'cooler', 'sub': 'air'}

            # match category:
            #     case "vga-card-man-hinh":  meta={'item_type': 'gpu'}
            #     case "cpu-bo-vi-xu-ly":  meta={'item_type': 'cpu'}
            #     case "mainboard-bo-mach-chu":  meta={'item_type': 'main'}
            #     case "psu-nguon-may-tinh":  meta={'item_type': 'psu'} 
            #     case "ram-pc":  meta={'item_type': 'ram'}
            #     case "hdd-o-cung-pc":  meta={'item_type': 'disk', 'sub': 'hdd'}
            #     case "ssd-o-cung-the-ran":  meta={'item_type': 'disk', 'sub': 'ssd'}
            #     case "case-thung-may-tinh": meta={'item_type': 'case'}
            #     case _: 
            #         if "tan-nhiet-nuoc" in category:  meta={'item_type': 'cooler', 'sub': 'aio'}
            #         elif "tan-nhiet-khi" in category:  meta={'item_type': 'cooler', 'sub': 'air'}
            yield scrapy.Request("https://gearvn.com/products/" + product.get('handle'), self.parse_item, meta=meta)         

        if len(products) > 0:
            yield scrapy.Request(self.gen_url(category, int(page)+1), self.parse, meta={'category': category, 'page': int(page)+1} )
            

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
            capacity_text = response.xpath('//div[@class="product-desc-short prtab2"]/ul/li[contains(., "Dung lượng")]/span/text()').get()
            if capacity_text:
                capacity = capacity_text.split(":", 1)[-1].strip()
                item['capacity'] = capacity        
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
        item['title'] = response.css('.product-name h1 ::text').get()
        item['warranty'] = "36 tháng"
        item['availability'] = response.css('.btn-buynow ::attr(disabled)').get()
        item['price'] = response.css('.pro-price.a ::text').get()
        item['short_specs'] = response.xpath('//*[@id="detail-product"]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[2]/div[6]/ul').get()
        item['long_specs'] = response.xpath('//*[@id="tblGeneralAttribute"]/tbody').get()
        
        brand_text = response.xpath('//div[@class="product-desc-short prtab2"]/ul/li[contains(., "xuất")]/span/text()').get()
        if brand_text:
            brand = brand_text.split(":", 1)[-1].strip()
            item['brand'] = brand
            
        item['description']= response.css('.desc-content').get()
        
        imgs=[]
        for img in response.css('.product-gallery--slide a'):
            imgs.append("https:"+ img.css('::attr(href)').get())
        item['imgs']= imgs
        
        yield item