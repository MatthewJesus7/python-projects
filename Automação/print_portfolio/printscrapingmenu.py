import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    """Configura o WebDriver com opções apropriadas."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service()
    return webdriver.Chrome(service=service, options=options)


def create_folder(folder_path):
    """Cria uma pasta no sistema se ela não existir."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")


def save_screenshot(driver, folder_path, filename):
    """Salva o screenshot da página atual."""
    screenshot_path = os.path.join(folder_path, filename)
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    return screenshot_path


def capture_screenshots_from_json(json_file, folder_path):
    """Captura screenshots dos links fornecidos em um arquivo JSON."""
    driver = setup_driver()
    try:
        # Ler o arquivo JSON
        with open(json_file, "r") as f:
            data = json.load(f)

        # Criar pasta para salvar os screenshots
        create_folder(folder_path)

        # Iterar sobre os links no JSON
        for category in data:
            category_name = category.get("name", "unnamed_category")
            items = category.get("items", [])

            print(f"Processing category: {category_name} ({len(items)} items)")

            for index, item in enumerate(items):
                href = item.get("href")
                if href:
                    try:
                        print(f"Accessing link {index + 1}: {href}")
                        driver.get(href)

                        # Esperar o carregamento da página
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                        # Salvar o screenshot
                        file_name = f"{category_name}_{index + 1}.png".replace(" ", "_")
                        save_screenshot(driver, folder_path, file_name)
                    except Exception as e:
                        print(f"Error capturing screenshot for link {index + 1}: {e}")
    finally:
        driver.quit()
        print("Driver closed.")


# Executar o script
if __name__ == "__main__":
    json_file_path = "data.json"  # Substitua pelo caminho para o arquivo JSON
    output_folder = "screenshots"
    capture_screenshots_from_json(json_file_path, output_folder)
