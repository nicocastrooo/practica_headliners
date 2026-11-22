## Prueba de usabilidad de caja negra

Documento de la tarea #142, historia de usuario #37 (Mejora de la interfaz gráfica).

## 1. Objetivo

Comprobar que una persona ajena al proyecto puede usar la aplicación siguiendo únicamente el `README.md`, sin ayuda del equipo, y detectar los puntos donde se atasca o duda.

## 2. Participante

| Dato | Valor |
|---|---|
| Participante | Hugo, amigo del equipo ajeno a la carrera |
| Conocimiento previo del proyecto | Ninguno |
| Observador | Samuel Piñeiro |
| Fecha de la prueba | 16/11/2026 |
| Versión probada | `c3dedd4` |

## 3. Método

Se entregó al participante:
- El enlace del repositorio.
- El archivo `housing.csv` (dataset de California Housing, 20.640 filas), facilitado a mano por el equipo porque los datasets no se incluyen en el repositorio.
- La lista de tareas, sin indicaciones sobre cómo realizarlas.

Tareas pedidas:
1. Instalar el entorno y abrir la aplicación siguiendo solo el `README.md`.
2. Cargar el dataset.
3. Crear un modelo de regresión lineal.
4. Guardar el modelo.
5. Volver a cargar el modelo guardado.
6. Cambiar la descripción del modelo.
7. Hacer una predicción con valores inventados.

El observador no dio indicaciones durante la prueba, salvo en el momento descrito en el problema 2 de la sección 5, en el que tuvo que intervenir para que el participante pudiera continuar.

## 4. Resultados

El participante completó las 7 tareas, pero **no de forma totalmente autónoma**: en el problema 2 el observador tuvo que intervenir. Al margen de los dos problemas de la sección 5, no hubo dificultades: la carga del dataset de 20.640 filas, la creación del modelo, el guardado, la carga del modelo guardado, el cambio de descripción y la predicción se realizaron sin incidencias.

## 5. Problemas observados y cambios realizados

| Nº | Problema observado | Gravedad | Solución | Estado |
|---|---|---|---|---|
| 1 | El README no explica dónde ni cómo abrir la terminal. El participante no sabía por dónde empezar. | Alta | Nuevo apartado "Antes de empezar: cómo abrir la terminal" en el README, con los pasos para Windows, macOS y Linux y cómo usarla. Commit `b5c9f75`. | Resuelto |
| 2 | Al seguir el README, el participante clonó la rama `main`, que no contiene las últimas funciones (descripción, cargar modelo, predicción), y la aplicación no le funcionaba como esperaba. **El observador tuvo que intervenir** y le indicó que cambiara a la rama `dev` para que pudiera seguir. | Alta | El comando de clonado del README pasa a usar la rama `dev`: `git clone -b dev <url>`. Commit `b5c9f75`. | Resuelto (provisional) |

Nota sobre el problema 2: la solución es provisional. Cuando el equipo publique una release en `main` con estas funciones, habrá que quitar `-b dev` del README.

## 6. Observaciones de la revisión interna

Al repetir el recorrido en una copia limpia del proyecto, el observador detectó además los siguientes puntos. No los encontró el participante externo y siguen **pendientes** de decisión del equipo:

| Nº | Observación | Propuesta |
|---|---|---|
| A | El campo "Semilla aleatoria" no explica su significado. | Añadir un texto de ayuda, por ejemplo "Semilla aleatoria (para repetir el mismo reparto)". |
| B | El formulario de predicción no indica las unidades de cada entrada (por ejemplo, `median_income` está en decenas de miles de dólares). | Mostrar las unidades o una breve descripción junto a cada campo. |
| C | La fórmula del modelo tiene un color fijo (azul oscuro) que se lee mal con el tema oscuro del sistema. | Quitar el color fijo para que el texto use el del tema. |

## 7. Conclusiones

- Una persona ajena al proyecto pudo completar el flujo completo de la aplicación, pero necesitó una intervención del observador por un problema que estaba en la documentación y no en la aplicación.
- Los dos obstáculos encontrados fueron de contexto de partida (dónde abrir la terminal y qué rama clonar), no de la interfaz.
- Tras los cambios del README, el criterio de usar la aplicación solo con el `README.md` debe volver a comprobarse. Se recomienda repetir la prueba con otro participante cuando se publique la release en `main` y se resuelvan los puntos pendientes de la sección 6.