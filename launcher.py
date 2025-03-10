import os
import sys

# Ruta del directorio donde se encuentra el ejecutable o el script
if getattr(sys, 'frozen', False):
    PROJECT_DIR = os.path.dirname(sys.executable)  # Si está en un .exe
else:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_SCRIPT = os.path.join(PROJECT_DIR, "__main__.py")

# Ejecutar `main.py`
if __name__ == "__main__":
    os.system(f'python "{MAIN_SCRIPT}"')
