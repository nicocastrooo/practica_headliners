import pandas as pd

class ErrorSeparacion(Exception):
    """Excepción personalizada para errores en la separación de datos."""
    pass

def separar_datos(df: pd.DataFrame, porcentaje_test: float = 20.0, semilla: int = 42):
    """
    Divide un DataFrame en conjuntos de entrenamiento y test.

    Args:
        df: DataFrame original.
        porcentaje_test: Porcentaje de datos para test (entre 1 y 99).
        semilla: Semilla para la generación aleatoria (debe ser entero).

    Returns:
        Tupla con (df_entrenamiento, df_test).
    """
    # 1. Validación de filas mínimas
    if len(df) < 5:
        raise ErrorSeparacion("El dataset debe tener al menos 5 filas para poder separarlo.")

    # 2. Validación del porcentaje
    if not isinstance(porcentaje_test, (int, float)) or not (1 <= porcentaje_test <= 99):
        raise ErrorSeparacion("El porcentaje de test debe ser un número entre 1 y 99.")

    # 3. Validación de la semilla
    if not isinstance(semilla, int):
        raise ErrorSeparacion("La semilla debe ser un número entero.")

    # Cálculo exacto de filas solucionando el error de coma flotante detectado en tests
    num_test = int(round(len(df) * (porcentaje_test / 100.0)))
    num_train = len(df) - num_test

    # 4. Validación de conjuntos vacíos
    if num_train == 0 or num_test == 0:
        raise ErrorSeparacion(
            f"Con un {porcentaje_test}% de test, alguno de los conjuntos quedaría vacío. "
            f"Filas calculadas -> Entrenamiento: {num_train}, Test: {num_test}."
        )

    # Separación aleatoria y reproducible
    df_test = df.sample(n=num_test, random_state=semilla)
    df_entrenamiento = df.drop(df_test.index)

    return df_entrenamiento, df_test