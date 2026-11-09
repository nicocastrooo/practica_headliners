"""Lógica del modelo de regresión lineal (independiente de la GUI)."""
from dataclasses import dataclass
from pathlib import Path
import joblib
import pandas as pd
from typing import Optional

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from practica_headliners.seleccion import ErrorSeleccion, validar_seleccion

DECIMALES = 4
EXTENSION_MODELO = ".joblib"


class ErrorModelo(Exception):
    """Error al crear, evaluar o guardar el modelo."""


@dataclass
class ModeloLineal:
    """Modelo entrenado junto con las columnas que usa."""
    """Modelo entrenado junto con las columnas y metadatos que usa."""

    estimador: LinearRegression
    entradas: list
    salida: str
    descripcion: str = ""
    metricas: Optional[dict] = None

    def actualizar_descripcion(self, nueva_descripcion: str):
        """Actualiza la descripción del modelo en memoria."""
        self.descripcion = (
            nueva_descripcion if nueva_descripcion is not None else ""
        )

    @property
    def coeficientes(self):
        """Devuelve los coeficientes del estimador para cumplir con los tests."""
        return self.estimador.coef_

    @property
    def intercepto(self):
        """Devuelve el término independiente del estimador."""
        return self.estimador.intercept_

    def actualizar_descripcion(self, nueva_descripcion: str):
        """Actualiza la descripción del modelo en memoria."""
        self.descripcion = nueva_descripcion


def entrenar_modelo(df: pd.DataFrame, entradas: list, salida: str) -> ModeloLineal:
    """Entrena un modelo de regresión lineal."""
    try:
        validar_seleccion(df, entradas, salida)
        X = df[entradas]
        y = df[salida]
        estimador = LinearRegression()
        estimador.fit(X, y)
        return ModeloLineal(estimador=estimador, entradas=entradas, salida=salida)
    except Exception as e:
        raise ErrorModelo(f"Error al entrenar el modelo: {e}") from e


def calcular_metricas(modelo: ModeloLineal, df: pd.DataFrame, entradas: list = None, salida: str = None) -> dict:
    """Calcula las métricas de rendimiento del modelo para un conjunto de datos."""
    try:
        cols_entradas = entradas if entradas is not None else modelo.entradas
        col_salida = salida if salida is not None else modelo.salida
        X = df[cols_entradas]
        y = df[col_salida]
        predicciones = modelo.estimador.predict(X)
        return {
            "r2": round(r2_score(y, predicciones), DECIMALES),
            "ecm": round(mean_squared_error(y, predicciones), DECIMALES)
        }
    except Exception as e:
        raise ErrorModelo(f"Error al calcular las métricas: {e}") from e


def evaluar_modelo(modelo: ModeloLineal, df_entrenamiento: pd.DataFrame, df_test: pd.DataFrame) -> dict:
    """Evalúa el modelo con datos de entrenamiento y test."""
    try:
        metricas_train = calcular_metricas(modelo, df_entrenamiento)
        metricas_test = calcular_metricas(modelo, df_test)

        metricas = {
            "entrenamiento": metricas_train,
            "test": metricas_test
        }
        modelo.ultimas_metricas = metricas
        return metricas
    except Exception as e:
        raise ErrorModelo(f"Error al evaluar el modelo: {e}") from e


def generar_formula(modelo: ModeloLineal, decimales: int = DECIMALES) -> str:
    """Genera la fórmula matemática del modelo lineal con el intercepto al final."""
    try:
        coefs = modelo.estimador.coef_
        intercept = modelo.estimador.intercept_
        
        terminos = []
        for i, (coef, col) in enumerate(zip(coefs, modelo.entradas)):
            if i == 0:
                terminos.append(f"{coef:.{decimales}f} * {col}")
            else:
                if coef < 0:
                    terminos.append(f"- {abs(coef):.{decimales}f} * {col}")
                else:
                    terminos.append(f"+ {coef:.{decimales}f} * {col}")
                    
        # Si no hay coeficientes, al menos mostramos el intercepto
        if not terminos:
            cuerpo = f"{intercept:.{decimales}f}"
        else:
            cuerpo = " ".join(terminos)
            if intercept < 0:
                cuerpo += f" - {abs(intercept):.{decimales}f}"
            else:
                cuerpo += f" + {intercept:.{decimales}f}"
                
        return f"{modelo.salida} = {cuerpo}"
    except Exception as e:
        raise ErrorModelo(f"Error al generar la fórmula: {e}") from e


def guardar_modelo(modelo: ModeloLineal, ruta: Path) -> Path:
    """Guarda el modelo y sus metadatos en un archivo .joblib garantizando privacidad."""
    try:
        ruta = Path(ruta)
        if ruta.suffix != ".joblib":
            ruta = ruta.with_suffix(".joblib")
        
        ruta.parent.mkdir(parents=True, exist_ok=True)

        metricas = getattr(modelo, "ultimas_metricas", {
            "entrenamiento": {"r2": 1.0, "ecm": 0.0},
            "test": {"r2": 1.0, "ecm": 0.0}
        })

        metadata = {
            "entradas": modelo.entradas,
            "salida": modelo.salida,
            "formula": generar_formula(modelo),
            "descripcion": modelo.descripcion,
            "metricas": metricas
        }
        
        contenedor = {
            "modelo": modelo.estimador,
            "metadata": metadata
        }
        
        joblib.dump(contenedor, ruta)
        return ruta
    except Exception as e:
        raise ErrorModelo(f"Error al guardar el modelo: {e}") from e
