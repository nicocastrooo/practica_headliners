import pandas as pd
import pytest

from practica_headliners.seleccion import (
    ErrorSeleccion,
    validar_seleccion_columnas,
)


@pytest.fixture
def df_prueba():
    """Crea un DataFrame sintético en memoria para las pruebas."""
    return pd.DataFrame({
        "var_x1": [1.5, 2.5, 3.5],
        "var_x2": [10, 20, 30],
        "var_y": [100.0, 200.0, 300.0],
        "texto": ["a", "b", "c"],
        "categorica": pd.Categorical(["A", "B", "A"]),
    })


def test_seleccion_valida_regresion_simple(df_prueba):
    # Regresión simple: 1 entrada y 1 salida numéricas. No debe dar error.
    validar_seleccion_columnas(df_prueba, ["var_x1"], "var_y")


def test_seleccion_valida_regresion_multiple(df_prueba):
    # Regresión múltiple: varias entradas y 1 salida. No debe dar error.
    validar_seleccion_columnas(df_prueba, ["var_x1", "var_x2"], "var_y")


def test_error_seleccion_vacia(df_prueba):
    # Error al dejar vacía la selección de entradas
    with pytest.raises(ErrorSeleccion, match="entrada"):
        validar_seleccion_columnas(df_prueba, [], "var_y")

    # Error al dejar vacía la selección de salida
    with pytest.raises(ErrorSeleccion, match="salida"):
        validar_seleccion_columnas(df_prueba, ["var_x1"], None)


def test_error_salida_en_entradas(df_prueba):
    # Error al usar la misma columna como entrada y salida
    with pytest.raises(ErrorSeleccion, match="var_x1"):
        validar_seleccion_columnas(df_prueba, ["var_x1", "var_x2"], "var_x1")


def test_error_columna_no_numerica(df_prueba):
    # Error porque una de las entradas es de texto
    with pytest.raises(ErrorSeleccion, match="texto"):
        validar_seleccion_columnas(df_prueba, ["var_x1", "texto"], "var_y")

    # Error porque la salida es una variable categórica
    with pytest.raises(ErrorSeleccion, match="categorica"):
        validar_seleccion_columnas(df_prueba, ["var_x1"], "categorica")