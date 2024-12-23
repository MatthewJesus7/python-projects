from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
from PIL import Image

def capture_screenshot(url, output_path):
    chrome_options = Options()
    chrome_options.add_argument("--start-fullscreen")
    chrome_options.add_argument("--headless")
    
    # Atualizando para usar o Service ao invés de executable_path
    service = Service(r"C:\chromedriver\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(url)
    time.sleep(5)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    driver.save_screenshot(output_path)
    driver.quit()
    
    image = Image.open(output_path)
    image = image.crop((0, 100, image.width, image.height - 100))
    image.save(output_path)
    
    print(f'Screenshot saved to {output_path}')

if __name__ == "__main__":
    capture_screenshot("https://portfolio-matheus-projects-30717bca.vercel.app/Progress", "imagens/screenshot.png")
