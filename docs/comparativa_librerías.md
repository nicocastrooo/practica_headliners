# Investigación y Comparativa de Librerías para Regresión Lineal

## 1. Introducción
Este documento recopila la investigación realizada para seleccionar la librería de Python que se utilizará en la creación de modelos de regresión lineal (simple y múltiple) para el proyecto.

## 2. Opciones Evaluadas
Se analizaron tres enfoques principales en el ecosistema de Python:
- **scikit-learn**: Enfoque orientado a Machine Learning y facilidad de uso.
- **statsmodels**: Enfoque orientado a la estadística inferencial y econometría.
- **numpy**: Enfoque de bajo nivel mediante álgebra lineal y mínimos cuadrados.

| Criterio / Aspecto | `scikit-learn` | `statsmodels` | `numpy` |
| :--- | :--- | :--- | :--- |
| **Enfoque principal** | Machine Learning predictivo. | Análisis estadístico inferencial. | Computación numérica de bajo nivel. |
| **Facilidad de uso y documentación** | **Alta**: Sintaxis intuitiva (`.fit()`, `.predict()`) y amplia documentación oficial. | **Media**: Enfocada en estadística; interfaz más formal. | **Baja**: Requiere implementar manualmente la lógica del modelo. |
| **Modelos simples y múltiples** | **Muy alta**: La clase `LinearRegression()` gestiona automáticamente ambos casos. | **Alta**: Permite uso de fórmulas (`smf.ols`) o matrices (`sm.OLS`). | **Baja**: Requiere `np.polyfit` para simple o `np.linalg.lstsq` para múltiple. |
| **Extracción de Coeficientes e Intercepto** | **Muy fácil**: Directo mediante atributos `.coef_` e `.intercept_`. | **Fácil**: Mediante atributo `.params` (incluye término independiente). | **Media**: Devuelve una tupla que requiere separación manual. |
| **Métricas de Error (ECM y R²)** | **Nativa**: Módulo `sklearn.metrics` (`mean_squared_error`, `r2_score`). | **Nativa**: Disponibles en el resumen (`.summary()`) o atributos del modelo. | **Manual**: Se deben programar manualmente con operaciones matemáticas. |
| **Instalación con `uv`** | `uv add scikit-learn` | `uv add statsmodels` | `uv add numpy` |

## 3. Justificación de la Elección
Se seleccionó **scikit-learn** debido a su simplicidad sintáctica, su robustez en la gestión automática de interceptos tanto en modelos simples como múltiples, y la disponibilidad directa de métricas estandarizadas como el Error Cuadrático Medio (ECM) y el Coeficiente de Determinación ($R^2$).

## 4. Dificultades Encontradas y Resolución
- **Dificultad inicial:** Asegurarse de que las dimensiones de los arrays de entrada cumplan con los requisitos de `scikit-learn` (matrices 2D para características y 1D para la variable objetivo).
- **Resolución:** Uso sistemático de métodos de Pandas (`df[['columna']]` para 2D y `df['columna']` para 1D) antes de alimentar el modelo.