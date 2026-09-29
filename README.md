# Books to Scrape Assessment

A small Python scraper that collects the first 100 books from [books.toscrape.com](https://books.toscrape.com/) (catalogue pages 1–5) and saves them to `books.csv`. SQL queries in `queries.sql` analyze that data in SQLite.

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the scraper

```bash
python scraper.py
```

This creates (or overwrites) `books.csv` in the project directory with 100 rows plus a header row.

## Run the SQLite queries

Create a database and import the CSV:

```bash
sqlite3 books.db
```

```sql
CREATE TABLE books (
    title TEXT NOT NULL,
    price REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock TEXT NOT NULL,
    url TEXT NOT NULL
);
.mode csv
.import --skip 1 books.csv books
```

Run the queries from `queries.sql` in the same `sqlite3` session, or:

```bash
sqlite3 books.db < queries.sql
```

(Use a one-off DB only for local verification; `books.db` is listed in `.gitignore`.)

## Employer questions

Nothing broke during scraping; the site markup was consistent across catalogue pages 1–5.
The only extra care was joining relative links to full URLs and mapping star-rating classes to integers 1–5.
If the site blocked me after about 50 requests, I would slow down with a delay between each page fetch.
I would reuse one HTTP session, send a clear User-Agent, and retry 429/503 responses with exponential backoff.
I would avoid parallel requests and keep the scraper sequential so it stays polite and easy to reason about.
