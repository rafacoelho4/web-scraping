# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import re
import json 

from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline

class customImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        # return request.url.split('/')[-1]
        return f"{item['code']}.jpg"
    
class customFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['code']}.pdf"
    
class ProductPipeline: 
    def process_item(self, item, spider): 
        
        adapter = ItemAdapter(item) 

        # bom description adapter  
        # remove excess whitespace 

        # bom quantity adapter (from '2.000 EA' to '2') 
        bom_list = adapter.get('bom') 
        if bom_list: 
            for index, material in enumerate(bom_list): 
                for key, value in material.items(): 
                    if key == 'quantity' and value: 
                        x = value.split('.') 
                        adapter['bom'][index]['quantity'] = x[0] 
                    

        # specs adapater (from '2hp' to '2' and '1750rpm' to '1750') 
        specs = adapter.get('specs')
        if specs: 
            for key, value in specs.items():
                if(key == 'voltage'): continue 
                numbers = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", value)
                # numbers = re.findall(r'\d+', value)
                adapter['specs'][key] = numbers[0] 

        return item

# class JsonWriterPipeline:
#     def open_spider(self, spider):
#         self.file = open("items.json", "w")

#     def close_spider(self, spider):
#         self.file.close()

#     def process_item(self, item, spider):
#         line = json.dumps(ItemAdapter(item).asdict()) + "\n"
#         self.file.write(line)
#         return item