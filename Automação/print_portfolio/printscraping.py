from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


def setup_driver():
    """Configura o WebDriver com opções apropriadas."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Para rodar sem interface gráfica
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


def capture_screenshots(url, folder_path):
    """Captura screenshots da página inicial e dos links encontrados."""
    driver = setup_driver()
    try:
        print(f"Accessing {url}...")
        driver.get(url)

        # Esperar que a página seja carregada completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Criar pasta para salvar os screenshots
        create_folder(folder_path)

        # Salvar screenshot da página inicial
        save_screenshot(driver, folder_path, "screenshot_1.png")

        # Capturar os links no menu
        print("Finding links on the menu...")
        links = driver.find_elements(By.CSS_SELECTOR, "#menu a")  # Usando o seletor correto
        hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]

        print(f"Found {len(hrefs)} links.")

        # Acessar cada link
        for index, href in enumerate(hrefs):
            try:
                print(f"Accessing link {index + 1}: {href}")
                driver.get(href)

                # Esperar o carregamento da página
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # Salvar o screenshot da página do link
                save_screenshot(driver, folder_path, f"screenshot_{index + 2}.png")

                # Voltar para a página inicial
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            except Exception as e:
                print(f"Error capturing screenshot for link {index + 1}: {e}")

    finally:
        driver.quit()
        print("Driver closed.")


# Executar o script
if __name__ == "__main__":
    target_url = "https://portfolio-matheus-projects-30717bca.vercel.app/Progress"
    output_folder = "imagens"
    capture_screenshots(target_url, output_folder)
