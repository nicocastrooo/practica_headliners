import pytest
import pandas as pd
import numpy as np

from practica_headliners.preprocesado import (
    detectar_valores_inexistentes,
    tratar_valores_inexistentes,
    ErrorPreprocesado
)

def test_detectar_valores_inexistentes():
    df_train = pd.DataFrame({
        "A": [1, 2, np.nan],
        "B": [np.nan, np.nan, 3]
    })
    df_test = pd.DataFrame({
        "A": [np.nan, 4],
        "B": [5, 6]
    })
    
    resultado = detectar_valores_inexistentes(df_train, df_test, ["A", "B"])
    
    assert resultado["entrenamiento"]["A"] == 1
    assert resultado["entrenamiento"]["B"] == 2
    assert resultado["test"]["A"] == 1
    assert resultado["test"]["B"] == 0

def test_estrategia_eliminar_filas():
    df_train = pd.DataFrame({"A": [1, np.nan, 3], "B": [4, 5, 6]})
    df_test = pd.DataFrame({"A": [np.nan, 8, 9], "B": [10, 11, np.nan]})
    
    train_proc, test_proc, resumen = tratar_valores_inexistentes(
        df_train, df_test, ["A", "B"], "eliminar_filas"
    )
    
    assert len(train_proc) == 2
    assert len(test_proc) == 1
    assert resumen["entrenamiento"] == 1 # 1 fila eliminada
    assert resumen["test"] == 2 # 2 filas eliminadas

def test_eliminar_filas_conjunto_vacio_lanza_error():
    df_train = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df_test = pd.DataFrame({"A": [np.nan, np.nan], "B": [5, 6]})
    
    with pytest.raises(ErrorPreprocesado, match="vacío"):
        tratar_valores_inexistentes(df_train, df_test, ["A", "B"], "eliminar_filas")

def test_estrategia_media_aislamiento_test():
    df_train = pd.DataFrame({"A": [10, 20, np.nan]}) # Media de A en train es 15
    df_test = pd.DataFrame({"A": [100, np.nan]})     # Media de A en test es 100
    
    train_proc, test_proc, _ = tratar_valores_inexistentes(
        df_train, df_test, ["A"], "media"
    )
    
    # El NaN de test debe rellenarse con 15 (media de train), no con 100
    assert test_proc.loc[1, "A"] == 15.0
    assert train_proc.loc[2, "A"] == 15.0

def test_estrategia_mediana_aislamiento_test():
    df_train = pd.DataFrame({"A": [10, 100, 200, np.nan]}) # Mediana de A en train es 100
    df_test = pd.DataFrame({"A": [500, np.nan]})
    
    train_proc, test_proc, _ = tratar_valores_inexistentes(
        df_train, df_test, ["A"], "mediana"
    )
    
    assert test_proc.loc[1, "A"] == 100.0
    assert train_proc.loc[3, "A"] == 100.0

def test_estrategia_valor_constante():
    df_train = pd.DataFrame({"A": [1, np.nan]})
    df_test = pd.DataFrame({"A": [np.nan, 2]})
    
    train_proc, test_proc, resumen = tratar_valores_inexistentes(
        df_train, df_test, ["A"], "valor_constante", valor_constante=99.0
    )
    
    assert train_proc.loc[1, "A"] == 99.0
    assert test_proc.loc[0, "A"] == 99.0
    assert resumen["entrenamiento"] == 1 # 1 NaN rellenado

def test_valor_constante_no_numerico_lanza_error():
    df_train = pd.DataFrame({"A": [1, np.nan]})
    df_test = pd.DataFrame({"A": [np.nan, 2]})
    
    with pytest.raises(ErrorPreprocesado, match="numérico"):
        tratar_valores_inexistentes(
            df_train, df_test, ["A"], "valor_constante", valor_constante="texto"
        )