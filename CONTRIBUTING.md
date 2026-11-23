# Guía de contribución (CONTRIBUTING.md)

Aquí dejamos anotadas las normas con las que trabajamos en el repositorio: cómo organizamos las ramas, el estilo de código, el uso de `uv`, las pruebas y los pasos para sacar una release.

## 1. Uso del repositorio y datos locales

- **No se suben datos ni modelos al repositorio:** Nunca hay que añadir a Git datasets (`.csv`, `.xlsx`, `.xls`, `.db`, `.sqlite`) ni modelos guardados (`.joblib`, `.pkl`).
- **Carpeta local `data/`:** Todos los archivos de prueba y modelos que generemos en local se guardan en la carpeta `data/` en la raíz del proyecto. Esa carpeta está en el `.gitignore` para que no se cuele nada por error.
- **Comprobación antes del commit:** Antes de hacer `git add` o `git commit`, conviene echar un ojo a `git status` para asegurarse de que no se está subiendo ningún archivo de datos ni temporal.

## 2. Modelo de ramas

Trabajamos con dos ramas fijas y ramas cortas para cada tarea:

- `main`: Solo contiene código estable de versiones publicadas (releases). Está protegida en GitHub y no se pueden hacer commits ni pushes directos.
- `dev`: Rama de integración donde vamos juntando las tareas terminadas antes de cada release. Tampoco se hacen commits directos aquí.
- **Ramas de trabajo:** Cada tarea de Taiga se hace en su propia rama, creada siempre desde `dev` actualizada (`git pull origin dev`):
  - Funcionalidades nuevas: `feature/<num-tarea>-<descripcion-corta>` (por ejemplo, `feature/121-gui-modelo`)
  - Corrección de errores: `fix/<num-tarea>-<descripcion-corta>` (por ejemplo, `fix/110-casos-limite-preprocesado`)
  - Documentación: `docs/<num-tarea>-<descripcion-corta>` (por ejemplo, `docs/148-contributing-inventario`)

Una vez fusionada una rama en `dev`, **no la borramos** de GitHub para mantener visible el historial de trabajo de cada tarea.

## 3. Estilo de código (PEP 8)

- Todo el código Python en `src/` y `tests/` sigue PEP 8 con un máximo de **79 caracteres por línea**.
- Nombres: `snake_case` para variables, funciones y módulos; `CamelCase` para clases; `MAYUSCULAS_CON_GUIONES` para constantes.
- Docstrings y comentarios: Las funciones públicas de los módulos de lógica llevan docstring explicando qué hacen, qué parámetros reciben, qué devuelven y qué errores pueden lanzar. Los comentarios sueltos los dejamos solo para aclarar cosas que no sean obvias.
- **Formateo con `autopep8`:** Tenemos la configuración en `[tool.autopep8]` dentro de `pyproject.toml` (`max_line_length = 79`, `in-place = true`, `recursive = true`, `aggressive = 1`). Antes de hacer commit, pasamos el formateador a lo que hayamos tocado:

```bash
uv run autopep8 src/ tests/
```

O solo sobre un archivo concreto:

```bash
uv run autopep8 src/practica_headliners/ruta_al_archivo.py
```

## 4. Mensajes de commit

Seguimos el formato de Conventional Commits añadiendo el número de tarea de Taiga:

```text
<tipo>: #<num-tarea> <descripción breve en minúsculas>
```

Los tipos que usamos son:
- `feat`: funcionalidad nueva (ej. `feat: #138 añade seccion de prediccion en la gui`)
- `fix`: corrección de un fallo (ej. `fix: #110 rechaza valores no finitos en constante`)
- `docs`: cambios en documentación (ej. `docs: #148 actualiza contributing e inventario en docs`)
- `refactor`: reorganización de código sin cambiar lo que hace (ej. `refactor: #118 simplifica validacion del modelo`)
- `test`: pruebas automatizadas nuevas o actualizadas (ej. `test: #104 añade pruebas unitarias de validacion de columnas`)

## 5. Dependencias y entorno con `uv`

Gestionamos Python (`>=3.12`) y las librerías con `uv`. No usamos `pip install` a mano.

- Sincronizar el entorno al clonar o al bajarse cambios:
  ```bash
  uv sync
  ```
- Añadir una librería de la aplicación:
  ```bash
  uv add <paquete>
  ```
- Añadir una librería solo para desarrollo (tests, formateo, etc.):
  ```bash
  uv add --dev <paquete>
  ```
