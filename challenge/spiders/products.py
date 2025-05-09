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

        categories_url = "https://www.baldor.com/api/products?include=category" 
        request = scrapy.Request(categories_url, callback=self.parse_categories, headers=self.headers)

        yield request
            
    def parse_categories(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        for category in data['category']['children']:
            id = category['id'] 
            page_size = category['count'] 

            if(page_size == 0 or page_size > 500): continue 

            # LIMITING THE SCRAPPING 
            page_size = 5
            
            url = f"https://www.baldor.com/api/products?include=results&language=en-US&include=filters&include=category&pageSize={page_size}&category={id}"
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

        # Manual  
        infoPacket = response.css("#infoPacket::attr(href)").extract()
        if infoPacket:
            infoPacket = infoPacket[0]
            infoPacket_url = ["https://www.baldor.com" + infoPacket]
        else: 
            infoPacket_url = []

        # Products's information is separated in different tabs 
        tabs = response.css(".tab-content h2::text").getall()
        # BOM (Bill Of Materials)
        bom = []
        if "Parts" in tabs:
            # Lists all the parts of the product 
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
        
        # Specifications  
        specs = {}
        specs_fields = ['Frame', 'Base Speed', 'Field Voltage', 'Output Power']
        if "Specs" in tabs:
            # Lists all the specifications of the product, with the first child being the label and the second child being the value 
            table_rows = response.css('.pane[data-tab="specs"] .product-overview .col div')
            if(table_rows):
                for i, row in enumerate(table_rows):
                    label = row.css('span:first-child::text').get()
                    if(label in specs_fields):
                        value = row.css('span:nth-child(2)::text').getall()
                        if(len(value) > 1): single_value = "/".join(value) # if there is more than one value, join with "/"
                        else: single_value = value[0] # if there is only one value, use it 

                        if label and single_value:
                            specs[label] = single_value

            # Changing the name of the keys  
            if 'Output Power' in specs: specs['hp'] = specs.pop('Output Power')
            if 'Field Voltage' in specs: specs['voltage'] = specs.pop('Field Voltage')
            if 'Base Speed' in specs: specs['rpm'] = specs.pop('Base Speed')
            if 'Frame' in specs: specs['frame'] = specs.pop('Frame')

        # Filling out product fields 
        product['product_id'] = item['code']
        product['name'] = item['name']
        product['description'] = item['description']
        product['specs'] = specs
        product['bom'] = bom
        product['image_urls'] = item['image_urls']
        product['manual'] = infoPacket_url

        yield product

# inside product page: 
# code:         response.css(".page-title h1::text").get() 
# description:  response.css(".product-description::text").get()
# image:        response.css(".product-image").getall() 
# infoPacket:   response.css("#infoPacket").getall() 

# images: https://www.baldor.com/api/images/201?bc=white&as=1&h=256&w=256