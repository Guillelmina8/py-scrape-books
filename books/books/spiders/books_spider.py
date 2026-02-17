from typing import Iterable, Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"

    custom_settings = {
        "CONCURRENT_REQUESTS": 32,
        "DOWNLOAD_DELAY": 0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 32,
        "AUTOTHROTTLE_ENABLED'": False,
    }

    start_urls = [
        (f"https://books.toscrape.com/catalogue/page-{i}"
         f".html") for i in range(1, 51)
    ]

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Iterable[scrapy.Request]:
        books = response.css("article.product_pod")

        for book in books:
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, callback=self.parse_book_details)

    def parse_book_details(
            self,
            response: Response,
            **kwargs
    ) -> Iterable[dict[str, Any]]:
        main = response.css(".product_main")

        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        raw_rating = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]

        yield {
            "title": main.css("h1::text").get(),
            "price":
                float(main.css(".price_color::text").re_first(r"\d+\.\d+")),
            "amount_in_stock":
                int(response.css(".availability::text").re_first(r"\d+")),
            "rating": rating_map.get(raw_rating, 0),
            "category":
                response.css(".breadcrumb li:nth-child(3) a::text").get(),
            "description":
                response.css("#product_description + p::text").get(),
            "upc": response.css("th:contains('UPC') + td::text").get(),
        }
