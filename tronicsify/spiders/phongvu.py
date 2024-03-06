import scrapy
import json
from tronicsify.items import GPUItem


class PhongvuSpider(scrapy.Spider):
    name = "phongvu"
    allowed_domains = ["phongvu.vn","discovery.tekoapis.com"]
    
    url = "https://discovery.tekoapis.com/api/v2/search-skus-v2"
    categories = ["/c/vga-card-man-hinh"]

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
                "slug": category
            }    
            yield scrapy.Request(self.url, self.parse, method="POST", body=json.dumps(payload), headers=self.header)

    def parse(self, response):
        data = json.loads(response.body).get('data')
        products = data.get('products')
        category = data.get('seoInfo').get('canonical')
        
        for product in products:
            prod_url = "https://discovery.tekoapis.com/api/v1/product?sku=" + product.get('sku') + "&location=&terminalCode=phongvu"
            match category: 
                case "/c/vga-card-man-hinh":  yield scrapy.Request(prod_url, self.parse_gpu, headers=self.header)

    def parse_gpu(self, response):
        # Process the response from the POST request
        # You can extract data or perform further parsing here
        result_data = json.loads(response.body)      
        gpu_item = GPUItem()
        
        product = result_data.get('result').get('product')
        info = product.get('productInfo')
        detail = product.get('productDetail')

        gpu_item['url']= "https://phongvu.vn/" + info.get('canonical'),
        gpu_item['title'] = info.get('name'),
        gpu_item['prod_id'] = info.get('sku'),
        gpu_item['warranty'] = info.get('warranty').get('months'),
        gpu_item['availability'] = product.get('totalAvailable') 
        gpu_item['num_reviews'] = None
        gpu_item['stars'] = None
        gpu_item['price'] = product.get('prices')[0].get('sellPrice') if product.get('prices') else None
        gpu_item['short_specs'] = detail.get('shortDescription')
        gpu_item['long_specs'] = detail.get('attributeGroups')
        gpu_item['num_comments'] = None
        gpu_item['views'] = None
        gpu_item['brand'] = info.get('brand').get('name')
        
        for i in detail.get('attributeGroups'):
            match i.get('name'):
                case "GPU": gpu_item['gpu'] = i.get('value')
                case "Part-number": gpu_item['model'] = i.get('value')
                case "Nguồn đề xuất":  gpu_item['tdp'] = i.get('value')

        gpu_item['imgs']= detail.get('images')

        yield gpu_item
