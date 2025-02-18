#Libraries
import pandas as pd
import re
import logging

#%%

# Configuración del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validar_formato(valor: str) -> bool:
    """
    Parameters
    ----------
    valor : str
        El valor del reg.

    Returns
    -------
    bool
    1. PL/número/EXP/ES/año (Ejemplo: PL/371/EXP/ES/2015)
    2. PL/número/TRA/OM/año (Ejemplo: PL/20046/TRA/OM/2017)
    Valida si el valor cumple con el formato requerido: PL/número/EXP/ES/año.
    Donde el número puede ser de longitud variable.

    """    
    # patron = r"^PL/\d+/EXP/ES/\d{4}$"
    patron = r"^PL/\d+/(EXP/ES|TRA/OM)/\d{4}$"
    return bool(re.match(patron, str(valor)))

def validacion_archivo(path: str) -> pd.DataFrame:
    """
    Parameters
    ----------
    path : str
        El directorio donde se encuentra el archivo
        excel o csv.

    Raises
    ------
    ValueError
        Regresa error en caso de que el archivo tenga algun
        error.

    Returns
    -------
    df : pd.DataFrame
    Carga un archivo Excel o CSV y verifica la columna 'reg'.
    - Si hay nulos, duplicados o formatos incorrectos, lanza un error y detiene el código.
    - Si todo está bien, devuelve el DataFrame.
    reggas = validacion_archivo(path='Input/reggas.xlsx')
    """
    # Detectamos el tipo de archivo
    extension = path.split('.')[-1].lower()
    
    if extension == 'csv':
        df = pd.read_csv(path, dtype=str)
    elif extension in ['xls', 'xlsx']:
        df = pd.read_excel(path, dtype=str)
    else:
        logging.error(f"Extensión de archivo no soportada: {extension}")
        raise ValueError("Tipo de archivo no soportado")

    if 'reg' not in df.columns:
        logging.error("La columna 'reg' no está presente en el archivo.")
        raise ValueError("Columna 'reg' faltante en el archivo")

    if df['reg'].isna().any():
        logging.error("Se encontraron valores nulos en la columna 'reg'. Deteniendo ejecución.")
        raise ValueError("La columna 'reg' contiene valores nulos")

    if df.duplicated(subset=['reg']).any():
        logging.error("Se encontraron valores duplicados en la columna 'reg'. Deteniendo ejecución.")
        raise ValueError("La columna 'reg' contiene valores duplicados")

    df_invalidos = df[~df['reg'].apply(validar_formato)]
    if not df_invalidos.empty:
        logging.error("Se encontraron registros con formato incorrecto en 'reg'. Deteniendo ejecución.")
        for index, row in df_invalidos.iterrows():
            logging.error(f"Fila {index + 1} -> Valor incorrecto: {row['reg']}")
        raise ValueError(f"La columna 'reg' contiene {len(df_invalidos)} valores con formato incorrecto.")

    logging.info("El archivo pasó todas las validaciones correctamente.")
    return df

