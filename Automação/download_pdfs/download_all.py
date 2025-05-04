from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time

# Configurações para rodar o Chrome em segundo plano
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Acessa o site
url = "https://www.townofhortonia.org/copy-of-current-meeting-agenda-and-mi-1"
driver.get(url)
time.sleep(3)  # Espera o site carregar

# Coleta todos os links que apontam para PDFs
pdf_links = []
elements = driver.find_elements(By.TAG_NAME, "a")
for elem in elements:
    href = elem.get_attribute("href")
    if href and href.endswith(".pdf"):
        pdf_links.append(href)

driver.quit()

# Salva os links em JSON
with open("pdf_links.json", "w") as f:
    json.dump(pdf_links, f, indent=2)

print(f"{len(pdf_links)} PDFs encontrados e salvos em pdf_links.json")
