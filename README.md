# price-scraper
Python price-scraper using Playwright &amp; ScraperAPI with proxy rotation and SQL Server integration
Price Scraper with Python, Playwright & ScraperAPI

This project automates price tracking from JavaScript-heavy websites using Playwright and ScraperAPI with proxy rotation. The collected data is stored in a SQL Server database.

Features:

Headless scraping with Playwright

Proxy rotation using ScraperAPI

Stores data in SQL Server via pyodbc

Handles multiple currencies with regex parsing

Retry logic and robust error handling

Timezone-aware timestamps

Requirements:

Python 3.8 or higher

Libraries: playwright, pyodbc, python-dotenv (optional)

Setup:

Install dependencies:
pip install -r requirements.txt
playwright install

Create a .env file with the following content:
SCRAPERAPI_KEY=your_scraperapi_key
CONN_STRING=your_sqlserver_connection_string
HEADLESS=true
TIMEZONE=America/Fortaleza

Run the script:
python main.py

Example SQL for inserting a product into the 'produtos' table:

INSERT INTO produtos (id_produto, nome_produto, url, seletor_css)
VALUES (1, 'Example Item', 'https://site.com/product', 'span.price');
