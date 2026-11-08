# Investigación sobre la Persistencia de Modelos

Como parte de la historia de usuario #20, se ha investigado cómo persistir modelos de regresión lineal y sus metadatos (fórmula, columnas, métricas y descripción). 

## 1. Comparativa de Métodos de Persistencia

Se han evaluado dos métodos de persistencia con diferentes enfoques: `joblib` (un estándar en el ecosistema scikit-learn que serializa objetos complejos) y `json` (formato de texto plano que requiere almacenamiento explícito de parámetros).

| Aspecto a Evaluar | `joblib` (Serialización binaria) | `json` (Almacenamiento de parámetros) |
| :--- | :--- | :--- |
| **Facilidad de uso** | **Muy alta**. Guarda y carga objetos Python enteros en una o dos líneas de código sin importar su complejidad interna. | **Baja**. Obliga a extraer manualmente los coeficientes (`coef_`), el término independiente (`intercept_`) y reconstruir el objeto del modelo al cargar. |
| **Tamaño y Legibilidad** | **Medio-Bajo**. Archivo binario optimizado para grandes arrays numéricos, pero totalmente ilegible para humanos. | **Variable**. Archivos de texto legibles y auditables, pero el tamaño se dispara drásticamente si se guardan matrices grandes. |
| **Seguridad** | **Riesgo Crítico**. Permite ejecución de código arbitrario al deserializar. | **Totalmente Seguro**. Solo parsea cadenas de texto y números; no ejecuta código nativo de Python. |
| **Compatibilidad** | **Baja-Media**. Altamente dependiente de las versiones de Python y `scikit-learn`. Cargar un modelo de una versión antigua suele fallar o requerir advertencias. | **Muy Alta**. Los parámetros matemáticos crudos (vectores y escalares) son universales e independientes del lenguaje o framework. |
| **Metadatos** | **Fácil**. Se puede guardar un diccionario contenedor con el objeto modelo y el resto de información (fórmula, columnas, etc.) directamente. | **Laborioso**. Se debe estructurar un diccionario anidado mapeando manualmente cada atributo y métrica para guardarlo como texto. |

## 2. Investigación de Seguridad en Serialización (`pickle` / `joblib`)

Tras consultar la [documentación oficial de Python sobre pickle](https://docs.python.org/3/library/pickle.html) y la [guía de persistencia de scikit-learn](https://scikit-learn.org/stable/model_persistence.html), se determina que `joblib` y `pickle` son inherentemente inseguros con archivos de origen desconocido.

**¿Por qué ocurre esto?**
El protocolo de `pickle` (usado internamente por `joblib`) no es un simple formato de almacenamiento de datos; es una máquina virtual de pila (*stack-based virtual machine*). Al utilizar la función `load()`, el sistema no se limita a inicializar objetos pasivamente, sino que ejecuta secuencias de instrucciones (opcodes) incrustadas en el archivo para reconstruir el estado. 

Un archivo manipulado maliciosamente puede incluir un opcode que instruya a `pickle` a utilizar el módulo `os` o `subprocess` del sistema para ejecutar comandos de consola silenciosamente, obteniendo control remoto o borrando datos en la máquina que abre el modelo.

## 3. Método Seleccionado y Justificación

**Método elegido:** `joblib`  
**Extensión de archivo:** `.joblib`

**Justificación:**
A pesar de sus riesgos de seguridad, se ha seleccionado `joblib` sobre `json` debido a que la aplicación actual tiene un alcance académico y el ahorro en complejidad técnica al guardar y recuperar el objeto completo de `scikit-learn` es indispensable. La facilidad para meter en un mismo archivo (usando un diccionario base) el modelo entrenado junto con la descripción, métricas y características supera el coste de desarrollo necesario para deconstruir y reconstruir el modelo matemáticamente en formato JSON.

Como mitigación del riesgo de seguridad, se ha documentado explícitamente en el manual y se asumirá como principio de uso cargar exclusivamente modelos generados por la propia aplicación o usuarios de total confianza.

## 4. Estructura de la Información

Para encapsular los metadatos y el modelo, guardaremos un único objeto `dict` en el archivo `.joblib` con los siguientes campos clave predefinidos (alineados con `modelo.py`):

```python
{
    "modelo": <objeto sklearn.linear_model.LinearRegression>,
    "metadata": {
        "descripcion": "Descripción textual del propósito del modelo",
        "entradas": ["feature_1", "feature_2"],
        "salida": "target_variable",
        "formula": "y = 1.2 * feature_1 + 2.5",
        "metricas": {
            "entrenamiento": {"r2": 0.85, "ecm": 0.12},
            "test": {"r2": 0.82, "ecm": 0.15}
        }
    }
}