# Prueba de concepto: regresión lineal sin interfaz gráfica

## 1. Objetivo y librería

Esta prueba de concepto (PoC) comprueba que podemos crear, interpretar y
evaluar un modelo de regresión lineal en Python antes de integrarlo en la
aplicación. El código está en `prototipos/poc_regresion.py`, separado del
código de la aplicación, y no usa interfaz gráfica.

- **Librería de regresión:** scikit-learn (`LinearRegression` y
  `sklearn.metrics`).
- **Reutiliza el código de la aplicación:** `importar_datos` (importación) y
  `separar_datos` (separación en entrenamiento y test).

La comparativa de librerías y la justificación de la elección están en
[comparativa de librerías](comparativa_librer%C3%ADas.md). Se eligió
scikit-learn por su simplicidad, la gestión automática del término
independiente y la disponibilidad directa de métricas como el ECM y el R².

## 2. Cómo se ejecuta

Desde la raíz del repositorio, con los datasets guardados en la carpeta
local `data/` (que no se sube a Git):

```
uv run python prototipos/poc_regresion.py data/housing.csv --entradas median_income housing_median_age total_rooms --salida median_house_value
```

| Argumento | Obligatorio | Descripción |
|---|---|---|
| `ruta` | Sí | Archivo CSV, Excel o SQLite |
| `--entradas` | Sí | Una o varias columnas de entrada |
| `--salida` | Sí | Columna de salida |
| `--test` | No | Porcentaje de test (20 por defecto) |
| `--semilla` | No | Semilla de la separación (42 por defecto) |

Con una sola entrada se obtiene regresión simple; con varias, regresión
múltiple. Las columnas deben ser numéricas.

## 3. Pasos del script

1. **Cargar los datos** con `importar_datos`, que elige el lector según la
   extensión del archivo (CSV, Excel o SQLite).
2. **Separar** en entrenamiento y test con `separar_datos` (aleatoria y
   reproducible gracias a la semilla).
3. **Entrenar** `LinearRegression` con el conjunto de entrenamiento.
4. **Imprimir** los coeficientes, el término independiente y la fórmula con
   los nombres de las columnas.
5. **Calcular** el error cuadrático medio (ECM) y el coeficiente de
   determinación (R²) en entrenamiento y en test.
6. **Predecir** la salida para un valor nuevo (la media de cada entrada).

Nota: antes de separar, el script elimina las filas con valores
inexistentes en las columnas elegidas. Es un atajo de la PoC; la aplicación
real usa el módulo de preprocesado.

## 4. Resultados

| Dataset | Entradas → salida | ECM train | ECM test | R² train | R² test |
|---|---|---|---|---|---|
| `housing.csv` | median_income, housing_median_age, total_rooms → median_house_value | 6,454·10⁹ | 6,563·10⁹ | 0,517 | 0,499 |
| `housing.xlsx` | (las mismas) | 6,454·10⁹ | 6,563·10⁹ | 0,517 | 0,499 |
| `housing.db` | (las mismas) | 6,454·10⁹ | 6,563·10⁹ | 0,517 | 0,499 |
| `sintetico.csv` | x1, x2 → y | 0,970 | 1,020 | 0,990 | 0,988 |
| `sintetico.csv` | x1 → y | 9,034 | 8,344 | 0,904 | 0,903 |
| `con_nan.csv` | x → y | 0,000 | 0,000 | 1,000 | 1,000 |
| `grande.csv` | 0, 1 → 2 | 0,080 | 0,073 | 0,000 | -0,002 |

### 4.1 Dataset de ejemplo: California housing

Se ejecutó la PoC con `housing.csv`, `housing.xlsx` y `housing.db`
(20.640 filas: 16.512 de entrenamiento y 4.128 de test), con las entradas
`median_income`, `housing_median_age` y `total_rooms` y la salida
`median_house_value`. No se descartó ninguna fila, porque estas columnas no
tienen valores inexistentes. **Los tres formatos dan exactamente los mismos
resultados**, lo que confirma que el módulo de importación trata igual CSV,
Excel y SQLite.

Fórmula:

```
median_house_value = 42653,33 * median_income + 1975,74 * housing_median_age
                     + 3,85 * total_rooms - 25029,51
```

- Cada unidad de `median_income` (10.000 $) suma unos 42.653 $ al precio
  mediano, manteniendo constantes las demás variables.
- Cada año más de antigüedad suma unos 1.976 $, y cada habitación adicional
  unos 3,85 $.
- El término independiente (−25.030 $) es el valor con todas las entradas a
  0 y no tiene interpretación práctica.
- ECM: 6,45·10⁹ (train) y 6,56·10⁹ (test), en dólares al cuadrado. Su raíz
  cuadrada (RMSE) es ≈ 80.300 $ y ≈ 81.000 $: el error típico de predicción
  ronda los 80.000 $ sobre un precio medio de unos 207.000 $.
- R²: 0,517 (train) y 0,499 (test): el modelo explica aproximadamente la
  mitad de la variabilidad del precio.
