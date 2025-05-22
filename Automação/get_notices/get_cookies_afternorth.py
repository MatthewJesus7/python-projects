import json
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://backoffice.afternorth.com/Manager/Common/MyBlogs")

input("Faça o login manual e pressione Enter...")  # Espera login manual

# Salva os cookies
with open("cookies.json", "w") as f:
    json.dump(driver.get_cookies(), f)

driver.quit()
