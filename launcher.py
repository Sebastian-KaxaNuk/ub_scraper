import os
import tkinter as tk
from tkinter import filedialog, messagebox

#%%

# Ruta del directorio del script
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(PROJECT_DIR, "Input")
MAIN_SCRIPT = os.path.join(PROJECT_DIR, "__main__.py")

class ExcelLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Launcher")
        self.root.geometry("400x200")

        self.selected_file = tk.StringVar()

        # Etiqueta de instrucción
        tk.Label(root, text="Selecciona un archivo de Input:").pack(pady=10)

        # Botón para seleccionar el archivo
        tk.Button(root, text="Buscar Excel", command=self.select_file).pack()

        # Mostrar archivo seleccionado
        self.label_file = tk.Label(root, textvariable=self.selected_file, wraplength=350)
        self.label_file.pack(pady=5)

        # Botón para ejecutar main.py
        tk.Button(root, text="Run", command=self.run_main, bg="green", fg="white").pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(initialdir=INPUT_DIR, filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.selected_file.set(file_path)

    def run_main(self):
        if not self.selected_file.get():
            messagebox.showerror("Error", "Por favor, selecciona un archivo.")
            return

        # Ejecutar el script main.py con el archivo seleccionado
        try:
            os.system(f'python "{MAIN_SCRIPT}" "{self.selected_file.get()}"')
            messagebox.showinfo("Éxito", "Script ejecutado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Ejecutar GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelLauncher(root)
    root.mainloop()
