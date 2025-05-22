import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def log(msg, color="white"):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[0m",
    }
    print(colors.get(color, "\033[0m") + msg + "\033[0m")

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)

def scroll_until_loaded(selector, max_scrolls=50, scroll_pause_time=2):
    last_count = 0
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == last_count:
            break
        last_count = len(items)
    return driver.find_elements(By.CSS_SELECTOR, selector)

def collect_post_data(description):
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    article = driver.find_element(By.TAG_NAME, "article")
    full_title = article.find_element(By.TAG_NAME, "h1").text
    full_date = article.find_element(By.CLASS_NAME, "time-ago").text
    full_read = article.find_element(By.CSS_SELECTOR, "[data-hook='time-to-read']").text
    full_pars = article.find_elements(By.CSS_SELECTOR, "main p")
    full_text = "\n".join(p.text for p in full_pars)

    post_data = {
        "titulo": full_title,
        "descricao": description,
        "data": full_date,
        "leitura": full_read,
        "texto": full_text,
        "pdf": None,
        "todos_os_pdfs": []
    }

    try:
        log("→ Buscando container do PDF antes do clique...", "blue")
        viewer = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="file-upload-viewer"]')))

        try:
            btn = viewer.find_element(By.TAG_NAME, "button")
            # btn.click()
            log("✓ Clique simulado com sucesso no botão de PDF.", "green")
            time.sleep(2)
        except NoSuchElementException:
            log("× Botão não encontrado, tentando extrair direto...", "yellow")

        log("→ Buscando container do PDF após o clique...", "blue")
        viewer = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="file-upload-viewer"]')))
        time.sleep(1)

        pdf_links = []

        # Procurar por <a>, <iframe> ou <embed>
        for tag in ["a", "iframe", "embed"]:
            try:
                elements = viewer.find_elements(By.TAG_NAME, tag)
                for el in elements:
                    href = el.get_attribute("href") or el.get_attribute("src")
                    if href and "pdf" in href.lower():
                        pdf_links.append(href)
            except:
                continue

        if pdf_links:
            post_data["pdf"] = pdf_links[0]
            post_data["todos_os_pdfs"] = list(set(pdf_links))  # remove duplicatas
            log(f"✓ PDF(s) extraído(s): {post_data['todos_os_pdfs']}", "green")
        else:
            log("× Nenhum PDF encontrado após o clique.", "red")

    except TimeoutException:
        log("× Timeout: container 'file-upload-viewer' não apareceu ou mudou.", "red")

    return post_data

def main():
    driver.get("https://www.townofhortonia.org/blog")
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))
    items = scroll_until_loaded(".item-link-wrapper")
    links = []
    for item in items:
        try:
            a_tag = item.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            desc = item.find_element(By.CSS_SELECTOR, "div.BOlnTh").text.strip()
            if href:
                links.append((href, desc))
        except:
            continue

    log(f"\n🔎 {len(links)} posts encontrados.", "blue")
    all_posts = []

    for idx, (url, desc) in enumerate(links, 1):
        log(f"\n➡️ Post {idx}/{len(links)}: {url}", "blue")
        driver.execute_script(f"window.open('{url}','_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        try:
            data = collect_post_data(desc)
            data["url"] = url
            all_posts.append(data)
        except Exception as e:
            log(f"× Erro no post: {e}", "red")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
        log("✓ posts.json salvo.", "green")

if __name__ == "__main__":
    main()
