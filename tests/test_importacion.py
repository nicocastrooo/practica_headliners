import sqlite3

import pytest

from practica_headliners.importacion import ErrorImportacion, leer_sqlite


def crear_bd(ruta, sentencias):
    conexion = sqlite3.connect(ruta)
    for sentencia in sentencias:
        conexion.execute(sentencia)
    conexion.commit()
    conexion.close()


def test_sqlite_una_tabla(tmp_path):
    ruta = tmp_path / "datos.db"
    crear_bd(ruta, [
        "CREATE TABLE medidas (x REAL, y INTEGER, nombre TEXT)",
        "INSERT INTO medidas VALUES (1.5, 2, 'a')",
        "INSERT INTO medidas VALUES (2.5, 4, 'b')",
    ])
    datos = leer_sqlite(ruta)
    assert list(datos.columns) == ["x", "y", "nombre"]
    assert len(datos) == 2
    assert datos["x"].dtype.kind == "f"
    assert datos["y"].dtype.kind == "i"


def test_sqlite_ruta_con_espacios_y_enye(tmp_path):
    carpeta = tmp_path / "año con espacios"
    carpeta.mkdir()
    ruta = carpeta / "diseño.sqlite"
    crear_bd(ruta, ["CREATE TABLE t (a INTEGER)", "INSERT INTO t VALUES (1)"])
    assert len(leer_sqlite(ruta)) == 1


def test_sqlite_no_existe(tmp_path):
    with pytest.raises(ErrorImportacion, match="no existe"):
        leer_sqlite(tmp_path / "nada.db")


def test_sqlite_sin_tablas(tmp_path):
    ruta = tmp_path / "vacia.db"
    crear_bd(ruta, ["CREATE VIEW v AS SELECT 1"])
    with pytest.raises(ErrorImportacion, match="ninguna tabla"):
        leer_sqlite(ruta)


def test_sqlite_varias_tablas(tmp_path):
    ruta = tmp_path / "dos.db"
    crear_bd(ruta, ["CREATE TABLE a (x INTEGER)", "CREATE TABLE b (x INTEGER)"])
    with pytest.raises(ErrorImportacion, match="2 tablas"):
        leer_sqlite(ruta)


def test_sqlite_tabla_sin_filas(tmp_path):
    ruta = tmp_path / "sin_filas.db"
    crear_bd(ruta, ["CREATE TABLE t (x INTEGER)"])
    with pytest.raises(ErrorImportacion, match="no contiene datos"):
        leer_sqlite(ruta)


def test_sqlite_archivo_danado(tmp_path):
    ruta = tmp_path / "falso.db"
    ruta.write_text("esto no es una base de datos SQLite " * 10)
    with pytest.raises(ErrorImportacion, match="dañado"):
        leer_sqlite(ruta)