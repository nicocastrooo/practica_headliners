# Normas de Contribución del Equipo

Para trabajar de forma ordenada en este proyecto, todos los integrantes seguimos estas pautas:

## 1. Ramas y Commits
- No hagas commits directos sobre la rama `main` o `master`.
- Crea una rama para cada tarea con el formato: `feature/nombre-tarea` o `fix/nombre-tarea`.
- Incluye el número de tarea de Taiga en el mensaje del commit (ejemplo: `feat: #91 agregadas normas de contribucion`).

## 2. Pruebas y Calidad
- Antes de subir tus cambios, pasa las pruebas en tu equipo ejecutando `pytest`.
- Ningún cambio se integrará si las pruebas automatizadas de GitHub Actions fallan.

## 3. Revisiones
- Al terminar una tarea, abre un Pull Request para que otro compañero pueda revisar el código antes de unirlo a la rama principal.

## Procedimiento de Release

Para publicar una nueva versión del proyecto, cualquier miembro del equipo debe seguir estrictamente estos pasos:

**1. Requisitos Previos y Revisión de Versión**
* Verificar que todas las historias del Epic correspondiente están fusionadas en `dev` y que la pipeline de GitHub Actions está en verde (`uv run pytest`).
* Comprobar que el campo `version` en `pyproject.toml` está actualizado (ej. `"0.2.0"`). Si requiere cambios, crear una rama desde `dev` para corregirlo.

**2. Fusión en main y Etiquetado (Tag)**
Llevar el código estable a la rama principal y crear la etiqueta anotada:
```bash
git checkout main
git pull origin main
git merge dev
git tag -a v0.2.0 -m "Versión 0.2.0"
git push origin main
git push origin v0.2.0