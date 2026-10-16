# Normas de Contribución del Equipo

Para trabajar de forma ordenada en este proyecto y cumplir con los estándares de Ingeniería del Software, todos los integrantes seguimos estas pautas:

## 1. Ramas y Convención de Commits
- **Prohibido** hacer commits directos sobre la rama `main`.
- Crea una rama específica para cada tarea de Taiga siguiendo estrictamente el formato: 
  `feature/<numero>-<descripcion>`, `fix/<numero>-<descripcion>` o `docs/<numero>-<descripcion>`.
- Los mensajes de commit deben seguir el estándar **Conventional Commits** en imperativo y sin punto final (ej. `feat(#91): añade normas de contribucion` o `docs(#91): documenta el manual de usuario`).

## 2. Pruebas Automatizadas (pytest) y Datos
- Todas las pruebas se ejecutan desde la raíz con el comando:
  uv run pytest
Cero archivos de datos o modelos en el repositorio: Las pruebas no deben usar archivos estáticos guardados en el disco ni en data/. Los datos necesarios se definen directamente en el código de la prueba.

Si una prueba necesita ficheros (CSV, Excel o SQLite), debe crearlos dinámicamente en una carpeta temporal utilizando la fixture tmp_path de pytest, que se elimina automáticamente al finalizar.

## 3. Reglas de Fusión y GitHub Actions
Antes de fusionar cualquier rama de trabajo en dev, el desarrollador debe actualizar su rama con los últimos cambios de dev y ejecutar todas las pruebas en local. Solo se fusiona si todas pasan.

La rama dev solo se podrá fusionar en main si todas las pruebas pasan correctamente en la pipeline de la nube.

Ningún cambio se integrará si las pruebas automatizadas de GitHub Actions devuelven error.

## 4. Revisiones
Al terminar una tarea, se puede abrir un Pull Request para que los compañeros revisen el código antes de integrarlo en la rama de desarrollo común.

4. Revisiones
Al terminar una tarea, se puede abrir un Pull Request para que los compañeros revisen el código antes de integrarlo en la rama de desarrollo común.
