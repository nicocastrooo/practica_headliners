"""Prueba de concepto de interfaz gráfica con Tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from practica_headliners.importacion import ErrorImportacion, importar_datos

LIMITE_FILAS = 20


class PrototipoTkinter:
    """Ventana de prueba de concepto para evaluar Tkinter."""

    def __init__(self, raiz):
        """Inicializa los componentes visuales del prototipo."""
        self.raiz = raiz
        self.raiz.title("Prueba de Concepto - Tkinter")
        self.raiz.geometry("750x500")

        self._crear_selector_archivo()
        self._crear_tabla()
        self._crear_controles_entrada()
        self._cargar_datos_ejemplo()

    def _crear_selector_archivo(self):
        """Crea el botón de selección de archivo y la etiqueta de ruta."""
        marco_archivo = ttk.Frame(self.raiz, padding=10)
        marco_archivo.pack(fill=tk.X)

        boton_archivo = ttk.Button(
            marco_archivo,
            text="Seleccionar archivo",
            command=self.seleccionar_archivo,
        )
        boton_archivo.pack(side=tk.LEFT)

        self.etiqueta_ruta = ttk.Label(
            marco_archivo,
            text="Ningún archivo seleccionado",
        )
        self.etiqueta_ruta.pack(side=tk.LEFT, padx=10)

    def _crear_tabla(self):
        """Crea la tabla con barras de desplazamiento vertical y horizontal."""
        marco_tabla = ttk.Frame(self.raiz, padding=10)
        marco_tabla.pack(fill=tk.BOTH, expand=True)

        self.tabla = ttk.Treeview(marco_tabla, show="headings")

        scroll_v = ttk.Scrollbar(
            marco_tabla, orient=tk.VERTICAL, command=self.tabla.yview
        )
        scroll_h = ttk.Scrollbar(
            marco_tabla, orient=tk.HORIZONTAL, command=self.tabla.xview
        )
        self.tabla.configure(
            yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_v.grid(row=0, column=1, sticky="ns")
        scroll_h.grid(row=1, column=0, sticky="ew")

        marco_tabla.rowconfigure(0, weight=1)
        marco_tabla.columnconfigure(0, weight=1)

    def _crear_controles_entrada(self):
        """Crea el desplegable, el cuadro de texto y el botón de mensaje."""
        marco_controles = ttk.Frame(self.raiz, padding=10)
        marco_controles.pack(fill=tk.X)

        ttk.Label(marco_controles, text="Opción:").pack(side=tk.LEFT)
        self.desplegable = ttk.Combobox(
            marco_controles,
            values=["Regresión simple", "Regresión múltiple", "Predicción"],
            state="readonly",
        )
        self.desplegable.current(0)
        self.desplegable.pack(side=tk.LEFT, padx=5)

        ttk.Label(marco_controles, text="Texto:").pack(side=tk.LEFT, padx=5)
        self.cuadro_texto = ttk.Entry(marco_controles, width=25)
        self.cuadro_texto.pack(side=tk.LEFT, padx=5)

        boton_mostrar = ttk.Button(
            marco_controles,
            text="Mostrar valores",
            command=self.mostrar_mensaje,
        )
        boton_mostrar.pack(side=tk.LEFT, padx=10)

    def _cargar_datos_ejemplo(self):
        """Rellena la tabla con datos de ejemplo iniciales."""
        columnas = ["ID", "Variable X", "Variable Y"]
        filas = [(i, i * 1.5, i * 3.0 + 1.0) for i in range(1, 25)]
        self._actualizar_tabla(columnas, filas)

    def _actualizar_tabla(self, columnas, filas):
        """Sustituye las columnas y filas mostradas en la tabla."""
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = columnas

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor=tk.CENTER)

        for fila in filas:
            self.tabla.insert("", tk.END, values=list(fila))

    def seleccionar_archivo(self):
        """Abre el diálogo de archivos e importa las primeras filas."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[
                (
                    "Archivos de datos",
                    "*.csv *.xlsx *.xls *.sqlite *.db",
                ),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not ruta:
            return

        self.etiqueta_ruta.config(text=ruta)
        try:
            datos = importar_datos(ruta)
            primeras_filas = datos.head(LIMITE_FILAS)
            columnas = list(primeras_filas.columns)
            filas = primeras_filas.itertuples(index=False, name=None)
            self._actualizar_tabla(columnas, filas)
        except ErrorImportacion as error:
            messagebox.showerror("Error de importación", str(error))

    def mostrar_mensaje(self):
        """Muestra un mensaje con la opción seleccionada y el texto."""
        opcion = self.desplegable.get()
        texto = self.cuadro_texto.get()
        mensaje = (
            f"Opción seleccionada: {opcion}\n"
            f"Texto introducido: {texto}"
        )
        messagebox.showinfo("Valores seleccionados", mensaje)


def main():
    """Punto de entrada para ejecutar el prototipo de Tkinter."""
    raiz = tk.Tk()
    PrototipoTkinter(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
