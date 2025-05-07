import scrapy
import json 

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
        PAGE_SIZE = 20
        url = f"https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize={PAGE_SIZE}&category=4"
        request = scrapy.Request(url, callback=self.parse_api, headers=self.headers)

        yield request 
            
    def parse_api(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        for product in data['results']['matches']:

            product_code = product['code']
            description = product['description']
            imageId = product['imageId']

            rpm = '' 
            voltage = '' 
            frame = '' 
            output = '' 
            img_url = f"https://www.baldor.com/api/images/{imageId}?bc=white&as=1&h=256&w=256" 
            # da pra fazer sem esses bg, sh, h, w 

            for attr in product['attributes']:
                if attr['name'] == 'base_speed':
                    rpm = attr['values'][0]['value']
                elif attr['name'] == 'field_voltage':
                    if len(attr['values']) == 1:
                        voltage = attr['values'][0]['value']
                    else:
                        for volts in attr['values']:
                            voltage += volts['value'] + '/'
                        if(voltage[-1] == '/'):
                            voltage = voltage[:-1]
                elif attr['name'] == 'frame':
                    frame = attr['values'][0]['value']
                elif attr['name'] == 'output':
                    output = attr['values'][0]['value']

            item = {
                "code": product_code,
                "description": description,
                "specs": {
                    "hp": output,
                    "voltage": voltage,
                    "rpm": rpm,
                    "frame": frame
                },
                "image_urls": [img_url]
            }

            product_url = f"https://www.baldor.com/catalog/{product_code}"
            yield response.follow(product_url, callback=self.parse_product, meta={'item': item})

    def parse_product(self, response, **kwargs):
        item = response.meta['item']
        product = ProductItem()

        # manual 
        infoPacket = response.css("#infoPacket::attr(href)").extract()[0]
        infoPacket_url = "https://www.baldor.com" + infoPacket

        # bom (bill of materials)
        tabs = response.css(".tab-content h2::text").getall()
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

        product['code'] = item['code']
        product['description'] = item['description']
        product['specs'] = item['specs']
        product['bom'] = bom
        assets = {
            "image": item['image_urls'],
            "manual": [infoPacket_url]
        }
        # product['assets'] = assets
        # product['image'] = item['image_urls']
        # product['manual'] = [infoPacket_url]

        yield product


# product code: 
# response.css("div.matches .overview h3 a::text").getall()
# go to https://www.baldor.com/catalog/{product.code} for details 

# inside product page: 
# code:         response.css(".page-title h1::text").get() 
# description:  response.css(".product-description::text").get()
# image:        response.css(".product-image").getall() 
# infoPacket:   response.css("#infoPacket").getall() 

# tabs:
# response.css(".tab-content h2::text").getall()
# ['Specs', 'Drawings', 'Nameplate', 'Performance', 'Parts']

# BOM (bill of materials): 
# part number: response.css(".tab-content:last-child .key::text").getall() 
# quantity: response.css(".tab-content:last-child .right::text").getall() 

# images: https://www.baldor.com/api/images/201?bc=white&as=1&h=256&w=256