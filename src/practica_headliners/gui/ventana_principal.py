import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
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
    QStatusBar,
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
    DECIMALES,
    EXTENSION_MODELO,
    ErrorModelo,
    entrenar_modelo,
    evaluar_modelo,
    generar_formula,
    guardar_modelo,
    realizar_prediccion,
    cargar_modelo, # NUEVO: Importación para la tarea #136
)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regresión Lineal")
        # Dimensiones adaptadas para pantallas de 1366x768 sin cortes
        self.setMinimumSize(900, 600)
        self.resize(1200, 700)

        # Estado de la aplicación
        self.datos = None
        self.nombre_archivo_actual = None
        self.features_seleccionadas = []
        self.target_seleccionado = None

        # Variables de estado para la separación y modelo
        self.df_entrenamiento = None
        self.df_test = None
        self.modelo_actual = None
        self.origen_modelo = None  # "creado" o "cargado"
        self.cambios_sin_guardar = False
        self._actualizando_ui_descripcion = False

        # Diccionario para almacenar los QLineEdit dinámicos de predicción
        # (#138)
        self.inputs_prediccion = {}

        # Hilos de carga (#140)
        self.hilo_carga = None
        self._ruta_cargando = None
        self._texto_ruta_previo = ""
        self._estado_botones = None

        # Scroll general para que todos los paneles sean accesibles en 1366x768
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        self.widget_central = QWidget()
        self.scroll_area.setWidget(self.widget_central)

        # Layout principal de la ventana
        self.layout_principal = QVBoxLayout(self.widget_central)
        self.layout_principal.setSpacing(8)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)

        # --- INDICACIÓN INICIAL DE CÓMO EMPEZAR ---
        self.lbl_indicacion_inicial = QLabel(
            "💡 Cómo empezar: Carga un dataset en el Paso 1 para crear un "
            "nuevo modelo paso a paso, o carga un modelo guardado previamente."
        )
        self.lbl_indicacion_inicial.setWordWrap(True)
        self.lbl_indicacion_inicial.setStyleSheet(
            "background-color: #eef6ff; color: #1b4f72; "
            "border: 1px solid #bdd7ee; border-radius: 4px; "
            "padding: 6px 10px; font-weight: bold;"
        )
        self.layout_principal.addWidget(self.lbl_indicacion_inicial)

        # --- PASO 1: CARGAR DATOS ---
        self.grupo_carga = QGroupBox("1. Cargar datos / Cargar modelo")
        layout_carga = QVBoxLayout()

        layout_superior = QHBoxLayout()
        self.btn_cargar = QPushButton("1. Cargar dataset")
        self.btn_cargar.clicked.connect(self.abrir_explorador_archivos)

        # NUEVO (#136): Botón para cargar modelo guardado
        self.btn_cargar_modelo = QPushButton("Cargar modelo")
        self.btn_cargar_modelo.clicked.connect(self.ejecutar_carga_modelo)

        self.lbl_ruta = QLabel("Ningún archivo seleccionado")
        self.lbl_ruta.setWordWrap(True)

        layout_superior.addWidget(self.btn_cargar)
        layout_superior.addWidget(self.btn_cargar_modelo) # Añadido a la interfaz
        layout_superior.addWidget(self.lbl_ruta, stretch=1)
        layout_carga.addLayout(layout_superior)

        # Tabla de datos con altura equilibrada para 1366x768
        self.tabla = TablaDatos()
        self.tabla.setMinimumHeight(130)
        self.tabla.setMaximumHeight(190)
        layout_carga.addWidget(self.tabla)

        self.grupo_carga.setLayout(layout_carga)
        self.layout_principal.addWidget(self.grupo_carga)

        # --- PASO 2: SELECCIONAR COLUMNAS ---
        self.grupo_selectores = QGroupBox("2. Seleccionar columnas")
        self.grupo_selectores.setEnabled(False)
        layout_grupo_selectores = QVBoxLayout()
        layout_selectores = QHBoxLayout()

        # Selector de Features
        layout_features = QVBoxLayout()
        layout_features.addWidget(QLabel("Variables de Entrada (Features):"))
        self.lista_features = QListWidget()
        self.lista_features.setMaximumHeight(85)
        layout_features.addWidget(self.lista_features)

        # Selector de Target
        layout_target = QVBoxLayout()
        layout_target.addWidget(QLabel("Variable de Salida (Target):"))
        self.combo_target = QComboBox()
        layout_target.addWidget(self.combo_target)
        layout_target.addStretch()

        layout_selectores.addLayout(layout_features, stretch=2)
        layout_selectores.addLayout(layout_target, stretch=1)
        layout_grupo_selectores.addLayout(layout_selectores)

        # Botón de confirmación de columnas
        self.btn_confirmar = QPushButton("2. Confirmar selección")
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.clicked.connect(self.confirmar_seleccion)
        layout_grupo_selectores.addWidget(self.btn_confirmar)

        self.grupo_selectores.setLayout(layout_grupo_selectores)
        self.layout_principal.addWidget(self.grupo_selectores)

        # --- PASO 3: SEPARAR DATOS ---
        self.grupo_separacion = QGroupBox(
            "3. Separar datos (Entrenamiento y Test)"
        )
        self.grupo_separacion.setEnabled(False)
        layout_grupo_separacion = QVBoxLayout()
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
        layout_grupo_separacion.addLayout(layout_separacion)

        # Botón para Separar Datos
        self.btn_separar = QPushButton("3. Separar datos")
        self.btn_separar.setEnabled(False)
        self.btn_separar.clicked.connect(self.ejecutar_separacion)
        layout_grupo_separacion.addWidget(self.btn_separar)

        self.grupo_separacion.setLayout(layout_grupo_separacion)
        self.layout_principal.addWidget(self.grupo_separacion)

        # --- PASO 4: PREPROCESAR ---
        self.panel_preprocesado = PanelPreprocesado()
        self.panel_preprocesado.aplicado.connect(self.on_preprocesado_aplicado)
        self.layout_principal.addWidget(self.panel_preprocesado)

        # --- PASO 5: CREAR MODELO, MÉTRICAS Y GRÁFICO ---
        self.grupo_modelo = QGroupBox("5. Crear modelo y evaluación")
        layout_modelo = QVBoxLayout()

        layout_botones_modelo = QHBoxLayout()
        self.btn_crear_modelo = QPushButton("5. Crear modelo")
        self.btn_crear_modelo.setEnabled(False)
        self.btn_crear_modelo.clicked.connect(self.ejecutar_creacion_modelo)
        layout_botones_modelo.addWidget(self.btn_crear_modelo)

        # Botón para guardar el modelo en disco (Tarea #134)
        self.btn_guardar = QPushButton("Guardar modelo")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self.guardar_modelo_en_disco)
        layout_botones_modelo.addWidget(self.btn_guardar)

        layout_modelo.addLayout(layout_botones_modelo)

        # Etiqueta para la fórmula
        self.lbl_formula = QLabel("Fórmula: (Modelo no creado)")
        self.lbl_formula.setStyleSheet(
            "font-weight: bold; color: #2c3e50; font-size: 14px;"
        )
        self.lbl_formula.setWordWrap(True)
        layout_modelo.addWidget(self.lbl_formula)

        # Tabla comparativa de métricas
        self.tabla_metricas = QTableWidget(2, 2)
        self.tabla_metricas.setHorizontalHeaderLabels(
            ["Entrenamiento", "Test"]
        )
        self.tabla_metricas.setVerticalHeaderLabels(["R²", "ECM"])
        self.tabla_metricas.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tabla_metricas.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla_metricas.setFixedHeight(90)
        layout_modelo.addWidget(self.tabla_metricas)

        layout_modelo.addWidget(QLabel("Descripción del modelo (opcional):"))
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setPlaceholderText(
            "Escribe aquí una descripción o propósito para este modelo..."
        )
        self.txt_descripcion.setFixedHeight(55)
        self.txt_descripcion.setEnabled(False)
        self.txt_descripcion.textChanged.connect(
            self.actualizar_descripcion_modelo
        )
        layout_modelo.addWidget(self.txt_descripcion)

        # Widget del gráfico integrado desde grafico.py (Tarea #120)
        self.grafico = GraficoRegresion()
        self.grafico.setMinimumHeight(280)
        layout_modelo.addWidget(self.grafico, stretch=1)

        self.grupo_modelo.setLayout(layout_modelo)
        self.layout_principal.addWidget(self.grupo_modelo, stretch=1)

        # --- PASO 6: PREDICCIÓN (Tarea #138) ---
        self.grupo_prediccion = QGroupBox("6. Realizar predicción")
        self.grupo_prediccion.setEnabled(False)
        layout_prediccion = QVBoxLayout()

        self.layout_inputs_prediccion = QFormLayout()
        layout_prediccion.addLayout(self.layout_inputs_prediccion)

        self.btn_predecir = QPushButton("6. Realizar predicción")
        self.btn_predecir.setEnabled(False)
        self.btn_predecir.clicked.connect(self.ejecutar_prediccion)
        layout_prediccion.addWidget(self.btn_predecir)

        self.lbl_resultado_prediccion = QLabel("Resultado: -")
        self.lbl_resultado_prediccion.setStyleSheet(
            "font-weight: bold; color: #2c3e50; font-size: 14px;"
        )
        layout_prediccion.addWidget(self.lbl_resultado_prediccion)

        self.grupo_prediccion.setLayout(layout_prediccion)
        self.layout_principal.addWidget(self.grupo_prediccion)

        # --- BARRA DE ESTADO INFERIOR FIJA (#139) ---
        self.barra_estado = QStatusBar()
        self.barra_estado.setStyleSheet(
            "QStatusBar { border-top: 1px solid #cccccc; padding: 2px 6px; }"
        )
        self.setStatusBar(self.barra_estado)
        self.lbl_estado_app = QLabel()
        self.barra_estado.addPermanentWidget(self.lbl_estado_app, 1)

        self.limpiar_metricas()
        self.actualizar_barra_estado()

    # --- NUEVAS FUNCIONES PARA TAREA #136 ---
    def comprobar_cambios_sin_guardar(self) -> bool:
        """Avisa al usuario si hay cambios sin guardar. Retorna False si cancela."""
        if self.cambios_sin_guardar:
            respuesta = QMessageBox.warning(
                self,
                "Cambios sin guardar",
                "El modelo actual tiene cambios sin guardar. Si continúas, se perderán.\n¿Deseas continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.No:
                return False
        return True

    def alternar_modo_interfaz(self, modo_modelo: bool):
        """Oculta o muestra los paneles dependientes de los datos crudos."""
        self.tabla.setVisible(not modo_modelo)
        self.grupo_selectores.setVisible(not modo_modelo)
        self.grupo_separacion.setVisible(not modo_modelo)
        self.panel_preprocesado.setVisible(not modo_modelo)
        self.btn_crear_modelo.setVisible(not modo_modelo)
        if hasattr(self, 'grafico'):
            self.grafico.setVisible(not modo_modelo)

    def ejecutar_carga_modelo(self):
        """Abre el diálogo, carga un modelo guardado y adapta la GUI."""
        if not self.comprobar_cambios_sin_guardar():
            return

        filtros = f"Archivos de modelo (*{EXTENSION_MODELO})"
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Cargar modelo guardado", "", filtros
        )

        if not ruta_archivo:
            return

        try:
            modelo = cargar_modelo(ruta_archivo)
            self.modelo_actual = modelo
            self.nombre_archivo_actual = Path(ruta_archivo).name
            self.lbl_ruta.setText(f"Modelo cargado: {self.nombre_archivo_actual}")
            
            # Limpiar datos previos y asegurar columnas correctas
            self.datos = None
            self.df_entrenamiento = None
            self.df_test = None
            self.features_seleccionadas = modelo.entradas
            self.target_seleccionado = modelo.salida
            
            # Ocultar paneles innecesarios
            self.alternar_modo_interfaz(modo_modelo=True)
            
            # Actualizar metadatos
            self.lbl_formula.setText(generar_formula(modelo))
            if modelo.metricas:
                self.tabla_metricas.setItem(0, 0, QTableWidgetItem(f"{modelo.metricas.get('entrenamiento', {}).get('r2', float('nan')):.4f}"))
                self.tabla_metricas.setItem(0, 1, QTableWidgetItem(f"{modelo.metricas.get('test', {}).get('r2', float('nan')):.4f}"))
                self.tabla_metricas.setItem(1, 0, QTableWidgetItem(f"{modelo.metricas.get('entrenamiento', {}).get('ecm', float('nan')):.4f}"))
                self.tabla_metricas.setItem(1, 1, QTableWidgetItem(f"{modelo.metricas.get('test', {}).get('ecm', float('nan')):.4f}"))
            
            self._actualizando_ui_descripcion = True
            self.txt_descripcion.setEnabled(True)
            self.txt_descripcion.setPlainText(modelo.descripcion or "")
            self._actualizando_ui_descripcion = False

            # Actualizar estados y habilitar paneles restantes
            self.btn_guardar.setEnabled(True)
            self.origen_modelo = "cargado"
            self.cambios_sin_guardar = False
            self.configurar_panel_prediccion()
            self.actualizar_barra_estado()

            QMessageBox.information(self, "Modelo Cargado", "El modelo se ha cargado correctamente.")

        except ErrorModelo as e:
            QMessageBox.critical(self, "Error al cargar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error al cargar el modelo:\n{str(e)}")
    # ----------------------------------------

    def actualizar_barra_estado(self, cargando=False):
        """Actualiza la barra de estado inferior con el archivo, modelo y cambios."""
        if cargando:
            texto_archivo = f"Archivo: Cargando ({
                Path(
                    self._ruta_cargando).name})..."
        elif self.nombre_archivo_actual:
            texto_archivo = f"Archivo cargado: {self.nombre_archivo_actual}"
        else:
            texto_archivo = "Archivo cargado: Ninguno"

        if self.modelo_actual is None:
            texto_modelo = "Modelo: Sin modelo"
            texto_cambios = "Estado: Sin cambios sin guardar"
        else:
            tipo = (
                "Modelo cargado"
                if self.origen_modelo == "cargado"
                else "Modelo creado"
            )
            texto_modelo = f"Modelo: {tipo}"
            if self.cambios_sin_guardar:
                texto_cambios = "Estado: Cambios sin guardar"
            else:
                texto_cambios = "Estado: Guardado (sin cambios pendientes)"

        self.lbl_estado_app.setText(
            f"{texto_archivo}   |   {texto_modelo}   |   {texto_cambios}"
        )

    def actualizar_porcentaje_entrenamiento(self, texto):
        try:
            valor_test = float(texto.replace(",", "."))
            if 0 <= valor_test <= 100:
                self.lbl_train.setText(f"{100.0 - valor_test:g}%")
            else:
                self.lbl_train.setText("N/A")
        except ValueError:
            self.lbl_train.setText("N/A")

    def limpiar_panel_prediccion(self):
        """Elimina los campos de entrada dinámicos y deshabilita la sección de predicción."""
        if hasattr(self, "layout_inputs_prediccion"):
            while self.layout_inputs_prediccion.count():
                item = self.layout_inputs_prediccion.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.inputs_prediccion.clear()
        if hasattr(self, "lbl_resultado_prediccion"):
            self.lbl_resultado_prediccion.setText("Resultado: -")
        if hasattr(self, "btn_predecir"):
            self.btn_predecir.setEnabled(False)
        if hasattr(self, "grupo_prediccion"):
            self.grupo_prediccion.setEnabled(False)

    def configurar_panel_prediccion(self):
        """Genera dinámicamente los campos de entrada según el modelo activo."""
        self.limpiar_panel_prediccion()
        if self.modelo_actual is None:
            return

        for col in self.modelo_actual.entradas:
            campo = QLineEdit()
            campo.setPlaceholderText(
                f"Introduce el valor numérico para {col} (ej. 3.5 o 3,5)"
            )
            self.layout_inputs_prediccion.addRow(f"{col}:", campo)
            self.inputs_prediccion[col] = campo

        self.lbl_resultado_prediccion.setText(
            f"{self.modelo_actual.salida} = -"
        )
        self.btn_predecir.setEnabled(True)
        self.grupo_prediccion.setEnabled(True)

    def ejecutar_prediccion(self):
        """Valida las entradas, realiza el parseo tolerante y calcula la predicción."""
        if self.modelo_actual is None:
            return

        faltantes = []
        for col in self.modelo_actual.entradas:
            texto = self.inputs_prediccion[col].text().strip()
            if not texto:
                faltantes.append(col)

        if faltantes:
            QMessageBox.warning(
                self,
                "Valores faltantes",
                "Falta introducir un valor para las siguientes variables:\n"
                f"{', '.join(faltantes)}\n\n"
                "Introduce un número en cada campo antes de predecir.",
            )
            return

        valores_entrada = []
        no_numericas = []
        for col in self.modelo_actual.entradas:
            texto = (
                self.inputs_prediccion[col].text().strip().replace(",", ".")
            )
            try:
                valor = float(texto)
                if valor != valor or valor in (float("inf"), float("-inf")):
                    raise ValueError
                valores_entrada.append(valor)
            except ValueError:
                no_numericas.append(col)

        if no_numericas:
            QMessageBox.warning(
                self,
                "Valor no válido",
                "Las siguientes variables tienen un valor no numérico o no válido:\n"
                f"{', '.join(no_numericas)}\n\n"
                "Usa únicamente números (por ejemplo, 12.5 o 12,5).",
            )
            return

        try:
            prediccion = realizar_prediccion(
                self.modelo_actual, valores_entrada
            )
            self.lbl_resultado_prediccion.setText(
                f"{self.modelo_actual.salida} = {prediccion:.{DECIMALES}f}"
            )
        except Exception:
            QMessageBox.critical(
                self,
                "Error en la predicción",
                "No se pudo calcular la predicción con los valores introducidos. "
                "Revisa que todos los datos de entrada sean números válidos.",
            )

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
            self._actualizando_ui_descripcion = True
            self.txt_descripcion.clear()
            self.txt_descripcion.setEnabled(False)
            self._actualizando_ui_descripcion = False

        self.limpiar_panel_prediccion()

    def limpiar_estado_flujo(self):
        """Descarta la separación y futuros modelos cuando cambia el dataset o las columnas."""
        self.df_entrenamiento = None
        self.df_test = None
        self.modelo_actual = None
        self.origen_modelo = None
        self.cambios_sin_guardar = False
        self.panel_preprocesado.invalidar()
        if hasattr(self, "btn_guardar"):
            self.btn_guardar.setEnabled(False)
        if hasattr(self, "btn_crear_modelo"):
            self.btn_crear_modelo.setEnabled(False)
            self.limpiar_metricas()
        self.actualizar_barra_estado()

    def actualizar_estado_modelo(self):
        """Habilita el botón de crear modelo si hay datos y no quedan NaN pendientes."""
        if self.df_entrenamiento is not None and self.df_test is not None:
            pendientes = self.panel_preprocesado.hay_pendientes()
            self.btn_crear_modelo.setEnabled(not pendientes)
        else:
            self.btn_crear_modelo.setEnabled(False)

    def abrir_explorador_archivos(self):
        # NUEVO (#136): Comprobar si hay cambios sin guardar antes de avanzar
        if not self.comprobar_cambios_sin_guardar():
            return
            
        filtros = "Archivos compatibles (*.csv *.xlsx *.xls *.sqlite *.db)"
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Selecciona el dataset", "", filtros
        )
        if not ruta_archivo:
            return
        self.iniciar_carga(str(Path(ruta_archivo).resolve()))

    def _botones_flujo(self):
        botones = [
            self.btn_cargar,
            self.btn_cargar_modelo, # NUEVO (#136): Añadido a control de bloqueo
            self.btn_confirmar,
            self.btn_separar,
            self.btn_crear_modelo,
            self.btn_guardar,
        ]
        if hasattr(self.panel_preprocesado, "btn_aplicar"):
            botones.append(self.panel_preprocesado.btn_aplicar)
        if hasattr(self, "btn_predecir"):
            botones.append(self.btn_predecir)
        return botones

    def iniciar_carga(self, ruta):
        """Lanza la importación en un hilo y bloquea botones incompatibles."""
        if self.hilo_carga is not None:
            return
        self._ruta_cargando = ruta
        self._texto_ruta_previo = self.lbl_ruta.text()
        self.lbl_ruta.setText(f"Cargando... {ruta}")

        # Guardamos qué botones estaban activos para restaurarlos si falla
        self._estado_botones = {
            b: b.isEnabled() for b in self._botones_flujo()
        }
        for boton in self._botones_flujo():
            boton.setEnabled(False)
        self.actualizar_barra_estado(cargando=True)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.hilo_carga = HiloCarga(ruta)
        self.hilo_carga.cargado.connect(self.on_carga_terminada)
        self.hilo_carga.fallido.connect(self.on_carga_fallida)
        self.hilo_carga.finished.connect(self.on_hilo_finalizado)
        self.hilo_carga.start()

    def on_carga_terminada(self, df):
        # NUEVO (#136): Restaurar la interfaz por si venimos del modo modelo
        self.alternar_modo_interfaz(modo_modelo=False)
        
        self.lbl_ruta.setText(f"Archivo: {self._ruta_cargando}")
        self.nombre_archivo_actual = Path(self._ruta_cargando).name
        self.tabla.mostrar(df)
        self.datos = df
        self.actualizar_selectores(df.columns.tolist())
        self.limpiar_estado_flujo()
        self._estado_botones = None  # carga correcta: no se restaura nada
        self.grupo_selectores.setEnabled(True)
        self.btn_confirmar.setEnabled(True)
        self.grupo_separacion.setEnabled(False)
        self.btn_separar.setEnabled(False)
        self.actualizar_barra_estado()

    def on_carga_fallida(self, mensaje):
        self.lbl_ruta.setText(self._texto_ruta_previo)
        self.actualizar_barra_estado()
        QMessageBox.critical(self, "Error de importación", mensaje)

    def on_hilo_finalizado(self):
        """Se ejecuta siempre al terminar el hilo, con éxito o con error."""
        QApplication.restoreOverrideCursor()
        if self._estado_botones:
            for boton, activo in self._estado_botones.items():
                boton.setEnabled(activo)
        self._estado_botones = None
        self.btn_cargar.setEnabled(True)
        self.actualizar_barra_estado()
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
                f"Entradas (Features): {', '.join(features)}\n"
                f"Salida (Target): {target}",
            )

            self.grupo_separacion.setEnabled(True)
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
        except Exception:
            QMessageBox.critical(
                self,
                "Error en la separación",
                "No se pudo realizar la separación de los datos. "
                "Revisa el porcentaje de test y la semilla introducidos.",
            )

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
                0,
                0,
                QTableWidgetItem(f"{metricas['entrenamiento']['r2']:.4f}"),
            )
            self.tabla_metricas.setItem(
                0, 1, QTableWidgetItem(f"{metricas['test']['r2']:.4f}")
            )
            self.tabla_metricas.setItem(
                1,
                0,
                QTableWidgetItem(f"{metricas['entrenamiento']['ecm']:.4f}"),
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
            self._actualizando_ui_descripcion = True
            self.txt_descripcion.clear()
            self.txt_descripcion.setEnabled(True)
            self._actualizando_ui_descripcion = False

            self.btn_guardar.setEnabled(True)
            self.origen_modelo = "creado"
            self.cambios_sin_guardar = True

            # Generar dinámicamente los inputs de predicción (Tarea #138)
            self.configurar_panel_prediccion()
            self.actualizar_barra_estado()

            QMessageBox.information(
                self,
                "Éxito",
                "El modelo se ha creado y evaluado correctamente.",
            )

        except ErrorModelo as e:
            self.btn_guardar.setEnabled(False)
            self.limpiar_panel_prediccion()
            self.actualizar_barra_estado()
            QMessageBox.critical(self, "Error al crear el modelo", str(e))
        except Exception:
            self.btn_guardar.setEnabled(False)
            self.limpiar_panel_prediccion()
            self.actualizar_barra_estado()
            QMessageBox.critical(
                self,
                "Error al crear el modelo",
                "No se pudo entrenar el modelo con los datos actuales. "
                "Verifica que las columnas seleccionadas sean numéricas y no contengan valores inexistentes.",
            )

    def actualizar_descripcion_modelo(self):
        """Actualiza la descripción en la estructura de memoria del modelo en tiempo real."""
        if self._actualizando_ui_descripcion:
            return
        if self.modelo_actual is not None:
            texto = self.txt_descripcion.toPlainText()
            if texto != self.modelo_actual.descripcion:
                self.modelo_actual.actualizar_descripcion(texto)
                self.cambios_sin_guardar = True
                self.actualizar_barra_estado()

    def closeEvent(self, evento):
        # NUEVO (#136): Validar cambios sin guardar antes de salir
        if not self.comprobar_cambios_sin_guardar():
            evento.ignore()
            return
            
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

        # NUEVO (#136): Sugerir la ruta original si el modelo fue cargado
        ruta_defecto = str(getattr(self.modelo_actual, 'ruta_archivo', '')) if self.origen_modelo == "cargado" else ""
        
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar modelo", ruta_defecto, f"Modelos (*{EXTENSION_MODELO})"
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

        self.cambios_sin_guardar = False
        self.actualizar_barra_estado()

        QMessageBox.information(
            self, "Modelo guardado", f"Modelo guardado en:\n{guardado}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())