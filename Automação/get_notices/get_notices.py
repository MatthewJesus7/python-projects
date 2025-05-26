import time
import json
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

def real_click_with_pyautogui(driver, element):
    time.sleep(1)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(1)

    rect = driver.execute_script("""
        const rect = arguments[0].getBoundingClientRect();
        return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2};
    """, element)

    window_pos = driver.get_window_position()
    browser_offset_y = 120  # <-- AJUSTADO: clique 100% certeiro

    abs_x = int(window_pos['x'] + rect['x'])
    abs_y = int(window_pos['y'] + rect['y'] + browser_offset_y)

    log(f"🖱 Clique exato em ({abs_x}, {abs_y})", "yellow")
    pyautogui.moveTo(abs_x, abs_y, duration=0.3)
    pyautogui.click()
    time.sleep(1)

def collect_post_data(description):
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    article = driver.find_element(By.TAG_NAME, "article")
    full_text = article.text.strip()
    full_read = description in full_text

    post_data = {
        "desc": description,
        "leitura": full_read,
        "texto": full_text,
        "pdf": None,
        "todos_os_pdfs": [],
        "nome_pdf": None,
        "bloco_pdf": None
    }

    try:
        log("→ Procurando div do PDF...", "blue")
        viewer = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="file-upload-viewer"]')))

        real_click_with_pyautogui(driver, viewer)

        log("⏳ Esperando PDF aparecer...", "yellow")
        wait.until(lambda d: len([
            el for el in d.find_elements(By.CSS_SELECTOR, 'a, iframe, embed')
            if "pdf" in (el.get_attribute("href") or el.get_attribute("src") or "").lower()
        ]) > 0)

        pdf_links = []
        for tag in ["a", "iframe", "embed"]:
            for el in driver.find_elements(By.TAG_NAME, tag):
                href = el.get_attribute("href") or el.get_attribute("src")
                if href and "pdf" in href.lower():
                    pdf_links.append(href)

        if pdf_links:
            post_data["pdf"] = pdf_links[0]
            post_data["todos_os_pdfs"] = list(set(pdf_links))
            log(f"✓ PDF(s) encontrados: {post_data['todos_os_pdfs']}", "green")
        else:
            log("× Nenhum PDF encontrado após clique.", "red")

        try:
            download_div = next(
                el for el in driver.find_elements(By.CSS_SELECTOR, "div")
                if "download pdf" in el.text.lower()
            )
            post_data["bloco_pdf"] = download_div.text.strip()
        except StopIteration:
            log("× Div com 'Download PDF' não encontrada.", "red")

        try:
            name_div = driver.find_element(By.CSS_SELECTOR, '[data-hook="file-upload-name-container"]')
            post_data["nome_pdf"] = name_div.text.strip()
        except NoSuchElementException:
            log("× Nome do PDF não encontrado.", "red")

    except TimeoutException:
        log("× Timeout esperando conteúdo do PDF.", "red")

    return post_data

def scroll_until_loaded(selector, max_scrolls=50, scroll_pause_time=5):
    last_count = 0
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        if len(items) == last_count:
            break
        last_count = len(items)
    return driver.find_elements(By.CSS_SELECTOR, selector)

def main():
    driver.get("https://www.townofhortonia.org/blog")
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))

    items = scroll_until_loaded(".item-link-wrapper")
    links = []
    for item in items:
        try:
            href = item.find_element(By.TAG_NAME, "a").get_attribute("href")
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
