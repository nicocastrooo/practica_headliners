"""Lógica del modelo de regresión lineal (independiente de la GUI)."""
from dataclasses import dataclass

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

    def actualizar_descripcion(self, nueva_descripcion: str):
        """Actualiza la descripción del modelo en memoria."""
        self.descripcion = nueva_descripcion if nueva_descripcion is not None else ""
    descripcion: str = ""

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
    """Calcula las métricas en entrenamiento y en test.

    Returns:
        {"entrenamiento": {"r2", "ecm"}, "test": {"r2", "ecm"}}

    Raises:
        ErrorModelo: igual que `calcular_metricas`.
    """
    return {
        "entrenamiento": calcular_metricas(modelo, entrenamiento),
        "test": calcular_metricas(modelo, test),
    }


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