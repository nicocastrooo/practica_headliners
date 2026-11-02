import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFileDialog,
                               QMessageBox, QGroupBox, QListWidget, QListWidgetItem, 
                               QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt

from practica_headliners.importacion import importar_datos, ErrorImportacion
from practica_headliners.gui.tabla_datos import TablaDatos

# Importamos la validación del core
from practica_headliners.seleccion import validar_seleccion, ErrorSeleccion

# Importamos la separación del core
from practica_headliners.separacion import separar_datos, ErrorSeparacion

# Importamos el panel de preprocesado visual
from practica_headliners.gui.panel_preprocesado import PanelPreprocesado

# Importamos la lógica del modelo del core (Tarea #118)
from practica_headliners.modelo import (
    entrenar_modelo, evaluar_modelo, generar_formula, ErrorModelo
)


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
        
        # Variables de estado para la separación y modelo
        self.df_entrenamiento = None
        self.df_test = None
        self.modelo_actual = None

        # Tabla de datos
        self.tabla = TablaDatos()
        self.layout_principal.addWidget(self.tabla, stretch=1)

        # --- ZONA DE SELECTORES ---
        self.grupo_selectores = QGroupBox("Selección de Variables")
        layout_selectores = QHBoxLayout()

        # Selector de Features
        layout_features = QVBoxLayout()
        layout_features.addWidget(QLabel("Variables de Entrada (Features):"))
        self.lista_features = QListWidget()
        layout_features.addWidget(self.lista_features)

        # Selector de Target
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
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.clicked.connect(self.confirmar_seleccion)
        self.layout_principal.addWidget(self.btn_confirmar)

        # --- ZONA DE SEPARACIÓN DE DATOS ---
        self.grupo_separacion = QGroupBox("Separación en Entrenamiento y Test")
        layout_separacion = QHBoxLayout()

        layout_pct = QVBoxLayout()
        layout_pct.addWidget(QLabel("Porcentaje Test (%):"))
        self.txt_porcentaje = QLineEdit("20")
        self.txt_porcentaje.textChanged.connect(self.actualizar_porcentaje_entrenamiento)
        layout_pct.addWidget(self.txt_porcentaje)

        layout_train = QVBoxLayout()
        layout_train.addWidget(QLabel("Porcentaje Entrenamiento:"))
        self.lbl_train = QLabel("80%")
        layout_train.addWidget(self.lbl_train)

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
        self.btn_separar.setEnabled(False)
        self.btn_separar.clicked.connect(self.ejecutar_separacion)
        self.layout_principal.addWidget(self.btn_separar)

        # --- ZONA DE PREPROCESADO ---
        self.panel_preprocesado = PanelPreprocesado()
        self.panel_preprocesado.aplicado.connect(self.on_preprocesado_aplicado)
        self.layout_principal.addWidget(self.panel_preprocesado)

        # --- ZONA DE CREACIÓN DE MODELO Y MÉTRICAS (Tarea #121) ---
        self.grupo_modelo = QGroupBox("Modelo y Evaluación")
        layout_modelo = QVBoxLayout()

        self.btn_crear_modelo = QPushButton("Crear modelo")
        self.btn_crear_modelo.setEnabled(False)
        self.btn_crear_modelo.clicked.connect(self.ejecutar_creacion_modelo)
        layout_modelo.addWidget(self.btn_crear_modelo)

        # Etiqueta para la fórmula
        self.lbl_formula = QLabel("Fórmula: (Modelo no creado)")
        self.lbl_formula.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        self.lbl_formula.setWordWrap(True)
        layout_modelo.addWidget(self.lbl_formula)

        # Tabla comparativa de métricas
        self.tabla_metricas = QTableWidget(2, 2)
        self.tabla_metricas.setHorizontalHeaderLabels(["Entrenamiento", "Test"])
        self.tabla_metricas.setVerticalHeaderLabels(["R²", "ECM"])
        self.tabla_metricas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_metricas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_metricas.setFixedHeight(95) # Altura compacta para 2 filas
        self.limpiar_metricas()
        
        layout_modelo.addWidget(self.tabla_metricas)
        self.grupo_modelo.setLayout(layout_modelo)
        self.layout_principal.addWidget(self.grupo_modelo)


    def actualizar_porcentaje_entrenamiento(self, texto):
        try:
            valor_test = float(texto.replace(',', '.'))
            if 0 <= valor_test <= 100:
                self.lbl_train.setText(f"{100.0 - valor_test:g}%")
            else:
                self.lbl_train.setText("N/A")
        except ValueError:
            self.lbl_train.setText("N/A")

    def limpiar_metricas(self):
        """Reinicia la visualización de la fórmula y la tabla de métricas."""
        self.lbl_formula.setText("Fórmula: (Modelo no creado)")
        for fila in range(2):
            for col in range(2):
                self.tabla_metricas.setItem(fila, col, QTableWidgetItem("-"))

    def limpiar_estado_flujo(self):
        """Descarta la separación y futuros modelos cuando cambia el dataset o las columnas."""
        self.df_entrenamiento = None
        self.df_test = None
        self.modelo_actual = None
        self.panel_preprocesado.invalidar()
        if hasattr(self, "btn_crear_modelo"):
            self.btn_crear_modelo.setEnabled(False)
            self.limpiar_metricas()

    def actualizar_estado_modelo(self):
        """Habilita el botón de crear modelo si hay datos y no quedan NaN pendientes."""
        if self.df_entrenamiento is not None and self.df_test is not None:
            pendientes = self.panel_preprocesado.hay_pendientes()
            self.btn_crear_modelo.setEnabled(not pendientes)
        else:
            self.btn_crear_modelo.setEnabled(False)

    def abrir_explorador_archivos(self):
        filtros = "Archivos compatibles (*.csv *.xlsx *.xls *.sqlite *.db)"
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Selecciona el dataset", "", filtros
        )

        if not ruta_archivo:
            return

        ruta_absoluta = str(Path(ruta_archivo).resolve())
        self.lbl_ruta.setText(f"Archivo: {ruta_absoluta}")

        try:
            df = importar_datos(ruta_absoluta)
            self.tabla.mostrar(df)
            self.datos = df
            
            self.actualizar_selectores(df.columns.tolist())
            self.btn_confirmar.setEnabled(True)
            
            self.btn_separar.setEnabled(False)
            self.limpiar_estado_flujo()

        except ErrorImportacion as e:
            QMessageBox.critical(self, "Error de importación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error inesperado:\n{str(e)}")

    def actualizar_selectores(self, columnas):
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

            self.btn_separar.setEnabled(True)
            self.limpiar_estado_flujo()
            
        except ErrorSeleccion as e:
            QMessageBox.warning(self, "Error de Validación", str(e))

    def ejecutar_separacion(self):
        texto_pct = self.txt_porcentaje.text().replace(',', '.')
        texto_sem = self.txt_semilla.text()

        try:
            pct_test = float(texto_pct)
        except ValueError:
            pct_test = texto_pct  

        try:
            semilla = int(texto_sem)
        except ValueError:
            try:
                semilla = float(texto_sem)
            except ValueError:
                semilla = texto_sem 

        try:
            self.limpiar_estado_flujo()
            train, test = separar_datos(self.datos, porcentaje_test=pct_test, semilla=semilla)
            
            self.df_entrenamiento = train
            self.df_test = test

            columnas_analisis = self.features_seleccionadas + [self.target_seleccionado]
            self.panel_preprocesado.establecer_conjuntos(train, test, columnas_analisis)

            QMessageBox.information(
                self,
                "Separación Completada",
                f"La división se ha realizado correctamente.\n\n"
                f"Filas Entrenamiento: {len(train)}\n"
                f"Filas Test: {len(test)}"
            )
            
            # Revisar si se puede habilitar el modelo inmediatamente (por si hay 0 NaN)
            self.actualizar_estado_modelo()

        except ErrorSeparacion as e:
            QMessageBox.warning(self, "Error de Separación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", str(e))

    def on_preprocesado_aplicado(self, entrenamiento, test):
        """Actualiza datasets procesados y verifica si se puede entrenar."""
        self.df_entrenamiento = entrenamiento
        self.df_test = test
        self.actualizar_estado_modelo()

    def ejecutar_creacion_modelo(self):
        """Crea el modelo de regresión, calcula métricas y actualiza la interfaz."""
        try:
            # 1. Entrenar solo con el conjunto de entrenamiento
            self.modelo_actual = entrenar_modelo(
                self.df_entrenamiento, 
                self.features_seleccionadas, 
                self.target_seleccionado
            )
            
            # 2. Generar y mostrar la fórmula
            formula = generar_formula(self.modelo_actual)
            self.lbl_formula.setText(formula)
            
            # 3. Calcular métricas para ambos conjuntos
            metricas = evaluar_modelo(self.modelo_actual, self.df_entrenamiento, self.df_test)
            
            # 4. Actualizar tabla visual (Fila 0: R², Fila 1: ECM)
            self.tabla_metricas.setItem(0, 0, QTableWidgetItem(f"{metricas['entrenamiento']['r2']:.4f}"))
            self.tabla_metricas.setItem(0, 1, QTableWidgetItem(f"{metricas['test']['r2']:.4f}"))
            self.tabla_metricas.setItem(1, 0, QTableWidgetItem(f"{metricas['entrenamiento']['ecm']:.4f}"))
            self.tabla_metricas.setItem(1, 1, QTableWidgetItem(f"{metricas['test']['ecm']:.4f}"))
            
            QMessageBox.information(self, "Éxito", "El modelo se ha creado y evaluado correctamente.")
            
        except ErrorModelo as e:
            QMessageBox.critical(self, "Error al crear el modelo", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())