- **Archivo `uv.lock`:** Siempre que cambie `pyproject.toml`, hay que subir también `uv.lock` en el mismo commit. GitHub Actions lanza `uv sync --locked` y fallará si no coinciden.
- Arrancar la aplicación en local:
  ```bash
  uv run python -m practica_headliners.gui.ventana_principal
  ```

## 6. Pruebas automatizadas

Las pruebas están en `tests/` y se lanzan con:

```bash
uv run pytest -v
```

- **Nada de leer de `data/`:** Los tests no pueden depender de archivos locales de `data/`. Si un test necesita un dataset o un archivo temporal, se crea en memoria o usando `tmp_path` de `pytest`.
- Cada funcionalidad nueva en los módulos de lógica tiene que llevar sus tests unitarios.

## 7. Integración continua (GitHub Actions) y reglas de fusión

El flujo de CI está en `.github/workflows/ci.yml` (y explicado con más detalle en `docs/integracion_continua.md`). Cada vez que hacemos `push` a cualquier rama, GitHub Actions levanta un entorno Ubuntu con las librerías de PySide6 y `xvfb`, instala las dependencias con `uv sync --locked` y ejecuta `xvfb-run -a uv run pytest -v`.

Reglas para fusionar cambios:
1. **De rama de trabajo a `dev`:** Solo se fusiona una rama (`feature/`, `fix/` o `docs/`) si los tests pasan en local (`uv run pytest -v`) y el último check de GitHub Actions está en verde.
2. **Revisión antes de integrar:** Se puede fusionar mediante Pull Request en GitHub o haciendo `git merge` en local sobre `dev` actualizada, comprobando antes que el código cumple PEP 8, que no se cuelan archivos de `data/`, que los commits siguen el formato y que los tests pasan.
3. **Si `dev` se rompe:** Después de cada fusión comprobamos que Actions sigue en verde en `dev`. Si falla, se abre una tarea en Taiga y se arregla en una rama `fix/` antes de seguir metiendo otras ramas.
4. **De `dev` a `main`:** Solo se hace para publicar una release, cuando `dev` está en verde, y obligatoriamente mediante Pull Request en GitHub con aprobación de otro compañero.

## 8. Cómo hacer una release

Para publicar una nueva versión (tanto pre-releases como la versión final `v1.0.0`), seguimos estos pasos:

### 1. Comprobaciones previas
- Confirmar que todas las historias de usuario y la documentación del hito están en `dev` y que GitHub Actions está en verde.
- Revisar que no haya ningún dataset ni modelo guardado en el repositorio.
- Comprobar que el campo `version` (y `description`) en `pyproject.toml` tiene el número de versión correcto (por ejemplo, `"1.0.0"`). Si hace falta cambiarlo, se hace en una rama desde `dev`, actualizando `pyproject.toml` y `uv.lock`, y se fusiona en `dev` antes de seguir.

### 2. Pull Request de `dev` a `main` en GitHub
Como la rama `main` está protegida, no se fusiona desde el ordenador ni se hace `git push origin main`:
1. En GitHub, ir a la pestaña **Pull requests** y pulsar **New pull request**.
2. Elegir `base: main` y `compare: dev`, poner un título claro (por ejemplo, `Release v1.0.0`) y crear el Pull Request.
3. Esperar a que pasen los checks de GitHub Actions y pedir a otro miembro del equipo que revise y apruebe el PR (**Approve**).
4. Una vez aprobado, pulsar **Merge pull request** directamente en GitHub.

### 3. Crear la etiqueta (tag)
Con `main` ya actualizada en GitHub, nos bajamos los cambios en local y subimos la etiqueta anotada (cambiando `v1.0.0` por la versión que toque):

```bash
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Versión 1.0.0"
git push origin v1.0.0
```

### 4. Publicar en GitHub Releases
1. Ir a **Releases** en GitHub y pulsar **Draft a new release**.
2. Seleccionar la etiqueta que acabamos de subir (`v1.0.0`), poner el título y escribir las notas de la versión (qué incluye, requisitos y limitaciones conocidas).
3. Marcar **Set as a pre-release** solo si es una versión preliminar (`v0.x.y`); para la versión final (`v1.0.0`) dejarla sin marcar.
4. Pulsar **Publish release**.

### 5. Comprobación final
Para cerrar el proceso, probar a clonar el repositorio desde `main` en una carpeta limpia y comprobar que `uv sync` y el arranque de la app funcionan siguiendo únicamente las instrucciones del `README.md`.