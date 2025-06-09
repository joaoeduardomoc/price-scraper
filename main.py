import os
import re
import pyodbc
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env

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
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

def get_produtos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id_produto, nome_produto, url, seletor_css FROM produtos;")
    return cursor.fetchall()

def format_price(texto):
    if not texto:
        return None
    texto = texto.strip()
    texto_limpo = re.sub(r"[^0-9\.,]", "", texto)
    if texto_limpo.count(",") > 0 and texto_limpo.count(".") > 0:
        texto_limpo = texto_limpo.replace(".", "").replace(",", ".")
    elif texto_limpo.count(",") > 0:
        texto_limpo = texto_limpo.replace(",", ".")
    try:
        return float(texto_limpo)
    except:
        return None

def scrape_preco():
    conn = connect_db()
    produtos = get_produtos(conn)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        for id_produto, nome, url, seletor_css in produtos:
            page = context.new_page()
            target_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={url}"
            try:
                page.goto(target_url, timeout=60000)
                page.wait_for_load_state('networkidle', timeout=30000)

                element = page.wait_for_selector(seletor_css, timeout=30000)
                texto_preco = element.inner_text()
                preco = format_price(texto_preco)

                if preco is not None:
                    cursor = conn.cursor()
                    query_insert = (
                        "INSERT INTO precos (id_produto, preco, data_coleta) "
                        "VALUES (?, ?, ?);"
                    )
                    data_coleta = datetime.now()
                    cursor.execute(query_insert, id_produto, preco, data_coleta)
                    conn.commit()
                    print(f"[{data_coleta}] Produto ID {id_produto}: R$ {preco:.2f}")
                else:
                    print(f"Falha ao converter preço para o produto ID {id_produto} (texto: '{texto_preco}')")

            except PlaywrightTimeoutError:
                print(f"Timeout: não foi possível encontrar seletor '{seletor_css}' para ID {id_produto} na URL {url}")
            except Exception as e:
                print(f"Erro ao coletar preço para ID {id_produto} na URL {url}: {e}")
            finally:
                page.close()

        browser.close()
    conn.close()

if __name__ == "__main__":
    scrape_preco()
