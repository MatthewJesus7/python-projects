import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do driver
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 15)

def scroll_until_loaded(item_selector, delay=2, max_idle_rounds=3):
    idle_rounds = 0
    last_count = 0
    while idle_rounds < max_idle_rounds:
        items = driver.find_elements(By.CSS_SELECTOR, item_selector)
        current_count = len(items)
        if current_count > last_count:
            idle_rounds = 0
            last_count = current_count
        else:
            idle_rounds += 1
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(delay)
    return driver.find_elements(By.CSS_SELECTOR, item_selector)

def collect_post_data():
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
    article = driver.find_element(By.TAG_NAME, "article")
    full_title = article.find_element(By.TAG_NAME, "h1").text
    full_date = article.find_element(By.CLASS_NAME, "time-ago").text
    full_read = article.find_element(By.CSS_SELECTOR, "[data-hook='time-to-read']").text
    full_pars = article.find_elements(By.CSS_SELECTOR, "main p")
    full_text = "\n".join(p.text for p in full_pars)

    post_data = {
        "titulo": full_title,
        "data": full_date,
        "leitura": full_read,
        "texto": full_text,
        "pdf": None  # default
    }

    try:
        pdf_block = driver.find_element(By.CSS_SELECTOR, '[data-hook="file-upload-viewer"]')
        a_tag = pdf_block.find_element(By.TAG_NAME, "a")
        pdf_link = a_tag.get_attribute("href")
        post_data["pdf"] = pdf_link
    except (NoSuchElementException, TimeoutException):
        post_data["pdf"] = None

    return post_data

def main():
    driver.get("https://www.townofhortonia.org/blog")
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-link-wrapper")))
    scroll_until_loaded(".item-link-wrapper")

    items = driver.find_elements(By.CSS_SELECTOR, ".item-link-wrapper")
    links = []
    for item in items:
        try:
            a_tag = item.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            if href:
                links.append(href)
        except NoSuchElementException:
            continue

    print(f"Encontrados {len(links)} posts para processar.")
    all_posts = []

    for idx, link in enumerate(links, start=1):
        print(f"\nProcessando post {idx}/{len(links)}: {link}")
        driver.execute_script(f"window.open('{link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        try:
            post_data = collect_post_data()
            post_data["url"] = link
            all_posts.append(post_data)
            print(f"Coletado: {post_data['titulo']}")
        except TimeoutException as e:
            print(f"Timeout ao processar post: {e}")
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    with open("noticias_hortonia.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"\n{len(all_posts)} posts salvos em 'noticias_hortonia.json'.")
    driver.quit()

if __name__ == "__main__":
    main()
