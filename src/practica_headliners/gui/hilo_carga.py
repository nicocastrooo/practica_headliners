from PySide6.QtCore import QThread, Signal

from practica_headliners.importacion import importar_datos, ErrorImportacion


class HiloCarga(QThread):
    """Importa un archivo en un hilo secundario para no bloquear la GUI.

    Este hilo nunca toca widgets: solo emite señales, y la ventana las
    recibe en su propio hilo.
    """

    cargado = Signal(object)  # DataFrame importado
    fallido = Signal(str)     # mensaje de error para el usuario

    def __init__(self, ruta, parent=None):
        super().__init__(parent)
        self.ruta = ruta

    def run(self):
        try:
            datos = importar_datos(self.ruta)
        except ErrorImportacion as error:
            self.fallido.emit(str(error))
        except Exception as error:
            self.fallido.emit(f"Ocurrió un error inesperado:\n{error}")
        else:
            self.cargado.emit(datos)