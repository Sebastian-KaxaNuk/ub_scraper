#Personal Modules
from src.scrapers_reggas.input_handlers import excel_handler as exlh

# Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
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

def scroll_element(driver, xpath: str, pixeles: str):
    """
    Hace scroll dentro de un 
    elemento específico.
    """
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script(f"arguments[0].scrollTop += {pixeles};", element)
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

def scroll_to_element(driver, xpath: str, timeout: int = 5):
    """
    Desplaza la vista hasta que el elemento especificado esté visible en la pantalla.

    :param driver: Instancia de Selenium WebDriver.
    :param xpath: XPath del elemento al que se desea hacer scroll.
    :param timeout: Tiempo máximo de espera para que el elemento aparezca (default 5s).
    """
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # Pequeña pausa para garantizar que el scroll se complete
        logger.info(f"Scrolled to element: {xpath}")
    except Exception as e:
        logger.error(f"Error al hacer scroll hasta {xpath}: {e}")

def enter_text_with_scroll(driver, xpath: str, text: str, timeout: int = 5):
    """
    Asegura que el campo de entrada esté visible en la pantalla antes de ingresar texto.

    :param driver: Instancia de Selenium WebDriver.
    :param xpath: XPath del campo de entrada.
    :param text: Texto que se desea ingresar.
    :param timeout: Tiempo de espera antes de fallar (default 5s).
    """
    try:
        # Primero, hacer scroll hasta el campo de entrada
        scroll_to_element(driver=driver, xpath=xpath, timeout=timeout)
        
        # Luego, esperar que el campo de entrada sea interactuable
        input_element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        
        # Limpiar el campo y escribir el texto
        input_element.clear()
        time.sleep(0.5)  # Pausa breve
        input_element.send_keys(text)
        
        logger.info(f"Texto ingresado: {text}")
    except Exception as e:
        logger.error(f"Error al ingresar texto en {xpath}: {e}")

def enter_text_with_dynamic_scroll(driver, xpath: str, text: str, max_attempts: int = 5, scroll_pixels: int = 300, timeout: int = 5):
    """
    Intenta encontrar un campo de entrada, hacer scroll si no está visible y volver a intentarlo hasta que se encuentre.

    :param driver: Instancia de Selenium WebDriver.
    :param xpath: XPath del campo de entrada.
    :param text: Texto que se desea ingresar.
    :param max_attempts: Número máximo de intentos de scroll antes de fallar (default 5).
    :param scroll_pixels: Cantidad de píxeles a desplazar en cada intento (default 300).
    :param timeout: Tiempo de espera antes de fallar un intento (default 5s).
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            # Intentar encontrar el elemento
            input_element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            
            # Si lo encuentra, limpiar el campo y escribir el texto
            input_element.clear()
            time.sleep(0.5)  # Pausa breve
            input_element.send_keys(text)
            logger.info(f"Texto ingresado: {text}")
            return  # Sale de la función si todo fue exitoso
        
        except Exception as e:
            logger.warning(f"Intento {attempts+1}: No se encontró el campo {xpath}, haciendo scroll y reintentando...")
            
            # Intentar hacer scroll hacia abajo
            driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            time.sleep(1)  # Pausa después del scroll
            
        attempts += 1
    
    # Si después de varios intentos no se encontró, se registra un error
    logger.error(f"No se pudo encontrar el campo {xpath} después de {max_attempts} intentos.")

def find_element_with_scroll(driver, xpath: str, max_attempts: int = 5, scroll_pixels: int = 300, timeout: int = 5):
    """
    Busca un elemento en la página. Si no lo encuentra, hace scroll y vuelve a intentarlo hasta alcanzarlo.

    :param driver: Instancia de Selenium WebDriver.
    :param xpath: XPath del elemento a buscar.
    :param max_attempts: Número máximo de intentos de scroll antes de fallar (default 5).
    :param scroll_pixels: Cantidad de píxeles a desplazar en cada intento (default 300).
    :param timeout: Tiempo máximo de espera por intento antes de fallar (default 5s).
    :return: True si encuentra el elemento, False si no lo encuentra después de los intentos.
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            # Intentar encontrar el elemento
            input_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            
            # Si lo encuentra, hacer scroll para centrarlo y salir del loop
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            time.sleep(1)  # Pequeña pausa para asegurar que el scroll se complete
            logger.info(f"Elemento {xpath} encontrado y centrado en pantalla.")
            return True  # Elemento encontrado y visible
        
        except Exception as e:
            logger.warning(f"Intento {attempts+1}: No se encontró {xpath}, haciendo scroll y reintentando...")
            
            # Intentar hacer scroll hacia abajo
            driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            time.sleep(1)  # Pausa después del scroll
            
        attempts += 1
    
    logger.error(f"No se pudo encontrar el elemento {xpath} después de {max_attempts} intentos.")
    return False  # Elemento no encontrado

