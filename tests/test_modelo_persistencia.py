"""Pruebas unitarias de serialización, guardado, carga y privacidad del modelo."""

import joblib
import pandas as pd
import pytest

from practica_headliners.modelo import (
    ErrorModelo,
    entrenar_modelo,
    evaluar_modelo,
    generar_formula,
    guardar_modelo,
    cargar_modelo,
)


def _crear_modelo_prueba():
    """Crea un ModeloLineal entrenado y evaluado con datos sintéticos."""
    train = pd.DataFrame({
        "x1": [1.0, 2.0, 3.0, 4.0],
        "x2": [2.0, 1.0, 4.0, 3.0],
    })
    train["y"] = 2.5 * train["x1"] + 1.1 * train["x2"] + 1.0

    test = pd.DataFrame({
        "x1": [5.0, 6.0],
        "x2": [2.0, 5.0],
    })
    test["y"] = 2.5 * test["x1"] + 1.1 * test["x2"] + 1.0

    modelo = entrenar_modelo(train, ["x1", "x2"], "y")
    evaluar_modelo(modelo, train, test)
    modelo.actualizar_descripcion(
        "Test unitario de serialización y privacidad"
    )
    return modelo, train, test


def test_guardar_modelo_metadatos_y_privacidad(tmp_path):
    """Verifica que el archivo .joblib guarda los metadatos y no los datos."""
    archivo_prueba = tmp_path / "carpeta con espacios y ñ" / "modelo.joblib"
    archivo_prueba.parent.mkdir(parents=True, exist_ok=True)

    modelo, train, test = _crear_modelo_prueba()

    # Simulamos que alguien adjunta datos y gráficos al objeto en memoria
    modelo.dataset_completo = train
    modelo.df_entrenamiento = train
    modelo.df_test = test
    modelo.objeto_grafico = "<figura_matplotlib>"
    modelo.estimador.dataset_oculto = train

    ruta_guardada = guardar_modelo(modelo, archivo_prueba)
    assert ruta_guardada.is_file()
    assert ruta_guardada.suffix == ".joblib"

    datos_cargados = joblib.load(ruta_guardada)

    # 1. Estructura oficial de la HU #20
    assert set(datos_cargados.keys()) == {"modelo", "metadata"}

    estimador_cargado = datos_cargados["modelo"]
    metadata = datos_cargados["metadata"]

    # 2. Verificación de coeficientes, término independiente y metadatos
    assert pytest.approx(estimador_cargado.coef_, rel=1e-4) == [2.5, 1.1]
    assert pytest.approx(estimador_cargado.intercept_, rel=1e-4) == 1.0
    assert metadata["entradas"] == ["x1", "x2"]
    assert metadata["salida"] == "y"
    assert metadata["formula"] == generar_formula(modelo)
    assert metadata["descripcion"] == (
        "Test unitario de serialización y privacidad"
    )
    assert pytest.approx(
        metadata["metricas"]["entrenamiento"]["r2"], rel=1e-4
    ) == 1.0
    assert pytest.approx(
        metadata["metricas"]["test"]["ecm"], abs=1e-6
    ) == 0.0

    # 3. Control de privacidad: ni DataFrames ni gráficos están en el archivo
    assert "dataset_completo" not in datos_cargados
    assert "dataset_completo" not in metadata
    assert "objeto_grafico" not in datos_cargados
    assert "objeto_grafico" not in metadata
    assert not hasattr(estimador_cargado, "dataset_oculto")
    for valor in metadata.values():
        assert not isinstance(valor, pd.DataFrame)


def test_guardar_modelo_añade_extension_joblib(tmp_path):
    """Si la ruta no tiene extensión .joblib, se añade automáticamente."""
    modelo, _, _ = _crear_modelo_prueba()
    ruta_sin_ext = tmp_path / "mi_modelo"

    ruta_final = guardar_modelo(modelo, ruta_sin_ext)
    assert ruta_final.name == "mi_modelo.joblib"
    assert ruta_final.is_file()


def test_guardar_modelo_error_ruta_invalida(tmp_path):
    """Lanza ErrorModelo si ocurre un fallo al escribir en disco."""
    modelo, _, _ = _crear_modelo_prueba()
    ruta_inexistente = tmp_path / "no_existe" / "subcarpeta" / "modelo.joblib"

    with pytest.raises(ErrorModelo):
        guardar_modelo(modelo, ruta_inexistente)


def test_cargar_modelo_exitoso(tmp_path):
    """Verifica que un modelo guardado se carga correctamente conservando toda su información y predicciones."""
    archivo_prueba = tmp_path / "modelo_valido.joblib"
    modelo_orig, train, _ = _crear_modelo_prueba()
    
    guardar_modelo(modelo_orig, archivo_prueba)

    # Cargar el modelo
    modelo_cargado = cargar_modelo(archivo_prueba)

    # Verificar coeficientes e intercepción
    assert pytest.approx(modelo_cargado.estimador.coef_, rel=1e-4) == [2.5, 1.1]
    assert pytest.approx(modelo_cargado.estimador.intercept_, rel=1e-4) == 1.0

    # Verificar que produce las mismas predicciones
    pred_orig = modelo_orig.estimador.predict(train[["x1", "x2"]])
    pred_cargado = modelo_cargado.estimador.predict(train[["x1", "x2"]])
    assert pytest.approx(pred_orig, rel=1e-4) == pred_cargado


def test_cargar_archivo_dañado(tmp_path):
    """Lanza ErrorModelo si el archivo está corrupto o no es un joblib válido."""
    archivo_dañado = tmp_path / "dañado.joblib"
    archivo_dañado.write_text("contenido corrupto no serializado")

    with pytest.raises(ErrorModelo):
        cargar_modelo(archivo_dañado)


def test_cargar_archivo_incompleto(tmp_path):
    """Lanza ErrorModelo si al archivo le faltan claves obligatorias (modelo o metadata)."""
    archivo_incompleto = tmp_path / "incompleto.joblib"
    joblib.dump({"solo_modelo": "datos"}, archivo_incompleto)

    with pytest.raises(ErrorModelo):
        cargar_modelo(archivo_incompleto)


def test_flujo_completo_ciclo_vida(tmp_path):
    """
    Prueba el flujo completo con tmp_path:
    entrenar, guardar, cargar de nuevo, modificar descripción, guardar y volver a cargar;
    verificando que se conservan los cambios de descripción sin alterar los coeficientes.
    """
    archivo_path = tmp_path / "ciclo_vida.joblib"
    
    # 1. Crear y guardar
    modelo_orig, _, _ = _crear_modelo_prueba()
    guardar_modelo(modelo_orig, archivo_path)

    # 2. Cargar modelo
    modelo_cargado = cargar_modelo(archivo_path)
    
    # 3. Modificar descripción
    nueva_desc = "Descripción modificada en el modelo cargado"
    modelo_cargado.actualizar_descripcion(nueva_desc)
    assert modelo_cargado.metadata["descripcion"] == nueva_desc

    # 4. Guardar de nuevo con la nueva descripción
    guardar_modelo(modelo_cargado, archivo_path)

    # 5. Volver a cargar para verificar persistencia
    modelo_recargado = cargar_modelo(archivo_path)
    
    assert modelo_recargado.metadata["descripcion"] == nueva_desc
    assert pytest.approx(modelo_recargado.estimador.coef_, rel=1e-4) == modelo_orig.estimador.coef_
    assert pytest.approx(modelo_recargado.estimador.intercept_, rel=1e-4) == modelo_orig.estimador.intercept_