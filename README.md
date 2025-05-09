# Web Scraping with Scrapy 

A web scrapping technical challenge to retrieve information from https://www.baldor.com/. 
It uses Python and Scrapy to get info on products such as product code, name, description, specifications and its parts. 
The project uses Scrapy Item and Item Pipelines to clean data and uses info on API to enter on a 3-depth search on product pages. 

### Running the code 
Clone this project:

```
git clone https://github.com/rafacoelho4/web-scrapping.git
```

Crawl: 

```
python src/main.py
```

### Output 
The output is a JSON file for every product retrieved, containing product id, name, description, specifications with output power, field voltage, frame and rpm, BOM (Bill Of Materials) with part number, description and quantity and assets with the path to the dowloaded product image and/or manual. 

### Limitations 
A limitation of the current project is its inability of downloading a product's CAD file. The HTTP request to download the file could not be recreated, being necessary the hability to interect with the page: selecting the type of file and clicking on a button. 

### Future work 
Some next steps to continue improving the project include retrieving more product specifications beyond the output power, field voltage, frame and rpm. 
For the output power field, some changes could be made to separate the value of the measurement since we got values in "HP" and "KW". 
A scheme of rotating proxies would be interesting too. 
