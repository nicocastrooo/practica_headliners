import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog)

from practica_headliners.importacion import importar_datos, ErrorImportacion

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regresión Lineal")
        self.resize(1024, 768)

        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        
        # Layout principal de la ventana
        self.layout_principal = QVBoxLayout(self.widget_central)

        # Barra superior con botón y ruta
        layout_superior = QHBoxLayout()
        
        self.btn_cargar = QPushButton("Cargar dataset")
        self.btn_cargar.clicked.connect(self.abrir_explorador_archivos)
        
        self.lbl_ruta = QLabel("Ningún archivo seleccionado")
        
        layout_superior.addWidget(self.btn_cargar)
        layout_superior.addWidget(self.lbl_ruta, stretch=1)
        
        self.layout_principal.addLayout(layout_superior)

        # AQUÍ SAMU (Historia #100) 
        # self.layout_principal.addWidget(tu_tabla)


    def abrir_explorador_archivos(self):
        # Filtramos solo por lo que pide la historia
        filtros = "Archivos compatibles (*.csv *.xlsx *.xls *.sqlite *.db)"
        
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona el dataset",
            "",
            filtros
        )

        # Si le dan a cancelar en el explorador, salimos sin hacer nada
        if not ruta_archivo:
            return

        # Pillamos la ruta absoluta (Path.resolve())
        ruta_absoluta = str(Path(ruta_archivo).resolve())
        
        # Actualizamos la etiqueta con la ruta
        self.lbl_ruta.setText(f"Archivo: {ruta_absoluta}")

        # Intentamos cargar los datos
        try:
            df = importar_datos(ruta_absoluta)
            
            # AQUÍ SAMU (Historia #100)
            # le pasas el 'df' a tu tabla para que muestre los datos
            pass
            
        except ErrorImportacion as e:
            # AQUÍ DIEGO (Historia #101)
            # tus QMessageBox para avisar de los errores
            pass
        except Exception as e:
            # Por si peta algo raro que no esté contemplado en ErrorImportacion
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())