# Quotes Spider

Este projeto é um spider simples feito com **Scrapy** para coletar citações do site [Quotes to Scrape](http://quotes.toscrape.com/). O spider navega por todas as páginas do site, extrai o texto da citação, o autor e as tags associadas, e salva todos os dados em um arquivo JSON.

Este README foi escrito também como material de estudo: além do "como usar", ele explica **por que** cada parte do código existe e documenta os erros mais comuns que aparecem ao construir um spider assim do zero.

## Estrutura do Projeto

```
scrapy-quotes/
├── qoutes.py
└── qoutes.json
```

> Nota: os nomes de arquivo usados aqui são `qoutes.py`/`qoutes.json` (com essa grafia), mas fique à vontade para renomear para `quotes.py`/`quotes.json` — só lembre de manter tudo consistente (ver seção "Erros comuns" abaixo).

## Como Funciona o Spider

```python
import scrapy 
from scrapy.crawler import CrawlerProcess
import json

class QoutesSpider(scrapy.Spider):
    name = "qoutes"
    start_urls = ["http://quotes.toscrape.com/"]

    # lista para acumular citações de todas as páginas
    quotes_list = []

    def parse(self, response):
        # extrair citações da página atual
        for quote in response.css("div.quote"):
            quote_data = {
                "text": quote.css("span.text::text").get().strip(),
                "autor": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }
            self.quotes_list.append(quote_data)

        # verifica se há próxima página
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            # segue para a próxima página, chamando parse() de novo
            yield response.follow(next_page, self.parse)
        else:
            # quando não há mais páginas, salva tudo em JSON
            with open("qoutes.json", "w", encoding="utf-8") as f:
                json.dump(self.quotes_list, f, ensure_ascii=False, indent=4)

# executa o spider fora de um projeto Scrapy completo
process = CrawlerProcess()
process.crawl(QoutesSpider)
process.start()
```

### Conceitos-chave do Scrapy usados aqui

| Conceito | O que é | Onde aparece |
|---|---|---|
| `scrapy.Spider` | Classe base que todo spider herda. Define o comportamento de rastreamento. | `class QoutesSpider(scrapy.Spider)` |
| `name` | Identificador único do spider, usado por `scrapy crawl <name>`. | `name = "qoutes"` |
| `start_urls` | Lista de URLs por onde o Scrapy começa a rastrear. **Atenção ao "s" no final** (ver erros comuns). | `start_urls = [...]` |
| `parse(self, response)` | Método callback padrão, chamado automaticamente para cada resposta HTTP recebida. | `def parse(self, response):` |
| Seletores CSS (`response.css(...)`) | Forma de localizar elementos HTML usando sintaxe CSS, similar ao `document.querySelectorAll` do JS. | `response.css("div.quote")` |
| `::text` | Pseudo-seletor do Scrapy/Parsel para pegar o texto de dentro de uma tag. | `"span.text::text"` |
| `.get()` vs `.getall()` | `.get()` retorna o primeiro resultado (ou `None`); `.getall()` retorna uma lista com todos os resultados. | autor usa `.get()`, tags usa `.getall()` |
| `yield response.follow(...)` | Gera uma nova requisição para o Scrapy processar, permitindo paginação recursiva sem loops manuais. | bloco de próxima página |
| `CrawlerProcess` | Permite rodar um spider como script Python puro (`python qoutes.py`), sem precisar de um projeto Scrapy completo (`scrapy startproject`). | final do arquivo |

## Como Usar

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd nome-da-pasta
```

### 2. Crie e ative o ambiente virtual

É recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
python3 -m venv .venv
```

Ative o ambiente:

- **macOS/Linux**
  ```bash
  source .venv/bin/activate
  ```
- **Windows**
  ```bash
  .venv\Scripts\activate
  ```

### 3. Instale as dependências

```bash
pip install scrapy
```

> Dica: se você tiver mais de uma versão do Python instalada (comum no macOS, entre a versão do sistema e a do Homebrew/pyenv), confirme que o `pip` que você está usando corresponde ao interpretador Python selecionado no seu editor. Um sintoma comum desse desalinhamento é o editor sublinhar `import scrapy` como erro mesmo depois de instalado — nesse caso, no VS Code, use `Cmd+Shift+P` → **Python: Select Interpreter** e escolha o ambiente onde o Scrapy foi de fato instalado.

### 4. Execute o spider

```bash
python qoutes.py                # roda o script diretamente, usando o CrawlerProcess no final do arquivo
scrapy runspider qoutes.py      # alternativa: roda um spider avulso, sem projeto Scrapy
scrapy crawl qoutes             # só funciona dentro de um projeto Scrapy criado com "scrapy startproject"
```

O spider vai percorrer todas as páginas do site (10 páginas, no caso do quotes.toscrape.com) e, ao final, salvar tudo em `qoutes.json`.

## Resultado Esperado

```json
[
    {
        "text": "Citação 1",
        "autor": "Autor 1",
        "tags": ["tag1", "tag2"]
    },
    {
        "text": "Citação 2",
        "autor": "Autor 2",
        "tags": ["tag3", "tag4"]
    }
]
```

## Erros Comuns (e por que acontecem)

Esta seção documenta os erros que realmente apareceram no desenvolvimento deste spider — vale a pena entender cada um, porque são erros clássicos de quem está aprendendo Scrapy.

### 1. `SyntaxError: 'yield' outside function`
Acontece quando o `yield response.follow(...)` fica **fora** da indentação do método `parse`, geralmente por um erro de indentação. Em Python, `yield` só é válido dentro do corpo de uma função/método.

### 2. `AttributeError: 'start_urls' not found or empty (did you miss an 's'?)`
O Scrapy espera exatamente o atributo `start_urls` (plural). Escrever `start_url` (singular) faz o Scrapy não encontrar nenhuma URL inicial — e a própria mensagem de erro já avisa isso, de tão comum que é o engano.

### 3. Resposta `404` na requisição inicial
Se a URL em `start_urls` estiver com erro de digitação (ex.: `qoutes.toscrape.com` em vez de `quotes.toscrape.com`), o servidor retorna 404 e o spider fecha sem coletar nada, sem lançar exceção — o sintoma é só "não salvou nada".

### 4. Seletor CSS não bate com o HTML real (`div.qoute` vs `div.quote`)
Se o seletor CSS usado no `.css(...)` não corresponde exatamente à classe HTML da página, o `for` simplesmente não itera nenhuma vez — sem erro, sem aviso. O resultado final é um JSON vazio (`[]`). Esse tipo de bug é silencioso e só é percebido comparando o HTML real da página (inspecionando no navegador) com o seletor usado no código.

### 5. `AttributeError: 'QoutesSpider' object has no attribute 'quotes_list'`
Esse é um erro de **nome inconsistente**: a lista foi declarada como atributo de classe com um nome (ex.: `qoutes_list`) mas usada com `self.` em outro nome (ex.: `self.quotes_list`). Como são identificadores diferentes para o Python, o segundo simplesmente não existe. A lição aqui: escolha um nome de variável e use-o **exatamente igual** em todos os lugares — declaração e uso.

### Resumo da lição principal
A maioria desses erros não trava o programa com um erro óbvio logo de cara — muitos falham silenciosamente (seletor errado = zero itens) ou só aparecem depois de um tempo de execução (erro no fim da última página). Por isso, ao depurar um spider Scrapy, vale sempre:
1. Ler o **traceback completo**, não só a última linha.
2. Conferir a contagem de itens nas estatísticas finais (`scrapy stats`) — "0 items" é um sinal de alerta mesmo sem erro explícito.
3. Inspecionar o HTML real da página (Ferramentas de Desenvolvedor do navegador) antes de escrever os seletores CSS.

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests com sugestões de melhorias!

## Licença

Este projeto está licenciado sob a MIT License.