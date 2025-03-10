# ub_scraper
Bienvenido al proyecto de automatizacion. Para asegurar una gestión eficiente y ordenada de los archivos y la configuración del entorno, sigue las siguientes instrucciones detalladas.

## Estructura de Carpetas

Mantener una estructura de carpetas organizada es crucial para la eficiencia del proyecto. Organiza tus archivos de la siguiente manera:

- **Carpeta `Input`**: Esta carpeta debe contener el archivo excel: `reggas.xlsx`

- **Carpeta `Config`**: Esta carpeta dos subcarpetas, `Loggers` y `Results`, donde `Results` contiene el archivo .txt que nos interesa.

## Configuración del Entorno y Dependencias

Para configurar tu entorno y asegurarte de que todas las dependencias necesarias están instaladas, sigue estos pasos:

1. **Descargar Anaconda**: Descarga la versión más reciente de Anaconda desde su [sitio web oficial](https://www.anaconda.com/products/distribution). Asegúrate de elegir la versión que corresponda a tu sistema operativo.

2. **Abrir Anaconda Prompt**: Una vez instalado Anaconda, inicia Anaconda Prompt desde tu menú de inicio.

3. **Crear un Nuevo Environment con Python 3.12**: En Anaconda Prompt, crea un nuevo environment llamado `env_ub_scraper` con Python 3.12 utilizando el siguiente comando:
   ```bash
   conda create --name env_ub_scraper python=3.12

4. **Activar el Environment**: Activa el environment recién creado con el comando:
   ```bash
   conda activate env_ub_scraper
   
5. **Cambiar al Directorio del Repositorio**: Navega al directorio donde está clonado el repositorio utilizando el comando cd. Por ejemplo:    
    ```bash
    cd C:\Users\TuUsuario\Documents\ub_scraper
    
6. **Instalar PDM**: Dentro del environment activado, instala PDM utilizando pip con el siguiente comando:
    ```bash
    pip install pdm
    
7. **Instalar Dependencias con PDM**: Ejecuta pdm install para instalar todas las dependencias del proyecto definidas en el archivo pyproject.toml. Usa el siguiente comando:
    ```bash
    pdm install

8. **Abrir Anaconda Navigator**: Por ultimo, dado que las ultimas versiones de Anaconda Navigator han tenido problemas para instalar Spyder desde Home, lo ideal
sera abrir spyder desde el Environment "root" y posteriormente, vamos a la barra de navegacion de spyder, luego a tools, luego a preferences, luego a Python Interpreter
y despues, seleccionamos la opcion "Use the following Python interpreter" y despues seleccionamos el icono del lado derecho para buscar el entorno, el cual deberia tener una 
ruta parecida a la siguiente: C:\Users\sebas\anaconda3\envs\env_ub_scraper\python.exe, una vez seleccionado, le damos en Apply y luego Ok. Finalmente, regresando a la pantalla
normal de spyder, reiniciamos la consola y veremos que aparecera una leyenda que nos dice que usemos conda o pip para instalar el kernel, entonces copiamos y pegamos
el comando de pip que nos da la consola de spyder y lo pegamos en el anaconda prompt y lo corremos, esto con el environment activado que hicimos anteriormente, llamado
env_ub_scraper 
