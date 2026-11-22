# Práctica Headliners - Ingeniería del Software (GIA - UDC)

Aplicación de escritorio hecha en Python para crear, evaluar, guardar y usar modelos de regresión lineal a partir de un dataset, todo desde interfaz gráfica.

Versión actual: `v0.2.0`

## Qué permite hacer

La aplicación sigue el flujo habitual para trabajar con regresión lineal:

1. Cargar datos desde archivos CSV, Excel (`.xlsx`, `.xls`) o bases de datos SQLite (`.sqlite`, `.db`).
2. Elegir las columnas numéricas de entrada y la columna de salida.
3. Separar los datos en entrenamiento y test indicando el porcentaje de test y una semilla.
4. Detectar valores vacíos (NaN) y tratarlos eliminando filas o rellenando con la media, la mediana o un valor constante.
5. Entrenar un modelo de regresión lineal simple o múltiple, mostrando la fórmula, las métricas (R² y ECM) en entrenamiento y test y el gráfico del ajuste.
6. Guardar el modelo en disco en formato `.joblib` (con una descripción opcional) y volver a cargarlo más adelante.
7. Hacer predicciones nuevas introduciendo valores para cada variable de entrada.

## Antes de empezar: cómo abrir la terminal

Los comandos de instalación se ejecutan en la terminal (la consola de comandos del sistema).

En Windows:
1. Abre el Explorador de archivos y entra en la carpeta donde quieras dejar el proyecto (por ejemplo, el Escritorio).
2. Haz clic derecho en un hueco vacío de la carpeta y elige **Abrir en Terminal** (en versiones anteriores de Windows sale como "Abrir ventana de PowerShell aquí").
3. También puedes pulsar la tecla Windows, escribir `PowerShell` y darle a Enter; se abrirá en tu carpeta de usuario.

En macOS: pulsa `Cmd + Espacio`, escribe `Terminal` y dale a Enter.

En Linux: pulsa `Ctrl + Alt + T` o busca "Terminal" en el menú de aplicaciones.

Un par de cosas a tener en cuenta al usarla:
- Se escribe a partir de la línea que acaba en `>` (Windows) o `$` (macOS/Linux).
- Copia cada comando de esta guía, pégalo en la terminal (`Ctrl + V` o clic derecho) y pulsa Enter.
- Ejecútalos de uno en uno, esperando a que termine el anterior antes de pegar el siguiente.
- Mantén abierta la misma terminal durante los pasos 1 a 3, salvo cuando se indique reiniciarla. Si sale algún error en rojo, copia el texto completo para revisarlo.

## Requisitos

- **Git**, para clonar el repositorio. Se descarga desde [https://git-scm.com/downloads](https://git-scm.com/downloads).
- **uv**, para gestionar el entorno virtual y las dependencias de Python. Si no lo tienes instalado:

  En Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  En macOS y Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  Al terminar de instalarlo, cierra la terminal y abre una nueva para que reconozca el comando `uv` (más info en [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)).

- **Python 3.12 o superior.** No hace falta instalarlo aparte porque `uv` lo descarga solo si no lo encuentra en el equipo.

## Instalación y arranque

### 1. Descargar el proyecto

Abre una terminal en la carpeta donde quieras guardar el código (por ejemplo, el Escritorio) y ejecuta:

```bash
git clone -b dev https://github.com/nicocastrooo/practica_headliners.git
cd practica_headliners
```

El segundo comando entra dentro de la carpeta del proyecto. A partir de aquí, la línea de la terminal debería terminar en `practica_headliners` y todos los comandos siguientes se lanzan desde ahí.

### 2. Instalar las dependencias

```bash
uv sync
```

Esto crea el entorno virtual e instala las librerías necesarias. La primera vez puede tardar un par de minutos.

### 3. Arrancar la aplicación

```bash
uv run python -m practica_headliners.gui.ventana_principal
```

Con esto se abrirá la ventana principal.

## Datasets de ejemplo y formato

Los datasets no están subidos al repositorio. Si tienes uno de prueba (como `housing.csv`), puedes guardarlo en cualquier carpeta de tu ordenador y abrirlo desde el explorador de la aplicación.

Para que funcione correctamente, el archivo debe cumplir lo siguiente:
- Estar en formato CSV (`.csv`), Excel (`.xlsx`, `.xls`) o SQLite (`.sqlite`, `.db`).
- En CSV y Excel, la primera fila tiene que llevar los nombres de las columnas.
- En SQLite, la base de datos debe tener una sola tabla.
- Las columnas que elijas como entrada y salida tienen que ser numéricas (las de texto no sirven para regresión lineal). Si hay celdas vacías, se pueden limpiar desde el paso 4 de la propia app.

## Guía rápida de uso

1. Pulsa **Cargar dataset** y selecciona el archivo. Mientras se lee aparecerá "Cargando..." y los botones se bloquean para evitar errores.
2. Marca las columnas de entrada, elige la columna de salida y confirma la selección.
3. Indica el porcentaje de test y la semilla, y pulsa **Separar datos**.
4. Si hay valores nulos, elige una estrategia de preprocesado y aplícala (no deja crear el modelo mientras queden nulos).
5. Pulsa **Crear modelo** para ver la fórmula, las métricas y el gráfico.
6. Si quieres, añade una descripción y pulsa **Guardar modelo** para guardarlo como archivo `.joblib`.
7. Para abrir un modelo que ya guardaste antes, usa **Cargar modelo**.
8. Para hacer una predicción, rellena los campos numéricos de entrada y pulsa **Realizar predicción**.

## Limitaciones conocidas

- Solo soporta modelos de regresión lineal (simple o múltiple).
- Todas las variables seleccionadas para entrenar el modelo (tanto entradas como salida) deben ser numéricas.

## Documentación

En la carpeta `docs/` está el resto de documentación del proyecto, por ejemplo:
- `docs/prueba_concepto.md`: prueba de concepto de regresión lineal.
- `docs/optimizacion_tabla.md`: técnica de paginación para tablas grandes.

## Pruebas automatizadas

Para lanzar los tests del proyecto:

```bash
uv run pytest
```

## Aviso de seguridad al cargar modelos

Los modelos se guardan y cargan con `joblib` (`.joblib`). Como este formato serializa objetos de Python, abrir un archivo `.joblib` de origen desconocido puede ejecutar código no deseado en tu equipo. Carga únicamente modelos que hayas generado tú o que vengan de alguien de confianza.