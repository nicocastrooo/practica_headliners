import pandas as pd
import math


class ErrorPreprocesado(Exception):
    """Excepción personalizada para errores en el preprocesado de datos."""
    pass


def detectar_valores_inexistentes(df_entrenamiento, df_test, columnas):
    """
    Analiza las columnas seleccionadas en entrenamiento y test por separado.

    Args:
        df_entrenamiento: DataFrame con los datos de entrenamiento.
        df_test: DataFrame con los datos de test.
        columnas: Lista de nombres de las columnas a analizar (features + target).

    Returns:
        Un diccionario con el conteo exacto de NaN por columna en cada conjunto.
    """
    conteo_train = df_entrenamiento[columnas].isna().sum().to_dict()
    conteo_test = df_test[columnas].isna().sum().to_dict()

    return {
        "entrenamiento": conteo_train,
        "test": conteo_test
    }


def tratar_valores_inexistentes(
        df_entrenamiento, df_test, columnas, estrategia, valor_constante=None):
    """
    Aplica una estrategia de preprocesado evitando el Data Leakage.

    Args:
        df_entrenamiento: DataFrame de entrenamiento.
        df_test: DataFrame de test.
        columnas: Columnas sobre las que aplicar el preprocesado.
        estrategia: "eliminar_filas", "media", "mediana", "valor_constante".
        valor_constante: Valor numérico si la estrategia es "valor_constante".

    Returns:
        Tupla con (train_procesado, test_procesado, resumen_resultados).

    Raises:
        ErrorPreprocesado: Si la constante no es numérica o un conjunto queda vacío.
    """
    train_procesado = df_entrenamiento.copy()
    test_procesado = df_test.copy()

    nulos_train = int(train_procesado[columnas].isna().sum().sum())
    nulos_test = int(test_procesado[columnas].isna().sum().sum())
    resumen = {"entrenamiento": 0, "test": 0}

    if estrategia == "eliminar_filas":
        train_procesado = train_procesado.dropna(subset=columnas)
        test_procesado = test_procesado.dropna(subset=columnas)

        if train_procesado.empty or test_procesado.empty:
            raise ErrorPreprocesado(
                "La eliminación de filas dejaría el conjunto de entrenamiento o el de test vacío."
            )

        resumen["entrenamiento"] = len(df_entrenamiento) - len(train_procesado)
        resumen["test"] = len(df_test) - len(test_procesado)

    elif estrategia == "media":
        valores_relleno = {
            col: train_procesado[col].mean() for col in columnas}

        columnas_vacias = [
            col for col,
            val in valores_relleno.items() if pd.isna(val)]
        if columnas_vacias:
            raise ErrorPreprocesado(
                f"No se puede calcular la media porque las siguientes columnas están completamente "
                f"vacías en el conjunto de entrenamiento: {
                    ', '.join(columnas_vacias)}."
            )

        train_procesado = train_procesado.fillna(value=valores_relleno)
        test_procesado = test_procesado.fillna(value=valores_relleno)

        resumen["entrenamiento"] = nulos_train
        resumen["test"] = nulos_test

    elif estrategia == "mediana":
        valores_relleno = {
            col: train_procesado[col].median() for col in columnas}

        columnas_vacias = [
            col for col,
            val in valores_relleno.items() if pd.isna(val)]
        if columnas_vacias:
            raise ErrorPreprocesado(
                f"No se puede calcular la mediana porque las siguientes columnas están completamente "
                f"vacías en el conjunto de entrenamiento: {
                    ', '.join(columnas_vacias)}."
            )

        train_procesado = train_procesado.fillna(value=valores_relleno)
        test_procesado = test_procesado.fillna(value=valores_relleno)

        resumen["entrenamiento"] = nulos_train
        resumen["test"] = nulos_test

    elif estrategia == "valor_constante":
        if valor_constante is None or isinstance(valor_constante, bool):
            raise ErrorPreprocesado(
                "Debe proporcionar un valor constante numérico.")

        try:
            valor_constante = float(valor_constante)
            if not math.isfinite(valor_constante):
                raise ErrorPreprocesado(
                    "El valor constante debe ser un número finito (no 'nan' ni 'inf').")
        except (ValueError, TypeError):
            raise ErrorPreprocesado(
                "El valor constante introducido debe ser numérico.")

        valores_relleno = {col: valor_constante for col in columnas}

        train_procesado = train_procesado.fillna(value=valores_relleno)
        test_procesado = test_procesado.fillna(value=valores_relleno)

        resumen["entrenamiento"] = nulos_train
        resumen["test"] = nulos_test

    else:
        raise ErrorPreprocesado(f"La estrategia '{estrategia}' no es válida.")

    return train_procesado, test_procesado, resumen
