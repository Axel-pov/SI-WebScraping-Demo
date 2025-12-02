# instagram_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# ---------------- CONFIG ----------------
INSTAGRAM_USERNAME = " "  # usuario objetivo
SCROLL_PAUSE = 2  # segundos de espera tras cada scroll
LIMIT_USERS = 50  # máximo de usuarios a extraer por demo

# ---------------- SETUP CHROME ----------------
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
# Descomentar si quieres ocultar navegador:
# options.add_argument("--headless=new")

chrome_path = "path to chrome.exe" 
chromedriver_path = "path to chromedrive.exe" # Indica el ejecutable de chrome explícitamente (útil si no está en PATH) 
if os.path.exists(chrome_path): 
    options.binary_location = chrome_path 
    service = Service(chromedriver_path) 
    driver = webdriver.Chrome(service=service, options=options)

driver.maximize_window()

# ---------------- FUNCIONES ----------------
def scroll_modal(driver, modal, max_scrolls=100):
    """Scroll dentro de un modal hasta cargar usuarios."""
    last_height = driver.execute_script("return arguments[0].scrollHeight", modal)
    scrolls = 0
    while scrolls < max_scrolls:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return arguments[0].scrollHeight", modal)
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1

def extract_usernames(driver, modal):
    """Extrae los usernames visibles en el modal."""
    elements = modal.find_elements(By.CSS_SELECTOR, "a.notranslate")
    return [el.get_attribute("innerText").strip() for el in elements if el.get_attribute("innerText").strip()]

def scrape_followers_or_following(username, mode="followers", limit=50, scroll_pause=2):
    """
    Extrae seguidores o seguidos de un usuario de Instagram.

    :param username: nombre del usuario de Instagram
    :param mode: "followers" o "following"
    :param limit: cantidad máxima de usuarios a extraer
    :param scroll_pause: segundos de espera tras cada scroll
    :return: lista de usernames
    """

    # Ir al perfil
    url = f"https://www.instagram.com/{username}/"
    driver.get(url)
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.TAG_NAME, "header"))
    )
    time.sleep(2)

    # Click en Followers / Following
    link_css = f"a[href='/{username}/{mode}/']"
    link_elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, link_css))
    )
    link_elem.click()
    time.sleep(2)

    # Esperar al modal completo
    modal = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
    )

    # Scroll y extracción de usuarios
    usernames = set()
    last_count = -1

    while len(usernames) < limit:
        # Extraer todos los <a class="notranslate"> visibles
        elements = modal.find_elements(By.CSS_SELECTOR, "a.notranslate")
        for el in elements:
            text = el.get_attribute("innerText").strip()
            if text:
                usernames.add(text)

        # Si no se cargan más usuarios, salir
        if len(usernames) == last_count:
            break
        last_count = len(usernames)

        # Scroll dentro del modal
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        time.sleep(scroll_pause)

    return list(usernames)[:limit]


if __name__ == "__main__":
    # Asegúrate de estar logueado manualmente
    driver.get("https://www.instagram.com/")
    print("Haz login manualmente si no estás logueado...")
    time.sleep(20)  # Ajusta según necesites

    followers = scrape_followers_or_following("test_scraping_si", mode="followers", limit=50)
    print("Followers:", followers)

    following = scrape_followers_or_following("test_scraping_si", mode="following", limit=50)
    print("Following:", following)

    driver.quit()



