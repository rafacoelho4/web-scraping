from scrapy.cmdline import execute
import os, sys

def main():
    print("Hello World!")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(['scrapy','crawl','products','-o','product.json'])

if __name__ == "__main__":
    main() 