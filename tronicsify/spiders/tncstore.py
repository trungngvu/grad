import scrapy
import json

from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, DiskItem, CaseItem

class TncstoreSpider(scrapy.Spider):
    name = "tncstore"
    allowed_domains = ["tncstore.vn"]

    url = "https://www.tncstore.vn/ajax/get_json.php?action=product&action_type=product-list&show=10000&category="
    categories = {
        "gpu": 65,
        "cpu": 62,
        "main": 61,
        'hdd':  64,
        'ssd': 69,
        'case': 66,
        "ram": 63,
        "psu": 67,
        "air": 105,
        "aio": 107
    }

    header = {
    'Authorization': 'Basic ssaaAS76DAs6faFFghs1',
    'Accept':    '*/*',
    'Content-Type':        'application/json',
    'Origin':        'https://www.tncstore.vn',
    'Referer':        'https://www.tncstore.vn/',
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
            url = self.url + str(self.categories[category])
            yield scrapy.Request(url, self.parse_list, headers=self.header, meta={'item_type': category})
           

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
            item['capacity'] = response.xpath("//td[contains(., 'Dung')]/following-sibling::td[1]/p/text() | //td[contains(., 'Dung')]/following-sibling::td[1]/text() ").get()
        elif item_type == 'psu':
            item = PSUItem()  
        elif item_type == 'case':
            item = CaseItem()            
        elif item_type == 'air':
            item = CoolerItem()
            item['sub_category'] = 'air'        
        elif item_type == 'aio':
            item = CoolerItem()
            item['sub_category'] = 'aio' 
        elif item_type == 'hdd':
            item = DiskItem()
            item['sub_category'] = 'hdd' 
        elif item_type == 'ssd':
            item = DiskItem()
            item['sub_category'] = 'ssd'  
        meta =response.meta
        
        item['url']= meta.get('url')
        item['title'] = meta.get('title')
        item['warranty'] = "36 tháng"
        item['availability'] =  meta.get('availability') 
        item['price'] = meta.get('price')
        item['brand'] = meta.get('brand')
        item['imgs'] = meta.get('imgs')
        item['short_specs'] = meta.get('short_specs')
        item['description']= response.css("#content-desciption").get()
        item['long_specs']= response.css("#content-specifications tbody").get()
        yield item 

    def parse_list(self, response): 
        data = json.loads(response.body).get('list')
            
        for item in data:
                
            meta = {
                'item_type': response.meta['item_type'],
                'url':"https://tncstore.vn" + item.get('productUrl'),
                'title' : item.get('productName'),
                'availability' :  "True" if item.get('quantity')>0 else "False", 
                'price' : item.get('price'),
                'brand' : item.get('brand').get('name'),
                'short_specs': item.get('productSummary'),
                'imgs': ["https://www.tncstore.vn" + item["image"]["large"] for item in item.get("imageCollection")]
            }    
          
            yield scrapy.Request("https://www.tncstore.vn" + item.get('productUrl'), self.parse_item, meta=meta)
            