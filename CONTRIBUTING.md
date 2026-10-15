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