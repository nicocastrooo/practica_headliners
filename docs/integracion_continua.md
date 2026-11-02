# Documentación de Integración Continua (GitHub Actions)

## 1. ¿Cuándo se ejecuta el workflow?
El flujo de integración continua está configurado para ejecutarse automáticamente en cada `push` subido a cualquier rama del repositorio GitHub.

## 2. Explicación paso a paso del archivo YAML (`.github/workflows/ci.yml`)

- `name`: Define el nombre visible del flujo de trabajo en GitHub Actions.
- `on: [push]`: Especifica el evento desencadenante; se ejecuta automáticamente con cada subida a cualquier rama.
- `jobs`: Agrupa la secuencia de ejecuciones.
  - `build-and-test`: Nombre del trabajo de pruebas.
  - `runs-on: ubuntu-latest`: Define el entorno de ejecución (máquina virtual Linux con Ubuntu).
  - `steps`: Lista de pasos que se ejecutan en orden secuencial:
    1. **Checkout del código (`actions/checkout@v4`)**: Descarga el código del repositorio en la máquina virtual.
    2. **Instalación de uv (`astral-sh/setup-uv@v5`)**: Configura el gestor de paquetes `uv` en el runner.
    3. **Instalación de dependencias (`uv sync --locked`)**: Instala las dependencias exactamente según el archivo `uv.lock`. Si el archivo de bloqueo no está actualizado respecto a `pyproject.toml`, la ejecución falla inmediatamente.
    4. **Ejecución de pruebas (`uv run pytest`)**: Ejecuta toda la suite de pruebas del proyecto.

## 3. Consultar resultados en GitHub Actions
1. Ve a la pestaña **Actions** en el repositorio de GitHub.
2. En el panel izquierdo, selecciona el workflow **CI** o la rama específica.
3. Haz clic en la ejecución correspondiente al último commit.
4. Si la ejecución muestra un **check verde (✔)**, todas las pruebas pasaron correctamente.
5. Si muestra una **X roja (✖)**, haz clic en el trabajo `build-and-test` para expandir la consola web y ver exactamente qué prueba o paso ha fallado y en qué línea de código.

## 4. Resolución de discrepancias: Entorno Local vs GitHub Actions
Si un test pasa en local pero falla en GitHub Actions:
- **Falta de archivos locales**: Comprobar si el test lee archivos (ej. en `data/`) ignorados en `.gitignore`. Solución: incluir datos de prueba mockeados o no depender de rutas locales absolutas.
- **Diferencias de Sistema Operativo (Rutas / Filenames)**: En Windows no influyen las mayúsculas/minúsculas en rutas, pero en el servidor Linux (`ubuntu-latest`) sí. Solución: usar `pathlib.Path`.
- **Servidor sin pantalla (Headless)**: Si un módulo de interfaz gráfica intenta inicializarse durante la importación o prueba, fallará en el servidor. Solución: ejecutar pruebas en modo headless o usar mockeos para los componentes gráficos.