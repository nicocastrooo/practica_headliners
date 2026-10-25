import pandas as pd
import pytest

from practica_headliners.separacion import ErrorSeparacion, separar_datos


def crear_datos(filas):
    return pd.DataFrame({
        "x": range(filas),
        "y": [2 * i for i in range(filas)],
    })


@pytest.mark.parametrize(
    "filas, porcentaje, esperado_test",
    [
        (100, 20, 20),
        (100, 25, 25),
        (100, 29, 29),
        (100, 50, 50),
        (10, 30, 3),
        (100, 12.5, 12),
    ],
)
def test_tamanos_segun_porcentaje(filas, porcentaje, esperado_test):
    entrenamiento, test = separar_datos(crear_datos(filas), porcentaje, 42)
    assert len(test) == esperado_test
    assert len(entrenamiento) == filas - esperado_test


@pytest.mark.parametrize("porcentaje", range(1, 100))
def test_tamano_test_exacto_en_100_filas(porcentaje):
    _, test = separar_datos(crear_datos(100), porcentaje, 42)
    assert len(test) == porcentaje


def test_valores_por_defecto_80_20():
    entrenamiento, test = separar_datos(crear_datos(100))
    assert len(entrenamiento) == 80
    assert len(test) == 20


def test_ninguna_fila_en_ambos_conjuntos():
    entrenamiento, test = separar_datos(crear_datos(50), 20, 42)
    assert set(entrenamiento.index).isdisjoint(set(test.index))


def test_los_conjuntos_cubren_todo_el_dataset():
    datos = crear_datos(50)
    entrenamiento, test = separar_datos(datos, 20, 42)
    assert set(entrenamiento.index) | set(test.index) == set(datos.index)


def test_misma_semilla_misma_separacion():
    datos = crear_datos(100)
    entr1, test1 = separar_datos(datos, 20, 7)
    entr2, test2 = separar_datos(datos, 20, 7)
    pd.testing.assert_frame_equal(entr1, entr2)
    pd.testing.assert_frame_equal(test1, test2)


def test_distinta_semilla_distinta_separacion():
    datos = crear_datos(100)
    _, test1 = separar_datos(datos, 20, 1)
    _, test2 = separar_datos(datos, 20, 2)
    assert list(test1.index) != list(test2.index)


def test_no_modifica_el_dataset_original():
    datos = crear_datos(20)
    copia = datos.copy()
    separar_datos(datos, 20, 42)
    pd.testing.assert_frame_equal(datos, copia)


@pytest.mark.parametrize("porcentaje", [0, -5, 100, 150])
def test_porcentaje_fuera_de_rango(porcentaje):
    with pytest.raises(ErrorSeparacion, match="porcentaje"):
        separar_datos(crear_datos(100), porcentaje, 42)


@pytest.mark.parametrize("porcentaje", ["abc", None])
def test_porcentaje_no_numerico(porcentaje):
    with pytest.raises(ErrorSeparacion, match="porcentaje"):
        separar_datos(crear_datos(100), porcentaje, 42)


@pytest.mark.parametrize("semilla", ["abc", 1.5, None])
def test_semilla_no_entera(semilla):
    with pytest.raises(ErrorSeparacion, match="semilla"):
        separar_datos(crear_datos(100), 20, semilla)


@pytest.mark.parametrize("filas", [0, 1, 4])
def test_dataset_con_menos_de_5_filas(filas):
    with pytest.raises(ErrorSeparacion, match="5 filas"):
        separar_datos(crear_datos(filas), 20, 42)


@pytest.mark.parametrize("filas, porcentaje", [(5, 1), (10, 4)])
def test_porcentaje_bajo_deja_test_vacio(filas, porcentaje):
    with pytest.raises(ErrorSeparacion, match="vacío"):
        separar_datos(crear_datos(filas), porcentaje, 42)


@pytest.mark.parametrize("filas, porcentaje", [(5, 99), (10, 96)])
def test_porcentaje_alto_deja_entrenamiento_vacio(filas, porcentaje):
    with pytest.raises(ErrorSeparacion, match="vacío"):
        separar_datos(crear_datos(filas), porcentaje, 42)
