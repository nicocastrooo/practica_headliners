# Práctica Headliners - GIA IS

Repositorio oficial del proyecto de desarrollo de software para la asignatura de Ingeniería del Software (GIA - UDC).

> **Estado de la versión:** `v0.2.0`
> Aplicación de escritorio para crear, evaluar, guardar y usar modelos de regresión lineal a partir de un dataset, mediante una interfaz gráfica.

---

## Qué hace la aplicación

La aplicación te guía por el flujo completo de regresión lineal:

1. **Cargar datos:** archivos CSV, Excel (`.xlsx`, `.xls`) y bases de datos SQLite (`.sqlite`, `.db`).
2. **Seleccionar columnas:** variables numéricas de entrada y una variable de salida.
3. **Separar datos:** división aleatoria en entrenamiento y test, indicando el porcentaje de test y una semilla.
4. **Preprocesar:** detección de valores inexistentes (NaN) y cuatro estrategias de tratamiento (eliminar filas, media, mediana o valor constante).
5. **Crear modelo:** regresión lineal simple o múltiple, con su fórmula, las métricas (R² y error cuadrático medio) en entrenamiento y test, y un gráfico del ajuste.
6. **Guardar y cargar modelos:** un modelo se guarda en un archivo `.joblib` junto con su descripción y se puede volver a cargar más tarde.
7. **Realizar predicciones:** con un modelo creado o cargado, introduce un valor para cada variable de entrada y obtén la predicción.

---

## Antes de empezar: cómo abrir la terminal

Todos los comandos de esta guía se escriben en una **terminal**: una ventana de texto donde se teclean órdenes para el ordenador. No hace falta saber nada más, solo abrirla y pegar los comandos.

**Cómo abrirla en Windows**
1. Abre el **Explorador de archivos** y entra en la carpeta donde quieras guardar el proyecto, por ejemplo el **Escritorio**.
2. Haz **clic derecho** en un espacio vacío de la carpeta (no sobre un archivo).
3. Elige **Abrir en Terminal** (en algunas versiones pone "Abrir ventana de PowerShell aquí").

Otra forma: pulsa la **tecla Windows**, escribe `PowerShell` y pulsa **Enter**. Se abre en tu carpeta personal, que también sirve.

**Cómo abrirla en macOS**
Pulsa **Cmd + Espacio**, escribe `Terminal` y pulsa **Enter**.

**Cómo abrirla en Linux**
Pulsa **Ctrl + Alt + T**, o busca "Terminal" en el menú de aplicaciones.

**Cómo usarla**
* Verás una línea de texto que termina en `>` (Windows) o `$` (macOS y Linux). Ahí se escribe.
* **Copia un comando de esta guía, pégalo en la terminal** (clic derecho o `Ctrl + V`) y pulsa **Enter**.
* Ejecuta los comandos **de uno en uno**, en el orden de la guía, y espera a que termine cada uno antes de pegar el siguiente.
* Si un comando da un error en rojo, copia el mensaje completo para poder consultarlo.
* Usa **siempre la misma terminal** durante los pasos 1 a 3, salvo que la guía indique cerrarla y abrir otra.

---

## Requisitos

* **Git**, para descargar el proyecto. Si no lo tienes, instálalo desde <https://git-scm.com/downloads>.
* **uv**, gestor de paquetes de Python. Si no lo tienes, instálalo así:

  Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  macOS y Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  Después de instalarlo, **cierra la terminal y abre una nueva** para que reconozca el comando `uv`. Más información: <https://docs.astral.sh/uv/>.

* **Python 3.12 o superior.** No hace falta instalarlo a mano: `uv` lo descarga automáticamente si no lo encuentra.

---

## Instalación y arranque

### 1. Descargar el proyecto

Abre una terminal (ver el apartado anterior) en la carpeta donde quieras guardar el proyecto, por ejemplo el Escritorio, y ejecuta:

```bash
git clone -b dev https://github.com/nicocastrooo/practica_headliners.git
cd practica_headliners
```

El segundo comando entra en la carpeta del proyecto. Si todo ha ido bien, la línea de la terminal terminará en `practica_headliners`. **Todos los comandos siguientes se ejecutan desde esa carpeta.**

### 2. Instalar las dependencias

```bash
uv sync
```

Crea el entorno virtual e instala todo lo necesario. La primera vez puede tardar un par de minutos.

### 3. Ejecutar la aplicación

```bash
uv run python -m practica_headliners.gui.ventana_principal
```

Se abrirá la ventana de la aplicación.

---

## Datasets de ejemplo

Los datasets **no se incluyen en el repositorio**. Si el equipo te ha entregado uno (por ejemplo `housing.csv`), guárdalo en cualquier carpeta de tu ordenador: la aplicación te deja elegir el archivo desde un explorador.

Para probar el flujo completo se recomienda un dataset con varias columnas numéricas. Las columnas de texto no se pueden usar como variables del modelo.

---

## Guía rápida de uso

1. Pulsa **Cargar dataset** y elige el archivo. Mientras carga verás "Cargando..." y los botones quedan bloqueados.
2. Marca las columnas de **entrada** y elige la columna de **salida**. Confirma la selección.
3. Indica el porcentaje de test y la semilla, y pulsa **Separar datos**.
4. Si aparecen valores inexistentes, elige una estrategia y aplícala. No se puede crear el modelo hasta resolverlos.
5. Pulsa **Crear modelo**. Verás la fórmula, las métricas y el gráfico.
6. Escribe una **descripción** del modelo (opcional, pero recomendable) y pulsa **Guardar modelo**. Elige dónde guardarlo; el archivo tendrá extensión `.joblib`.
7. Para recuperar un modelo guardado, pulsa **Cargar modelo** y elige el archivo.
8. Para predecir, introduce un número en cada campo de entrada y pulsa **Realizar predicción**.

---

## Documentación

La carpeta `docs/` contiene la documentación técnica del proyecto, entre otros:

* `docs/prueba_concepto.md`: prueba de concepto de la regresión lineal.
* `docs/optimizacion_tabla.md`: técnica usada para mostrar tablas grandes.

---

## Ejecutar las pruebas (para desarrolladores)

```bash
uv run pytest
```

---

## Advertencia de seguridad sobre modelos externos

La aplicación utiliza el formato de serialización `.joblib` para guardar y cargar modelos. Debido al diseño interno de este formato en Python, **cargar archivos `.joblib` de fuentes no confiables o desconocidas puede permitir la ejecución de código malicioso en tu ordenador**.

Solo debes cargar modelos generados por ti mismo o descargados de fuentes absolutamente fiables y conocidas.