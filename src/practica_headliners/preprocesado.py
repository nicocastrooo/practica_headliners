import pandas as pd


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
    # Trabajamos sobre copias para no tocar los originales
    train_procesado = df_entrenamiento.copy()
    test_procesado = df_test.copy()

    # Contamos cuántos NaN hay antes de rellenar para el resumen de la GUI
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
        # REGLA CRÍTICA: Se calcula la media SOLO con entrenamiento
        valores_relleno = {
            col: train_procesado[col].mean() for col in columnas}

        train_procesado = train_procesado.fillna(value=valores_relleno)
        test_procesado = test_procesado.fillna(value=valores_relleno)

        resumen["entrenamiento"] = nulos_train
        resumen["test"] = nulos_test

    elif estrategia == "mediana":
        # REGLA CRÍTICA: Se calcula la mediana SOLO con entrenamiento
        valores_relleno = {
            col: train_procesado[col].median() for col in columnas}

        train_procesado = train_procesado.fillna(value=valores_relleno)
        test_procesado = test_procesado.fillna(value=valores_relleno)

        resumen["entrenamiento"] = nulos_train
        resumen["test"] = nulos_test

    elif estrategia == "valor_constante":
        # Validación estricta para asegurar que es numérico
        if valor_constante is None or isinstance(valor_constante, bool):
            raise ErrorPreprocesado(
                "Debe proporcionar un valor constante numérico.")

        try:
            valor_constante = float(valor_constante)
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
