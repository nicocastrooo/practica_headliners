class ErrorSeleccion(Exception):
    """Error al validar las columnas seleccionadas para el modelo."""


def validar_seleccion_columnas(df, entradas, salida):
    """Valida la selección de columnas (entradas y salida).

    Args:
        df: DataFrame de pandas con los datos.
        entradas: Lista de nombres de las columnas de entrada (features).
        salida: Nombre de la columna de salida (target).

    Raises:
        ErrorSeleccion: Si la selección no es válida.
    """
    pass  # Samuel aquí vas tu
