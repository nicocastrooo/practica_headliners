import pytest
import json

def test_guardar_modelo_metadatos_y_privacidad(tmp_path):
    # Definimos la ruta temporal usando el fixture tmp_path de pytest
    archivo_prueba = tmp_path / "modelo_test.json"
    
    # 1. Simulamos un modelo que incluye metadatos y elementos prohibidos (datos y gráficos)
    modelo_ficticio = {
        "coeficientes": [2.5, 1.1],
        "termino_independiente": 1.0,
        "formula": "y = 2.5*x1 + 1.1*x2 + 1.0",
        "columnas_entrada": ["x1", "x2"],
        "columna_salida": "y",
        "metricas": {
            "R2_train": 0.88, 
            "ECM_train": 0.12, 
            "R2_test": 0.85, 
            "ECM_test": 0.15
        },
        "descripcion": "Test unitario de serialización y privacidad",
        "dataset_completo": [[1, 2], [3, 4]],  # Esto NO debe guardarse
        "objeto_grafico": "<figura_matplotlib>"  # Esto NO debe guardarse
    }

    # 2. Llamas a tu función de guardado (reemplaza 'guardar_modelo' por tu función real)
    # guardar_modelo(modelo_ficticio, archivo_prueba)
    
    # --- Simulación temporal para que veas cómo actuaría el filtro ---
    # (Si tu función ya filtra esto internamente, omite este bloque de simulación y usa solo tu función)
    datos_a_guardar = {
        k: v for k, v in modelo_ficticio.items() 
        if k not in ["dataset_completo", "objeto_grafico"]
    }
    with open(archivo_prueba, "w", encoding="utf-8") as f:
        json.dump(datos_a_guardar, f)
    # -------------------------------------------------------------

    # 3. Cargamos el archivo recién guardado para verificarlo
    with open(archivo_prueba, "r", encoding="utf-8") as f:
        datos_cargados = json.load(f)

    # 4. Aserciones (Asserts): Verificamos metadatos esperados
    assert datos_cargados["coeficientes"] == [2.5, 1.1]
    assert datos_cargados["formula"] == "y = 2.5*x1 + 1.1*x2 + 1.0"
    assert datos_cargados["columnas_entrada"] == ["x1", "x2"]
    assert datos_cargados["columna_salida"] == "y"
    assert datos_cargados["metricas"]["R2_train"] == 0.88
    assert datos_cargados["descripcion"] == "Test unitario de serialización y privacidad"

    # 5. Control de privacidad: Verificamos que los datos y gráficos NO están presentes
    assert "dataset_completo" not in datos_cargados
    assert "objeto_grafico" not in datos_cargados