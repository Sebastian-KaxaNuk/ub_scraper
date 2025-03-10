#Personal Modules
from src.scrapers_reggas.input_handlers import excel_handler as exlh

# Libraries
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
import logging
import time
import os
from datetime import datetime
import psutil
import gc

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
    #logger.addHandler(console_handler)

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

def check_memory_usage():
    """
    Displays and returns the total memory usage of Selenium/Chrome, including child processes.

    :return: Total memory used in MB (float)
    """
    try:
        driver_process = psutil.Process(driver.service.process.pid)
        child_processes = driver_process.children(recursive=True)  # Get all child processes

        total_memory = driver_process.memory_info().rss  # Main process memory
        for child in child_processes:
            total_memory += child.memory_info().rss  # Add memory from child processes

        total_memory_mb = total_memory / 1024 / 1024  # Convert to MB
        logger.info(f"🔴 Total memory used by Selenium/Chrome: {total_memory_mb:.2f} MB")

        return total_memory_mb  # ✅ Now it returns the memory usage!

    except Exception as e:
        logger.error(f"❌ Error measuring memory usage: {e}")
        return 0  # If error occurs, return 0 to avoid crashing the process

def check_total_system_memory():
    """
    Muestra el consumo total de memoria RAM del sistema
    """
    mem = psutil.virtual_memory()
    total_mb = mem.total / 1024 / 1024
    available_mb = mem.available / 1024 / 1024
    used_mb = mem.used / 1024 / 1024
    percent_used = mem.percent

    logger.info(f"🖥️ Total System Memory: {total_mb:.2f} MB")
    logger.info(f"✅ Available Memory: {available_mb:.2f} MB")
    logger.info(f"🚀 Used Memory: {used_mb:.2f} MB ({percent_used:.2f}%)")

    return available_mb

#%%

os.makedirs("Output/Results", exist_ok=True)

ruta_archivo = os.path.join("Output", "Results", "resultado.txt")

directorio_reggas = 'Input/reggas.xlsx'

reggas_file = exlh.validacion_archivo(path=directorio_reggas)

reggas_list = list(reggas_file['reg'])

#%%

update = True

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
    cantidad_ids_procesados = len(existing_identifiers)
    logger.info(f"Cantidad de identificadores ya procesados: {cantidad_ids_procesados}")
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
options.add_argument("--renderer-process-limit=2")
options.add_argument("--single-process")  # Force Chrome to use a single process
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")  # Desactiva la GPU
options.add_argument("--blink-settings=imagesEnabled=false")  # Desactiva imágenes
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
executable_path_user = r'chromedriver.exe'
s = Service(r'chromedriver.exe')
options.add_argument("--enable-precise-memory-info")

#%%

url = 'https://energeo.cre.gob.mx/Acceso/SesionExpirada#5/24.567/-101.755'

#%%

#driver = webdriver.Chrome(service=s, options=options)
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
retry_xpath = '//*[@id="autocomplete-list"]/div[2]'


#%%


click_button(driver=driver, xpath='/html/body/div/div/div/div[2]/div[2]', button_name="Botón de Inicio")
click_button(driver=driver, xpath='//*[@id="terms-and-conditions-modal"]/div/div/div[3]/button', button_name="Botón de Aceptar Términos")
click_button(driver=driver, xpath='//*[@id="consultaPublica"]/div/div[2]/a', button_name="Botón de Consulta Pública")

click_button(driver=driver, xpath='/html/body/header/div[1]/div/div/div/div[1]', button_name="Botón de tres rayas")

click_button(driver=driver, xpath='//*[@id="app-nav-main"]/li[2]/a', button_name="Botón de Sistema Energético Mexicano")


driver.execute_script("document.body.style.zoom='60%'")
time.sleep(5)

element_found = find_element_with_scroll(driver, xpath=buscar_en_el_mapa_xpath, max_attempts=5, scroll_pixels=300)

nap = 6

time.sleep(2)

resultados = {}

