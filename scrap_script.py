from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import os

def scrape_quotes_js(limit=5, headless=False, timeout=10):
    url = "https://quotes.toscrape.com/js/"

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(url)
        time.sleep(0.5)  # carga inicial muy breve

        # 1) demostrar que el HTML inicial NO contiene las citas
        initial_html = driver.page_source
        contains_quote_markup = "class=\"quote\"" in initial_html or "<div class=\"quote\"" in initial_html
        print("¿HTML inicial contiene .quote? ->", contains_quote_markup)

        # 2) esperar a que las citas sean inyectadas por JS
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.quote")))

        # 3) ahora extraer las primeras `limit` quotes
        quotes = driver.find_elements(By.CSS_SELECTOR, "div.quote")[:limit]
        results = []
        for q in quotes:
            texto = q.find_element(By.CSS_SELECTOR, "span.text").text.strip()
            autor = q.find_element(By.CSS_SELECTOR, "small.author").text.strip()
            tags_elems = q.find_elements(By.CSS_SELECTOR, "div.tags a.tag")
            tags = [t.text.strip() for t in tags_elems]
            results.append({"text": texto, "author": autor, "tags": tags})

        print(f"\nExtraídas {len(results)} citas (limit={limit}):")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['text']} — {r['author']} [{', '.join(r['tags'])}]")

        return results

    finally:
        driver.quit()

if __name__ == "__main__":

    """
    PRIMER CASO DE USO, USAREMOS BEAUTIFULSOUP
    PARA ACCEDER AL HTML ESTÁTICO DE LA WEB
    """

    # Fetch the page
    url='https://miguelitosruiz.com/blog-miguelitos/novedades/asi-es-la-receta-tradicional-del-bizcocho-casero-de-toda-la-vida'
    response = requests.get(url)

    # Parse the HTML content
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1') #find the first h1 tag
    print(title.text)

    """
    SEGUNDO CASO DE USO, USAREMOS SELENIUM PARA ACCEDER
    A CIERTAS CITAS DE UNA WEB CARGADAS DINÁMICAMENTE
    """
    scrape_quotes_js(limit=5, headless=False, timeout=12)


