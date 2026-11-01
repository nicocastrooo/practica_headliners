"""Prueba de concepto: regresión lineal con scikit-learn, sin GUI.

Uso:
    uv run python prototipos/poc_regresion.py data/archivo.csv \
        --entradas x1 x2 --salida y [--test 20] [--semilla 42]
"""
import argparse

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from practica_headliners.importacion import importar_datos
from practica_headliners.separacion import separar_datos


def formula(modelo, entradas, salida):
    terminos = " + ".join(
        f"{c:.4f} * {n}" for c, n in zip(modelo.coef_, entradas))
    return f"{salida} = {terminos} + {modelo.intercept_:.4f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ruta")
    p.add_argument("--entradas", nargs="+", required=True)
    p.add_argument("--salida", required=True)
    p.add_argument("--test", type=float, default=20.0)
    p.add_argument("--semilla", type=int, default=42)
    a = p.parse_args()

    # 1. Cargar
    datos = importar_datos(a.ruta)
    columnas = a.entradas + [a.salida]
    datos = datos.dropna(subset=columnas)  # la PoC no preprocesa

    # 2. Separar
    train, test = separar_datos(datos, a.test, a.semilla)
    print(f"Filas: entrenamiento={len(train)}, test={len(test)}")

    # 3. Entrenar
    modelo = LinearRegression()
    modelo.fit(train[a.entradas], train[a.salida])

    # 4. Coeficientes y fórmula
    for n, c in zip(a.entradas, modelo.coef_):
        print(f"Coeficiente de {n}: {c:.6f}")
    print(f"Término independiente: {modelo.intercept_:.6f}")
    print("Fórmula:", formula(modelo, a.entradas, a.salida))

    # 5. Métricas
    for nombre, conj in (("entrenamiento", train), ("test", test)):
        real = conj[a.salida]
        pred = modelo.predict(conj[a.entradas])
        print(f"{nombre}: ECM={mean_squared_error(real, pred):.6f}  "
              f"R2={r2_score(real, pred):.6f}")

    # 6. Predicción con un valor nuevo (la media de cada entrada)
    nuevo = train[a.entradas].mean().to_frame().T
    print("Predicción para", nuevo.iloc[0].to_dict(), "->",
          float(modelo.predict(nuevo)[0]))


if __name__ == "__main__":
    main()
