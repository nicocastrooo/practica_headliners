from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

EXTENSION_MODELO = ".joblib"


class ErrorModelo(Exception):
    """Excepción personalizada para errores relacionados con el modelo."""
    pass


class ModeloLineal:
    def __init__(self, modelo_sklearn, entradas, salida):
        self.estimador = modelo_sklearn
        self.modelo = modelo_sklearn
        self.entradas = entradas
        self.salida = salida
        self.descripcion = ""
        self.metadata = {}

    @property
    def coeficientes(self):
        """Devuelve los coeficientes de la regresión lineal de scikit-learn."""
        return self.estimador.coef_

    @property
    def intercepto(self):
        """Devuelve el término independiente (intercepto) de la regresión."""
        return self.estimador.intercept_

    def actualizar_descripcion(self, texto: str):
        """Actualiza la descripción interna y la metainformación del modelo."""
        self.descripcion = texto
        self.metadata["descripcion"] = texto


def entrenar_modelo(df: pd.DataFrame, entradas: list, salida: str) -> ModeloLineal:
    """Entrena un modelo de regresión lineal con los datos y variables indicadas."""
    if df[entradas + [salida]].isna().any().any():
        raise ErrorModelo("El conjunto de datos contiene valores nulos (NaN).")

    X = df[entradas]
    y = df[salida]

    reg = LinearRegression()
    reg.fit(X, y)

    modelo = ModeloLineal(reg, entradas, salida)
    return modelo


def evaluar_modelo(modelo: ModeloLineal, df_train: pd.DataFrame, df_test: pd.DataFrame) -> dict:
    """Evalúa el modelo calculando R² y ECM para entrenamiento y test."""
    try:
        X_train = df_train[modelo.entradas]
        y_train = df_train[modelo.salida]
        pred_train = modelo.estimador.predict(X_train)

        r2_train = r2_score(y_train, pred_train)
        ecm_train = mean_squared_error(y_train, pred_train)

        X_test = df_test[modelo.entradas]
        y_test = df_test[modelo.salida]
        pred_test = modelo.estimador.predict(X_test)

        r2_test = r2_score(y_test, pred_test)
        ecm_test = mean_squared_error(y_test, pred_test)

        metricas = {
            "entrenamiento": {"r2": float(r2_train), "ecm": float(ecm_train)},
            "test": {"r2": float(r2_test), "ecm": float(ecm_test)}
        }
        modelo.metadata["metricas"] = metricas
        return metricas
    except Exception as e:
        raise ErrorModelo(f"Error al evaluar el modelo: {e}")


def calcular_metricas(modelo: ModeloLineal, df_datos: pd.DataFrame, df_test: pd.DataFrame = None) -> dict:
    """Calcula y devuelve las métricas para compatibilidad con las pruebas unitarias."""
    evals = evaluar_modelo(modelo, df_datos, df_test if df_test is not None else df_datos)
    if df_test is None and isinstance(evals, dict) and "entrenamiento" in evals:
        return evals["entrenamiento"]
    return evals.get("entrenamiento", evals)


def generar_formula(modelo: ModeloLineal, decimales: int = None) -> str:
    """Genera la fórmula matemática del modelo formateada como texto."""
    coefs = modelo.coeficientes
    intercepto = modelo.intercepto

    terminos = []
    for i, (c, feat) in enumerate(zip(coefs, modelo.entradas)):
        if decimales is not None:
            val_str = f"{abs(c):.{decimales}f}"
        else:
            val_str = f"{abs(c)}"

        if i == 0:
            if c < 0:
                terminos.append(f"- {val_str} * {feat}")
            else:
                terminos.append(f"{val_str} * {feat}")
        else:
            if c < 0:
                terminos.append(f"- {val_str} * {feat}")
            else:
                terminos.append(f"+ {val_str} * {feat}")

    if decimales is not None:
        inter_str = f"{abs(intercepto):.{decimales}f}"
    else:
        inter_str = f"{abs(intercepto)}"

    formula = f"{modelo.salida} = " + " ".join(terminos)
    if intercepto >= 0:
        formula += f" + {inter_str}"
    else:
        formula += f" - {inter_str}"

    modelo.metadata["formula"] = formula
    return formula


def realizar_prediccion(modelo: ModeloLineal, valores: list) -> float:
    """Realiza una predicción matemática numérica para una lista de valores de entrada."""
    try:
        pred = sum(c * v for c, v in zip(modelo.coeficientes, valores)) + modelo.intercepto
        return float(pred)
    except Exception as e:
        raise ErrorModelo(f"Error al realizar la predicción: {e}")


def guardar_modelo(modelo: ModeloLineal, ruta: Path) -> Path:
    """Serializa y guarda el diccionario estructurado (modelo y metadatos) en disco."""
    try:
        destino = Path(ruta)
        if destino.suffix.lower() != EXTENSION_MODELO:
            destino = destino.with_name(destino.name + EXTENSION_MODELO)

        formula = generar_formula(modelo)
        metricas = modelo.metadata.get("metricas", {})

        metadata = {
            "entradas": modelo.entradas,
            "salida": modelo.salida,
            "formula": formula,
            "descripcion": modelo.descripcion,
            "metricas": metricas,
        }

        import copy
        estimador_limpio = copy.copy(modelo.estimador)
        if hasattr(estimador_limpio, "dataset_oculto"):
            delattr(estimador_limpio, "dataset_oculto")

        datos_a_guardar = {
            "modelo": estimador_limpio,
            "metadata": metadata,
        }

        joblib.dump(datos_a_guardar, destino)
        return destino
    except Exception as e:
        raise ErrorModelo(f"No se pudo guardar el modelo: {e}")


def cargar_modelo(ruta: Path) -> ModeloLineal:
    """Carga el archivo desde disco y reconstruye y devuelve un objeto ModeloLineal."""
    try:
        ruta_path = Path(ruta)
        if not ruta_path.exists():
            raise ErrorModelo(f"El archivo {ruta_path} no existe.")
        
        contenido = joblib.load(ruta_path)
        
        if isinstance(contenido, ModeloLineal):
            return contenido
            
        if isinstance(contenido, dict) and "modelo" in contenido and "metadata" in contenido:
            estimador = contenido["modelo"]
            metadata = contenido["metadata"]
            entradas = metadata.get("entradas", [])
            salida = metadata.get("salida", "")
            
            modelo = ModeloLineal(estimador, entradas, salida)
            modelo.metadata = metadata
            modelo.descripcion = metadata.get("descripcion", "")
            return modelo
            
        raise ErrorModelo("El archivo no contiene un formato de modelo válido.")
    except Exception as e:
        if isinstance(e, ErrorModelo):
            raise e
        raise ErrorModelo(f"El archivo está dañado o no se pudo cargar correctamente: {e}")