import pandas as pd


class ErrorSeleccion(Exception):
    """Error en la selección de columnas de entrada y salida."""


def validar_seleccion(datos, entradas, salida):
    """Valida la selección de columnas para un modelo de regresión lineal.

    Args:
        datos: DataFrame con el dataset cargado.
        entradas: lista con los nombres de las columnas de entrada.
        salida: nombre de la columna de salida (o None si no hay).

    Raises:
        ErrorSeleccion: si falta alguna selección, alguna columna no
            existe, la salida también está en las entradas o alguna
            columna seleccionada no es numérica.
    """
    entradas = list(entradas) if entradas is not None else []
    hay_salida = salida is not None and salida != ""

    if not entradas and not hay_salida:
        raise ErrorSeleccion(
            "Falta seleccionar al menos una columna de entrada y "
            "una columna de salida."
        )
    if not entradas:
        raise ErrorSeleccion(
            "Falta seleccionar al menos una columna de entrada.")
    if not hay_salida:
        raise ErrorSeleccion("Falta seleccionar la columna de salida.")

    seleccionadas = entradas + [salida]
    inexistentes = [c for c in seleccionadas if c not in datos.columns]
    if inexistentes:
        raise ErrorSeleccion(
            "Las siguientes columnas no existen en el dataset: "
            f"{', '.join(map(str, inexistentes))}."
        )

    if salida in entradas:
        raise ErrorSeleccion(
            f"La columna '{salida}' no puede ser a la vez entrada y salida."
        )

    no_numericas = [
        c for c in dict.fromkeys(seleccionadas)
        if not pd.api.types.is_numeric_dtype(datos[c])
        or pd.api.types.is_bool_dtype(datos[c])
    ]
    if no_numericas:
        raise ErrorSeleccion(
            "Las siguientes columnas no son numéricas y no se pueden "
            f"usar en regresión lineal: {', '.join(map(str, no_numericas))}."
        )