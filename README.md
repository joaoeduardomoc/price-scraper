price-scraper
Python price scraper using Playwright & ScraperAPI with proxy rotation and SQL Server integration.

This project automates price tracking from JavaScript-heavy websites using Playwright and ScraperAPI’s proxy rotation. The collected data is stored in a SQL Server database.

Features:

Headless scraping with Playwright (optional, configurable)

Proxy rotation via ScraperAPI (avoids IP blocking and improves reliability)

Stores data in SQL Server using pyodbc

Parses multiple currency formats with regex

Robust error handling and retry logic

Timezone-aware timestamps for accurate data logging

Environment variables support for sensitive info (API keys, DB connection)

Requirements:

Python 3.8 or higher

Libraries: playwright, pyodbc, python-dotenv (optional but recommended)

Setup Instructions:

Install dependencies:

pip install -r requirements.txt
playwright install

Create a .env file in the same folder as main.py with your credentials:

SCRAPERAPI_KEY=your_scraperapi_key_here
CONN_STRING=your_sqlserver_connection_string_here
HEADLESS=true
TIMEZONE=America/Fortaleza

Run the script:

python main.py

Database Setup Example:
To add products to scrape, insert them into your SQL Server database’s produtos table:

INSERT INTO produtos (id_produto, nome_produto, url, seletor_css)
VALUES (1, 'Example Item', 'https://site.com/product', 'span.price');

Notes:

Keep your .env file secret and never upload it to public repositories.

The use of ScraperAPI with proxy rotation helps avoid IP bans and captcha blocks common in web scraping, ensuring better uptime and data accuracy.

Adjust HEADLESS to false if you want to see the browser while scraping (useful for debugging).

Modify TIMEZONE to your local timezone for correct timestamps.
