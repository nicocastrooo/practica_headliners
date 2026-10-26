import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd


class ErrorImportacion(Exception):
    """Error al importar un archivo de datos."""


def leer_sqlite(ruta):
    """Importa la única tabla de una base de datos SQLite.

    Args:
        ruta: ruta (str o Path) del archivo .sqlite o .db.

    Returns:
        DataFrame con el contenido de la tabla.

    Raises:
        ErrorImportacion: si el archivo no existe, está dañado, no
            contiene tablas, contiene más de una o la tabla está vacía.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorImportacion(f"El archivo no existe: {ruta}")

    # Modo solo lectura: evita que sqlite3 cree un archivo nuevo.
    # as_uri() codifica espacios, tildes y la ñ.
    uri = f"{ruta.resolve().as_uri()}?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True)) as conexion:
            tablas = [
                fila[0]
                for fila in conexion.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            if len(tablas) == 0:
                raise ErrorImportacion(
                    f"La base de datos no contiene ninguna tabla: {ruta}"
                )
            if len(tablas) > 1:
                raise ErrorImportacion(
                    f"La base de datos contiene {len(tablas)} tablas "
                    f"({', '.join(tablas)}) y solo se admite una: {ruta}"
                )
            datos = pd.read_sql_query(f'SELECT * FROM "{tablas[0]}"', conexion)
    except (sqlite3.DatabaseError, pd.errors.DatabaseError) as error:
        raise ErrorImportacion(
            f"El archivo está dañado o no es una base de datos SQLite: {ruta}"
        ) from error

    if datos.empty:
        raise ErrorImportacion(
            f"La tabla '{
                tablas[0]}' no contiene datos: {ruta}")
    return datos


EXTENSIONES_EXCEL = {
    ".xlsx": "openpyxl",
    ".xls": "xlrd",
}
EXTENSIONES_SQLITE = {".sqlite", ".db"}


def leer_csv(ruta):
    """Importa los datos de un archivo CSV.

    Args:
        ruta: ruta (str o Path) del archivo .csv.

    Returns:
        DataFrame con el contenido del archivo CSV.

    Raises:
        ErrorImportacion: si el archivo no existe, está dañado, su
            contenido no corresponde a un CSV o no contiene datos.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorImportacion(f"El archivo no existe: {ruta}")

    try:
        if b"\x00" in ruta.read_bytes():
            raise ErrorImportacion(
                f"El archivo está dañado o no es un archivo CSV: {ruta}"
            )
        datos = pd.read_csv(ruta)
    except ErrorImportacion:
        raise
    except pd.errors.EmptyDataError as error:
        raise ErrorImportacion(
            f"El archivo CSV no contiene datos: {ruta}"
        ) from error
    except (
        pd.errors.ParserError,
        UnicodeDecodeError,
        OSError,
        ValueError,
    ) as error:
        raise ErrorImportacion(
            f"El archivo está dañado o no es un archivo CSV: {ruta}"
        ) from error

    if datos.empty:
        raise ErrorImportacion(f"El archivo CSV no contiene datos: {ruta}")
    return datos


def leer_excel(ruta):
    """Importa los datos de un archivo Excel (.xlsx o .xls).

    Args:
        ruta: ruta (str o Path) del archivo .xlsx o .xls.

    Returns:
        DataFrame con el contenido del archivo Excel.

    Raises:
        ErrorImportacion: si el archivo no existe, la extensión no es de
            Excel, está dañado o no contiene datos.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorImportacion(f"El archivo no existe: {ruta}")

    extension = ruta.suffix.lower()
    motor = EXTENSIONES_EXCEL.get(extension)

    try:
        datos = pd.read_excel(ruta, engine=motor)
    except Exception as error:
        raise ErrorImportacion(
            f"El archivo está dañado o no es un archivo Excel: {ruta}"
        ) from error

    if datos.empty:
        raise ErrorImportacion(f"El archivo Excel no contiene datos: {ruta}")
    return datos


def importar_datos(ruta):
    """Importa datos desde un archivo CSV, Excel o SQLite según su extensión.

    Args:
        ruta: ruta (str o Path) del archivo a importar.

    Returns:
        DataFrame con los datos importados.

    Raises:
        ErrorImportacion: si el archivo no existe, la extensión no está
            soportada, el archivo está dañado o no contiene datos.
    """
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorImportacion(f"El archivo no existe: {ruta}")

    extension = ruta.suffix.lower()
    if extension == ".csv":
        return leer_csv(ruta)
    if extension in EXTENSIONES_EXCEL:
        return leer_excel(ruta)
    if extension in EXTENSIONES_SQLITE:
        return leer_sqlite(ruta)

    raise ErrorImportacion(
        f"La extensión '{ruta.suffix}' no está soportada: {ruta}"
    )
