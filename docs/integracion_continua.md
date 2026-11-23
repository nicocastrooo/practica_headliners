# Documentación de Integración Continua (GitHub Actions)

## 1. ¿Cuándo se ejecuta el workflow?
El flujo de integración continua (**Integración Continua (CI)**) está configurado para ejecutarse automáticamente en cada `push` subido a cualquier rama del repositorio (`branches: [ "**" ]`).

## 2. Explicación paso a paso del archivo `.github/workflows/ci.yml`

- `name: Integración Continua (CI)`: Define el nombre visible del flujo de trabajo en GitHub Actions.
- `on: push: branches: [ "**" ]`: Desencadena el workflow automáticamente al subir commits a cualquier rama (`main`, `dev`, `feature/`, `fix/`, `docs/`).
- `jobs`:
  - `test` (`name: Pruebas automatizadas`): Trabajo encargado de preparar el entorno y ejecutar toda la batería de pruebas.
  - `runs-on: ubuntu-latest`: Entorno virtual Linux (Ubuntu) donde se ejecuta la verificación.
  - `steps`: Pasos ejecutados en orden secuencial:
    1. **Descargar el código (`actions/checkout@v4`)**: Descarga el código de la rama en la máquina virtual.
    2. **Instalar dependencias del sistema para PySide6 y Xvfb**: Instala con `apt-get` el servidor gráfico virtual `xvfb` y las librerías de sistema necesarias para Qt/PySide6 (`libxkbcommon-x11-0`, `libxcb-*`, `libegl1`, `libgl1`).
    3. **Instalar `uv` y caché (`astral-sh/setup-uv@v5`)**: Instala `uv` activando la caché de dependencias vinculada a `uv.lock` (`enable-cache: true`).
    4. **Configurar Python (`actions/setup-python@v5`)**: Selecciona automáticamente la versión de Python definida en `.python-version`.
    5. **Instalar dependencias bloqueadas (`uv sync --locked`)**: Instala las dependencias exactamente según `uv.lock`. Si `uv.lock` no está actualizado respecto a `pyproject.toml`, la ejecución falla inmediatamente.
    6. **Ejecutar pruebas (`xvfb-run -a uv run pytest -v`)**: Lanza toda la suite de pruebas en modo detallado (`-v`) dentro de un entorno gráfico virtual con `xvfb-run`, permitiendo ejecutar pruebas que importan o instancian componentes de PySide6 sin pantalla física.

## 3. Consultar resultados en GitHub Actions
1. Ve a la pestaña **Actions** en el repositorio de GitHub.
2. En el panel izquierdo, selecciona el workflow **Integración Continua (CI)**.
3. Haz clic en la ejecución correspondiente al último commit.
4. Si muestra un **check verde (✔)**, todas las pruebas pasaron correctamente.
5. Si muestra una **X roja (✖)**, haz clic en el trabajo **Pruebas automatizadas** (`test`) para desplegar los logs del paso fallido y revisar el detalle del error.

## 4. Resolución de discrepancias: Entorno Local vs GitHub Actions
Si una prueba pasa en local pero falla en GitHub Actions:
- **Dependencias desincronizadas (`uv sync --locked`)**: Si se añadió una librería sin subir `uv.lock`, la sincronización fallará. Solución: ejecutar `uv sync` y subir tanto `pyproject.toml` como `uv.lock`.
- **Dependencia de archivos locales**: Comprobar si algún test intenta leer archivos de `data/` (ignorados en `.gitignore`). Solución: crear siempre los datos de prueba en memoria o usando el *fixture* `tmp_path`.
- **Diferencias de sistema operativo (Windows vs Linux)**: Linux distingue mayúsculas y minúsculas en rutas y nombres de archivo. Solución: usar `pathlib.Path` y respetar exactamente las mayúsculas.
- **Componentes gráficos sin pantalla (*headless*)**: El workflow ejecuta `pytest` bajo `xvfb-run -a`, pero las pruebas no deben quedar bloqueadas esperando interacción manual en diálogos (`QMessageBox`, `QFileDialog`); usa *mocks* o `monkeypatch` al probar componentes interactivos.