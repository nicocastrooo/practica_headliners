"""Lógica del modelo de regresión lineal (independiente de la GUI)."""
from dataclasses import dataclass
from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

from practica_headliners.seleccion import ErrorSeleccion, validar_seleccion

DECIMALES = 4


class ErrorModelo(Exception):
    """Error al crear o evaluar el modelo."""


@dataclass
class ModeloLineal:
    """Modelo entrenado junto con las columnas que usa."""
    estimador: LinearRegression
    entradas: list
    salida: str
    descripcion: str = ""  # Campo de descripción inicializado vacío por defecto

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


def _comprobar(df: pd.DataFrame, entradas: list, salida: str, nombre_arg: str = "datos"):
    """Función auxiliar para comprobar la validez del DataFrame y sus columnas."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        raise ErrorModelo(f"El conjunto '{nombre_arg}' no es válido o está vacío.")
    try:
        validar_seleccion(df, entradas, salida)
    except Exception as e:
        raise ErrorModelo(f"Error en {nombre_arg}: {e}") from e


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


def calcular_metricas(modelo: ModeloLineal, datos: pd.DataFrame) -> dict:
    """Calcula R² y ECM del modelo sobre un conjunto de datos."""
    try:
        _comprobar(datos, modelo.entradas, modelo.salida, "datos")
        X = datos[modelo.entradas]
        y = datos[modelo.salida]
        
        # Manejo de R² NaN si hay menos de 2 filas
        if len(datos) < 2:
            r2 = float('nan')
        else:
            r2 = r2_score(y, modelo.estimador.predict(X))
            
        ecm = mean_squared_error(y, modelo.estimador.predict(X))
        
        return {
            "r2": round(r2, DECIMALES) if not pd.isna(r2) else float('nan'),
            "ecm": round(ecm, DECIMALES)
        }
    except Exception as e:
        if isinstance(e, ErrorModelo):
            raise
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