import scrapy

class MotorsSpider(scrapy.Spider):
    name = "motors"
    allowed_domains = ["baldor.com"]
    start_urls = ["https://www.baldor.com/brands/baldor-reliance/products/ac-motors"]

    def parse(self, response, **kwargs):
        products = response.css("ul.list-sub-product-item li")
        print("prod:", products, len(products))
        
        for product in products:
            product_name = product.css("div::text").get()
            product_link = product.css("a").attrib["href"]
            # product_link = product_link if product_link.startswith("http") else " "
            
            yield {
                "name": product_name,
                "link": product_link 
            }

# HVAC
# works just the same as the original ac motors scheme with products being ul li and getting the div::text 