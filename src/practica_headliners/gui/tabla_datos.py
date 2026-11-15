import math
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QTableView, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel


class ModeloDataFrame(QAbstractTableModel):
    """Modelo de Qt que expone un bloque (página) de un DataFrame de pandas."""

    def __init__(self, datos=None):
        super().__init__()
        self._datos = datos
        self.filas_por_pagina = 100
        self.pagina_actual = 0

    def rowCount(self, parent=QModelIndex()):
        if self._datos is None:
            return 0
        inicio = self.pagina_actual * self.filas_por_pagina
        fin = inicio + self.filas_por_pagina
        return len(self._datos.iloc[inicio:fin])

    def columnCount(self, parent=QModelIndex()):
        return 0 if self._datos is None else len(self._datos.columns)

    def data(self, index, role=Qt.DisplayRole):
        if self._datos is None or not index.isValid():
            return None
        if role == Qt.DisplayRole:
            fila_real = index.row() + (self.pagina_actual * self.filas_por_pagina)
            return str(self._datos.iat[fila_real, index.column()])
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignVCenter | Qt.AlignLeft)
        return None

    def headerData(self, seccion, orientacion, role=Qt.DisplayRole):
        if self._datos is None or role != Qt.DisplayRole:
            return None
        if orientacion == Qt.Horizontal:
            return str(self._datos.columns[seccion])
        # Las cabeceras verticales mantienen el índice real de la fila (empezando en 1)
        fila_real = seccion + (self.pagina_actual * self.filas_por_pagina)
        return str(fila_real + 1)

    def cambiar_pagina(self, nueva_pagina):
        """Actualiza el índice de página y notifica a la vista que debe refrescarse."""
        self.beginResetModel()
        self.pagina_actual = nueva_pagina
        self.endResetModel()

    def establecer_datos(self, datos):
        """Sustituye el DataFrame completo y vuelve a la primera página."""
        self.beginResetModel()
        self._datos = datos
        self.pagina_actual = 0
        self.endResetModel()


class TablaDatos(QWidget):
    """Componente que integra una tabla de datos con controles de paginación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(5)
        
        # Visor de la tabla
        self.vista = QTableView()
        self._modelo = ModeloDataFrame()
        self.vista.setModel(self._modelo)
        self.vista.setAlternatingRowColors(True)
        self.vista.setEditTriggers(QTableView.NoEditTriggers)
        self.vista.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.vista.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.layout_principal.addWidget(self.vista)
        
        # Controles de paginación inferiores
        self.layout_controles = QHBoxLayout()
        self.layout_controles.setContentsMargins(5, 0, 5, 0)
        
        self.btn_anterior = QPushButton("⬅ Anterior")
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        
        self.lbl_paginacion = QLabel("Página 0 de 0")
        self.lbl_paginacion.setAlignment(Qt.AlignCenter)
        
        self.btn_siguiente = QPushButton("Siguiente ➡")
        self.btn_siguiente.clicked.connect(self.siguiente_pagina)
        
        self.layout_controles.addWidget(self.btn_anterior)
        self.layout_controles.addWidget(self.lbl_paginacion, stretch=1)
        self.layout_controles.addWidget(self.btn_siguiente)
        
        self.layout_principal.addLayout(self.layout_controles)
        self.actualizar_controles()

    def mostrar(self, datos):
        """Muestra un DataFrame, carga la página 1 y adapta las columnas."""
        self._modelo.establecer_datos(datos)
        self.vista.resizeColumnsToContents()
        self.actualizar_controles()

    def limpiar(self):
        """Vacía la tabla y bloquea los botones."""
        self._modelo.establecer_datos(None)
        self.actualizar_controles()
        
    def pagina_anterior(self):
        """Retrocede una página si no estamos en la primera."""
        if self._modelo.pagina_actual > 0:
            self._modelo.cambiar_pagina(self._modelo.pagina_actual - 1)
            self.actualizar_controles()

    def siguiente_pagina(self):
        """Avanza una página si no hemos llegado al límite."""
        total_paginas = self._obtener_total_paginas()
        if self._modelo.pagina_actual < total_paginas - 1:
            self._modelo.cambiar_pagina(self._modelo.pagina_actual + 1)
            self.actualizar_controles()
            
    def _obtener_total_paginas(self):
        """Calcula matemáticamente cuántas páginas hay basadas en el límite de 100 filas."""
        if self._modelo._datos is None or len(self._modelo._datos) == 0:
            return 0
        return math.ceil(len(self._modelo._datos) / self._modelo.filas_por_pagina)
        
    def actualizar_controles(self):
        """Activa/Desactiva botones según la posición de la página y el total."""
        total_paginas = self._obtener_total_paginas()
        pagina_actual = self._modelo.pagina_actual + 1 if total_paginas > 0 else 0
        
        self.lbl_paginacion.setText(f"Página {pagina_actual} de {total_paginas}")
        self.btn_anterior.setEnabled(self._modelo.pagina_actual > 0)
        self.btn_siguiente.setEnabled(self._modelo.pagina_actual < total_paginas - 1)