# Guía de Contribución (`CONTRIBUTING.md`)

Este documento recoge las normas de uso del repositorio, estilo de código, pruebas, integración continua y publicación que sigue el equipo.

---

## 1. Uso del Repositorio y Prohibición de Subir Datos

- **Prohibido subir archivos de datos o modelos al repositorio:** Nunca se deben añadir a Git datasets (`.csv`, `.xlsx`, `.xls`, `.db`, `.sqlite`) ni modelos entrenados guardados (`.joblib`, `.pkl`).
- **Uso de la carpeta local `data/`:** Todos los datasets de prueba y modelos generados localmente deben guardarse dentro de la carpeta `data/` en la raíz del proyecto. Esta carpeta está excluida en `.gitignore` para evitar que se suban datos por error.
- **Revisión previa al commit:** Antes de ejecutar `git add` o `git commit`, revisa siempre `git status` para confirmar que no se ha incluido ningún archivo de datos ni temporal.

---

## 2. Modelo de Ramas

El repositorio cuenta con dos ramas permanentes y ramas de trabajo de vida corta:

- **`main`:** Contiene únicamente código estable correspondiente a versiones publicadas (*releases*). **Está prohibido hacer commits directos en `main`.**
- **`dev`:** Rama de integración donde se reúne el trabajo completado antes de cada *release*. **Está prohibido hacer commits directos en `dev`.**
- **Ramas de trabajo:** Cada tarea se desarrolla en una rama creada siempre desde `dev` actualizada (`git pull origin dev`), siguiendo esta nomenclatura:
  - Nuevas funcionalidades: `feature/<num-tarea>-<descripcion-corta>` (ej. `feature/121-gui-modelo`)
  - Corrección de errores: `fix/<num-tarea>-<descripcion-corta>` (ej. `fix/110-casos-limite-preprocesado`)
  - Documentación: `docs/<num-tarea>-<descripcion-corta>` (ej. `docs/148-contributing-inventario`)
- **Conservación de ramas:** Una vez fusionadas en `dev`, **las ramas de trabajo no se eliminan** del repositorio en GitHub para conservar la trazabilidad del historial del proyecto.

---

## 3. Estilo de Código (PEP 8)

- Todo el código Python en `src/` y `tests/` sigue la guía **PEP 8**, con un límite máximo de **79 caracteres por línea**.
- **Nomenclatura:** `snake_case` para variables, funciones y módulos; `CamelCase` para clases; `MAYUSCULAS_CON_GUIONES` para constantes.
- **Docstrings y comentarios:** Las funciones públicas de los módulos de lógica deben incluir un *docstring* indicando qué hacen, sus parámetros, qué devuelven y qué excepciones pueden lanzar. Los comentarios en línea se usan solo para explicar decisiones no evidentes.
- **Formateo automático con `autopep8`:** La configuración del formateador está definida en `[tool.autopep8]` dentro de `pyproject.toml` (`max_line_length = 79`, `in-place = true`, `recursive = true`, `aggressive = 1`). Antes de hacer commit, formatea los archivos modificados con:

```bash
uv run autopep8 src/ tests/
```

O sobre un archivo concreto:

```bash
uv run autopep8 src/practica_headliners/ruta_al_archivo.py
```

---

## 4. Formato de los Mensajes de Commit

Los mensajes de commit siguen **Conventional Commits** e incluyen el número de tarea de Taiga:

```text
<tipo>: #<num-tarea> <descripción breve en minúsculas>
```

Tipos utilizados en el proyecto:
- `feat:` Nueva funcionalidad (ej. `feat: #138 añade seccion de prediccion en la gui`)
- `fix:` Corrección de errores (ej. `fix: #110 rechaza valores no finitos en constante`)
- `docs:` Cambios en la documentación (ej. `docs: #148 actualiza contributing e inventario en docs`)
- `refactor:` Mejora interna del código sin alterar su comportamiento (ej. `refactor: #118 simplifica validacion del modelo`)
- `test:` Creación o actualización de pruebas automatizadas (ej. `test: #104 añade pruebas unitarias de validacion de columnas`)

---

## 5. Gestión de Dependencias con `uv`

El proyecto gestiona el entorno virtual y las dependencias mediante **`uv`** (Python `>=3.12`). **No se debe usar `pip install` directamente.**

- **Sincronizar el entorno** tras clonar o actualizar la rama:
  ```bash
  uv sync
  ```
- **Añadir una dependencia de la aplicación:**
  ```bash
  uv add <paquete>
  ```
- **Añadir una dependencia de desarrollo** (pruebas, formateadores, etc.):
  ```bash
  uv add --dev <paquete>
  ```
