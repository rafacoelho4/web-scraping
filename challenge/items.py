# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):

    product_id = scrapy.Field() 
    name = scrapy.Field()
    description = scrapy.Field() 

    specs = scrapy.Field()
    bom = scrapy.Field()

    assets = scrapy.Field()
    image_urls = scrapy.Field()
    manual = scrapy.Field()

    downloaded_files = scrapy.Field()  
    downloaded_images = scrapy.Field() 
    
    pass
