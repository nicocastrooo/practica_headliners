"""Pruebas unitarias de serialización, guardado y privacidad del modelo."""

import joblib

import pandas as pd

import pytest



from practica_headliners.modelo import (

    ErrorModelo,

    entrenar_modelo,

    evaluar_modelo,

    generar_formula,

    guardar_modelo,

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