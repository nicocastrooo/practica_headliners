import sqlite3

import pandas as pd
import pytest

from practica_headliners.importacion import (
    ErrorImportacion,
    importar_datos,
    leer_csv,
    leer_excel,
    leer_sqlite,
)


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
    crear_bd(ruta, ["CREATE TABLE a (x INTEGER)",
             "CREATE TABLE b (x INTEGER)"])
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


def test_csv_valido(tmp_path):
    ruta = tmp_path / "datos.csv"
    ruta.write_text("x,y,nombre\n1.5,2,a\n2.5,4,b\n", encoding="utf-8")
    datos = leer_csv(ruta)
    assert list(datos.columns) == ["x", "y", "nombre"]
    assert len(datos) == 2
    assert datos["x"].dtype.kind == "f"
    assert datos["y"].dtype.kind == "i"


def test_csv_ruta_con_espacios_y_enye(tmp_path):
    carpeta = tmp_path / "año con espacios"
    carpeta.mkdir()
    ruta = carpeta / "diseño.csv"
    ruta.write_text("a,b\n1,2\n", encoding="utf-8")
    assert len(leer_csv(ruta)) == 1


def test_csv_no_existe(tmp_path):
    with pytest.raises(ErrorImportacion, match="no existe"):
        leer_csv(tmp_path / "inexistente.csv")


def test_csv_vacio(tmp_path):
    ruta = tmp_path / "vacio.csv"
    ruta.write_text("", encoding="utf-8")
    with pytest.raises(ErrorImportacion, match="no contiene datos"):
        leer_csv(ruta)


def test_csv_sin_filas(tmp_path):
    ruta = tmp_path / "solo_cabecera.csv"
    ruta.write_text("x,y\n", encoding="utf-8")
    with pytest.raises(ErrorImportacion, match="no contiene datos"):
        leer_csv(ruta)


def test_csv_archivo_danado(tmp_path):
    ruta = tmp_path / "falso.csv"
    ruta.write_bytes(b"\x00\xff\xfe contenido binario invalido")
    with pytest.raises(ErrorImportacion, match="dañado"):
        leer_csv(ruta)


def test_excel_xlsx_valido(tmp_path):
    ruta = tmp_path / "datos.xlsx"
    df_original = pd.DataFrame(
        {"x": [1.5, 2.5], "y": [2, 4], "nombre": ["a", "b"]}
    )
    df_original.to_excel(ruta, index=False)
    datos = leer_excel(ruta)
    assert list(datos.columns) == ["x", "y", "nombre"]
    assert len(datos) == 2
    assert datos["x"].dtype.kind == "f"
    assert datos["y"].dtype.kind == "i"


def test_excel_ruta_con_espacios_y_enye(tmp_path):
    carpeta = tmp_path / "campaña datos"
    carpeta.mkdir()
    ruta = carpeta / "otoño.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(ruta, index=False)
    assert len(leer_excel(ruta)) == 1


def test_excel_no_existe(tmp_path):
    with pytest.raises(ErrorImportacion, match="no existe"):
        leer_excel(tmp_path / "inexistente.xlsx")


def test_excel_sin_filas(tmp_path):
    ruta = tmp_path / "sin_filas.xlsx"
    pd.DataFrame(columns=["x", "y"]).to_excel(ruta, index=False)
    with pytest.raises(ErrorImportacion, match="no contiene datos"):
        leer_excel(ruta)


def test_excel_archivo_danado(tmp_path):
    ruta = tmp_path / "falso.xlsx"
    ruta.write_text("esto no es un archivo excel", encoding="utf-8")
    with pytest.raises(ErrorImportacion, match="dañado"):
        leer_excel(ruta)


def test_excel_xls_archivo_danado(tmp_path):
    ruta = tmp_path / "falso.xls"
    ruta.write_text("esto tampoco es un xls antiguo", encoding="utf-8")
    with pytest.raises(ErrorImportacion, match="dañado"):
        leer_excel(ruta)


def test_importar_datos_detecta_formatos(tmp_path):
    ruta_csv = tmp_path / "prueba.csv"
    ruta_csv.write_text("a,b\n1,2\n", encoding="utf-8")
    assert len(importar_datos(ruta_csv)) == 1

    ruta_xlsx = tmp_path / "prueba.xlsx"
    pd.DataFrame({"a": [1], "b": [2]}).to_excel(ruta_xlsx, index=False)
    assert len(importar_datos(ruta_xlsx)) == 1

    ruta_db = tmp_path / "prueba.sqlite"
    crear_bd(ruta_db, ["CREATE TABLE t (a INT)", "INSERT INTO t VALUES (1)"])
    assert len(importar_datos(ruta_db)) == 1


def test_importar_datos_extension_no_soportada(tmp_path):
    ruta = tmp_path / "notas.txt"
    ruta.write_text("hola", encoding="utf-8")
    with pytest.raises(ErrorImportacion, match="no está soportada"):
        importar_datos(ruta)
