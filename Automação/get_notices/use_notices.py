import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Carrega o JSON de notícias
with open('noticias_hortonia.json', 'r') as f:
    noticias = json.load(f)

# Inicia o navegador
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# Acessa a página de login
driver.get("https://backoffice.afternorth.com")

# Preenche email e senha
wait.until(EC.presence_of_element_located((By.ID, "user_email"))).send_keys("matheuscostajesus1590@gmail.com")
driver.find_element(By.ID, "user_password").send_keys("Matheus1590")

# Pausa para você clicar manualmente no botão com class="link"
input("[INFO] Pressione Enter após clicar manualmente no botão de login (class='link')...")

# Pausa para ajustes manuais pós-login
input("[INFO] Pressione Enter após terminar os ajustes manuais (dashboard carregado)...")

# Início do processo de postagem
for noticia in noticias:
    driver.get("https://backoffice.afternorth.com/Manager/Common/MyBlogs")

    try:
        btn_add = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.toolbar.fixed.form.h button")))
        btn_add.click()
    except:
        print(f"[ERRO] Não foi possível abrir o formulário para: {noticia['titulo']}")
        continue

    wait.until(EC.presence_of_element_located((By.ID, "blog_title"))).send_keys(noticia["titulo"])
    resumo = noticia["texto"].split('.')[0]
    driver.find_element(By.ID, "blog_summary").send_keys(resumo)
    driver.find_element(By.ID, "blog_summary").send_keys(noticia["data"])
    driver.find_element(By.ID, "blog_summary").send_keys(noticia["leitura"])

    try:
        driver.find_element(By.ID, "blog_summary").send_keys(Keys.SHIFT, Keys.ENTER)
        driver.find_element(By.ID, "blog_summary").send_keys(noticia["texto"].split('.')[1].strip())
    except IndexError:
        pass

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "blog_content_ifr")))
    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    body.send_keys(noticia["texto"])
    driver.switch_to.default_content()

    if noticia["pdf"]:
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Insert/edit link"]'))).click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="url"]'))).send_keys(noticia["pdf"])
            driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').send_keys("Download PDF")
            driver.find_element(By.CSS_SELECTOR, 'button[title="Save"]').click()
        except:
            print(f"[ERRO] Falha ao inserir link PDF para: {noticia['titulo']}")

    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Save"))).click()
    except:
        print(f"[ERRO] Falha ao salvar o post: {noticia['titulo']}")

driver.quit()
