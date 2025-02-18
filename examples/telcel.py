# Libraries

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchFrameException



'Options, parameters and data'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# browser = webdriver.Chrome(options=chrome_options)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
executable_path_user = r'chromedriver.exe'
url = 'https://www.telcel.com/personas/telefonia/amigo/recarga-compra-ahora?utm_source=google&utm_medium=socialmedia&utm_campaign=12022_google_RECARGASAON2022_trafico_prepago_amigokitsinlimite_sem&utm_content=google_recargar_nacional_na_recargar_contextual_contextual&utm_term=google_recargar_nacional_na_recargar_contextual_contextual&utm_id=%7b%7bcampaign.id%7d%7d&&&&&&campaignid=16074714926&network=g&device=c&gclid=EAIaIQobChMIrNjAx5zT_wIVTQGtBh2XUAj3EAAYASAAEgJcuvD_BwE&gclsrc=aw.ds'
phones = pd.read_excel('telefonos.xlsx')
phone = '5585533248'
phone_2 = '8211592032'
# phone_2 = str(phones.iloc[2,0])
# phones_list = (phones['Telefonos:']).to_list()
final_df = pd.DataFrame()
# final_df['Telefonos'] = phones_list
final_list = []

'Code'

for i in range(len(phones_list)):
    

    driver = webdriver.Chrome(options=chrome_options, executable_path=executable_path_user)
    driver.get(url)
    
    'Aceptar cookies'
    try:
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="acepto-cookies"]'))).click()
        print('First stage done')
    except:
        pass
    
    'Anuncio whats'
    try:
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="banner-flotante-inferior"]/div'))).click() 
        print('Second stage done')
    except:
        print('Whats button not exist')
        pass
    
    time.sleep(1)
    for attempt in range(2):
        try:
            elemento_actual = driver.switch_to.active_element
            time.sleep(1)
            for _ in range(19):
                elemento_actual.send_keys(Keys.TAB)
        except NoSuchFrameException:
            pass

    elemento_actual.send_keys(phones_list[i]) #primer telefono
    time.sleep(.05)
    elemento_actual.send_keys(Keys.TAB) #pasamos al segundo telefono
    time.sleep(.05)
    elemento_actual.send_keys(phones_list[i]) #mandamos el segundo telefono
    time.sleep(.05)
    elemento_actual.send_keys(Keys.TAB) #pasamos al segundo telefono
    time.sleep(.05)
    id1 = elemento_actual.get_attribute('id')
    driver.switch_to.frame(id1)
    time.sleep(.05)
    elemento_dentro_del_iframe = driver.find_element(By.XPATH, '//*[@id="errNumero"]')
    text_proof = elemento_dentro_del_iframe.text
    
    if text_proof != '':
        
        print('El telefono ingresado no es de telcel')
        final_list.append('False')
    
    else:
        final_list.append('True')
        print('el telefono es telcel')
    driver.close()

final_df['Result'] = final_list
