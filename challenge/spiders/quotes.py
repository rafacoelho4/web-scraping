# importar bibliotecas
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/page/1/", "https://quotes.toscrape.com/page/2/"]

    def parse(self, response, **kwargs):
        for quote in response.css("div.quote"):
            yield {
                'text:': quote.css("span:first-child::text").get(),
                'author': quote.css("span:nth_child(2) small::text").get(),
                'tags': quote.css("div.tags a::text").getall()
            }