import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QTextEdit,
)
from PySide6.QtCore import Qt
from practica_headliners.gui.hilo_carga import HiloCarga
 
from practica_headliners.importacion import importar_datos, ErrorImportacion
from practica_headliners.gui.tabla_datos import TablaDatos
from practica_headliners.seleccion import validar_seleccion, ErrorSeleccion
from practica_headliners.separacion import separar_datos, ErrorSeparacion
from practica_headliners.gui.panel_preprocesado import PanelPreprocesado
from practica_headliners.gui.grafico import GraficoRegresion
from practica_headliners.modelo import (
    entrenar_modelo,
    evaluar_modelo,
    generar_formula,
    guardar_modelo,
    EXTENSION_MODELO,
    ErrorModelo,
)
 
 
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regresión Lineal")
        self.resize(1100, 850)
 
        # Scroll general para que los paneles y el gráfico tengan espacio amplio
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)
 
        self.widget_central = QWidget()
        self.scroll_area.setWidget(self.widget_central)
 
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

        #hilos de carga 140
        self.hilo_carga = None
        self._ruta_cargando = None
        self._texto_ruta_previo = ""
        self._estado_botones = None
 
        # Tabla de datos con altura equilibrada
        self.tabla = TablaDatos()
        self.tabla.setMinimumHeight(140)
        self.tabla.setMaximumHeight(200)
        self.layout_principal.addWidget(self.tabla)
 
        # --- ZONA DE SELECTORES ---
        self.grupo_selectores = QGroupBox("Selección de Variables")
        layout_selectores = QHBoxLayout()
 
        # Selector de Features
        layout_features = QVBoxLayout()
        layout_features.addWidget(QLabel("Variables de Entrada (Features):"))
        self.lista_features = QListWidget()
        self.lista_features.setMaximumHeight(95)
        layout_features.addWidget(self.lista_features)
 
        # Selector de Target
        layout_target = QVBoxLayout()
        layout_target.addWidget(QLabel("Variable de Salida (Target):"))
        self.combo_target = QComboBox()
        layout_target.addWidget(self.combo_target)
        layout_target.addStretch()
 
        layout_selectores.addLayout(layout_features, stretch=2)
        layout_selectores.addLayout(layout_target, stretch=1)
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
        self.txt_porcentaje.textChanged.connect(
            self.actualizar_porcentaje_entrenamiento
        )
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
 
        # --- ZONA DE CREACIÓN DE MODELO, MÉTRICAS Y GRÁFICO (Tareas #120 y #121) ---
        self.grupo_modelo = QGroupBox("Modelo y Evaluación")
        layout_modelo = QVBoxLayout()
 
        self.btn_crear_modelo = QPushButton("Crear modelo")
        self.btn_crear_modelo.setEnabled(False)
        self.btn_crear_modelo.clicked.connect(self.ejecutar_creacion_modelo)
        layout_modelo.addWidget(self.btn_crear_modelo)

        # Botón para guardar el modelo en disco (Tarea #134)
        self.btn_guardar = QPushButton("Guardar modelo")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.guardar_modelo_en_disco)
        layout_modelo.addWidget(self.btn_guardar)
 
        # Etiqueta para la fórmula
        self.lbl_formula = QLabel("Fórmula: (Modelo no creado)")
        self.lbl_formula.setStyleSheet(
            "font-weight: bold; color: #2c3e50; font-size: 14px;"
        )
        self.lbl_formula.setWordWrap(True)
        layout_modelo.addWidget(self.lbl_formula)
 
        # Tabla comparativa de métricas
        self.tabla_metricas = QTableWidget(2, 2)
        self.tabla_metricas.setHorizontalHeaderLabels(["Entrenamiento", "Test"])
        self.tabla_metricas.setVerticalHeaderLabels(["R²", "ECM"])
        self.tabla_metricas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_metricas.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla_metricas.setFixedHeight(95)
        layout_modelo.addWidget(self.tabla_metricas)

        layout_modelo.addWidget(QLabel("Descripción (opcional):"))
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setPlaceholderText("Escribe aquí una descripción o propósito para este modelo...")
        self.txt_descripcion.setFixedHeight(60)
        self.txt_descripcion.setEnabled(False) 
        self.txt_descripcion.textChanged.connect(self.actualizar_descripcion_modelo)
        layout_modelo.addWidget(self.txt_descripcion)

        # Widget del gráfico integrado desde grafico.py (Tarea #120)
        self.grafico = GraficoRegresion()
        self.grafico.setMinimumHeight(350)
        layout_modelo.addWidget(self.grafico, stretch=1)
 
        self.limpiar_metricas()
 
        self.grupo_modelo.setLayout(layout_modelo)
        self.layout_principal.addWidget(self.grupo_modelo, stretch=1)
 
    def actualizar_porcentaje_entrenamiento(self, texto):
        try:
            valor_test = float(texto.replace(",", "."))
            if 0 <= valor_test <= 100:
                self.lbl_train.setText(f"{100.0 - valor_test:g}%")
            else:
                self.lbl_train.setText("N/A")
        except ValueError:
            self.lbl_train.setText("N/A")
 
    def limpiar_metricas(self):
        """Reinicia la visualización de la fórmula, la tabla de métricas, el gráfico y la descripción."""
        self.lbl_formula.setText("Fórmula: (Modelo no creado)")
        for fila in range(2):
            for col in range(2):
                self.tabla_metricas.setItem(fila, col, QTableWidgetItem("-"))
        if hasattr(self, "grafico"):
            self.grafico.limpiar_grafico()
            
        # Ocultar y limpiar la descripción si no hay modelo activo
        if hasattr(self, "txt_descripcion"):
            self.txt_descripcion.clear()
            self.txt_descripcion.setEnabled(False)
 
    def limpiar_estado_flujo(self):
        """Descarta la separación y futuros modelos cuando cambia el dataset o las columnas."""
        self.df_entrenamiento = None
        self.df_test = None
        self.modelo_actual = None
        self.panel_preprocesado.invalidar()
        if hasattr(self, "btn_guardar"):
            self.btn_guardar.setEnabled(False)
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
        self.iniciar_carga(str(Path(ruta_archivo).resolve()))

    def _botones_flujo(self):
        return [
            self.btn_cargar,
            self.btn_confirmar,
            self.btn_separar,
            self.btn_crear_modelo,
            self.btn_guardar,
        ]

    def iniciar_carga(self, ruta):
        """Lanza la importación en un hilo y bloquea botones incompatibles."""
        if self.hilo_carga is not None:
            return
        self._ruta_cargando = ruta
        self._texto_ruta_previo = self.lbl_ruta.text()
        self.lbl_ruta.setText(f"Cargando... {ruta}")

        # Guardamos qué botones estaban activos para restaurarlos si falla
        self._estado_botones = {b: b.isEnabled() for b in self._botones_flujo()}
        for boton in self._botones_flujo():
            boton.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.hilo_carga = HiloCarga(ruta)
        self.hilo_carga.cargado.connect(self.on_carga_terminada)
        self.hilo_carga.fallido.connect(self.on_carga_fallida)
        self.hilo_carga.finished.connect(self.on_hilo_finalizado)
        self.hilo_carga.start()

    def on_carga_terminada(self, df):
        self.lbl_ruta.setText(f"Archivo: {self._ruta_cargando}")
        self.tabla.mostrar(df)
        self.datos = df
        self.actualizar_selectores(df.columns.tolist())
        self.limpiar_estado_flujo()
        self._estado_botones = None  # carga correcta: no se restaura nada
        self.btn_confirmar.setEnabled(True)
        self.btn_separar.setEnabled(False)

    def on_carga_fallida(self, mensaje):
        self.lbl_ruta.setText(self._texto_ruta_previo)
        QMessageBox.critical(self, "Error de importación", mensaje)

    def on_hilo_finalizado(self):
        """Se ejecuta siempre al terminar el hilo, con éxito o con error."""
        QApplication.restoreOverrideCursor()
        if self._estado_botones:
            for boton, activo in self._estado_botones.items():
                boton.setEnabled(activo)
        self._estado_botones = None
        self.btn_cargar.setEnabled(True)
        self.hilo_carga.wait()  # evita destruir el hilo antes de que acabe
        self.hilo_carga = None
 
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
                f"Entradas (Features): {', '.join(features)}\nSalida (Target): {target}",
            )
 
            self.btn_separar.setEnabled(True)
            self.limpiar_estado_flujo()
 
        except ErrorSeleccion as e:
            QMessageBox.warning(self, "Error de Validación", str(e))
 
    def ejecutar_separacion(self):
        texto_pct = self.txt_porcentaje.text().replace(",", ".")
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
            train, test = separar_datos(
                self.datos, porcentaje_test=pct_test, semilla=semilla
            )
 
            self.df_entrenamiento = train
            self.df_test = test
 
            columnas_analisis = self.features_seleccionadas + [
                self.target_seleccionado
            ]
            self.panel_preprocesado.establecer_conjuntos(
                train, test, columnas_analisis
            )
 
            QMessageBox.information(
                self,
                "Separación Completada",
                f"La división se ha realizado correctamente.\n\n"
                f"Filas Entrenamiento: {len(train)}\n"
                f"Filas Test: {len(test)}",
            )
 
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
        """Crea el modelo de regresión, calcula métricas y actualiza el gráfico."""
        try:
            self.modelo_actual = entrenar_modelo(
                self.df_entrenamiento,
                self.features_seleccionadas,
                self.target_seleccionado,
            )

            formula = generar_formula(self.modelo_actual)
            self.lbl_formula.setText(formula)

            metricas = evaluar_modelo(
                self.modelo_actual, self.df_entrenamiento, self.df_test
            )
            # Necesario para poder guardar el modelo (Tarea #134)
            self.modelo_actual.metricas = metricas

            self.tabla_metricas.setItem(
                0, 0, QTableWidgetItem(f"{metricas['entrenamiento']['r2']:.4f}")
            )
            self.tabla_metricas.setItem(
                0, 1, QTableWidgetItem(f"{metricas['test']['r2']:.4f}")
            )
            self.tabla_metricas.setItem(
                1, 0, QTableWidgetItem(f"{metricas['entrenamiento']['ecm']:.4f}")
            )
            self.tabla_metricas.setItem(
                1, 1, QTableWidgetItem(f"{metricas['test']['ecm']:.4f}")
            )

            self.grafico.dibujar_grafico(
                self.df_entrenamiento,
                self.df_test,
                self.features_seleccionadas,
                self.target_seleccionado,
                self.modelo_actual,
            )

            # Preparar la caja de descripción para el nuevo modelo
            self.txt_descripcion.clear()
            self.txt_descripcion.setEnabled(True)
            self.btn_guardar.setEnabled(True)

            QMessageBox.information(
                self,
                "Éxito",
                "El modelo se ha creado y evaluado correctamente.",
            )

        except ErrorModelo as e:
            self.btn_guardar.setEnabled(False)
            QMessageBox.critical(self, "Error al crear el modelo", str(e))
 
    def actualizar_descripcion_modelo(self):
        """Actualiza la descripción en la estructura de memoria del modelo en tiempo real."""
        if self.modelo_actual is not None:
            texto = self.txt_descripcion.toPlainText()
            self.modelo_actual.actualizar_descripcion(texto)


    def closeEvent(self, evento):
        if self.hilo_carga is not None and self.hilo_carga.isRunning():
            QMessageBox.information(
                self,
                "Carga en curso",
                "Espera a que termine la carga del archivo para cerrar "
                "la aplicación.",
            )
            evento.ignore()
        else:
            evento.accept()

    def guardar_modelo_en_disco(self):
        """Pide la ruta y guarda el modelo con avisos y control de errores."""
        if self.modelo_actual is None:
            return

        if not (self.modelo_actual.descripcion or "").strip():
            respuesta = QMessageBox.warning(
                self,
                "Descripción vacía",
                "El modelo no tiene descripción. ¿Quieres guardarlo "
                "igualmente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if respuesta != QMessageBox.StandardButton.Yes:
                return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar modelo", "", f"Modelos (*{EXTENSION_MODELO})"
        )
        if not ruta:  # cerró el diálogo: no se hace nada
            return

        destino = Path(ruta)
        if destino.suffix.lower() != EXTENSION_MODELO:
            destino = destino.with_name(destino.name + EXTENSION_MODELO)
            # el diálogo no conocía este nombre: preguntamos nosotros
            if destino.exists():
                respuesta = QMessageBox.question(
                    self,
                    "Sobrescribir",
                    f"{destino.name} ya existe. ¿Quieres sobrescribirlo?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if respuesta != QMessageBox.StandardButton.Yes:
                    return

        try:
            guardado = guardar_modelo(self.modelo_actual, destino)
        except ErrorModelo as e:
            QMessageBox.critical(
                self, "No se pudo guardar", f"No se guardó el modelo:\n{e}"
            )
            return

        QMessageBox.information(
            self, "Modelo guardado", f"Modelo guardado en:\n{guardado}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())