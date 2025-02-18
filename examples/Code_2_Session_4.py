# Description

"""
The objective of this code is to learn some useful tools to webscrap prices using bs4 and selenium. 

"""

# Libraries
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging

#Logging config
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

#%%

'Functions'

def bs4W(df_x: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    df_x : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    df_x : TYPE
        DESCRIPTION.

    """
    soup = BeautifulSoup(driver.page_source, "html.parser")
    time.sleep(nap2)
    results = soup.find(class_="product-grid__container col-sm-12 col-lg-9 product-recommendations mb-5")
    elements = results.find_all('div', class_="col-12 col-sm-3 col-md-3 product-tile--wrapper d-flex list-item-product pb-1")

    list_titles = []
    list_prices = []
    time.sleep(1)
    
    for j in elements:
        
        title_element = j.find("a", class_="link plp-link font-primary--regular product-tile--link ellipsis-product-name font-size-16")
        titles = title_element.text.strip()
        list_titles.append(titles)
        price_element = j.find('div', {'class': 'price plp-price text-left plp-price reverse'})
        list_prices.append(price_element.text.strip())
        
    time.sleep(1)     
    df_x["Product"] = list_titles
    df_x["Price"] = list_prices
    df_x["Sections"] = sections[i]
    df_x = df_x[["Sections", "Product", "Price"]]
    return df_x

def df_structure(links: list) -> pd.DataFrame:
    
    """
    Parameters
    ----------
    links : list
        List of Links.

    Returns
    -------
    df_prices : Pd DataFrame
        Prices DataFrame.

    """
    
    df_list = []
    
    'We join the dataframes'
    
    for i in range(len(links)):
        df_list.append(globals()['prices_%s' % i])
    
    df_prices = pd.concat(df_list)
    return df_prices
    
def try_click(xpath: str, stage_name: str) -> None:
    
    """
    Parameters
    ----------
    xpath : str
        DESCRIPTION.
    stage_name : str
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        WebDriverWait(driver, nap1).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        logging.info(f'{stage_name} done: Button clicked')
    except TimeoutException:
        logging.info(f'{stage_name} done with no button click: Element not clickable within {nap1} seconds')
    except Exception as e:
        logging.error(f'Unexpected error during {stage_name}: {e}')
    finally:
        time.sleep(nap)
    return None

#%%

'Options we need'

options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("start-maximized")
# options.add_argument("--headless")  
# options.add_argument("--no-sandbox")  # Bypass OS security model, REQUIRED on Linux if you're running as root
# options.add_argument("--disable-dev-shm-usage")  # Supera las limitaciones de recursos en contenedores
options.add_experimental_option('useAutomationExtension', False)
headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
executable_path_user = r'chromedriver.exe'
s = Service(r'chromedriver.exe')

'Some naps'

nap = 1
nap1 = 3
nap2 = 2

'We bring our links df'

df = pd.read_csv('soriana_links.csv')

'Our principal link'

url_principal = 'https://www.soriana.com'

'Links list'

list_links_soriana = []

'We join the principal link with the other links'

for i in df['Links'].values:
    list1 = url_principal + i
    list_links_soriana.append(list1)

list_links_soriana = list_links_soriana[0:3]
list_links_soriana = pd.Series(list_links_soriana)
sections = df['Sections'][0:3]

#%%

for i, url_soriana in enumerate(list_links_soriana):
    driver = webdriver.Chrome(service=s, options=options)
    globals()['prices_%s' % i] = pd.DataFrame(data={})
    driver.get(url_soriana)
    
    # Click in each stage
    try_click('/html/body/div[1]/header/div[4]/div/div[2]/div[2]/button[1]', 'First stage')
    try_click('/html/body/div[1]/div[3]/div/div[2]/div[3]/div[1]/div/div/div/div/div/div[2]/select', 'Second stage')
    try_click('//*[@id="store-select"]/div/div/div[1]/button', 'Third stage')
    try_click('//*[@id="sas_closeButton_11043931"]', 'Fourth stage')
    try_click('//*[@id="sas_closeButton_11043931"]', 'Fifth stage')
    
    # Scrolling 
    bottom = False
    num_trys = 0    
    while not bottom:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        num_trys += 1
        if num_trys > 10:
            bottom = True
        time.sleep(1)  # pause to make sure the page load with success
    
    time.sleep(nap2)
    
    # IPrice Extraction
    try:
        bs4W(globals()['prices_%s' % i])  
        logging.info('Prices extracted with success')
    except Exception as e:
        logging.error(f"Something's wrong with the price extraction function: {e}")
    
    driver.quit()

#%%

'We structure our final dataframe'

df_precios = df_structure(list_links_soriana)    
