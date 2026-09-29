"""Scrape the first 100 books from books.toscrape.com (pages 1–5)."""

import csv
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = urljoin(BASE_URL, "catalogue/page-{page}.html")
OUTPUT_FILE = "books.csv"
MAX_BOOKS = 100
PAGES = range(1, 6)

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def parse_book(article: BeautifulSoup, page_url: str) -> dict:
    title_link = article.select_one("h3 a")
    if not title_link:
        raise ValueError("Book title link not found")

    title = title_link.get("title") or title_link.get_text(strip=True)
    relative_url = title_link["href"]
    url = urljoin(page_url, relative_url)

    price_text = article.select_one("p.price_color").get_text(strip=True)
    price = float(re.sub(r"[^\d.]", "", price_text))

    rating_el = article.select_one("p.star-rating")
    rating_class = next(
        (c for c in rating_el.get("class", []) if c in RATING_MAP),
        None,
    )
    if rating_class is None:
        raise ValueError(f"Unknown rating classes: {rating_el.get('class')}")
    rating = RATING_MAP[rating_class]

    availability = article.select_one("p.instock.availability")
    in_stock = availability.get_text(strip=True).lower() == "in stock"

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "in_stock": in_stock,
        "url": url,
    }


def scrape_books() -> list[dict]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (compatible; BooksAssessmentScraper/1.0; "
                "+https://books.toscrape.com/)"
            )
        }
    )

    books: list[dict] = []
    for page in PAGES:
        page_url = CATALOGUE_URL.format(page=page)
        response = session.get(page_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for article in soup.select("article.product_pod"):
            books.append(parse_book(article, page_url))
            if len(books) >= MAX_BOOKS:
                return books

    if len(books) != MAX_BOOKS:
        raise RuntimeError(f"Expected {MAX_BOOKS} books, got {len(books)}")

    return books


def write_csv(books: list[dict], path: str) -> None:
    fieldnames = ["title", "price", "rating", "in_stock", "url"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book in books:
            writer.writerow(
                {
                    **book,
                    "in_stock": "true" if book["in_stock"] else "false",
                }
            )


def main() -> None:
    books = scrape_books()
    write_csv(books, OUTPUT_FILE)
    print(f"Wrote {len(books)} books to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
