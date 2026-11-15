from PySide6.QtCore import QThread, Signal

from practica_headliners.importacion import ErrorImportacion, importar_datos


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
        except Exception:
            self.fallido.emit(
                "No se pudo leer el archivo seleccionado. "
                "Comprueba que el archivo no esté dañado ni abierto en otro "
                "programa y que tenga un formato válido (.csv, .xlsx, .xls, .sqlite o .db)."
            )
        else:
            self.cargado.emit(datos)