#%%

os.makedirs("Output/Results", exist_ok=True)

ruta_archivo = os.path.join("Output", "Results", "resultado.txt")

directorio_reggas = 'Input/reggas.xlsx'

reggas_file = exlh.validacion_archivo(path=directorio_reggas)

reggas_list = list(reggas_file['reg'])

#%%

update = False

folder = os.path.join("Output", "Results")
os.makedirs(folder, exist_ok=True)
file_path = os.path.join(folder, "resultado.txt")
    
if os.path.exists(file_path) and update:
    existing_identifiers = set()
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split(" - ")
            if parts:
                existing_identifiers.add(parts[0].strip())
    logger.info(f"Identificadores ya procesados: {existing_identifiers}")
else:
    existing_identifiers = set()
    if not os.path.exists(file_path):
        logger.warning("No se encontró el archivo de resultados. Se procesarán todos los identificadores.")
    else:
        logger.info("Parámetro update=False. Se procesarán todos los identificadores.")

if update:
    ids_to_process = [iden for iden in reggas_list if iden not in existing_identifiers]
else:
    ids_to_process = reggas_list


#%%


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("start-maximized")
options.add_argument("--disable-javascript")

# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
executable_path_user = r'chromedriver.exe'
s = Service(r'chromedriver.exe')

#%%

url = 'https://energeo.cre.gob.mx/Acceso/SesionExpirada#5/24.567/-101.755'

#%%

driver = webdriver.Chrome(service=s, options=options)
# driver = webdriver.Chrome(options=options)
driver.get(url)

#%%

buscar_en_el_mapa_xpath = '//*[@id="busquedaGeneralInput"]'
lupa_buscar_xpath = '//*[@id="search-container"]/button'
icono_mapa_xpath = '//*[@id="map"]/div[1]/div[4]/div'
icono_gas_xpath = '//*[@id="map"]/div[1]/div[4]/img[1]'
cajita_popup_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div'
ver_detalle_boton_xpath = '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]'
caja_con_contenido_xpath = '//*[@id="contact2"]/div/div/div[4]'
retry_xpath = '//*[@id="autocomplete-list"]/div[2]'


#%%


click_button(driver=driver, xpath='/html/body/div/div/div/div[2]/div[2]', button_name="Botón de Inicio")
click_button(driver=driver, xpath='//*[@id="terms-and-conditions-modal"]/div/div/div[3]/button', button_name="Botón de Aceptar Términos")
click_button(driver=driver, xpath='//*[@id="consultaPublica"]/div/div[2]/a', button_name="Botón de Consulta Pública")
driver.execute_script("document.body.style.zoom='50%'")  # Ajusta el porcentaje según necesites
click_button(driver=driver, xpath='/html/body/header/div[1]/div/div/div/div[1]', button_name="Botón de tres rayas")

click_button(driver=driver, xpath='//*[@id="app-nav-main"]/li[2]/a', button_name="Botón de Sistema Energético Mexicano")

