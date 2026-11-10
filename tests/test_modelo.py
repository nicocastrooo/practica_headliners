"""Pruebas unitarias para la lógica y estructura del modelo lineal."""
import numpy as np
import pandas as pd
import pytest

from practica_headliners.modelo import (
    ErrorModelo,
    ModeloLineal,
    calcular_metricas,
    entrenar_modelo,
    evaluar_modelo,
    generar_formula,
    realizar_prediccion,
)


def _crear_datos_sinteticos():
    """Crea un DataFrame sintético simple para las pruebas."""
    return pd.DataFrame({
        "x1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [3.0, 5.0, 7.0, 9.0, 11.0],
    })


# --- TAREA #130: Pruebas unitarias de la estructura de descripción ---

def test_modelo_nuevo_tiene_descripcion_estrictamente_vacia():
    """Comprueba que al inicializar un modelo nuevo la descripción está vacía."""
    datos = _crear_datos_sinteticos()
    modelo = entrenar_modelo(datos, ["x1"], "y")

    assert isinstance(modelo.descripcion, str)
    assert modelo.descripcion == ""


def test_almacenar_descripcion_en_modelo():
    """Comprueba que el texto de la descripción se almacena en el objeto."""
    datos = _crear_datos_sinteticos()
    modelo = entrenar_modelo(datos, ["x1"], "y")

    texto = "Modelo para predecir el rendimiento en función de x1."
    modelo.descripcion = texto

    assert modelo.descripcion == texto


def test_sobrescribir_descripcion_en_modelo():
    """Comprueba que la descripción del modelo se puede sobrescribir."""
    datos = _crear_datos_sinteticos()
    modelo = entrenar_modelo(datos, ["x1"], "y")

    modelo.descripcion = "Descripción inicial del modelo."
    assert modelo.descripcion == "Descripción inicial del modelo."

    modelo.descripcion = "Descripción modificada tras revisar las métricas."
    assert modelo.descripcion == "Descripción modificada tras revisar las métricas."


def test_nuevo_modelo_reinicia_descripcion_vacia():
    """Comprueba que crear un segundo modelo no conserva la descripción anterior."""
    datos = _crear_datos_sinteticos()
    modelo_1 = entrenar_modelo(datos, ["x1"], "y")
    modelo_1.descripcion = "Descripción del primer modelo."

    modelo_2 = entrenar_modelo(datos, ["x1"], "y")

    assert modelo_1.descripcion == "Descripción del primer modelo."
    assert modelo_2.descripcion == ""


# --- Pruebas unitarias de entrenamiento, métricas y fórmula (#119) ---

def test_entrenar_modelo_devuelve_objeto_valido():
    """Verifica que el entrenamiento devuelve un ModeloLineal válido."""
    datos = _crear_datos_sinteticos()
    modelo = entrenar_modelo(datos, ["x1"], "y")

    assert isinstance(modelo, ModeloLineal)
    assert modelo.entradas == ["x1"]
    assert modelo.salida == "y"
    assert pytest.approx(modelo.coeficientes[0], rel=1e-4) == 2.0
    assert pytest.approx(modelo.intercepto, rel=1e-4) == 1.0


def test_calculo_metricas_sin_errores():
    """Verifica que los cálculos de R² y ECM funcionan en train y test."""
    train = _crear_datos_sinteticos()
    test = pd.DataFrame({
        "x1": [6.0, 7.0],
        "y": [13.0, 15.0],
    })
    modelo = entrenar_modelo(train, ["x1"], "y")

    metricas_train = calcular_metricas(modelo, train)
    assert pytest.approx(metricas_train["r2"], rel=1e-4) == 1.0
    assert pytest.approx(metricas_train["ecm"], abs=1e-6) == 0.0

    evaluacion = evaluar_modelo(modelo, train, test)
    assert "entrenamiento" in evaluacion
    assert "test" in evaluacion
    assert pytest.approx(evaluacion["test"]["r2"], rel=1e-4) == 1.0
    assert pytest.approx(evaluacion["test"]["ecm"], abs=1e-6) == 0.0


def test_formula_con_coeficiente_negativo():
    """Comprueba que la fórmula formatea coeficientes negativos sin '+ -'."""
    datos = pd.DataFrame({
        "x1": [1.0, 2.0, 3.0, 4.0],
        "x2": [1.0, 3.0, 2.0, 5.0],
    })
    datos["y"] = 2.0 * datos["x1"] - 1.5 * datos["x2"] + 10.0

    modelo = entrenar_modelo(datos, ["x1", "x2"], "y")
    formula = generar_formula(modelo, decimales=2)

    assert "+ -" not in formula
    assert "+-" not in formula
    assert "- 1.50 * x2" in formula
    assert formula == "y = 2.00 * x1 - 1.50 * x2 + 10.00"


def test_entrenar_modelo_con_nulos_lanza_error():
    """Verifica que entrenar con valores NaN lanza ErrorModelo."""
    datos = pd.DataFrame({
        "x1": [1.0, float("nan"), 3.0],
        "y": [2.0, 4.0, 6.0],
    })
    with pytest.raises(ErrorModelo):
        entrenar_modelo(datos, ["x1"], "y")


# --- TAREA #137: Pruebas unitarias de predicción matemática ---

def test_realizar_prediccion_matematica():
    """Comprueba que la predicción coincide con el cálculo manual a partir de la fórmula del modelo."""
    datos_prueba = pd.DataFrame({
        "x1": [1.0, 2.0, 3.0, 4.0],
        "x2": [2.0, 1.0, 4.0, 3.0],
        "y": [8.0, 9.0, 16.0, 17.0]
    })
    modelo = entrenar_modelo(datos_prueba, ["x1", "x2"], "y")
    
    valores_prueba = [2.0, 3.0]
    
    resultado_prediccion = realizar_prediccion(modelo, valores_prueba)
    
    calculo_manual = (modelo.coeficientes[0] * valores_prueba[0]) + (modelo.coeficientes[1] * valores_prueba[1]) + modelo.intercepto
    
    assert isinstance(resultado_prediccion, float)
    assert np.isclose(resultado_prediccion, calculo_manual)