"""PoC de persistencia: guarda y carga un modelo con joblib.

El archivo guarda un diccionario con el modelo y sus metadatos, con la
estructura definida en la documentación (tarea #127). Después se carga y
se comprueba que el modelo cargado predice igual que el original.

Uso:
    uv run python prototipos/poc_persistencia.py data/housing.csv \
        --entradas median_income housing_median_age \
        --salida median_house_value
"""
import argparse
import tempfile
from pathlib import Path

import joblib
import numpy as np

from practica_headliners.importacion import importar_datos
from practica_headliners.modelo import (
    entrenar_modelo, evaluar_modelo, generar_formula)
from practica_headliners.separacion import separar_datos


def guardar(ruta, modelo, train, test, descripcion):
    """Guarda el modelo y sus metadatos en un archivo .joblib."""
    contenido = {
        "modelo": modelo.estimador,
        "metadata": {
            "descripcion": descripcion,
            "entradas": modelo.entradas,
            "salida": modelo.salida,
            "formula": generar_formula(modelo),
            "metricas": evaluar_modelo(modelo, train, test),
        },
    }
    joblib.dump(contenido, ruta)


def cargar(ruta):
    """Carga el archivo y devuelve (estimador, metadata)."""
    contenido = joblib.load(ruta)
    return contenido["modelo"], contenido["metadata"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ruta")
    p.add_argument("--entradas", nargs="+", required=True)
    p.add_argument("--salida", required=True)
    p.add_argument("--descripcion",
                   default="Modelo de ejemplo de la prueba de concepto.")
    a = p.parse_args()

    # 1. Entrenar
    datos = importar_datos(a.ruta)
    datos = datos.dropna(subset=a.entradas + [a.salida])
    train, test = separar_datos(datos, 20, 42)
    modelo = entrenar_modelo(train, a.entradas, a.salida)

    with tempfile.TemporaryDirectory() as carpeta:
        archivo = Path(carpeta) / "modelo.joblib"

        # 2. Guardar
        guardar(archivo, modelo, train, test, a.descripcion)
        print(f"Archivo guardado: {archivo.name} "
              f"({archivo.stat().st_size} bytes)")

        # 3. Cargar y mostrar la información asociada
        estimador, info = cargar(archivo)
        print("\nInformación cargada:")
        print("  Descripción:", info["descripcion"])
        print("  Columnas de entrada:", info["entradas"])
        print("  Columna de salida:", info["salida"])
        print("  Fórmula:", info["formula"])
        for conjunto, valores in info["metricas"].items():
            print(f"  Métricas ({conjunto}):", valores)

        # 4. Comprobar que las predicciones coinciden
        original = modelo.estimador.predict(test[a.entradas])
        cargado = estimador.predict(test[info["entradas"]])
        print("\nDiferencia máxima entre predicciones:",
              float(np.max(np.abs(original - cargado))))
        print("¿Mismas predicciones?",
              "SÍ" if np.allclose(original, cargado) else "NO")


if __name__ == "__main__":
    main()
