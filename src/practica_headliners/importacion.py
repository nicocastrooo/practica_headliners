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
        raise ErrorImportacion(f"La tabla '{tablas[0]}' no contiene datos: {ruta}")
    return datos