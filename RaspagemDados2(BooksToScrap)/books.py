import scrapy
from scrapy.crawler import CrawlerProcess
import json
from pathlib import Path

# Salva o json na msm pasta desse arquivo
ARQUIVO_JSON = Path(__file__).parent / "books.json"


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    # lista para acumular os livros de toda pagina
    books_list = []

    def parse(self, response):
        for book in response.css("article.product_pod"):
            book_data = {
                "image": book.css("img.thumbnail::attr(src)").get(),
                "stars": book.css('p.star-rating::attr(class)').re_first(
                    r'star-rating (\w+)'
                ),
                "title": book.css("h3 a::attr(title)").get(),
                "price": float(
                    book.css('p.price_color::text').get().replace('£', '')
                ),
                'availability': book.css(
                    'p.instock.availability::text'
                ).re_first(r'(\S+\s\S+)'),
            }
            # envia cada livro pra lista(SEM FILTRO)
            # self.books_list.append(book_data)

            # Ou pode filtrar tbm:
            barato = book_data['price'] <= 50
            bem_avaliado = book_data['stars'] in ['Four', 'Five']
            if barato and bem_avaliado:
                self.books_list.append(book_data)

        # existe mais paginas, entao:

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            # Segue para proxima caso exista
            yield response.follow(next_page, self.parse)
        else:
            # cria o arquivo JSON caso n exista mais paginas
            with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
                json.dump(self.books_list, f, ensure_ascii=False, indent=4)


# EXECUTA
process = CrawlerProcess()
process.crawl(BooksSpider)
process.start()