with open(ruta_archivo, "a", encoding="utf-8") as file:
    for valor in ids_to_process:

        # 🔄 CONTROL DE MEMORIA: Si la memoria es alta, reinicia el navegador
        while True:
            available_memory = check_total_system_memory()
            used_memory = check_memory_usage()

            if used_memory > 2600 or available_memory < 500:
                logger.warning("⚠️ Memoria demasiado alta o poca memoria libre. Reiniciando Chrome...")

                driver.quit()
                time.sleep(5)
                driver = webdriver.Chrome(options=options)
                driver.get(url)

                click_button(driver, '/html/body/div/div/div/div[2]/div[2]', "Botón de Inicio")
                click_button(driver, '//*[@id="terms-and-conditions-modal"]/div/div/div[3]/button', "Botón de Aceptar Términos")
                click_button(driver, '//*[@id="consultaPublica"]/div/div[2]/a', "Botón de Consulta Pública")
                click_button(driver, '/html/body/header/div[1]/div/div/div/div[1]', "Botón de tres rayas")
                click_button(driver, '//*[@id="app-nav-main"]/li[2]/a', "Botón de Sistema Energético Mexicano")

                driver.execute_script("document.body.style.zoom='60%'")
                time.sleep(5)
                find_element_with_scroll(driver, buscar_en_el_mapa_xpath, max_attempts=5, scroll_pixels=300)
                time.sleep(2)

                continue  # 🔄 Volver a checar la memoria antes de iniciar el proceso

            break  # ✅ Salir del while si la memoria está en niveles seguros

        for intento in range(2):
            try:
                logger.info(f"🛠️ Iniciando búsqueda para: {valor}")

                driver.refresh()
                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                logger.info("📊 Medición inicial de memoria RAM")
                time.sleep(1)
                check_memory_usage()

                driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(2)

                # 🔹 Manejo de alerta de doble sesión
                try:
                    boton_doble_sesion = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="btnContinuarSesion"]'))
                    )
                    driver.execute_script("arguments[0].click();", boton_doble_sesion)
                except:
                    logger.info("No apareció alerta de doble sesión, continuando...")

                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                time.sleep(1)
                check_memory_usage()

                # 🔹 Buscar input y escribir texto
                try:
                    time.sleep(nap)
                    logger.info("📊 Medición antes de encontrar el campo de texto")

                    # ✅ Medir memoria antes de interactuar
                    used_memory = check_memory_usage()

                    if used_memory < 50:
                        logger.warning("⚠️ Posible error en la medición de memoria. Revisando Chrome...")
                        continue  # 🔄 Volver a intentar

                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")

                    input_element = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="busquedaGeneralInput"]'))
                    )
                    time.sleep(1)

                    # ✅ Medir memoria después de encontrar el input
                    used_memory = check_memory_usage()

                    if used_memory > 2600:
                        logger.warning("🚨 Memoria excedida después de encontrar el input. Volviendo al inicio...")
                        continue  # 🔄 Volver a intentar con el mismo `valor`

                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")
                    time.sleep(0.5)

                    input_element.clear()
                    time.sleep(0.5)
                    input_element.send_keys(valor)
                    logger.info(f"📝 Texto ingresado: {valor}")

                    time.sleep(1)
                    driver.execute_script("window.localStorage.clear();")
                    driver.execute_script("window.sessionStorage.clear();")
                    time.sleep(.05)

                    # ✅ Medir memoria después de ingresar el texto
                    used_memory = check_memory_usage()

                    if used_memory > 2600:
                        logger.warning("🚨 Memoria excedida después de ingresar el texto. Volviendo al inicio...")
                        continue  # 🔄 Volver a intentar con el mismo `valor`

                    time.sleep(5)

                except Exception as e:
                    logger.error(f"❌ Error al ingresar texto: {e}")
                    continue

                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                check_memory_usage()

                # 🔹 Buscar botón de retry
                try:
                    button_retry = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="autocomplete-list"]/div[1]'))
                    )
                    driver.execute_script("arguments[0].click();", button_retry)
                except:
                    logger.warning("⚠️ Botón de retry no encontrado.")
                    continue

                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                check_memory_usage()

                datos_encontrados = False

                # ========== 🔹 PROCESAR ÍCONOS ========== #
                def procesar_iconos_de_gas():
                    """ Procesa íconos de gasolina visibles en pantalla y extrae datos. """
                    try:
                        gas_icons = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="map"]/div[1]/div[4]/img'))
                        )
                        driver.execute_script("window.localStorage.clear();")
                        driver.execute_script("window.sessionStorage.clear();")
                        check_memory_usage()

                        # Filtrar íconos visibles
                        visible_gas_icons = [icon for icon in gas_icons if icon.is_displayed()]
                        if not visible_gas_icons:
                            logger.warning("⚠️ No hay íconos de gas visibles.")
                            return False

                    except:
                        logger.warning("⚠️ No se encontraron íconos de gasolina en el DOM.")
                        return False

                    logger.info(f"✅ Se encontraron {len(visible_gas_icons)} íconos de gasolina.")

                    for gas_idx, icon in enumerate(visible_gas_icons):
                        try:
                            logger.info(f"🛠️ Procesando ícono de gas {gas_idx + 1}")

                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
                            time.sleep(1)

                            try:
                                driver.execute_script("arguments[0].click();", icon)
                            except:
                                icon.click()

                            time.sleep(nap)

                            # Scroll en el contenedor de detalles
                            element_para_scroll = WebDriverWait(driver, 8).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div'))
                            )

                            for _ in range(3):
                                driver.execute_script("arguments[0].scrollTop += 155;", element_para_scroll)
                                time.sleep(1)
                                if driver.execute_script("return arguments[0].scrollTop;", element_para_scroll) > 100:
                                    break

                            # 🔹 Extraer información
                            element_texto = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/ul/li[2]'))
                            )
                            text = element_texto.text.split(": ")[1]

                            if text == valor:
                                boton_detalle = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="map"]/div[1]/div[6]/div/div[1]/div/div/a[1]'))
                                )
                                driver.execute_script("arguments[0].click();", boton_detalle)
                                time.sleep(3)

                                original_window = driver.current_window_handle
                                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                                new_window = [w for w in driver.window_handles if w != original_window][0]
                                driver.switch_to.window(new_window)

                                if original_window:
                                    texto_extraido = extract_text(driver, '//*[@id="contact2"]/div/div/div[4]')
                                    razon_social = extract_text(driver, '//*[@id="contact2"]/div/div/div[3]')
                                    marca = extract_text(driver, '//*[@id="contact2"]/div/div/div[5]')

                                    if texto_extraido and razon_social and marca:
                                        file.write(f"{valor} - {text} - {razon_social} - {marca} - {texto_extraido}\n")
                                        file.flush()

                                        driver.execute_script("window.localStorage.clear();")
                                        driver.execute_script("window.sessionStorage.clear();")
                                        check_memory_usage()

                                        del gas_icons, visible_gas_icons
                                        gc.collect()

                                        driver.close()
                                        driver.switch_to.window(original_window)

                                        return True

                        except Exception as e:
                            logger.error(f"❌ Error procesando ícono {gas_idx + 1}: {e}")

                    return False

                datos_encontrados = procesar_iconos_de_gas()

                # 🔹 Si no se encontraron datos en los íconos, buscar en botones verdes
                if not datos_encontrados:
                    logger.warning(f"⚠️ No se encontraron datos en los íconos de gas para {valor}, buscando botones verdes.")

                    try:
                        green_buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="map"]/div[1]/div[4]/div'))
                        )
                    except:
                        green_buttons = []

                    for idx, green_button in enumerate(green_buttons):
                        try:
                            logger.info(f"🔍 Clic en botón verde {idx+1} para {valor}")
                            driver.execute_script("arguments[0].click();", green_button)
                            time.sleep(nap)

                            datos_encontrados = procesar_iconos_de_gas()
                            if datos_encontrados:
                                break
                        except Exception as e:
                            logger.error(f"❌ Error clic en botón verde {idx+1}: {e}")

                if datos_encontrados:
                    break

            except Exception as e:
                logger.error(f"❌ Error en intento {intento + 1} para {valor}: {e}")

        else:
            logger.warning(f"⚠️ Se agotaron intentos para {valor}, pasando al siguiente.")

logger.info("✅ Proceso finalizado correctamente.")
driver.quit()
