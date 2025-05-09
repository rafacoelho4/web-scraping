import scrapy
import json 
import re 

from challenge.items import ProductItem 

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["baldor.com"]
    start_urls = ["https://www.baldor.com/catalog"]

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }

    def parse(self, response, **kwargs):
        PAGE_SIZE = 5
        CATEGORY = 5
        url = f"https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize={PAGE_SIZE}&category={CATEGORY}"
        request = scrapy.Request(url, callback=self.parse_api, headers=self.headers)

        yield request 
            
    def parse_api(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        name = data['category']['longText']

        for product in data['results']['matches']:

            product_code = product['code']
            description = product['description']
            imageId = product['imageId']

            img_url = f"https://www.baldor.com/api/images/{imageId}?bc=white&as=1&h=256&w=256" 
            # da pra fazer sem esses bg, sh, h, w 

            item = {
                "code": product_code,
                "name": name,
                "description": description,
                "image_urls": [img_url]
            }

            product_url = f"https://www.baldor.com/catalog/{product_code}"
            yield response.follow(product_url, callback=self.parse_product_page, meta={'item': item})

    def parse_product_page(self, response, **kwargs):
        item = response.meta['item']
        product = ProductItem()

        # manual 
        infoPacket = response.css("#infoPacket::attr(href)").extract()
        if infoPacket:
            infoPacket = infoPacket[0]
            infoPacket_url = "https://www.baldor.com" + infoPacket
        else: 
            infoPacket_url = ''

        # tabs 
        tabs = response.css(".tab-content h2::text").getall()
        # bom (bill of materials)
        bom = []
        if "Parts" in tabs:
            rows = response.css('.pane[data-tab="parts"] tbody tr')
            for i, row in enumerate(rows):
                p = rows[i].css('td::text').getall()
                part_number = p[0]
                description = p[1]
                quantity = p[2]

                part = {
                    "part_number": part_number,
                    "description": description,
                    "quantity": quantity
                }

                bom.append(part)
        
        # specs 
        specs = {}
        if "Specs" in tabs:
            table_rows = response.css('.pane[data-tab="specs"] .product-overview .col div')
            if(table_rows):
                for i, row in enumerate(table_rows):
                    label = row.css('span:first-child::text').get()
                    if(label == 'Frame' or label == 'Base Speed' or label == 'Field Voltage' or label == 'Output Power'):
                        value = row.css('span:nth-child(2)::text').getall()
                        if(len(value) > 1): single_value = "/".join(value)
                        else: single_value = value[0]

                        if label and single_value:
                            specs[label] = single_value

            if 'Output Power' in specs: specs['hp'] = specs.pop('Output Power')
            if 'Field Voltage' in specs: specs['voltage'] = specs.pop('Field Voltage')
            if 'Base Speed' in specs: specs['rpm'] = specs.pop('Base Speed')
            if 'Frame' in specs: specs['frame'] = specs.pop('Frame')

        product['product_id'] = item['code']
        product['name'] = item['name']
        product['description'] = item['description']
        product['specs'] = specs
        product['bom'] = bom
        product['image_urls'] = item['image_urls']
        product['manual'] = [infoPacket_url]

        yield product

# product code: 
# response.css("div.matches .overview h3 a::text").getall()
# go to https://www.baldor.com/catalog/{product.code} for details 

# inside product page: 
# code:         response.css(".page-title h1::text").get() 
# description:  response.css(".product-description::text").get()
# image:        response.css(".product-image").getall() 
# infoPacket:   response.css("#infoPacket").getall() 

# images: https://www.baldor.com/api/images/201?bc=white&as=1&h=256&w=256