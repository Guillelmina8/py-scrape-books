from typing import Iterable, Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"

    custom_settings = {
        "CONCURRENT_REQUESTS": 16,
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
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
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_text = rating_class.split()[-1] if rating_class else "Zero"

        price_raw = main.css(".price_color::text").re_first(r"\d+\.\d+")
        stock_raw = response.css(".availability::text").re_first(r"\d+")

        yield {
            "title": main.css("h1::text").get(),
            "price": float(price_raw) if price_raw else 0.0,
            "amount_in_stock": int(stock_raw) if stock_raw else 0,
            "rating": rating_map.get(rating_text, 0),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css(
                "#product_description + p::text").get(),
            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::"
                "td[1]/text()").get(),
        }
