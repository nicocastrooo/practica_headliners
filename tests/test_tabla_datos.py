import pandas as pd
from PySide6.QtCore import Qt

from practica_headliners.gui.tabla_datos import ModeloDataFrame


def test_modelo_dimensiones_y_cabeceras():
    datos = pd.DataFrame({"x": [1.5, 2.5], "y": [2, 4]})
    modelo = ModeloDataFrame(datos)
    assert modelo.rowCount() == 2
    assert modelo.columnCount() == 2
    assert modelo.headerData(0, Qt.Horizontal) == "x"
    assert modelo.headerData(1, Qt.Horizontal) == "y"


def test_modelo_sustituye_datos():
    modelo = ModeloDataFrame(pd.DataFrame({"a": [1]}))
    modelo.establecer_datos(pd.DataFrame({"b": [1, 2, 3]}))
    assert modelo.rowCount() == 3
    assert modelo.headerData(0, Qt.Horizontal) == "b"