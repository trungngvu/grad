import scrapy
import json
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, CaseItem, DiskItem

class PhongvuSpider(scrapy.Spider):
    name = "phongvu"
    allowed_domains = ["phongvu.vn","discovery.tekoapis.com"]
    
    url = "https://discovery.tekoapis.com/api/v2/search-skus-v2"
    categories = ["cpu", "vga-card-man-hinh", "mainboard-bo-mach-chu", "psu-nguon-may-tinh" ,"ram", "tan-nhiet-khi", "tan-nhiet-nuoc", "case",
                  "o-cung-ssd", "o-cung-hdd"]

    header = {
    ':authority':'discovery.tekoapis.com',
    ':method': 'POST',
    ':path': '/api/v2/search-skus-v2',
    ':scheme':  'https',
    'Accept':    '*/*',
    'Accept-Encoding':        'gzip, deflate, br',
    'Accept-Language':        'vi',
    'Content-Type':        'application/json',
    'Origin':        'https://phongvu.vn',
    'Referer':        'https://phongvu.vn/',
    'Sec-Ch-Ua':        '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    'Sec-Ch-Ua-Mobile':        '?0',
    'Sec-Ch-Ua-Platform':        '"Windows"',
    'Sec-Fetch-Dest':        'empty',
    'Sec-Fetch-Mode':        'cors',
    'Sec-Fetch-Site':        'cross-site',
    'User-Agent':    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    
    def start_requests(self):
        
        for category in self.categories:
            payload = {            
                "terminalId": 4,
                "pageSize": 5000,
                "slug": "/c/" + category
            }    
            if "hdd" in category:
                payload['filter'] = {'attributes': [{'code': "ocung_phanloai", 'optionIds': ["5930"]}]}
            elif "ssd" in category:
                payload['filter'] = {'attributes': [{'code': "ocung_phanloai", 'optionIds': ["5929"]}]}
            yield scrapy.Request(self.url, self.parse, method="POST", body=json.dumps(payload), headers=self.header)

    def parse(self, response):
        data = json.loads(response.body).get('data')
        products = data.get('products')
        category = data.get('seoInfo').get('canonical')
        
        for product in products:
            prod_url = "https://discovery.tekoapis.com/api/v1/product?sku=" + product.get('sku') + "&location=&terminalCode=phongvu"
            meta= {}
            if category == "/c/vga-card-man-hinh":
                meta = {'item_type': 'gpu'}
            elif category == "/c/cpu":
                meta = {'item_type': 'cpu'}
            elif category == "/c/mainboard-bo-mach-chu":
                meta = {'item_type': 'main'}
            elif category == "/c/psu-nguon-may-tinh":
                meta = {'item_type': 'psu'}
            elif category == "/c/ram":
                meta = {'item_type': 'ram'}
            elif category == "/c/case":
                meta = {'item_type': 'case'}
            elif category == "/c/tan-nhiet-khi" or category == "/c/tan-nhiet-nuoc":
                meta = {'item_type': 'cooler', 'sub': 'air'}
            elif category == "/c/o-cung-ssd" or category == "/c/o-cung-hdd":
                meta = {'item_type': 'disk', 'sub': 'ssd'}

            yield scrapy.Request(prod_url, self.parse_item, headers=self.header, meta=meta)     

    def parse_item(self, response):
        # Process the response from the POST request
        # You can extract data or perform further parsing here
        result_data = json.loads(response.body)      
        item_type = response.meta['item_type']
        product = result_data.get('result').get('product')
        info = product.get('productInfo')
        detail = product.get('productDetail')
        attributeGroups = detail.get('attributeGroups')
        
        if item_type == 'cpu':
            item = CPUItem()
        elif item_type == 'gpu':
            item = GPUItem()
        elif item_type == 'main':
            item = MainboardItem()
        elif item_type == 'ram':
            item = RAMItem()  
        
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

        item['url']= "https://phongvu.vn/" + info.get('canonical')
        item['title'] = info.get('displayName')
        item['warranty'] = str(info.get('warranty').get('months')) + " tháng"
        item['availability'] = "False" if product.get('totalAvailable') == 0 else "True" 
        item['price'] = product.get('prices')[0].get('sellPrice') if product.get('prices') else None
        item['short_specs'] = detail.get('shortDescription')
        item['long_specs'] = attributeGroups
        item['description'] = detail.get('description')
        item['brand'] = info.get('brand').get('name')
        item['imgs']= [item.get('url') for item in detail.get('images')]

        yield item