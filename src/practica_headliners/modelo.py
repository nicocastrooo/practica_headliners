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
    cambios_sin_guardar: bool = False
    ruta_archivo: Optional[Path] = None  # Para saber de dónde se cargó o dónde se guardó

    def actualizar_descripcion(self, nueva_descripcion: str):
        """Actualiza la descripción del modelo en memoria y marca cambios pendientes.

        Args:
            nueva_descripcion: Nuevo texto de descripción (si es None se guarda vacío).
        """
        self.descripcion = (
            nueva_descripcion if nueva_descripcion is not None else ""
        )
        self.cambios_sin_guardar = True  # Modificar la descripción cuenta como cambio
        
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
        entrenamiento: DataFrame con los datos de entrenamiento.
        entradas: Lista con los nombres de las columnas de entrada (features).
        salida: Nombre de la columna de salida (target).

    Returns:
        Objeto ModeloLineal entrenado y marcado con cambios sin guardar.

    Raises:
        ErrorModelo: Si la selección no es válida, el conjunto está vacío
            o contiene valores inexistentes (NaN).
    """
    entradas = list(entradas)
    _comprobar(entrenamiento, entradas, salida, "entrenamiento")
    estimador = LinearRegression()
    estimador.fit(entrenamiento[entradas], entrenamiento[salida])
    modelo = ModeloLineal(estimador, entradas, salida)
    modelo.cambios_sin_guardar = True  # Un modelo recién creado no está guardado
    return modelo


def predecir(modelo, datos):
    """Devuelve las predicciones del modelo para las filas de un DataFrame.

    Args:
        modelo: Objeto ModeloLineal entrenado.
        datos: DataFrame que contiene las columnas de entrada del modelo.

    Returns:
        Array de NumPy con los valores predichos.

    Raises:
        ErrorModelo: Si faltan columnas de entrada o hay valores inexistentes.
    """
    faltan = [c for c in modelo.entradas if c not in datos.columns]
    if faltan:
        raise ErrorModelo(
            f"Faltan columnas de entrada: {', '.join(map(str, faltan))}."
        )
    if datos[modelo.entradas].isna().any().any():
        raise ErrorModelo("Hay valores inexistentes en las entradas.")
    return modelo.estimador.predict(datos[modelo.entradas])


def calcular_metricas(modelo, datos):
    """Calcula R² y ECM del modelo sobre un conjunto de datos.

    Args:
        modelo: Objeto ModeloLineal entrenado.
        datos: DataFrame con las columnas de entrada y salida.

    Returns:
        Diccionario con las claves 'r2' y 'ecm' (float).

    Raises:
        ErrorModelo: Si los datos no son válidos, están vacíos o tienen NaN.
    """
    _comprobar(datos, modelo.entradas, modelo.salida, "datos")
    real = datos[modelo.salida]
    predicho = modelo.estimador.predict(datos[modelo.entradas])
    r2 = r2_score(real, predicho) if len(datos) >= 2 else float("nan")
    return {
        "r2": float(r2),
        "ecm": float(mean_squared_error(real, predicho)),
    }


def evaluar_modelo(modelo, entrenamiento, test):
    """Calcula las métricas en entrenamiento y en test y las asocia al modelo.

    Args:
        modelo: Objeto ModeloLineal entrenado.
        entrenamiento: DataFrame de entrenamiento.
        test: DataFrame de test.

    Returns:
        Diccionario con las claves 'entrenamiento' y 'test', cada una con 'r2' y 'ecm'.

    Raises:
        ErrorModelo: Si alguno de los conjuntos no es válido o contiene NaN.
    """
    resultado = {
        "entrenamiento": calcular_metricas(modelo, entrenamiento),
        "test": calcular_metricas(modelo, test),
    }
    modelo.metricas = resultado
    return resultado


def generar_formula(modelo, decimales=DECIMALES):
    """Genera el texto legible de la fórmula matemática del modelo.

    Args:
        modelo: Objeto ModeloLineal entrenado.
        decimales: Número de decimales para redondear coeficientes e intercepto.

    Returns:
        Cadena de texto con la fórmula usando los nombres de las columnas.
    """
    texto = f"{modelo.salida} = "
    for i, (coef, nombre) in enumerate(
        zip(modelo.coeficientes, modelo.entradas)
    ):
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

    Args:
        modelo: Objeto ModeloLineal entrenado.
        ruta: Ruta de destino (str o Path). Si no termina en .joblib, se añade.
        metricas: Diccionario opcional de métricas (si no se pasa, usa modelo.metricas).

    Returns:
        Path absoluto del archivo guardado.

    Raises:
        ErrorModelo: Si el modelo no es válido, la ruta está vacía, faltan
            métricas o falla la escritura en disco.
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
                if modelo.descripcion is not None
                else ""
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
        modelo.cambios_sin_guardar = False
        modelo.ruta_archivo = ruta_destino.resolve()
    except Exception as error:
        raise ErrorModelo(
            f"No se pudo guardar el modelo en '{ruta_destino.name}'. "
            "Comprueba que tienes permisos de escritura y espacio disponible."
        ) from error

    return ruta_destino.resolve()


def realizar_prediccion(modelo, valores_entrada):
    """Calcula el valor predicho (Y) para una única observación nueva.

    Args:
        modelo: Objeto ModeloLineal o estimador entrenado.
        valores_entrada: Diccionario {columna: valor} o lista con los valores numéricos.

    Returns:
        Valor numérico predicho (float).

    Raises:
        ValueError: Si el modelo no está entrenado o el número de variables
            de entrada no coincide con el modelo.
    """
    if isinstance(valores_entrada, dict):
        if hasattr(modelo, "entradas"):
            x_valores = [valores_entrada[col] for col in modelo.entradas]
        else:
            x_valores = list(valores_entrada.values())
    else:
        x_valores = list(valores_entrada)

    estimador = modelo.estimador if hasattr(modelo, "estimador") else modelo

    if not hasattr(estimador, "coef_") or not hasattr(estimador, "intercept_"):
        raise ValueError(
            "El modelo proporcionado no es válido o no está entrenado."
        )

    coeficientes = np.array(estimador.coef_)
    x_array = np.array(x_valores)

    if len(coeficientes) != len(x_array):
        raise ValueError(
            "El número de variables de entrada no coincide con el modelo."
        )

    prediccion = np.dot(coeficientes, x_array) + estimador.intercept_

    return float(prediccion)

def cargar_modelo(ruta) -> ModeloLineal:
    """Carga un modelo guardado desde disco validando su estructura.

    Args:
        ruta: Ruta (str o Path) del archivo .joblib a cargar.

    Returns:
        Objeto ModeloLineal reconstruido con sus metadatos y métricas.

    Raises:
        ErrorModelo: Si el archivo no existe, está dañado, no tiene el formato
            esperado o le faltan campos obligatorios.
    """
    ruta_origen = Path(ruta)
    if not ruta_origen.exists():
        raise ErrorModelo(f"El archivo '{ruta_origen.name}' no existe.")

    try:
        contenido = joblib.load(ruta_origen)
    except Exception as error:
        raise ErrorModelo(f"El archivo '{ruta_origen.name}' está dañado o no es un modelo válido.") from error

    if not isinstance(contenido, dict) or "modelo" not in contenido or "metadata" not in contenido:
        raise ErrorModelo("El archivo no tiene la estructura de metadatos esperada.")

    meta = contenido["metadata"]
    try:
        modelo = ModeloLineal(
            estimador=contenido["modelo"],
            entradas=meta["entradas"],
            salida=meta["salida"],
            descripcion=meta.get("descripcion", ""),
            metricas=meta.get("metricas")
        )
        modelo.cambios_sin_guardar = False 
        modelo.ruta_archivo = ruta_origen.resolve()
        return modelo
    except KeyError as e:
        raise ErrorModelo(f"Faltan datos obligatorios en el archivo del modelo: {e}")