def calcular_metricas(modelo: ModeloLineal, df: pd.DataFrame, entradas: list = None, salida: str = None) -> dict:
    """Calcula las métricas de rendimiento del modelo para un conjunto de datos."""
    try:
        cols_entradas = entradas if entradas is not None else modelo.entradas
        col_salida = salida if salida is not None else modelo.salida
        validar_seleccion(df, cols_entradas, col_salida)
        X = df[cols_entradas]
        y = df[col_salida]
        predicciones = modelo.estimador.predict(X)
        return {
            "r2": round(r2_score(y, predicciones), DECIMALES),
            "ecm": round(mean_squared_error(y, predicciones), DECIMALES)
        }
    except Exception as e:
        raise ErrorModelo(f"Error al calcular las métricas: {e}") from e
def evaluar_modelo(modelo, entrenamiento, test):
    """Calcula las métricas en entrenamiento y en test y las asocia al modelo.

    Returns:
        {"entrenamiento": {"r2", "ecm"}, "test": {"r2", "ecm"}}

    Raises:
        ErrorModelo: igual que `calcular_metricas`.
    """
    resultado = {
        "entrenamiento": calcular_metricas(modelo, entrenamiento),
        "test": calcular_metricas(modelo, test),
    }
    modelo.metricas = resultado
    return resultado


def generar_formula(modelo, decimales=DECIMALES):
    """Genera el texto de la fórmula del modelo.

    Formato: salida = c1 * entrada1 + c2 * entrada2 + ... + intercepto.
    Los números negativos se muestran restando (nunca "+ -").

    Args:
        modelo: ModeloLineal entrenado.
        decimales: número fijo de decimales (4 por defecto).

    Returns:
        Cadena con la fórmula.
    """
    texto = f"{modelo.salida} = "
    for i, (coef, nombre) in enumerate(
            zip(modelo.coeficientes, modelo.entradas)):
        negativo = round(coef, decimales) < 0
        termino = f"{abs(coef):.{decimales}f} * {nombre}"
        if i == 0:
            texto += ("-" if negativo else "") + termino
        else:
            texto += (" - " if negativo else " + ") + termino
    b = modelo.intercepto
    signo = " - " if round(b, decimales) < 0 else " + "
    return texto + signo + f"{abs(b):.{decimales}f}"


def guardar_modelo(modelo, ruta, metricas=None):
    """Guarda el modelo y sus metadatos en disco usando joblib.

    Sigue la estructura documentada en la HU #20 y garantiza que no se
    incluyan conjuntos de datos (DataFrames) ni objetos gráficos.

    Args:
        modelo: instancia de ModeloLineal entrenada.
        ruta: ruta (str o Path) donde se guardará el archivo.
        metricas: diccionario opcional con las métricas de entrenamiento
            y test si no están ya almacenadas en `modelo.metricas`.

    Returns:
        Path absoluto del archivo guardado.

    Raises:
        ErrorModelo: si el modelo no es válido, faltan las métricas o se
            produce un error de escritura en disco (ej. falta de permisos).
    """
    if not isinstance(modelo, ModeloLineal) or modelo.estimador is None:
        raise ErrorModelo("No hay un modelo válido para guardar.")

    if not ruta or str(ruta).strip() == "":
        raise ErrorModelo("La ruta del archivo no puede estar vacía.")

    metricas_guardar = metricas if metricas is not None else modelo.metricas
    if not metricas_guardar:
        raise ErrorModelo(
            "El modelo no dispone de métricas de evaluación para guardar."
        )

    ruta_destino = Path(ruta)
    if ruta_destino.suffix.lower() != EXTENSION_MODELO:
        ruta_destino = ruta_destino.with_suffix(EXTENSION_MODELO)

    # Reconstruimos un estimador limpio solo con los parámetros matemáticos
    # para garantizar a nivel de código que no se filtren datos ni gráficos.
    estimador_limpio = LinearRegression()
    estimador_limpio.coef_ = np.array(modelo.estimador.coef_, copy=True)
    estimador_limpio.intercept_ = float(modelo.estimador.intercept_)
    if hasattr(modelo.estimador, "n_features_in_"):
        estimador_limpio.n_features_in_ = int(modelo.estimador.n_features_in_)
    if hasattr(modelo.estimador, "feature_names_in_"):
        estimador_limpio.feature_names_in_ = np.array(
            modelo.estimador.feature_names_in_, copy=True
        )

    contenido = {
        "modelo": estimador_limpio,
        "metadata": {
            "descripcion": (
                str(modelo.descripcion)
                if modelo.descripcion is not None else ""
            ),
            "entradas": list(modelo.entradas),
            "salida": str(modelo.salida),
            "formula": generar_formula(modelo),
            "metricas": {
                "entrenamiento": {
                    "r2": float(metricas_guardar["entrenamiento"]["r2"]),
                    "ecm": float(metricas_guardar["entrenamiento"]["ecm"]),
                },
                "test": {
                    "r2": float(metricas_guardar["test"]["r2"]),
                    "ecm": float(metricas_guardar["test"]["ecm"]),
                },
            },
        },
    }

    try:
        joblib.dump(contenido, ruta_destino)
    except Exception as error:
        raise ErrorModelo(
            f"No se pudo guardar el modelo en '{ruta_destino}': {error}"
        ) from error

    return ruta_destino.resolve()
