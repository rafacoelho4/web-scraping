# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

def serialize_rpm(value):
    value['rpm'] = value['rpm'][:-3]
    return value

class ProductItem(scrapy.Item):
    # define the fields for your item here like:

    name = scrapy.Field()
    code = scrapy.Field() 
    description = scrapy.Field() 

    specs = scrapy.Field(serializer=serialize_rpm)
    bom = scrapy.Field()

    image = scrapy.Field()
    manual = scrapy.Field()
    
    pass