- La diferencia entre train y test es pequeña (0,018 en R²), así que no hay
  sobreajuste. El límite del modelo es su simplicidad (tres variables y
  relación lineal), no la falta de generalización.
- Predicción para el distrito "medio" (media de cada entrada): 207.195 $.

### 4.2 Dataset sintético

Generado con `y = 3·x1 − 2·x2 + 7 + ruido` (ruido normal de desviación 1,
200 filas: 160 de entrenamiento y 40 de test).

- Regresión múltiple: `y = 2,9993 * x1 - 1,9664 * x2 + 6,9176`, muy cerca de
  los valores reales (3, −2 y 7). El ECM (≈ 1) coincide con la varianza del
  ruido: el modelo captura todo lo que se podía capturar.
- Regresión simple (solo x1): coeficiente 3,0530 y término independiente
  1,5988. El término independiente se aleja de 7 porque el efecto de x2, que
  queda fuera del modelo, se absorbe en él.
- Añadir x2 reduce el ECM de ≈ 9 a ≈ 1 y sube el R² de 0,90 a 0,99.

### 4.3 Casos límite

- **`con_nan.csv`** (`y = 2·x` sin ruido y con valores inexistentes): quedan
  16 filas útiles (13 de entrenamiento y 3 de test). El modelo obtiene
  coeficiente 2 y término independiente 0, con R² = 1. Con un test de solo 3
  filas, ese resultado no demuestra capacidad de generalización.
- **`grande.csv`** (200 filas × 30 columnas aleatorias independientes): los
  coeficientes son prácticamente 0 y el término independiente (0,5) coincide
  con la media de una variable uniforme entre 0 y 1. El R² es ≈ 0 y negativo
  en test (−0,002): el modelo no mejora a predecir siempre la media, algo
  esperable cuando no hay relación entre las columnas.

### 4.4 Sobre la predicción

Con la media de las entradas, el modelo devuelve la media de la salida de
entrenamiento. No es casualidad: una regresión lineal con término
independiente siempre pasa por el punto formado por las medias de las
entradas y la media de la salida.

## 5. Interpretación de las métricas

### Coeficientes y término independiente

Cada coeficiente indica cuánto cambia la salida por cada unidad que aumenta
esa entrada, manteniendo constantes las demás. Un coeficiente negativo
indica que a más entrada, menos salida. El término independiente es la
salida estimada cuando todas las entradas valen 0.

### ECM (error cuadrático medio)

Es la media de los errores de predicción elevados al cuadrado, y se mide en
unidades de la salida al cuadrado. Cuanto más bajo, mejor. Para interpretarlo
en las unidades originales se usa su raíz cuadrada (RMSE).

### R² (coeficiente de determinación)

Es la proporción de la variabilidad de la salida que explica el modelo.
Vale 1 si el ajuste es perfecto y 0 si el modelo no mejora a predecir
siempre la media. Puede ser negativo en test si el modelo es peor que
predecir la media.

### Diferencia entre entrenamiento y test

El modelo se ajusta con los datos de entrenamiento, así que sus métricas ahí
son optimistas. Las de test miden la capacidad de generalizar a datos que no
ha visto.

- Si el rendimiento en entrenamiento es mucho mejor que en test (R² mucho
  más alto, ECM mucho más bajo), hay **sobreajuste**.
- Si son parecidos, el modelo **generaliza**. Es lo que ocurre en housing
  (R² 0,517 frente a 0,499) y en el sintético (0,990 frente a 0,988).
- Un modelo puede generalizar bien y aun así ser malo: en housing y en
  `grande.csv` train y test se parecen, pero el R² es bajo.

## 6. Dificultades encontradas y cómo se resolvieron

- **Marcadores en los comandos.** Al copiar comandos con `<archivo>` o
  `<col1>`, PowerShell da error porque `<` es un operador reservado. Hay que
  sustituir los marcadores por nombres reales.
- **Nombres inexistentes.** Un archivo inventado provocó
  `ErrorImportacion: El archivo no existe`, que es justo el mensaje que debe
  dar el módulo de importación.
- **Columna de texto.** `ocean_proximity` es de texto y no puede usarse en
  regresión lineal, por lo que se usaron solo columnas numéricas.
- **Tipos distintos entre formatos.** Algunas columnas llegan como `int64` en
  Excel y SQLite y como `float64` en CSV. Es numérico en todos los casos y no
  afecta al resultado.
- **Columnas numéricas como nombre.** En `grande.csv` las columnas se llaman
  `0`, `1`, `2`, lo que hace confusa la fórmula. Es un efecto del dataset de
  prueba.
- **Muestras pequeñas.** Con pocas filas el test es demasiado pequeño para
  sacar conclusiones fiables.
- **Valores inexistentes.** `LinearRegression` no admite NaN, por lo que la
  PoC descarta esas filas antes de separar.
- **ECM enorme.** Con la salida en dólares, el ECM es del orden de 10⁹; se
  interpreta mejor con el RMSE.