def test_simulacion_fallo_ci():
    # Prueba destinada a fallar a propósito para verificar el pipeline
    assert 1 == 2, "Fallo provocado intencionadamente para verificar GitHub Actions"