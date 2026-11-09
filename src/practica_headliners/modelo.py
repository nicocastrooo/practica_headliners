"""Lógica del modelo de regresión lineal (independiente de la GUI)."""
from dataclasses import dataclass
from pathlib import Path
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
        return [float(c) for c in self.estimador.coef_]

    @property
    def intercepto(self):
        return float(self.estimador.intercept_)


def _comprobar(datos, entradas, salida, conjunto):
    """Comprueba que el conjunto sirve para entrenar o evaluar."""
    try:
        validar_seleccion(datos, entradas, salida)
    except ErrorSeleccion as error:
        raise ErrorModelo(str(error)) from error
    if len(datos) == 0:
        raise ErrorModelo(f"El conjunto de {conjunto} está vacío.")
    columnas = list(entradas) + [salida]
    if datos[columnas].isna().any().any():
        raise ErrorModelo(
            f"El conjunto de {conjunto} tiene valores inexistentes en las "
            "columnas seleccionadas. Aplica antes el preprocesado."
        )


def entrenar_modelo(entrenamiento, entradas, salida):
    """Ajusta un modelo de regresión lineal con el conjunto de entrenamiento.

    Args:
        entrenamiento: DataFrame de entrenamiento.
        entradas: lista con los nombres de las columnas de entrada.
        salida: nombre de la columna de salida.

    Returns:
        ModeloLineal entrenado únicamente con `entrenamiento`.

    Raises:
        ErrorModelo: si la selección no es válida, el conjunto está vacío
            o quedan valores inexistentes en las columnas seleccionadas.
    """
    entradas = list(entradas)
    _comprobar(entrenamiento, entradas, salida, "entrenamiento")
    estimador = LinearRegression()
    estimador.fit(entrenamiento[entradas], entrenamiento[salida])
    return ModeloLineal(estimador, entradas, salida)


def predecir(modelo, datos):
    """Devuelve las predicciones del modelo para las filas de `datos`.

    Args:
        modelo: ModeloLineal entrenado.
        datos: DataFrame con, al menos, las columnas de entrada del modelo.

    Returns:
        Array de NumPy con un valor predicho por fila.

    Raises:
        ErrorModelo: si faltan columnas o hay valores inexistentes.
    """
    faltan = [c for c in modelo.entradas if c not in datos.columns]
    if faltan:
        raise ErrorModelo(
            f"Faltan columnas de entrada: {', '.join(map(str, faltan))}.")
    if datos[modelo.entradas].isna().any().any():
        raise ErrorModelo("Hay valores inexistentes en las entradas.")
    return modelo.estimador.predict(datos[modelo.entradas])


def calcular_metricas(modelo, datos):
    """Calcula R² y ECM del modelo sobre un conjunto de datos.

    Args:
        modelo: ModeloLineal entrenado.
        datos: DataFrame (entrenamiento o test) con entradas y salida.

    Returns:
        Diccionario {"r2": float, "ecm": float}. El R² es NaN si el
        conjunto tiene menos de 2 filas, porque no está definido.

    Raises:
        ErrorModelo: si el conjunto está vacío, no tiene las columnas o
            tiene valores inexistentes.
    """
    _comprobar(datos, modelo.entradas, modelo.salida, "datos")
    real = datos[modelo.salida]
    predicho = modelo.estimador.predict(datos[modelo.entradas])
    r2 = r2_score(real, predicho) if len(datos) >= 2 else float("nan")
    return {"r2": float(r2),
            "ecm": float(mean_squared_error(real, predicho))}


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

    metricas_guardar = (
        metricas if metricas is not None else getattr(modelo, "metricas", None)
    )
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
