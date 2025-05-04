from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuração do driver
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # descomente para rodar em background
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 15)

def scroll_until_loaded(item_selector, delay=2, max_idle_rounds=3):
    """
    Rola até o fim repetidamente para carregar mais itens.
    Interrompe quando, após uma rolagem, o número de itens não aumentar
    por `max_idle_rounds` vezes consecutivas.
    """
    idle_rounds = 0
    last_count = 0

    while idle_rounds < max_idle_rounds:
        items = driver.find_elements(By.CSS_SELECTOR, item_selector)
        current_count = len(items)

        # Se aumentou, reset idle rounds
        if current_count > last_count:
            idle_rounds = 0
            last_count = current_count
        else:
            idle_rounds += 1

        # Rola até o fim
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(delay)

    # Retorna a lista final de elementos
    return driver.find_elements(By.CSS_SELECTOR, item_selector)

def get_fresh_item(idx, selector, retries=3, delay=1):
    """
    Busca novamente o item no índice idx em caso de StaleElementReferenceException ou IndexError.
    """
    for _ in range(retries):
        try:
            items = driver.find_elements(By.CSS_SELECTOR, selector)
            return items[idx]
        except (StaleElementReferenceException, IndexError):
            time.sleep(delay)
    # Última tentativa
    items = driver.find_elements(By.CSS_SELECTOR, selector)
    return items[idx]

try:
    driver.get("https://www.townofhortonia.org/blog")
    # Aguarda os itens iniciais aparecerem
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))

    # Carrega todos os itens via scroll
    scroll_until_loaded(".item-link-wrapper")

    idx = 0
    while True:
        # Recarrega lista de itens e verifica se há algo para processar
        items = driver.find_elements(By.CSS_SELECTOR, ".item-link-wrapper")
        if idx >= len(items):
            break  # fim da lista

        try:
            # Obtém o item seguro
            item = get_fresh_item(idx, ".item-link-wrapper")
            a_tag = item.find_element(By.TAG_NAME, "a")
            title = item.find_element(By.TAG_NAME, "h2").text
            main_text = item.find_element(By.CSS_SELECTOR, "div.BOlnTh").text

            print(f"\n[{idx+1}/{len(items)}] Título (prévia): {title}")
            print("Texto (prévia):", main_text)

            # Abre o post completo
            a_tag.click()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

            # Coleta dados completos
            article = driver.find_element(By.TAG_NAME, "article")
            full_title = article.find_element(By.TAG_NAME, "h1").text
            full_date = article.find_element(By.CLASS_NAME, "time-ago").text
            full_read = article.find_element(
                By.CSS_SELECTOR, "[data-hook='time-to-read']"
            ).text
            full_pars = article.find_elements(By.CSS_SELECTOR, "main p")
            full_text = "\n".join(p.text for p in full_pars)

            print("Página completa - Título:", full_title)
            print("Data:", full_date, "| Leitura:", full_read)
            print("Texto completo (trecho):", full_text[:200], "...")

            # Tenta coletar HIMPS, se existir
            try:
                himps_nome = driver.find_element(By.CLASS_NAME, "hIMZo").text
                himps_cont = driver.find_element(By.CLASS_NAME, "UuE3e").text
                pdf_info = driver.find_element(
                    By.PARTIAL_LINK_TEXT, "Download PDF"
                ).text
                print("HIMPS:", himps_nome, himps_cont, "|", pdf_info)
            except NoSuchElementException:
                print("HIMPS: não encontrado")

            # Volta para a lista, aguarda e recarrega via scroll
            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))
            time.sleep(1)
            scroll_until_loaded(".item-link-wrapper")

        except (StaleElementReferenceException, TimeoutException) as e:
            print(f"Erro ao processar item [{idx+1}]: {e}. Tentando recuperar...")
            # Tenta voltar e recarregar tudo
            try:
                driver.back()
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))
                time.sleep(1)
                scroll_until_loaded(".item-link-wrapper")
            except Exception:
                pass

        idx += 1

finally:
    driver.quit()