- **Archivo de bloqueo (`uv.lock`):** Siempre que se modifique `pyproject.toml`, deben incluirse tanto `pyproject.toml` como `uv.lock` en el mismo commit. GitHub Actions ejecuta `uv sync --locked` y fallará si ambos archivos no coinciden.
- **Ejecutar la aplicación en desarrollo:**
  ```bash
  uv run python src/practica_headliners/gui/ventana_principal.py
  ```

---

## 6. Ejecución de las Pruebas Automatizadas

- Todas las pruebas se encuentran en la carpeta `tests/` y se ejecutan con `pytest` a través de `uv`:
  ```bash
  uv run pytest -v
  ```
- **Sin dependencias de `data/`:** Los tests nunca deben leer archivos de la carpeta local `data/`. Cualquier archivo o dataset de prueba debe generarse en memoria o mediante el *fixture* `tmp_path` de `pytest`.
- Toda funcionalidad nueva en los módulos de lógica debe incluir sus pruebas unitarias correspondientes.

---

## 7. Integración Continua (GitHub Actions) y Reglas de Fusión

El flujo de CI está definido en `.github/workflows/ci.yml` y explicado en [`docs/integracion_continua.md`](docs/integracion_continua.md). Con cada `push` a cualquier rama, GitHub Actions prepara un entorno `ubuntu-latest` con las librerías del sistema para PySide6 y `xvfb`, configura Python según `.python-version`, sincroniza las dependencias con `uv sync --locked` y ejecuta `xvfb-run -a uv run pytest -v`.

### Reglas de integración
1. **Fusión de ramas de trabajo en `dev`:** Una rama (`feature/`, `fix/` o `docs/`) solo se fusiona en `dev` si las pruebas pasan en local (`uv run pytest -v`) **y** su última ejecución en GitHub Actions ha terminado correctamente (check verde).
2. **Modalidad de fusión y revisión:** Se admite tanto abrir un **Pull Request** en GitHub como realizar una **fusión local** (`git merge` sobre `dev` actualizada), siempre que no afecte negativamente al proyecto y se compruebe antes de integrar que:
   - El código cumple PEP 8 y mantiene nombres claros.
   - No se han incluido archivos de datos (`data/`) ni modelos guardados.
   - Los mensajes de commit siguen el formato acordado.
   - Las pruebas automatizadas pasan en local y en GitHub Actions.
3. **Mantenimiento de `dev`:** Después de cada fusión en `dev`, se comprueba que GitHub Actions sigue terminando en verde. Si falla, se crea inmediatamente una tarea de corrección en Taiga y se resuelve en una rama `fix/` antes de fusionar cualquier otra rama.
4. **Fusión a `main`:** La rama `dev` solo se fusiona en `main` si su última ejecución en GitHub Actions ha terminado en verde y se va a publicar una nueva *release*.

---

## 8. Procedimiento de Release

Para publicar una nueva versión del proyecto (tanto *pre-releases* como la versión final `v1.0.0`), cualquier miembro del equipo debe seguir estos pasos:

### 1. Requisitos previos y revisión de versión
- Verificar que todas las historias de usuario y la documentación del hito están fusionadas en `dev` y que la pipeline de GitHub Actions está en verde.
- Comprobar que el repositorio no contiene archivos de datos ni modelos guardados.
- Comprobar que el campo `version` (y `description`) en `pyproject.toml` refleja la versión a publicar (ej. `"1.0.0"`). Si requiere cambios, crear una rama desde `dev`, actualizar `pyproject.toml` y `uv.lock`, y fusionarla en `dev` antes de continuar.

### 2. Fusión en `main` y etiquetado (`tag`)
Llevar el código estable a la rama principal y crear la etiqueta anotada (sustituye `v1.0.0` por la versión correspondiente):

```bash
git checkout main
git pull origin main
git merge dev
git tag -a v1.0.0 -m "Versión 1.0.0"
git push origin main
git push origin v1.0.0
```

### 3. Publicación en GitHub Releases
1. Ir a la pestaña **Releases** del repositorio en GitHub y pulsar **Draft a new release**.
2. Seleccionar la etiqueta creada (`v1.0.0`), indicar el título y redactar las notas de la versión (funcionalidades incluidas, requisitos y limitaciones conocidas).
3. Marcar **Set as a pre-release** solo en versiones preliminares (`v0.x.y`); dejarla **desmarcada** para la versión final (`v1.0.0`).
4. Pulsar **Publish release**.

### 4. Comprobación posterior
Tras publicar la *release*, verificar en una instalación limpia desde `main` que `uv sync` instala el entorno sin errores y que la aplicación arranca y funciona siguiendo únicamente el `README.md`.