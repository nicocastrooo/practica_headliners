from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QTableView


class ModeloDataFrame(QAbstractTableModel):
    """Modelo de Qt que expone un DataFrame de pandas como tabla."""

    def __init__(self, datos=None):
        super().__init__()
        self._datos = datos

    def rowCount(self, parent=QModelIndex()):
        return 0 if self._datos is None else len(self._datos)

    def columnCount(self, parent=QModelIndex()):
        return 0 if self._datos is None else len(self._datos.columns)

    def data(self, index, role=Qt.DisplayRole):
        if self._datos is None or not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._datos.iat[index.row(), index.column()])
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignVCenter | Qt.AlignLeft)
        return None

    def headerData(self, seccion, orientacion, role=Qt.DisplayRole):
        if self._datos is None or role != Qt.DisplayRole:
            return None
        if orientacion == Qt.Horizontal:
            return str(self._datos.columns[seccion])
        return str(seccion + 1)

    def establecer_datos(self, datos):
        """Sustituye el DataFrame mostrado por otro."""
        self.beginResetModel()
        self._datos = datos
        self.endResetModel()


class TablaDatos(QTableView):
    """Tabla con scroll horizontal y vertical que muestra un DataFrame."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._modelo = ModeloDataFrame()
        self.setModel(self._modelo)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.setVerticalScrollMode(QTableView.ScrollPerPixel)

    def mostrar(self, datos):
        """Muestra un DataFrame, sustituyendo los datos anteriores.

        Args:
            datos: DataFrame de pandas con los datos a mostrar.
        """
        self._modelo.establecer_datos(datos)
        self.resizeColumnsToContents()

    def limpiar(self):
        """Vacía la tabla."""
        self._modelo.establecer_datos(None)
