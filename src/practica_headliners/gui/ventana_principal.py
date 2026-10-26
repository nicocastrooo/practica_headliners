import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QMessageBox, QGroupBox, QListWidget, QListWidgetItem, 
                               QComboBox, QLineEdit)
from PySide6.QtCore import Qt

from practica_headliners.importacion import importar_datos, ErrorImportacion
from practica_headliners.gui.tabla_datos import TablaDatos

# Importamos la validación del core (Tarea #103)
from practica_headliners.seleccion import validar_seleccion, ErrorSeleccion

# Importamos la separación del core (Tarea #106)
from practica_headliners.separacion import separar_datos, ErrorSeparacion

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
        
        # Nuevas variables de estado para la separación (Tarea #108)
        self.df_entrenamiento = None
        self.df_test = None

        # Tabla de datos (Tarea #100)
        self.tabla = TablaDatos()
        self.layout_principal.addWidget(self.tabla, stretch=1)

        # --- ZONA DE SELECTORES (Tarea #105) ---
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

        # Botón de confirmación de columnas
        self.btn_confirmar = QPushButton("Confirmar selección")
        self.btn_confirmar.setEnabled(False) # Se habilita solo al cargar datos
        self.btn_confirmar.clicked.connect(self.confirmar_seleccion)
        self.layout_principal.addWidget(self.btn_confirmar)

        # --- ZONA DE SEPARACIÓN DE DATOS (Tu Tarea #108) ---
        self.grupo_separacion = QGroupBox("Separación en Entrenamiento y Test")
        layout_separacion = QHBoxLayout()

        # Campo: Porcentaje de Test
        layout_pct = QVBoxLayout()
        layout_pct.addWidget(QLabel("Porcentaje Test (%):"))
        self.txt_porcentaje = QLineEdit("20")
        self.txt_porcentaje.textChanged.connect(self.actualizar_porcentaje_entrenamiento)
        layout_pct.addWidget(self.txt_porcentaje)

        # Etiqueta: Porcentaje de Entrenamiento (calculado automáticamente)
        layout_train = QVBoxLayout()
        layout_train.addWidget(QLabel("Porcentaje Entrenamiento:"))
        self.lbl_train = QLabel("80%")
        layout_train.addWidget(self.lbl_train)

        # Campo: Semilla Aleatoria
        layout_semilla = QVBoxLayout()
        layout_semilla.addWidget(QLabel("Semilla Aleatoria:"))
        self.txt_semilla = QLineEdit("42")
        layout_semilla.addWidget(self.txt_semilla)

        layout_separacion.addLayout(layout_pct)
        layout_separacion.addLayout(layout_train)
        layout_separacion.addLayout(layout_semilla)
        
        self.grupo_separacion.setLayout(layout_separacion)
        self.layout_principal.addWidget(self.grupo_separacion)

        # Botón para Separar Datos
        self.btn_separar = QPushButton("Separar datos")
        self.btn_separar.setEnabled(False) # Se habilita al confirmar las columnas
        self.btn_separar.clicked.connect(self.ejecutar_separacion)
        self.layout_principal.addWidget(self.btn_separar)


    def actualizar_porcentaje_entrenamiento(self, texto):
        """Calcula visualmente el porcentaje complementario en tiempo real."""
        try:
            valor_test = float(texto.replace(',', '.'))
            if 0 <= valor_test <= 100:
                self.lbl_train.setText(f"{100.0 - valor_test:g}%")
            else:
                self.lbl_train.setText("N/A")
        except ValueError:
            self.lbl_train.setText("N/A")

    def limpiar_estado_flujo(self):
        """Descarta la separación y futuros modelos cuando cambia el dataset o las columnas."""
        self.df_entrenamiento = None
        self.df_test = None
        # NOTA: En futuras historias, añadir aquí self.modelo = None o self.datos_preprocesados = None

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
            
            # Flujo: Bloqueamos separación y limpiamos estados antiguos
            self.btn_separar.setEnabled(False)
            self.limpiar_estado_flujo()

        except ErrorImportacion as e:
            QMessageBox.critical(self, "Error de importación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error inesperado al leer el archivo:\n{str(e)}")

    def actualizar_selectores(self, columnas):
        """Limpia y rellena las listas con las columnas del nuevo dataset."""
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
            validar_seleccion(self.datos, features, target)
            
            self.features_seleccionadas = features
            self.target_seleccionado = target
            
            QMessageBox.information(
                self,
                "Selección Confirmada",
                f"Entradas (Features): {', '.join(features)}\nSalida (Target): {target}"
            )

            # Flujo: Al confirmar columnas correctamente, habilitamos la separación
            self.btn_separar.setEnabled(True)
            self.limpiar_estado_flujo()
            
        except ErrorSeleccion as e:
            QMessageBox.warning(self, "Error de Validación", str(e))

    def ejecutar_separacion(self):
        # 1. Capturar los textos de la interfaz gráfica
        texto_pct = self.txt_porcentaje.text().replace(',', '.')
        texto_sem = self.txt_semilla.text()

        # 2. Conversión básica para enviar parámetros al Core
        try:
            pct_test = float(texto_pct)
        except ValueError:
            pct_test = texto_pct  # Se pasa como string para que el Core lo intercepte

        try:
            semilla = int(texto_sem)
        except ValueError:
            # Si el usuario escribe '42.5' o letras, intentamos pasarlo tal cual al Core 
            # para que la excepción isinstance(semilla, int) de tu compañero salte.
            try:
                semilla = float(texto_sem)
            except ValueError:
                semilla = texto_sem 

        # 3. Ejecutar la función lógica de tu compañero
        try:
            # Si repiten la separación, limpiamos el modelo anterior (Flujo #108)
            self.limpiar_estado_flujo()

            train, test = separar_datos(self.datos, porcentaje_test=pct_test, semilla=semilla)
            
            # Guardamos el estado para futuras historias (preprocesado y modelo)
            self.df_entrenamiento = train
            self.df_test = test

            # Visualización de confirmación
            QMessageBox.information(
                self,
                "Separación Completada",
                f"La división de datos se ha realizado correctamente.\n\n"
                f"Filas de Entrenamiento: {len(train)}\n"
                f"Filas de Test: {len(test)}"
            )

        except ErrorSeparacion as e:
            QMessageBox.warning(self, "Error de Separación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())