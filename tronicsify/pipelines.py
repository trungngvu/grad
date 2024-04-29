# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from tronicsify.items import Product
from tronicsify.items import GPUItem, CPUItem, MainboardItem, PSUItem, RAMItem, CoolerItem, CPUCategory, CaseItem, DiskItem

from tronicsify.items import GPUCategory

from tronicsify.getmongo import get_database

import re
from urllib.parse import urlparse
from datetime import datetime
from slugify import slugify
from sentence_transformers import SentenceTransformer

# pipelines.py
class ProductsPipeline:
    def __init__(self):
        # Get the database using the method we defined in pymongo_test_insert file
        self.dbname = get_database()
        self.productsCollectionName = "products"
        # https://huggingface.co/keepitreal/vietnamese-sbert
        self.embedding_model = SentenceTransformer("keepitreal/vietnamese-sbert")
        self.products_collection = self.dbname[self.productsCollectionName]
        
    def process_item(self, item, spider):
        if isinstance(item, Product):
            adapter = ItemAdapter(item)
            
            ## Drop item without required field
            required_fields = ['title', 'price']
            for field in required_fields:
                if adapter.get(field) == "": raise DropItem(f"Missing price or title in {item}")

            def get_embedding(text: str) -> list[float]:
                if not text.strip():
                    print("Attempted to get embedding for empty text.")
                    return []

                embedding = self.embedding_model.encode(text)

                return embedding.tolist()
            adapter["embedding"] = get_embedding(adapter["title"])
                
            ## Set product category
            if isinstance(item, GPUItem): adapter['category'] = "gpu"
            elif isinstance(item, CPUItem): adapter['category'] = "cpu"
            elif isinstance(item, MainboardItem): adapter['category'] = "main"
            elif isinstance(item, PSUItem): adapter['category'] = "psu"
            elif isinstance(item, RAMItem): adapter['category'] = "ram"
            elif isinstance(item, CoolerItem): adapter['category'] = "cooler"
            elif isinstance(item, DiskItem): adapter['category'] = "disk"
            elif isinstance(item, CaseItem): adapter['category'] = "case"
            
            ## Normalize brand
            if adapter.get('brand', None):
                brand = str(adapter['brand'])
                brand = brand.strip().lower()
                adapter['brand'] = brand 
                if brand and (brand[0].isnumeric() or brand.count(" ")>2 or brand.count("-")>2): del adapter['brand']
            
            ## Add slug
            parsed_url = urlparse(adapter.get('url'))
            domain = parsed_url.netloc.split('.')[0]
            adapter['slug'] = slugify(domain + " " +  adapter.get('title'))
            
            ## Strip whitespace
            strip_keys = ['warranty']
            for key in strip_keys:
                value = str(adapter.get(key))
                adapter[key] = value.strip()
            
            ## Convert warranty to int
            int_keys = ['price']
            for int_key in int_keys:
                value = adapter.get(int_key)
                number_pattern = re.compile(r'\d+')
                numbers = number_pattern.findall(str(value))
                try:
                    adapter[int_key] = int(''.join(numbers))
                except ValueError:
                    raise DropItem(f"Price is NaN in {item}")
                
            ## Availability --> extract boolean   
            avail = ["Đặt mua ngay", "Còn hàng", "True"]
            availability_string = adapter.get('availability')
            if availability_string == None: 
                adapter['availability'] = False
            elif any(substring in availability_string for substring in avail): 
                adapter['availability'] = True 
            else: adapter['availability'] = False
            
            ## Record date
            adapter['updatedAt'] = datetime.now().isoformat()
            
            
            lowered_title = adapter['title'].lower()
            ## CPU brand is Intel | AMD
            if isinstance(item, CPUItem): 
                if 'intel' in lowered_title or 'core' in lowered_title: adapter['brand']= 'intel'
                elif 'amd' in lowered_title: adapter['brand']= 'amd'
                else: del adapter['brand']
                
            ## GPU brand is Intel | Nvidia | AMD    
            if isinstance(item, GPUItem):
                ## GPU scraped brand is manufacturer
                adapter['manufacturer'] = adapter.get('brand')
                
                if 'intel' in lowered_title: adapter['brand']= 'intel'
                elif any(keyword in lowered_title for keyword in ['nvidia', 'gt', 'rtx', 'quadro', 'geforce', 'ti']): adapter['brand']= 'nvidia'
                elif any(keyword in lowered_title for keyword in ['amd', 'radeon', 'rx']): adapter['brand']= 'amd'
                else: del adapter['brand']
                
            ## Extract Wattage from products' title  
            if isinstance(item, PSUItem):  
                wattage = re.search(r'\d+W', adapter['title'] )
                if wattage:
                    adapter['wattage'] = int(wattage.group()[:-1])
                    
            if adapter.get('long_specs', None):
                long_specs = str(adapter['long_specs']) 
            else: long_specs = None
            if adapter.get('short_specs', None):
                short_specs = str(adapter['short_specs']) 
            else: short_specs = None
            if isinstance(item, MainboardItem):  
                ## Normalize socket
                sockets= ['1150', '1151', '1155', '1200', '1700', '2011', '2066', 'AM4', 'AM5', 'sTR5', 'sTRX4']
                for socket in sockets:
                    if long_specs and socket in long_specs: 
                        adapter['socket'] = socket
                        break
                    elif short_specs and socket in short_specs:  
                        adapter['socket'] = socket
                        break
            if isinstance(item, MainboardItem) or isinstance(item, RAMItem):
                ## Normalize supported RAM
                ram_lines = ['DDR3','DDR4','DDR5']
                for ram_line in ram_lines:
                    if long_specs and ram_line in long_specs: 
                        adapter['ram'] = ram_line
                        break
                    elif short_specs and ram_line in short_specs:  
                        adapter['ram'] = ram_line
                        break
                        
            if isinstance(item, DiskItem):
                ## Normalize socket
                if adapter['sub_category'] == 'hdd': 
                    adapter['connector'] = 'SATA'
                elif (long_specs and ('pcie' in long_specs.lower() or 'nvme' in long_specs.lower())) or (short_specs and ('pcie' in short_specs.lower() or 'nvme' in short_specs.lower())): 
                    adapter['connector'] = 'M.2 NVMe'                 
                elif (long_specs and ('M2' in long_specs or 'M.2' in long_specs)) or (short_specs and (  'M2' in short_specs or 'M.2' in short_specs)) : 
                    adapter['connector'] = 'M.2 SATA'
                elif (short_specs and ('SATA' in short_specs)) or (long_specs and ( 'SATA' in long_specs)):  
                    adapter['connector'] = 'SATA'
                ## Normalize capacity
                def extract_capacity(product_title):
                    # Define regular expression pattern to match capacity
                    pattern = r'(\d+)(GB|TB)'

                    # Search for matches
                    matches = re.search(pattern, product_title, re.IGNORECASE)

                    if matches:
                        # Extract capacity value and unit
                        capacity = int(matches.group(1))
                        unit = matches.group(2)

                        # Convert TB to GB if unit is TB
                        if unit == 'TB' or unit == 'tb' or unit == 'Tb':
                            capacity *= 1024

                        return capacity
                    else:
                        return None
                adapter['capacity'] =  extract_capacity(adapter['title'])   
                
            if isinstance(item, RAMItem):
                ## Normalize capacity
                def extract_ram_capacity(ram_description):
                    # Define a regular expression pattern to match numbers followed by "GB"
                    pattern = r'\b(\d+)\s*GB\b'

                    # Use re.sub() to remove characters inside parentheses
                    cleaned_description = re.sub(r'\([^)]*\)', '', ram_description)

                    # Use re.search() to find the first match of the pattern in the cleaned description
                    match = re.search(pattern, cleaned_description, re.IGNORECASE)

                    if match:
                        # Extract the matched capacity and convert it to an integer
                        capacity = int(match.group(1))
                        return capacity
                    else:
                        # Return None if no capacity is found
                        return None
                adapter_capacity = adapter.get('capacity')  # Get the value of 'capacity' or None if not found
                title_capacity = adapter.get('title')  # Get the value of 'title' or None if not found

                # Check if adapter_capacity is not None before calling strip() method
                if adapter_capacity is not None and adapter_capacity.strip() != "":
                    capacity = extract_ram_capacity(adapter_capacity)
                else:
                    capacity = extract_ram_capacity(title_capacity)
                adapter['capacity'] = capacity       

            if isinstance(item, CaseItem) or isinstance(item, MainboardItem):
                ## Normalize size
                sizes = [['E-ATX', 'Extended-ATX', 'eATX'], ['M-ATX', 'Micro-ATX', 'mATX', 'microATX'], ['ATX'] , ['ITX']]   
                for size_variations in sizes:
                    found = False
                    for size_variation in size_variations:
                        if long_specs and size_variation.lower() in str(long_specs).lower():
                            adapter['size'] = size_variations[0]
                            found = True
                            break  # No need to continue once size is normalized
                        if short_specs and size_variation.lower() in str(short_specs).lower():
                            adapter['size'] = size_variations[0]
                            found = True
                            break  # No need to continue once size is normalized
                    if found:
                        break  # Break out of the outer loop as well
                    
                    
            ## Del all empty strings
            field_names = adapter.field_names()
            for field_name in field_names:
                if adapter.get(field_name) == "": del adapter[field_name]
                            
            self.products_collection.update_one({'url': adapter['url']}, {'$set': item}, upsert=True)

            return item
        else:
            # handle other item types or pass through
            return item
    
    def close_spider(self, spider):
        # Fetch CPU keywords from CPU collection
        cpu_keywords = self.dbname["cpu_category"].distinct("keyword")
        cpu_regex = "|".join(cpu_keywords)
        regex_pattern = r"\b(" + cpu_regex + r")\b"
        print(regex_pattern)

        # Aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "category": 'cpu'
                }
            },
            {
                "$addFields": {
                    "cpuKeyword": {
                        "$regexFind": {
                            "input": "$title",
                            "regex": regex_pattern,
                            "options": "i"
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "cpuKeyword": "$cpuKeyword.match"
                }
            },
            {
                "$lookup": {
                    "from": "cpu_category",
                    "localField": "cpuKeyword",
                    "foreignField": "keyword",
                    "as": "cpu"
                }
            },
            {
                "$project": {
                    "cpu": {
                        "$cond": {
                            "if": {"$ne": [{"$size": "$cpu"}, 0]},  # Check if cpu array is not empty
                            "then": {"$arrayElemAt": ["$cpu._id", 0]},  # Take the _id of the first element
                            "else": "$$REMOVE"  # Exclude cpu field if the array is empty
                        }
                    },
                    "imgs": 1,
                    "category": 1,
                    "title": 1,
                    "description": 1,
                    "warranty": 1,
                    "long_specs": 1,
                    "slug": 1,
                    "updatedAt": 1,
                    "url": 1,
                    "availability": 1,
                    "short_specs": 1,
                    "brand": 1,
                }
            },
            {
                "$merge": {
                    "into": self.productsCollectionName,  # Update the documents in the "products" collection with the aggregation result
                    "on": "_id",
                    "whenMatched": "merge"
                }
            }
        ]

        # Perform aggregation
        self.products_collection.aggregate(pipeline)
        
        # Fetch GPU keywords from GPU collection
        gpu_keywords = self.dbname["gpu_category"].distinct("keyword")
        def generate_regex_from_keyword_arrays(keywords, special_keywords):
            # Create regex pattern
            pattern = "(?:(?:"
            
            # Iterate over each keyword
            for index, keyword in enumerate(keywords):
                parts = keyword.split()  # Split keyword by whitespace
                if len(parts) == 1:
                    pattern += f"{parts[0]}"
                else:
                    pattern += "\\s+".join(parts)
                
                # Iterate over specialKeywords
                for word in special_keywords:
                    # Construct a regular expression pattern to check for each word
                    word_reg_exp = re.compile(re.escape(word), re.IGNORECASE)

                    # Test if the keyword contains the current word from the array
                    if not word_reg_exp.search(keyword):
                        # If the keyword doesn't contain the current word, add negative lookahead
                        pattern += "(?!\\s+" + re.escape(word) + ")"  # Ensure the word doesn't follow
                
                # Add '|' if it's not the last keyword
                if index != len(keywords) - 1:
                    pattern += "|"
            
            # Close the regex pattern
            pattern += "))"

            # Construct regex with 'i' flag for case-insensitive matching
            return re.compile(pattern, re.IGNORECASE)
        regex_pattern = generate_regex_from_keyword_arrays(gpu_keywords, ["Super", "Ti", "XT", "GRE" ])

        # Aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "category": 'gpu'
                }
            },
            {
                "$addFields": {
                    "gpuKeyword": {
                        "$regexFind": {
                            "input": "$title",
                            "regex": regex_pattern,
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "gpuKeyword": "$gpuKeyword.match"
                }
            },
            {
                "$lookup": {
                    "from": "gpu_category",
                    "localField": "gpuKeyword",
                    "foreignField": "keyword",
                    "as": "gpu"
                }
            },
            {
                "$project": {
                    "gpu": {
                        "$cond": {
                            "if": {"$ne": [{"$size": "$gpu"}, 0]},  # Check if gpu array is not empty
                            "then": {"$arrayElemAt": ["$gpu._id", 0]},  # Take the _id of the first element
                            "else": "$$REMOVE"  # Exclude gpu field if the array is empty
                        }
                    },
                    "imgs": 1,
                    "category": 1,
                    "title": 1,
                    "description": 1,
                    "warranty": 1,
                    "long_specs": 1,
                    "slug": 1,
                    "updatedAt": 1,
                    "url": 1,
                    "availability": 1,
                    "short_specs": 1,
                    "brand": 1,
                    "manufacturer": 1
                }
            },
            {
                "$merge": {
                    "into": self.productsCollectionName,  # Update the documents in the "products" collection with the aggregation result
                    "on": "_id",
                    "whenMatched": "merge"
                }
            }
        ]

        # Perform aggregation
        self.products_collection.aggregate(pipeline)
        
class GPUCategoryPipeline:
    def __init__(self):
        # Get the database using the method we defined in pymongo_test_insert file
        self.dbname = get_database()
        self.gpu_collection = self.dbname["gpu_category"]
        
    def process_item(self, item, spider):
        if isinstance(item, GPUCategory):
                   
            self.gpu_collection.insert_one(item)
            return item
        else:
            # handle other item types or pass through
            return item      
        
class CPUCategoryPipeline:
    def __init__(self):
        # Get the database using the method we defined in pymongo_test_insert file
        self.dbname = get_database()
        self.cpu_collection = self.dbname["cpu_category"]
        
    def process_item(self, item, spider):
        if isinstance(item, CPUCategory):

            adapter = ItemAdapter(item)
            
            def convert_to_int(s):
                try:
                    cleaned_str = ''.join(filter(str.isdigit, s))
                    return int(cleaned_str)
                except ValueError:
                    print("Unable to convert the string to an integer.")
                    return None
                
            def convert_to_float(s):
                try:
                    cleaned_str = ''.join(filter(lambda x: x.isdigit() or x == '.', s))
                    float_num = float(cleaned_str)
                    if float_num >100: return float_num/1000
                    else: return float_num
                except ValueError:
                    print("Unable to convert the string to a float.")
                    return None    

            ## Strip whitespace
            strip_keys = ['cpu','socket','keyword','iGPU', 'socket']
            for key in strip_keys:
                value = str(adapter.get(key))
                adapter[key] = value.strip()
                
            int_keys = ['core','thread','tdp']
            for key in int_keys:
                value = str(adapter.get(key))
                adapter[key] = convert_to_int(value)
                
            float_keys = ['boost_clock','base_clock']
            for key in float_keys:
                value = str(adapter.get(key))
                adapter[key] = convert_to_float(value)   
             
            self.cpu_collection.update_one({'cpu': adapter['cpu']}, {'$set': item}, upsert=True)

            return item
        else:
            # handle other item types or pass through
            return item             

# class MyPipeline2:
#     def process_item(self, item, spider):
#         if isinstance(item, MyItem2):
#             # process MyItem2 here
#             return item
#         else:
#             # handle other item types or pass through
#             return item

