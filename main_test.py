#Personal Modules
from src.scrapers_reggas.input_handlers import excel_handler as exlh

# Libraries
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import time

#Logging config
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

#%%

directorio_reggas = 'Input/reggas.xlsx'

reggas_file = exlh.validacion_archivo(path=directorio_reggas)

#%%

test = 'PL/658/EXP/ES/2015'

#%%


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("start-maximized")
options.add_argument("--disable-javascript")

# options.add_argument("--headless")  
options.add_argument("--no-sandbox")  # Bypass OS security model, REQUIRED on Linux if you're running as root
options.add_argument("--disable-dev-shm-usage")  # Supera las limitaciones de recursos en contenedores
options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
executable_path_user = r'chromedriver.exe'
s = Service(r'chromedriver.exe')

#%%

url = 'https://energeo.cre.gob.mx/Acceso/SesionExpirada#5/24.567/-101.755'

#%%

driver = webdriver.Chrome(service=s, options=options)
driver.get(url)

#%%

botton_iniciar_boton_xpath = '/html/body/div/div/div/div[2]/div[2]'

#%%

botton_iniciar_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, botton_iniciar_boton_xpath)))

elemento_referencia_xpath = '/html/body/div/div/div/div[2]/div[3]'

elemento = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, elemento_referencia_xpath))
    )

if botton_iniciar_boton is not None:
    logging.info("Boton de inicio encontrado")
    botton_iniciar_boton.click()
else:
    logging.error("Boton de inicio de sesión no encontrado")

#%%

boton_aceptar_terminos_xpath = '//*[@id="terms-and-conditions-modal"]/div/div/div[3]/button'

boton_aceptar_terminos_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, boton_aceptar_terminos_xpath)))

if boton_aceptar_terminos_boton is not None:
    logging.info("Boton de aceptar terminos encontrado")
    boton_aceptar_terminos_boton.click()
else:
    logging.error("Boton de inicio de sesión no encontrado")

#%%

boton_ingresa_consulta_publica_xpath = '//*[@id="consultaPublica"]/div/div[2]/a'

boton_ingresa_consulta_publica = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, boton_ingresa_consulta_publica_xpath)))

if boton_ingresa_consulta_publica is not None:
    logging.info("Boton de ingresa consulta publica encontrado")
    boton_ingresa_consulta_publica.click()
else:
    logging.error("Boton de consulta publica no encontrado")

#%%

sistema_energetico_mexicano_xpath = '//*[@id="app-nav-main"]/li[2]/a'

sistema_energetico_mexicano_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, sistema_energetico_mexicano_xpath)))

if sistema_energetico_mexicano_boton is not None:
    logging.info("Boton de sistema mexicano encontrado")
    sistema_energetico_mexicano_boton.click()
else:
    logging.error("Boton de sistema energetico mexicano no encontrado")

#%%

time.sleep(5)

driver.execute_script("window.scrollBy(0, 600);")  # Baja 300 píxeles

#%%

buscar_en_el_mapa_xpath = '//*[@id="busquedaGeneralInput"]'

buscar_en_el_mapa_campo = driver.find_element(By.XPATH, '//*[@id="busquedaGeneralInput"]')

time.sleep(1.5)

buscar_en_el_mapa_campo.send_keys(test)

#%%

lupa_buscar_xpath = '//*[@id="search-container"]/button'

lupa_buscar_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, lupa_buscar_xpath)))

if lupa_buscar_boton is not None:
    logging.info("Boton de lupa encontrado")
    lupa_buscar_boton.click()
else:
    logging.error("Boton de lupa para buscar no encontrado")

#%%

icono_mapa_xpath = '//*[@id="map"]/div[1]/div[4]/div'

icono_mapa_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, icono_mapa_xpath)))

if icono_mapa_boton is not None:
    logging.info("Boton verde en el mapa encontrado")
    icono_mapa_boton.click()
else:
    logging.error("Icono de mapa no encontrado")

#%%

icono_gas_xpath = '//*[@id="map"]/div[1]/div[4]/img[1]'

icono_gas_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, icono_gas_xpath)))

if icono_gas_boton is not None:
    logging.info("Boton de icono de gasolina en el mapa encontrado")
    icono_gas_boton.click()
else:
    logging.error("Icono de gas no encontrado")

#%%

cajita_popup_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div'

popup_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, cajita_popup_xpath))
)

driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", popup_element)

#%%

ver_detalle_boton_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]'

ver_detalle_boton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, ver_detalle_boton_xpath)))

if ver_detalle_boton is not None:
    logging.info("Boton de ver detalle encontrado")
    ver_detalle_boton.click()
else:
    logging.error("Boton de ver detalle no encontrado")


#%%

original_window = driver.current_window_handle
new_window = [window for window in driver.window_handles if window != original_window][0]
driver.switch_to.window(new_window)

#%%

caja_con_contenido_xpath = '//*[@id="contact2"]/div/div/div[4]'

caja_elemento = WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.XPATH, caja_con_contenido_xpath))
)

texto_caja = caja_elemento.text

#%%

driver.close()

driver.switch_to.window(original_window)

#%%

test_2 = 'PL/902/EXP/ES/2015'

buscar_en_el_mapa_campo = driver.find_element(By.XPATH, '//*[@id="busquedaGeneralInput"]')

time.sleep(1)

buscar_en_el_mapa_campo.clear()

time.sleep(1)

buscar_en_el_mapa_campo.send_keys(test_2)

#AQUI, ES DONDE REPETIMOS EL PROCESO DE 

















