#Personal Modules
from src.scrapers_reggas.input_handlers import excel_handler as exlh

# Libraries
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging
import time
import os
from datetime import datetime

#%%

log_directory = "Output/Loggers"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

fecha_actual = datetime.now().strftime("%Y-%m-%d")
log_filename = f"{log_directory}/logger_{fecha_actual}.txt"

logger = logging.getLogger('myAppLogger')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logger.info(f"Logger inicializado. Guardando logs en: {log_filename}")

logger.info("Iniciando el proceso de scraping...")

directorio_reggas = 'Input/reggas.xlsx'
reggas_file = exlh.validacion_archivo(path=directorio_reggas)
logger.info("Archivo validado correctamente.")


#%%

#functions
def click_button(driver, xpath: str, button_name: str, timeout: int=5) -> None:
    """
    Hace clic en un botón si está disponible y registra el proceso en el logger.
    
    :param xpath: XPath del botón.
    :param button_name: Nombre del botón (para mostrar en logs).
    :param timeout: Tiempo de espera antes de fallar (default 5s).
    """
    try:
        button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button.click()
        logger.info(f"Clic en botón: {button_name}")
    except Exception as e:
        logger.error(f"Error al hacer clic en '{button_name}': {e}")

def enter_text(driver, xpath: str, text: str, timeout: int=5):
    """
    Limpia un campo de entrada y 
    escribe un nuevo valor.
    """
    try:
        input_element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        input_element.clear()
        time.sleep(0.5)  # Pausa breve
        input_element.send_keys(text)
        logger.info(f"Texto ingresado: {text}")
    except Exception as e:
        logger.error(f"Error al ingresar texto en {xpath}: {e}")

def scroll_element(driver, xpath: str):
    """
    Hace scroll dentro de un 
    elemento específico.
    """
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", element)
        logger.info("Scroll realizado")
    except Exception as e:
        logger.error(f"Error al hacer scroll en {xpath}: {e}")

def switch_to_new_tab(driver):
    """
    Cambia a la nueva pestaña 
    cuando se abre.
    """
    try:
        original_window = driver.current_window_handle
        WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
        new_window = [w for w in driver.window_handles if w != original_window][0]
        driver.switch_to.window(new_window)
        logger.info("Cambiado a nueva pestaña")
        return original_window
    except Exception as e:
        logger.error(f"Error al cambiar de pestaña: {e}")
        return None

def close_current_tab_and_return(driver, original_window):
    """
    Cierra la pestaña actual y 
    vuelve a la original.
    """
    try:
        driver.close()
        driver.switch_to.window(original_window)
        logger.info("Cerrada la pestaña actual y vuelta a la principal")
    except Exception as e:
        logger.error(f"Error al cerrar pestaña: {e}")

def extract_text(driver, xpath: str, timeout: int=5):
    """
    Extrae el 
    texto de un elemento.
    """
    try:
        element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        text = element.text
        logger.info(f"Texto extraído de {xpath}: {text}")
        return text
    except Exception as e:
        logger.error(f"Error al extraer texto de {xpath}: {e}")
        return None


#%%

directorio_reggas = 'Input/reggas.xlsx'

reggas_file = exlh.validacion_archivo(path=directorio_reggas)

reggas_list = list(reggas_file['reg'])

#%%


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("start-maximized")
options.add_argument("--disable-javascript")

options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
# executable_path_user = r'chromedriver.exe'
# s = Service(r'chromedriver.exe')

#%%

url = 'https://energeo.cre.gob.mx/Acceso/SesionExpirada#5/24.567/-101.755'

#%%

# driver = webdriver.Chrome(service=s, options=options)
driver = webdriver.Chrome(options=options)
driver.get(url)

#%%

buscar_en_el_mapa_xpath = '//*[@id="busquedaGeneralInput"]'
lupa_buscar_xpath = '//*[@id="search-container"]/button'
icono_mapa_xpath = '//*[@id="map"]/div[1]/div[4]/div'
icono_gas_xpath = '//*[@id="map"]/div[1]/div[4]/img[1]'
cajita_popup_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div'
ver_detalle_boton_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]'
caja_con_contenido_xpath = '//*[@id="contact2"]/div/div/div[4]'

#%%


click_button(driver=driver, xpath='/html/body/div/div/div/div[2]/div[2]', button_name="Botón de Inicio")
click_button(driver=driver, xpath='//*[@id="terms-and-conditions-modal"]/div/div/div[3]/button', button_name="Botón de Aceptar Términos")
click_button(driver=driver, xpath='//*[@id="consultaPublica"]/div/div[2]/a', button_name="Botón de Consulta Pública")
click_button(driver=driver, xpath='//*[@id="app-nav-main"]/li[2]/a', button_name="Botón de Sistema Energético Mexicano")

time.sleep(2)
driver.execute_script("window.scrollBy(0, 450);")

#%%

def main_function():

    nap = 3
    
    time.sleep(2)
    
    resultados = {}
    
    for valor in reggas_list[:3]:
        
        logger.info(f"Iniciando búsqueda para: {valor}")
    
        enter_text(driver=driver, xpath=buscar_en_el_mapa_xpath, text=valor)
        time.sleep(nap)
        
        click_button(driver=driver, xpath=lupa_buscar_xpath, button_name=f"Botón de Lupa (Buscar) para {valor}")
        time.sleep(nap)
    
        click_button(driver=driver, xpath='//*[@id="map"]/div[1]/div[4]/div', button_name=f"Botón Verde en Mapa para {valor}")
        time.sleep(nap)
    
        gas_icons = driver.find_elements(By.XPATH, '//*[@id="map"]/div[1]/div[4]/img')
    
        if gas_icons:
            logger.info(f"Se encontraron {len(gas_icons)} iconos de gasolina para {valor}")
        else:
            logger.warning(f"No se encontraron iconos de gasolina para {valor}")
            continue
    
        detalles_extraidos = []
    
        for idx, icon in enumerate(gas_icons, start=1):
            try:
                logger.info(f"Haciendo clic en el icono de gasolina {idx} para {valor}")
                icon.click()
                time.sleep(nap)
    
                scroll_element(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div')
                time.sleep(nap)
    
                click_button(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]', 
                             button_name=f"Botón de Ver Detalle para {valor}")
                time.sleep(nap)
    
                original_window = switch_to_new_tab(driver=driver)
                if original_window:
                    texto_extraido = extract_text(driver=driver, xpath='//*[@id="contact2"]/div/div/div[4]')
    
                    if texto_extraido:
                        detalles_extraidos.append(texto_extraido)
                        logger.info(f"Datos obtenidos del icono {idx} para {valor}: {texto_extraido}")

                    time.sleep(2)
                    close_current_tab_and_return(driver=driver, original_window=original_window)
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error al procesar el icono {idx} para {valor}: {e}")

        resultados[valor] = detalles_extraidos

    logger.info("Proceso finalizado correctamente.")

    return resultados

results_dict = main_function()