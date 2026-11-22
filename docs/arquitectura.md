# Arquitectura del Proyecto

Este documento describe cómo está organizado el código fuente de la aplicación (`src/practica_headliners/`), qué hace cada módulo y cómo se mantiene separada la lógica de datos y regresión respecto a la interfaz gráfica.

## 1. Estructura de carpetas

```text
src/practica_headliners/
├── __init__.py
├── importacion.py          # Lectura de datasets (CSV, Excel, SQLite)
├── seleccion.py            # Validación de columnas de entrada y salida
├── separacion.py           # División aleatoria en entrenamiento y test
├── preprocesado.py         # Detección y tratamiento de valores nulos (NaN)
├── modelo.py               # Entrenamiento, métricas, fórmula, predicción y persistencia
└── gui/
    ├── __init__.py
    ├── ventana_principal.py  # Ventana principal y coordinación del flujo (pasos 1 a 6)
    ├── hilo_carga.py         # Hilo secundario (QThread) para carga asíncrona de archivos
    ├── tabla_datos.py        # Visor de tabla con paginación (100 filas/página)
    ├── panel_preprocesado.py # Panel interactivo del paso 4 (detección y estrategias NaN)
    └── grafico.py            # Widget de Matplotlib integrado en PySide6