time.sleep(4)
# driver.execute_script("window.scrollBy(0, 430);")

#%%

driver.execute_script("document.body.style.zoom='50%'")  # Ajusta el porcentaje según necesites

element_found = find_element_with_scroll(driver, xpath=buscar_en_el_mapa_xpath, max_attempts=5, scroll_pixels=300)

# driver.execute_script("window.scrollBy(0, 150);")

#%%

nap = 6

time.sleep(2)

resultados = {}

with open(ruta_archivo, "a", encoding="utf-8") as file:
    for valor in ids_to_process:
        logger.info(f"Iniciando búsqueda para: {valor}")
        
        click_button(driver=driver, xpath='//*[@id="btnContinuarSesion"]', button_name="Botón de Inicio de Sesion doble")
        time.sleep(1)

        enter_text(driver=driver, xpath=buscar_en_el_mapa_xpath, text=valor)
        time.sleep(nap)

        click_button(driver=driver, xpath=retry_xpath, button_name=f"Botón de RETRY - {valor}")
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

                scroll_element(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div', pixeles=150)
                time.sleep(nap)
                
                pl_valor_confirmar = extract_text(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/ul/li[2]')
                pl_valor_confirmar = pl_valor_confirmar.split(": ")[1]
                
                if pl_valor_confirmar == valor:
                    logger.info(f"El icono {idx} coincide con {valor}, extrayendo detalles.")
                    
                    scroll_element(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div', pixeles=300)

                    click_button(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]', 
                                 button_name=f"Botón de Ver Detalle para {valor}")

                    time.sleep(nap)

                    original_window = switch_to_new_tab(driver=driver)
                    
                    if original_window:
                        texto_extraido = extract_text(driver=driver, xpath='//*[@id="contact2"]/div/div/div[4]')
                        razon_social = extract_text(driver=driver, xpath='//*[@id="contact2"]/div/div/div[3]')
                        marca = extract_text(driver=driver, xpath='//*[@id="contact2"]/div/div/div[5]')
                        if texto_extraido:
                            detalles_extraidos.append(texto_extraido)
                            detalles_extraidos.append(f"Razón Social - {razon_social}")
                            detalles_extraidos.append(f"Marca - {marca}")
                            logger.info(f"Datos obtenidos del icono {idx} para {valor}: {texto_extraido}")
                            
                            if len(detalles_extraidos) >= 3:
                                direccion_info = {}
                                for linea in detalles_extraidos[0].splitlines():
                                    if ":" in linea:
                                        campo, valor_campo = linea.split(":", 1)
                                        direccion_info[campo.strip()] = valor_campo.strip()

                                salida = (
                                    f"{valor} - {direccion_info.get('Calle', '')} - Código Postal {direccion_info.get('Código Postal', '')} "
                                    f"- Colonia {direccion_info.get('Colonia', '')} - Estado {direccion_info.get('ID Entidad Federativa', '')} "
                                    f"- Municipio {direccion_info.get('ID Municipio', '')} - {detalles_extraidos[1]} - {detalles_extraidos[2]}"
                                )
                                file.write(salida + "\n")
                                file.flush()

                        time.sleep(2)
                        close_current_tab_and_return(driver=driver, original_window=original_window)
                        time.sleep(2)

                    break
                
                else:
                    logger.info(f"El icono {idx} no coincide con {valor}, cerrando popup y buscando otro.")
                    scroll_element(driver=driver, xpath='//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div', pixeles=300)
                    time.sleep(nap)

                    xpath_cerrar = '//*[@id="map"]/div[1]/div[6]/div/a'
                    click_button(driver=driver, xpath=xpath_cerrar, button_name="Botón para cerrar")
                    time.sleep(1.5)
            except Exception as e:
                logger.error(f"Error al procesar el icono {idx} para {valor}: {e}")
            
logger.info("Proceso finalizado correctamente.")
