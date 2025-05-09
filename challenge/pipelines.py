# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import re
import json 
import os 

from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline

class customImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        product_id = item['product_id']
        return f'assets/{product_id}/img.jpg'

    def item_completed(self, results, item, info):
        item['downloaded_images'] = {}
        for success, image_info in results:
            if success:
                item['downloaded_images']['image'] = image_info['path']
        return item

class customFilePipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        product_id = item['product_id']
        return f'assets/{product_id}/manual.pdf'

    def item_completed(self, results, item, info):
        item['downloaded_files'] = {}
        for success, file_info in results:
            if success:
                item['downloaded_files']['manual'] = file_info['path']
        return item

def clean_string_with_slashes(input_string):
    # Replace multiple spaces (but protect slashes)
    cleaned_string = re.sub(r'[ ]+/', '/', input_string)  # Remove spaces before /
    cleaned_string = re.sub(r'/[ ]+', '/', cleaned_string)  # Remove spaces after /
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string.strip())  # Normalize remaining spaces
    return cleaned_string

class ProductPipeline: 
    def process_item(self, item, spider): 
        adapter = ItemAdapter(item) 

        # bom quantity and description adapter (from '2.000 EA' to '2') 
        bom_list = adapter.get('bom') 
        if bom_list: 
            for index, material in enumerate(bom_list): 
                for key, value in material.items(): 
                    if key == 'quantity' and value: 
                        x = value.split('.') 
                        adapter['bom'][index]['quantity'] = x[0] 
                    if key == 'description' and value:
                        # remove excess whitespace 
                        cleaned = clean_string_with_slashes(value)
                        adapter['bom'][index]['description'] = cleaned
                    

        # specs adapater (from '2hp' to '2' and '1750rpm' to '1750') 
        specs = adapter.get('specs')
        if specs: 
            for key, value in specs.items():
                # if(key == 'voltage' or value == ''): continue 
                if(value == ''): continue 
                cleaned = re.sub(r'[^a-zA-Z0-9/]', '', value)
                # numbers = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", value)
                # numbers = re.findall(r'\d+', value)
                # adapter['specs'][key] = numbers[0] 
                adapter['specs'][key] = cleaned

        # assets 
        assets = {}
        
        # Add image only if downloaded
        if 'downloaded_images' in item and 'image' in item['downloaded_images']:
            assets['image'] = item['downloaded_images']['image']
        
        # Add manual only if downloaded
        if 'downloaded_files' in item and 'manual' in item['downloaded_files']:
            assets['manual'] = item['downloaded_files']['manual']
        
        # Only add assets if we have at least one file
        if assets:
            item['assets'] = assets
        
         # Clean up temporary and download fields
        fields_to_remove = [
            'image_urls', 'images',
            'manual', 'files',
            'downloaded_files', 'downloaded_images'
        ]
        for field in fields_to_remove:
            item.pop(field, None)

        return item
    
class JsonWriterPipeline:
    def __init__(self, output_dir='products'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get('PRODUCTS_OUTPUT_DIR', 'products')
        )

    def process_item(self, item, spider):
        product_id = item.get('product_id', 'unknown')
        safe_filename = self.sanitize_filename(product_id) + '.json'
        filepath = os.path.join(self.output_dir, safe_filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False, indent=2)
        
        return item

    def sanitize_filename(self, filename):
        """Convert string to safe filename"""
        # Replace invalid characters with underscore
        filename = str(filename).strip()
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        filename = re.sub(r'\s+', '_', filename)
        return filename