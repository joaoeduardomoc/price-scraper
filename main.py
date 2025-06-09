import os
import re
import pyodbc
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

CONN_STRING = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    f"Trusted_Connection={os.getenv('DB_TRUSTED_CONNECTION')};"
)

def connect_db():
    try:
        conn = pyodbc.connect(CONN_STRING)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def get_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, url, css_selector FROM products;")
    return cursor.fetchall()

def format_price(text):
    if not text:
        return None
    text = text.strip()
    clean_text = re.sub(r"[^0-9\.,]", "", text)
    if clean_text.count(",") > 0 and clean_text.count(".") > 0:
        clean_text = clean_text.replace(".", "").replace(",", ".")
    elif clean_text.count(",") > 0:
        clean_text = clean_text.replace(",", ".")
    try:
        return float(clean_text)
    except:
        return None

def scrape_price():
    conn = connect_db()
    products = get_products(conn)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        for product_id, name, url, css_selector in products:
            page = context.new_page()
            target_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={url}"
            try:
                page.goto(target_url, timeout=60000)
                page.wait_for_load_state('networkidle', timeout=30000)

                element = page.wait_for_selector(css_selector, timeout=30000)
                price_text = element.inner_text()
                price = format_price(price_text)

                if price is not None:
                    cursor = conn.cursor()
                    insert_query = (
                        "INSERT INTO prices (product_id, price, scrape_date) "
                        "VALUES (?, ?, ?);"
                    )
                    scrape_date = datetime.now()
                    cursor.execute(insert_query, product_id, price, scrape_date)
                    conn.commit()
                    print(f"[{scrape_date}] Product ID {product_id}: $ {price:.2f}")
                else:
                    print(f"Failed to convert price for product ID {product_id} (text: '{price_text}')")

            except PlaywrightTimeoutError:
                print(f"Timeout: could not find selector '{css_selector}' for product ID {product_id} at URL {url}")
            except Exception as e:
                print(f"Error scraping price for product ID {product_id} at URL {url}: {e}")
            finally:
                page.close()

        browser.close()
    conn.close()

if __name__ == "__main__":
    scrape_price()
