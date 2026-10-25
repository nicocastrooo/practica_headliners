import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QComboBox)
from PySide6.QtCore import Qt

from practica_headliners.importacion import importar_datos, ErrorImportacion
from practica_headliners.gui.tabla_datos import TablaDatos

# Importamos la validación del core (Tarea #103)
from practica_headliners.seleccion import validar_seleccion, ErrorSeleccion

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

        # Estado de la aplicación
        self.datos = None
        self.features_seleccionadas = []
        self.target_seleccionado = None

        # Tabla de datos (Tarea #100)
        self.tabla = TablaDatos()
        self.layout_principal.addWidget(self.tabla, stretch=1)

        # --- ZONA DE SELECTORES (Tu Tarea #105) ---
        self.grupo_selectores = QGroupBox("Selección de Variables")
        layout_selectores = QHBoxLayout()

        # Selector de Features (Selección múltiple con casillas)
        layout_features = QVBoxLayout()
        layout_features.addWidget(QLabel("Variables de Entrada (Features):"))
        self.lista_features = QListWidget()
        layout_features.addWidget(self.lista_features)

        # Selector de Target (Selección única con desplegable)
        layout_target = QVBoxLayout()
        layout_target.addWidget(QLabel("Variable de Salida (Target):"))
        self.combo_target = QComboBox()
        layout_target.addWidget(self.combo_target)

        layout_selectores.addLayout(layout_features)
        layout_selectores.addLayout(layout_target)
        self.grupo_selectores.setLayout(layout_selectores)
        
        self.layout_principal.addWidget(self.grupo_selectores)

        # Botón de confirmación
        self.btn_confirmar = QPushButton("Confirmar selección")
        self.btn_confirmar.setEnabled(False) # Se habilita solo al cargar datos
        self.btn_confirmar.clicked.connect(self.confirmar_seleccion)
        self.layout_principal.addWidget(self.btn_confirmar)

    def abrir_explorador_archivos(self):
        filtros = "Archivos compatibles (*.csv *.xlsx *.xls *.sqlite *.db)"

        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona el dataset",
            "",
            filtros
        )

        if not ruta_archivo:
            return

        ruta_absoluta = str(Path(ruta_archivo).resolve())
        self.lbl_ruta.setText(f"Archivo: {ruta_absoluta}")

        try:
            df = importar_datos(ruta_absoluta)
            self.tabla.mostrar(df)
            self.datos = df
            
            # Al cargar datos nuevos, poblamos los selectores
            self.actualizar_selectores(df.columns.tolist())
            self.btn_confirmar.setEnabled(True)

        except ErrorImportacion as e:
            QMessageBox.critical(self, "Error de importación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error inesperado al leer el archivo:\n{str(e)}")

    def actualizar_selectores(self, columnas):
        """Limpia y rellena las listas con las columnas del nuevo dataset (US #11)."""
        self.lista_features.clear()
        self.combo_target.clear()
        
        self.combo_target.addItem("-- Selecciona una salida --", userData=None)

        for col in columnas:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_features.addItem(item)
            
            self.combo_target.addItem(col)

    def confirmar_seleccion(self):
        features = []
        for i in range(self.lista_features.count()):
            item = self.lista_features.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                features.append(item.text())
        
        target = self.combo_target.currentText()
        if self.combo_target.currentIndex() == 0: 
            target = None

        try:
            # Llamamos a la función real de Samu
            validar_seleccion(self.datos, features, target)
            
            self.features_seleccionadas = features
            self.target_seleccionado = target
            
            QMessageBox.information(
                self,
                "Selección Confirmada",
                f"Entradas (Features): {', '.join(features)}\nSalida (Target): {target}"
            )
            
        except ErrorSeleccion as e:
            # Capturamos la excepción real
            QMessageBox.warning(self, "Error de Validación", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())