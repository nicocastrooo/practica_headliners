# Elección de librería para la interfaz gráfica (GUI)

En este documento resumimos la comparativa que hicimos al inicio del proyecto para elegir la librería de interfaz gráfica (#12 - tarea #96) y el problema que nos encontramos al montar el primer prototipo.

## 1. Comparativa de librerías

Probamos y revisamos tres opciones: **Tkinter**, **PySide6** y **Dear PyGui**. Las evaluamos fijándonos en lo que íbamos a necesitar para la aplicación (tablas grandes, selección múltiple, explorador de archivos y gráficos de Matplotlib):

| Criterio | Tkinter | PySide6 | Dear PyGui |
| :--- | :--- | :--- | :--- |
| **Facilidad de uso** | Muy fácil para hacer una ventana rápida, pero en cuanto metes varios paneles el código se vuelve bastante lioso. | Algo más larga de aprender al principio por los layouts y las señales, pero luego queda todo mucho más ordenado. | Diferente a lo habitual (va por frames/renderizado continuo), cuesta un poco hacerse a ella al principio. |
| **Sistemas operativos** | Funciona en Windows, macOS y Linux, aunque la estética cambia bastante de uno a otro y se ve algo anticuada. | Funciona igual de bien en Windows, macOS y Linux con aspecto nativo. | Funciona en los tres, pero tira de GPU (OpenGL/DirectX), lo que en algún portátil o máquina virtual puede dar guerra. |
| **Licencia** | Licencia abierta de Python (PSF), sin problemas. | LGPLv3 (oficial de Qt). Se puede usar gratis sin problema mientras no modifiquemos la librería por dentro. | Licencia MIT, totalmente libre. |
| **Documentación y comunidad** | Muchísima documentación y ejemplos por llevar años en Python. | Muy buena documentación oficial de Qt for Python y muchísima gente usándola. | Documentación correcta, pero comunidad más pequeña y centrada sobre todo en herramientas gráficas o juegos. |
| **Componentes que necesitamos** | Tiene selector de archivos, combos y cuadros de texto, pero **no trae una tabla real** (hay que apañar un `Treeview` con barras de scroll a mano). Sí integra Matplotlib. | Trae todo hecho: `QFileDialog`, tablas completas (`QTableWidget`/`QTableView`) con scroll automático, listas con checkboxes (`QListWidget`), áreas de texto y soporte directo para Matplotlib. | Tiene tablas y combos propios, pero meter dentro gráficas normales de Matplotlib es bastante enrevesado. |
| **Instalación con `uv`** | Ya viene con Python (aunque en algunos Linux hay que instalar `python3-tk` aparte). | Se instala directo con `uv add PySide6` sin configurar nada más. | Se instala con `uv add dearpygui`. |

## 2. Decisión final: PySide6

Nos quedamos con **PySide6** y la añadimos al proyecto con `uv add PySide6`.

Descartamos Dear PyGui porque encajar las gráficas de Matplotlib nos iba a complicar innecesariamente, y descartamos Tkinter porque tener que construir una tabla con scroll horizontal y vertical para datasets de 20.000 filas a base de parches en `Treeview` iba a dar muchos problemas.

Con PySide6 tenemos todos los widgets listos de serie, podemos agrupar cada paso de la aplicación en bloques (`QGroupBox`) que se activan o desactivan según avanza el usuario, e incrustar el gráfico de Matplotlib directamente en la ventana sin abrir ventanas externas. Además, al instalarse por `uv`, nos aseguramos de que a todos en el grupo nos funciona igual.

## 3. Problemas en el prototipo y cómo los resolvimos

Al hacer la prueba de concepto en la carpeta `prototipos/` nos topamos con tres cosas que tuvimos que ajustar antes de pasar a programar la app real:

- **Sincronización de dependencias:** Al meter `PySide6` junto con `pandas` y `matplotlib`, tuvimos que actualizar el `uv.lock` y hacer `uv sync` en los ordenadores de todos para evitar conflictos de versiones con Python 3.12.