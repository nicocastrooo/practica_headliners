# Plan de Pruebas Funcionales — Aplicación de Regresión Lineal

Este documento recoge los casos de prueba funcionales para validar la aplicación antes de publicar la release (HU #29), trabajando sobre la rama `dev`.

Las pruebas se hacen directamente sobre la interfaz gráfica, sin mirar el código. Si algún paso no se entiende o no coincide con lo que sale en pantalla, se avisa antes de seguir para corregirlo. Al terminar cada caso, se apunta el resultado y el estado en la tabla del final.

## 1. Datos de prueba

Los datasets no se suben al repositorio. Antes de empezar, hay que meter los tres archivos del campus virtual en la carpeta local `data/` con estos nombres exactos:

| Archivo | Formato | Hoja / Tabla | Filas | Columnas | Columnas usadas en las pruebas | Valores nulos (`NaN`) | Columnas de texto |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| `data/housing.csv` | CSV | — | 20.640 | 10 | `housing_median_age`, `total_bedrooms`, `median_income`, `median_house_value`, `ocean_proximity` | `total_bedrooms` (207) | `ocean_proximity` |
| `data/housing.xlsx` | Excel | `housing` | 20.640 | 10 | `median_income`, `median_house_value` | `total_bedrooms` (207) | `ocean_proximity` |
| `data/housing.db` | SQLite | `california_housing_dataset` | 20.640 | 10 | `housing_median_age`, `median_income`, `median_house_value` | `total_bedrooms` (207) | `ocean_proximity` |

Las 10 columnas que tienen los tres archivos son: `longitude`, `latitude`, `housing_median_age`, `total_rooms`, `total_bedrooms`, `population`, `households`, `median_income`, `median_house_value` y `ocean_proximity`.

Los archivos pequeños para probar errores (vacíos o corruptos) tampoco están en el repo; en cada caso se indica cómo crearlos en `data/`.

## 2. Bloque de Datos y Modelo (Tarea #144)

### CP-01. Estado inicial, carga de CSV y cancelación del diálogo
- **Historia:** #14, #37
- **Objetivo:** Verificar cómo arranca la ventana, cargar un CSV válido y comprobar que cancelar el explorador no da error.
- **Precondiciones:** La aplicación está recién abierta.
- **Datos de prueba:** `data/housing.csv`.
- **Pasos:**
  1. Mirar la ventana nada más abrirla, sin tocar nada.
  2. Pulsar "1. Cargar dataset".
  3. En el explorador, fijarse en que solo deja elegir archivos compatibles (`*.csv *.xlsx *.xls *.sqlite *.db`) y darle a "Cancelar".
  4. Volver a pulsar "1. Cargar dataset", entrar en `data/`, elegir `housing.csv` y pulsar "Abrir".
- **Resultado esperado:**
  - Al abrir: sale el mensaje inicial de ayuda arriba, la barra inferior marca `Archivo cargado: Ninguno | Modelo: Sin modelo | Estado: Sin cambios sin guardar`, y los botones de los pasos 2, 3, 5, "Guardar modelo" y 6 están deshabilitados.
  - Al cancelar: no salta ningún error y sigue poniendo `Ningún archivo seleccionado`.
  - Al cargar: aparece la ruta de `housing.csv`, la tabla carga las 10 columnas y 20.640 filas, la barra inferior pone `Archivo cargado: housing.csv` y se activa el paso 2 ("2. Confirmar selección").

### CP-02. Carga de Excel (.xlsx) y respuesta durante la lectura
- **Historia:** #14, #37
- **Objetivo:** Cargar un Excel grande, ver que sustituye a los datos anteriores y comprobar que la ventana no se congela.
- **Precondiciones:** `data/housing.csv` está cargado (CP-01).
- **Datos de prueba:** `data/housing.xlsx`.
- **Pasos:**
  1. Pulsar "1. Cargar dataset".
  2. Ir a `data/`, seleccionar `housing.xlsx` y pulsar "Abrir".
  3. Mientras carga, fijarse en el cursor, los botones y arrastrar la ventana por la pantalla para ver si responde.
- **Resultado esperado:** Mientras lee el archivo, sale el cursor de espera, pone `Cargando...`, los botones del flujo se bloquean y la ventana se mueve con fluidez sin colgarse. Al acabar, la tabla reemplaza los datos anteriores por las 10 columnas y 20.640 filas de `housing.xlsx` y la barra inferior se actualiza a `Archivo cargado: housing.xlsx`.

### CP-03. Carga de SQLite (.db) en una ruta con espacios y ñ
- **Historia:** #14
- **Objetivo:** Comprobar que lee una base de datos SQLite metida en una carpeta con espacios, tildes y `ñ`.
- **Precondiciones:** La aplicación está abierta.
- **Datos de prueba:** Copia de `data/housing.db` dentro de `data/carpeta pruebas ñ á/`.
- **Pasos:**
  1. En el explorador de Windows, crear la carpeta `data/carpeta pruebas ñ á/` y pegar dentro `housing.db`.
  2. En la app, pulsar "1. Cargar dataset".
  3. Entrar en `data/carpeta pruebas ñ á/`, elegir `housing.db` y pulsar "Abrir".
- **Resultado esperado:** Importa automáticamente la tabla `california_housing_dataset` sin pedir su nombre. La ruta con espacios, tilde y `ñ` se muestra bien en pantalla y la tabla carga las 20.640 filas y 10 columnas.

### CP-04. Error al cargar un archivo vacío manteniendo los datos anteriores
- **Historia:** #14, #37
- **Objetivo:** Comprobar que si se intenta abrir un archivo vacío salta un error claro (sin trazas de Python) y no se pierden los datos que ya estaban cargados.
- **Precondiciones:** `data/housing.csv` está cargado en la tabla (CP-01).
- **Datos de prueba:** `data/vacio.csv` (creado en el paso 1).
- **Pasos:**
  1. En el explorador de archivos, crear un archivo vacío llamado `vacio.csv` dentro de `data/`.
  2. En la app, pulsar "1. Cargar dataset", elegir `data/vacio.csv` y pulsar "Abrir".
  3. Cerrar el aviso pulsando "OK".
- **Resultado esperado:** Salta una ventana de error con título "Error de importación" explicando el fallo en lenguaje normal, sin trazas de código. Al cerrarla, la app sigue funcionando y mantiene cargados los datos de `housing.csv`.

### CP-05. Selección válida de entradas y salida
- **Historia:** #11
- **Objetivo:** Seleccionar varias columnas numéricas como entrada y una como salida para habilitar la separación.
- **Precondiciones:** `data/housing.csv` está cargado (CP-01).
- **Datos de prueba:** Entradas: `housing_median_age` y `median_income`; Salida: `median_house_value`.
- **Pasos:**
  1. En "Variables de Entrada (Features):", marcar `housing_median_age` y `median_income`.
  2. En el desplegable "Variable de Salida (Target):", elegir `median_house_value`.
  3. Pulsar "2. Confirmar selección".
- **Resultado esperado:** Sale un aviso de "Selección Confirmada" con `Entradas (Features): housing_median_age, median_income` y `Salida (Target): median_house_value`. Al darle a "OK", se activa el panel 3 y el botón "3. Separar datos".

### CP-06. Errores al seleccionar columnas (vacía, texto y repetida)
- **Historia:** #11
- **Objetivo:** Comprobar que no deja confirmar si falta alguna selección, si se elige texto o si la salida también está marcada como entrada.
- **Precondiciones:** `data/housing.csv` está recién cargado.
- **Datos de prueba:** `ocean_proximity` y `median_house_value`.
- **Pasos:**
  1. Sin marcar ninguna entrada y dejando la salida en `-- Selecciona una salida --`, pulsar "2. Confirmar selección" y cerrar el aviso.
  2. Marcar `ocean_proximity` en entradas, elegir `median_house_value` en salida, pulsar "2. Confirmar selección" y cerrar el aviso.
  3. Desmarcar `ocean_proximity`, marcar `median_house_value` en entradas (dejándola también en salida) y pulsar "2. Confirmar selección".
- **Resultado esperado:** En los tres casos salta un aviso "Error de Validación" explicando el problema (falta selección, columna no numérica y variable repetida). El botón "3. Separar datos" sigue deshabilitado.

### CP-07. Separación de datos en límites válidos (1%, 20%, 99%) y misma semilla
- **Historia:** #41
- **Objetivo:** Probar los porcentajes límite válidos (1 y 99), el porcentaje por defecto (20) y comprobar que con la misma semilla da exactamente lo mismo.
- **Precondiciones:** `data/housing.csv` cargado y columnas confirmadas (CP-05).
- **Datos de prueba:** Porcentajes de test: `1`, `99` y `20`; Semilla: `42`.
- **Pasos:**
  1. Borrar el campo "Porcentaje Test (%):", escribir `1`, mirar qué pone en "Porcentaje Entrenamiento:" y pulsar "3. Separar datos". Cerrar el aviso.
  2. Escribir `99` en "Porcentaje Test (%):", mirar el porcentaje de entrenamiento y pulsar "3. Separar datos". Cerrar el aviso.
  3. Escribir `20` en "Porcentaje Test (%):", dejar "Semilla Aleatoria:" en `42` y pulsar "3. Separar datos". Cerrar el aviso.
  4. Sin tocar nada, volver a pulsar "3. Separar datos".
- **Resultado esperado:**
  - Con `1%`: entrenamiento marca `99%` y salen 20.433 filas de entrenamiento y 207 de test.
  - Con `99%`: entrenamiento marca `1%` y salen 206 filas de entrenamiento y 20.434 de test.
  - Con `20%` (pasos 3 y 4): entrenamiento marca `80%`, ambas veces salen 16.512 filas de entrenamiento y 4.128 de test, y se activa "5. Crear modelo".

### CP-08. Errores en separación: límites 0 y 100, semilla decimal y pocas filas
- **Historia:** #41
- **Objetivo:** Comprobar que rechaza porcentajes de 0 o 100, semillas con decimales y datasets de menos de 5 filas.
- **Precondiciones:** `data/housing.csv` cargado y columnas confirmadas (CP-05).
- **Datos de prueba:** Porcentajes `0` y `100`; semilla `3.5`; `data/pocas_filas.csv` (3 filas).
- **Pasos:**
  1. Poner `0` en "Porcentaje Test (%):", pulsar "3. Separar datos" y cerrar el aviso.
  2. Poner `100` en "Porcentaje Test (%):", pulsar "3. Separar datos" y cerrar el aviso.
  3. Volver a poner `20` en porcentaje, escribir `3.5` en "Semilla Aleatoria:", pulsar "3. Separar datos" y cerrar el aviso.
  4. Crear `data/pocas_filas.csv` con este texto:
     ```csv
     x,y
     1,2
     2,4
     3,6
     ```
  5. Cargar `data/pocas_filas.csv`, elegir `x` como entrada e `y` como salida, confirmar selección, poner semilla `42` y pulsar "3. Separar datos".
- **Resultado esperado:** En los cuatro intentos salta "Error de Separación" indicando el fallo (rango 1-99, semilla entera o mínimo 5 filas). No divide los datos y "5. Crear modelo" sigue deshabilitado.

### CP-09. Preprocesado de nulos con las 4 estrategias
- **Historia:** #26
- **Objetivo:** Comprobar el conteo de nulos en entrenamiento y test y probar eliminación, media, mediana y valor constante.
- **Precondiciones:** `data/housing.csv` cargado.
- **Datos de prueba:** Entrada: `total_bedrooms`; Salida: `median_house_value`; Test: `20%`; Semilla: `1`; Constante: `500`.
- **Pasos:**
  1. Marcar `total_bedrooms` en entradas, elegir `median_house_value` en salida y pulsar "2. Confirmar selección".
  2. Poner `20` en porcentaje de test y `1` en semilla, pulsar "3. Separar datos" y cerrar el aviso.
  3. Revisar el panel 4 (preprocesado) y comprobar que "5. Crear modelo" y el campo de constante están bloqueados.
  4. Elegir **eliminar filas** y pulsar "Aplicar preprocesado". Ver el aviso y comprobar que "5. Crear modelo" se activa.
  5. Volver a pulsar "3. Separar datos" para recuperar los nulos, elegir **media** y pulsar "Aplicar preprocesado".
  6. Repetir el paso 5 eligiendo **mediana**.
  7. Repetir el paso 5 eligiendo **valor constante**, comprobar que se activa la caja de texto, escribir `500` y pulsar "Aplicar preprocesado".
- **Resultado esperado:** En el paso 3 el panel detecta 163 nulos en entrenamiento y 44 en test para `total_bedrooms`. Tras aplicar cada una de las 4 estrategias sale un mensaje con el resumen de cambios y se habilita "5. Crear modelo". El archivo `data/housing.csv` original no se modifica.

### CP-10. Errores en preprocesado (constante no numérica y conjunto vacío)
- **Historia:** #26
- **Objetivo:** Comprobar qué pasa si se mete texto en el valor constante o si eliminar filas deja vacío un conjunto.
- **Precondiciones:** `data/housing.csv` cargado y separado con nulos pendientes (pasos 1-2 de CP-09).
- **Datos de prueba:** Constante `abc`; `data/todo_nulos.csv`.
- **Pasos:**
  1. Elegir **valor constante**, escribir `abc` y pulsar "Aplicar preprocesado". Cerrar el aviso.
  2. Crear `data/todo_nulos.csv` con 6 filas donde `x` esté vacía en todas:
     ```csv
     x,y
     ,10
     ,20
     ,30
     ,40
     ,50
     ,60
     ```
  3. Cargar `data/todo_nulos.csv`, elegir `x` e `y`, confirmar selección y separar (20%, semilla 42).
  4. Elegir **eliminar filas** y pulsar "Aplicar preprocesado".
- **Resultado esperado:** En el paso 1 da error porque la constante no es un número y "5. Crear modelo" sigue bloqueado. En el paso 4 avisa de que no se puede aplicar porque dejaría vacío el conjunto de entrenamiento o de test, dejando elegir otra opción.

### CP-11. Creación de modelo simple (recta de ajuste, fórmula y métricas)
- **Historia:** #16
- **Objetivo:** Crear un modelo con una sola entrada y comprobar la fórmula, las métricas y el gráfico con recta de ajuste.
- **Precondiciones:** `data/housing.csv` cargado.
- **Datos de prueba:** Entrada: `median_income`; Salida: `median_house_value`; Test: `20%`; Semilla: `42`.
- **Pasos:**
  1. Marcar solo `median_income` en entradas, elegir `median_house_value` en salida y pulsar "2. Confirmar selección".
  2. Separar con `20` en porcentaje de test y `42` en semilla.
  3. Pulsar "5. Crear modelo".
- **Resultado esperado:** Sale el mensaje "Éxito". La fórmula muestra `median_house_value = 41933.8494 * median_income + 44459.7292`. La tabla de métricas marca:
  - Entrenamiento: `R² = 0.4770`, `ECM = 6991447170.1828`
  - Test: `R² = 0.4589`, `ECM = 7091157771.7655`
  El gráfico dibuja los puntos de entrenamiento y test con su leyenda, la recta de ajuste y los ejes `median_income` y `median_house_value`. Se activan la descripción, "Guardar modelo" y el paso 6.

### CP-12. Creación de modelo múltiple (sustitución, signo negativo y gráfico real vs. predicho)
- **Historia:** #16
- **Objetivo:** Crear un modelo múltiple comprobando que limpia el anterior, formatea bien los términos negativos y dibuja valores reales frente a predichos.
- **Precondiciones:** Modelo simple creado (CP-11) con `data/housing.csv` cargado.
- **Datos de prueba:** Entradas: `housing_median_age`, `median_income`; Salida: `median_house_value`; Test: `20%`; Semilla: `42`.
- **Pasos:**
  1. Marcar `housing_median_age` y `median_income` en entradas, elegir `median_house_value` en salida y pulsar "2. Confirmar selección". Fijarse en que se borra el modelo anterior.
  2. Pulsar "3. Separar datos" (20% y semilla 42).
  3. Pulsar "5. Crear modelo".
- **Resultado esperado:** Al confirmar en el paso 1 se reinician fórmula, métricas y gráfico. Tras el paso 3, la fórmula es `median_house_value = 1748.5735 * housing_median_age + 43342.2840 * median_income - 11029.7493` (con `-`, sin `+ -`). Las métricas son:
  - Entrenamiento: `R² = 0.5128`, `ECM = 6513066873.6164`
  - Test: `R² = 0.4941`, `ECM = 6629874283.0482`
  El gráfico muestra puntos de entrenamiento y test con leyenda, la diagonal de coincidencia y los ejes "Valor real" y "Valor predicho". La barra inferior marca `Modelo: Modelo creado | Estado: Cambios sin guardar`.

## 3. Bloque de Persistencia, Predicciones y GUI (Tarea #145)

### CP-13. Aviso por descripción vacía y cancelación al guardar
- **Historia:** #21, #33
- **Objetivo:** Comprobar que avisa si la descripción está vacía y que cerrar el diálogo de guardado no da error.
- **Precondiciones:** Modelo múltiple creado (CP-12) con el cuadro de descripción vacío.
- **Datos de prueba:** Ninguno.
- **Pasos:**
  1. Pulsar "Guardar modelo".
  2. En el aviso "Descripción vacía", darle a "No".
  3. Volver a pulsar "Guardar modelo" y esta vez darle a "Yes".
  4. En la ventana de guardado, comprobar que propone `.joblib` y pulsar "Cancelar".
- **Resultado esperado:** En el paso 2 se cancela antes de abrir el explorador. En el paso 4 no se guarda nada, no sale ningún error y la barra inferior mantiene `Estado: Cambios sin guardar`.

### CP-14. Guardado con descripción, extensión automática, ruta con ñ y sobrescritura
- **Historia:** #21, #33
- **Objetivo:** Guardar un modelo en una carpeta con espacios y `ñ` sin escribir la extensión y comprobar la confirmación si ya existe.
- **Precondiciones:** Modelo múltiple creado (CP-12).
- **Datos de prueba:** Descripción: `Modelo múltiple vivienda`; Carpeta: `data/carpeta pruebas ñ á/`; Nombre: `modelo_vivienda`.
- **Pasos:**
  1. Escribir `Modelo múltiple vivienda` en "Descripción del modelo (opcional):".
  2. Pulsar "Guardar modelo".
  3. Ir a `data/carpeta pruebas ñ á/`, escribir `modelo_vivienda` (sin `.joblib`) y darle a "Guardar". Cerrar la confirmación.
  4. Pulsar otra vez "Guardar modelo", elegir `modelo_vivienda.joblib`, darle a "Guardar" y responder "No" cuando pregunte si sobrescribir.
- **Resultado esperado:** En el paso 3 sale "Modelo guardado" con la ruta acabada en `modelo_vivienda.joblib` y la barra inferior cambia a `Estado: Guardado (sin cambios pendientes)`. En el paso 4 pide confirmación antes de machacar el archivo y, al elegir "No", lo deja intacto sin dar error.

### CP-15. Carga de modelo, ocultación de paneles y edición de descripción
- **Historia:** #24, #33
- **Objetivo:** Recuperar un modelo desde disco, ver que se ocultan los paneles de datos, editar su descripción y volver a guardarlo.
- **Precondiciones:** Aplicación recién abierta y `data/carpeta pruebas ñ á/modelo_vivienda.joblib` creado (CP-14).
- **Datos de prueba:** `modelo_vivienda.joblib`; Nueva descripción: `Descripción actualizada tras carga`.
- **Pasos:**
  1. Pulsar "Cargar modelo", verificar que filtra por `*.joblib` y darle a "Cancelar".
  2. Pulsar "Cargar modelo", seleccionar `data/carpeta pruebas ñ á/modelo_vivienda.joblib` y darle a "Abrir". Cerrar el aviso.
  3. Mirar qué paneles quedan visibles, comprobar los datos del modelo e intentar hacer doble clic en la tabla de métricas para ver si deja editarla.
  4. Cambiar el texto de "Descripción del modelo (opcional):" por `Descripción actualizada tras carga`.
  5. Fijarse en la barra inferior y pulsar "Guardar modelo".
  6. Comprobar qué carpeta y nombre propone por defecto, pulsar "Guardar" y aceptar la sobrescritura.
- **Resultado esperado:**
  - Al cancelar: no pasa nada ni da error.
  - Al cargar: sale "Modelo Cargado", se ocultan la tabla, los pasos 2, 3 y 4, el botón "5. Crear modelo" y el gráfico. Se ven la fórmula, las métricas de CP-12 (bloqueadas para edición) y la descripción `Modelo múltiple vivienda`. La barra inferior marca `Modelo: Modelo cargado | Estado: Guardado (sin cambios pendientes)`.
  - Al editar: la barra pasa a `Estado: Cambios sin guardar`.
  - Al re-guardar: propone la ruta original (`modelo_vivienda.joblib`), pide confirmar la sobrescritura y vuelve a `Estado: Guardado (sin cambios pendientes)`.

### CP-16. Error con modelo corrupto y vuelta de modelo cargado a dataset nuevo
- **Historia:** #24
- **Objetivo:** Comprobar que un archivo inválido no rompe el estado actual y que cargar un dataset desde modo modelo vuelve a mostrar todos los paneles.
- **Precondiciones:** Modelo cargado en pantalla (CP-15).
- **Datos de prueba:** `data/corrupto.joblib` (creado en el paso 1) y `data/housing.csv`.
- **Pasos:**
  1. Crear un archivo `data/corrupto.joblib` con el texto `no es un modelo`.
  2. Pulsar "Cargar modelo", elegir `data/corrupto.joblib`, pulsar "Abrir" y cerrar el error.
  3. Añadir ` (sin guardar)` al final de la descripción sin pulsar "Guardar modelo".
  4. Pulsar "1. Cargar dataset" y responder "No" al aviso de cambios sin guardar.
  5. Volver a pulsar "1. Cargar dataset", responder "Yes", elegir `data/housing.csv` y pulsar "Abrir".
- **Resultado esperado:** En el paso 2 sale "Error al cargar" y el modelo sigue en pantalla. En el paso 4 no se pierde el modelo. En el paso 5 se carga `housing.csv` y reaparecen la tabla, los pasos 2, 3 y 4, el botón "5. Crear modelo" y el gráfico.

### CP-17. Predicciones con punto o coma decimal y control de errores
- **Historia:** #22
- **Objetivo:** Calcular predicciones usando punto y coma decimal y comprobar los avisos si faltan datos o se mete texto.
- **Precondiciones:** Modelo múltiple activo (CP-12 o CP-15) con entradas `housing_median_age` y `median_income`.
- **Datos de prueba:** Vacío; `abc`; `housing_median_age = 30`, `median_income = 5.0` y `5,0`.
- **Pasos:**
  1. Con los campos del paso 6 vacíos, pulsar "6. Realizar predicción" y cerrar el aviso.
  2. Escribir `30` en `housing_median_age` y `abc` en `median_income`, pulsar "6. Realizar predicción" y cerrar el aviso.
  3. Escribir `30` en `housing_median_age` y `5.0` en `median_income`, y pulsar "6. Realizar predicción".
  4. Cambiar `5.0` por `5,0` y volver a pulsar "6. Realizar predicción".
- **Resultado esperado:**
  - Paso 1: Aviso "Valores faltantes" indicando `housing_median_age, median_income`.
  - Paso 2: Aviso "Valor no válido" indicando `median_income`.
  - Pasos 3 y 4: En ambos casos muestra `median_house_value = 258138.8768` (4 decimales).

### CP-18. Regeneración de campos de predicción al cambiar de modelo
- **Historia:** #22
- **Objetivo:** Comprobar que al crear otro modelo con distintas variables se actualizan los campos de predicción y se borra el resultado anterior.
- **Precondiciones:** Predicción anterior visible en pantalla (CP-17).
- **Datos de prueba:** `data/housing.csv` con entrada `median_income` y salida `median_house_value`.
- **Pasos:**
  1. Cargar `data/housing.csv` (aceptando descartar cambios si pregunta), elegir solo `median_income` en entradas y `median_house_value` en salida, confirmar, separar (20%, semilla 42) y pulsar "5. Crear modelo".
  2. Mirar el panel "6. Realizar predicción".
- **Resultado esperado:** Ya no aparece `housing_median_age`, solo queda el campo `median_income:` vacío y el resultado vuelve a `median_house_value = -`.

### CP-19. Recorrido por tabla grande (20.640 filas), redimensionado y aviso al cerrar
- **Historia:** #37, #24
- **Objetivo:** Comprobar que la tabla va fluida con más de 20.000 filas, que la ventana no corta nada en 1366x768 ni en 900x600, y que avisa antes de cerrar sin guardar.
- **Precondiciones:** `data/housing.csv` cargado y modelo creado con cambios sin guardar (CP-18).
- **Datos de prueba:** `data/housing.csv`.
- **Pasos:**
  1. En la tabla del Paso 1, moverse por las páginas/scroll hasta llegar a la última fila (20.640) y desplazarse hacia la derecha hasta ver la columna `ocean_proximity`.
  2. Redimensionar la ventana al mínimo (900x600) y luego a tamaño de portátil (1366x768), bajando con el scroll desde el Paso 1 al Paso 6.
  3. Pulsar la `X` de cerrar la ventana y darle a "No" en el aviso.
- **Resultado esperado:** La tabla responde rápido y deja ver todas las filas y columnas. En ambos tamaños de ventana se ven todos los controles sin cortes ni solapamientos. Al intentar cerrar salta "Cambios sin guardar" y al decir "No" la ventana sigue abierta.

## 4. Flujo Completo (End-to-End)

### CP-20. Ciclo completo: SQLite → Crear modelo → Predecir → Guardar → Cargar → Predecir
- **Historia:** #14, #11, #41, #16, #33, #21, #24, #22
- **Objetivo:** Probar todo el flujo de principio a fin y comprobar que el modelo cargado predice exactamente lo mismo que el recién creado.
- **Precondiciones:** Aplicación recién abierta.
- **Datos de prueba:** `data/housing.db`; Entradas: `housing_median_age`, `median_income`; Salida: `median_house_value`; Test: `20%`; Semilla: `42`; Descripción: `Modelo E2E final`; Archivo: `data/modelo_e2e.joblib`; Predicción: `housing_median_age = 30`, `median_income = 5.0`.
- **Pasos:**
  1. Pulsar "1. Cargar dataset", abrir `data/housing.db`.
  2. Marcar `housing_median_age` y `median_income` como entradas, elegir `median_house_value` como salida y pulsar "2. Confirmar selección". Cerrar el aviso.
  3. Dejar porcentaje de test en `20` y semilla en `42`, pulsar "3. Separar datos" y cerrar el aviso.
  4. Pulsar "5. Crear modelo" y cerrar el aviso.
  5. Escribir `Modelo E2E final` en "Descripción del modelo (opcional):".
  6. En el paso 6, escribir `30` en `housing_median_age` y `5.0` en `median_income`, y pulsar "6. Realizar predicción".
  7. Pulsar "Guardar modelo", guardarlo como `data/modelo_e2e.joblib` y cerrar el aviso.
  8. Cerrar la aplicación (no debe pedir confirmación) y volver a abrirla.
  9. Pulsar "Cargar modelo", abrir `data/modelo_e2e.joblib` y cerrar el aviso.
  10. Volver a escribir `30` en `housing_median_age` y `5.0` en `median_income`, y pulsar "6. Realizar predicción".
- **Resultado esperado:**
  - En el paso 6 da `median_house_value = 258138.8768`.
  - En el paso 9 recupera la misma fórmula (`median_house_value = 1748.5735 * housing_median_age + 43342.2840 * median_income - 11029.7493`), las mismas métricas (`R²` Train `0.5128`, Test `0.4941`; `ECM` Train `6513066873.6164`, Test `6629874283.0482`) y la descripción `Modelo E2E final`.
  - En el paso 10 vuelve a dar exactamente `median_house_value = 258138.8768`.

## 5. Registro de Ejecución

| ID | Bloque | Ejecutor | Fecha | Resultado obtenido | Estado (`Correcto` / `Fallido`) | Ticket Taiga (si falla) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CP-01 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Estado inicial, cancelación sin error y carga de `housing.csv` (20.640 filas, 10 columnas) correctos | Correcto | — |
| CP-02 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Carga fluida sin congelación, sustituye tabla por `housing.xlsx` (20.640 filas, 10 columnas) | Correcto | — |
| CP-03 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Importación automática de SQLite desde ruta con espacios, tilde y `ñ` correcta (20.640 filas, 10 columnas) | Correcto | — |
| CP-04 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Muestra "Error de importación" sin trazas y mantiene los datos previos de `housing.csv` | Correcto | — |
| CP-05 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Muestra "Selección Confirmada" con entradas y salida elegidas y activa el paso 3 | Correcto | — |
| CP-06 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Muestra "Error de Validación" en los 3 casos inválidos y mantiene bloqueado el paso 3 | Correcto | — |
| CP-07 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Límites 1%, 99% y 20% con semilla 42 devuelven conteos exactos y reproducibles; activa paso 5 | Correcto | — |
| CP-08 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Muestra "Error de Separación" en 0%, 100%, semilla 3.5 y 3 filas; paso 5 sigue deshabilitado | Correcto | — |
| CP-09 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Detecta 163/44 nulos y aplica eliminación, media, mediana y constante (500) sin alterar el CSV | Correcto | — |
| CP-10 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Rechaza constante `abc` y avisa si eliminar filas deja vacío train/test permitiendo reelegir | Correcto | — |
| CP-11 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Fórmula, métricas (`R²` y `ECM`) y gráfico simple con recta de ajuste coinciden exactamente | Correcto | — |
| CP-12 | Datos y Modelo (#144) | Diego Grande Goyanes | 21/11/2026 | Limpia modelo previo fórmula con signo `-`, métricas, gráfico múltiple y barra inferior correctos | Correcto | — |
| CP-13 | Persistencia y GUI (#145) | | | | | |
| CP-14 | Persistencia y GUI (#145) | | | | | |
| CP-15 | Persistencia y GUI (#145) | | | | | |
| CP-16 | Persistencia y GUI (#145) | | | | | |
| CP-17 | Persistencia y GUI (#145) | | | | | |
| CP-18 | Persistencia y GUI (#145) | | | | | |
| CP-19 | Persistencia y GUI (#145) | | | | | |
| CP-20 | Flujo Completo E2E | | | | | |