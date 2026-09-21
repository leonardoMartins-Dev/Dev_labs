import scrapy 
from scrapy.crawler import CrawlerProcess
import json

class QoutesSpider(scrapy.Spider):
    name = "qoutes"
    start_urls = ["http://quotes.toscrape.com/"]

    #lista para acumular citacoes de toda pagina
    quotes_list = []

    def parse(self, response):
        #extrair citacoes da pagina
        for quote in response.css("div.quote"):
            qoute_data={
                "text" : quote.css("span.text::text").get().strip(),
                "autor" : quote.css("small.author::text").get(),
                "tags" : quote.css("div.tags a.tag::text").getall(),
            }
            self.quotes_list.append(qoute_data)

        #CASO HAJA PROXIMA PAGINA
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            #SEGUE PARA A PROXIMA
            yield response.follow(next_page, self.parse)
        else:
            #QUANDO NAO A MAIS PAGINAS
            with open("qoutes.json", "w", encoding="utf-8") as f:
                json.dump(self.quotes_list, f, ensure_ascii=False, indent=4)

#EXECUTA
process = CrawlerProcess()
process.crawl(QoutesSpider)
process.start()