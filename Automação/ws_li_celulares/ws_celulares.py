from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pickle

caminho_chromedriver = r"C:\chromedriver\chromedriver.exe"

service = Service(executable_path=caminho_chromedriver)
driver = webdriver.Chrome(service=service)

driver.get("https://www.amazon.com.br")

cookies = pickle.load(open("cookies/amazon_cookies.pkl", "rb"))

for cookie in cookies:
    if 'domain' in cookie:
        del cookie['domain']
    driver.add_cookie(cookie)

driver.refresh()

driver.get("https://www.tudocelular.com/celulares/fichas-tecnicas.html?o=2")
elementos_links = driver.find_elements(By.CSS_SELECTOR, ".pic")
urls = [element.get_attribute("href") for element in elementos_links]


cards = []

for index, url in enumerate(urls):
    if index % 2 == 0:
        driver.execute_script("window.open('');") 
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

        try:
            itens_compra = driver.find_elements(By.CLASS_NAME, "item_compra")
            
            for item in itens_compra:
                try:
                    shop_logo_div = item.find_element(By.CLASS_NAME, "shop_logo")
                    img_element = shop_logo_div.find_element(By.TAG_NAME, "img")
                    loja_nome = img_element.get_attribute("alt")
                    
                    if "Amazon" in loja_nome:
                        print(f"'Amazon' encontrado na página {index + 1}")

                        # Coleta de dados das colunas
                        pai_das_colunas = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'phone_column'))
                        )

                        colunas = pai_das_colunas.find_elements(By.CLASS_NAME, 'phone_column_features')

                        for index, coluna in enumerate(colunas):
                            if index == 2:
                                print(f"Processando a coluna {index + 1}")
                                 # Captura todos os itens da colunaa
                                itens = coluna.find_elements(By.TAG_NAME, 'li')

                                # Certifique-se de que há pelo menos 5 itens na lista
                                if len(itens) >= 5:
                                    try:
                                        custo_beneficio = itens[0].text.replace(itens[0].find_element(By.TAG_NAME, 'small').text, '') if itens[0].find_elements(By.TAG_NAME, 'small') else itens[0].text

                                        hardware = itens[1].text.replace(itens[1].find_element(By.TAG_NAME, 'small').text, '') if itens[1].find_elements(By.TAG_NAME, 'small') else itens[1].text

                                        tela = itens[2].text.replace(itens[2].find_element(By.TAG_NAME, 'small').text, '') if itens[2].find_elements(By.TAG_NAME, 'small') else itens[2].text

                                        camera = itens[3].text.replace(itens[3].find_element(By.TAG_NAME, 'small').text, '') if itens[3].find_elements(By.TAG_NAME, 'small') else itens[3].text

                                        desempenho = itens[4].text.replace(itens[4].find_element(By.TAG_NAME, 'small').text, '') if itens[4].find_elements(By.TAG_NAME, 'small') else itens[4].text

                                        print(f"Custo-benefício: {custo_beneficio}")
                                        print(f"Hardware: {hardware}")
                                        print(f"Tela: {tela}")
                                        print(f"Câmera: {camera}")
                                        print(f"Desempenho: {desempenho}")

                                    except Exception as e:
                                        print(f"Erro ao acessar os itens: {e}")


                        oferta_link = item.find_element(By.CSS_SELECTOR, ".green_button").get_attribute("href")
                        print("Abrindo oferta da amazon")
                        
                        driver.execute_script(f"window.open('{oferta_link}');")
                        driver.switch_to.window(driver.window_handles[-1])

                        cookies = pickle.load(open("cookies/amazon_cookies.pkl", "rb"))

                        for cookie in cookies:
                            if 'domain' in cookie:
                                del cookie['domain']
                            driver.add_cookie(cookie)

                        driver.refresh()
       
                        # Aguardar que a nova página da Amazon seja carregada
                        WebDriverWait(driver, 20).until(EC.url_contains("amazon"))

                        try:


                            # Extração de dados da página da Amazon com tempos de espera maiores
                            title = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.ID, 'productTitle'))
                            ).text

                            price = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'best-offer-name'))
                            ).text

                            price_whole = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'a-price-whole'))
                            ).text
                            
                            price_fraction = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'a-price-fraction'))
                            ).text

                            # div_of_image_element = WebDriverWait(driver, 20).until(
                            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div#imgTagWrapperId'))
                            # )
                            
                            image_element = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, 'img#landingImage'))
                            )
                            image_url = image_element.get_attribute('src')

                            # Formar o preço completo
                            total_price = f"R$ {price_whole},{price_fraction}"

                            # Armazenar os dados em uma lista de cartões
                            cards.append({'link': oferta_link, 
                                          'title': title,
                                          'price': price,
                                          'total_price': total_price,
                                          'image_url': image_url,
                                          'custo_beneficio': custo_beneficio,
                                          'hardware': hardware,
                                          'tela': tela,
                                          'camera': camera,
                                          'desempenho': desempenho
                                          })

                            print(f"Dados coletados da página {index + 1}: {cards[-1]}")
                            
                        except TimeoutException:
                            print(f"Timeout ao carregar elementos na página da Amazon (página {index + 1}).")

                        driver.close() 
                        driver.switch_to.window(driver.window_handles[-1])

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                        break
                        
                except NoSuchElementException:
                    print(f"Elemento não encontrado em um item na página {index + 1}, pulando item...")

        except Exception as e:
            print(f"Erro na página {index + 1}: {e}")


# Salvar dados em arquivo JSON
if cards:
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(cards, file, ensure_ascii=False, indent=4)
    print(f"Dados únicos salvos no arquivo JSON: {cards}")
else:
    print("Nenhum dado foi coletado.")

driver.quit()
