import pandas as pd
import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from practica_headliners.gui.hilo_carga import HiloCarga


@pytest.fixture(scope="module")
def app():
    return QCoreApplication.instance() or QCoreApplication([])


def ejecutar(ruta):
    resultado = {}
    hilo = HiloCarga(str(ruta))
    bucle = QEventLoop()
    hilo.cargado.connect(lambda df: resultado.update(df=df))
    hilo.fallido.connect(lambda msg: resultado.update(error=msg))
    hilo.finished.connect(bucle.quit)
    QTimer.singleShot(10000, bucle.quit)  # por si se cuelga
    hilo.start()
    bucle.exec()
    hilo.wait()
    return resultado


def test_carga_csv_correcta(app, tmp_path):
    ruta = tmp_path / "datos.csv"
    pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]}).to_csv(ruta, index=False)
    resultado = ejecutar(ruta)
    assert "error" not in resultado
    assert list(resultado["df"].columns) == ["x", "y"]


def test_archivo_inexistente_emite_fallido(app, tmp_path):
    resultado = ejecutar(tmp_path / "no_existe.csv")
    assert "df" not in resultado
    assert "no existe" in resultado["error"]